from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, SignupForm, AccountUpdateForm
from .models import Exercise, ExerciseAlternative, Bookmark, MuscleGroup, Muscle
from collections import OrderedDict

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignupForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def account_detail(request):
    bookmarks = (
        Bookmark.objects.filter(user=request.user)
        .select_related("exercise")
        .order_by("-created_at")
    )
    return render(
        request,
        "dex/account_detail.html",
        {"bookmarks": bookmarks},
    )

@login_required
def account_edit(request):
    if request.method == "POST":
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("account_detail")
    else:
        form = AccountUpdateForm(instance=request.user)
    return render(request, "dex/account_edit.html", {"form": form})


@login_required
def toggle_bookmark(request, slug):
    exercise = get_object_or_404(Exercise, slug=slug)

    bookmark, created = Bookmark.objects.get_or_create(
        user = request.user,
        exercise = exercise
    )
    if not created:
        bookmark.delete()
    
    return redirect("exercise_detail", slug=exercise.slug)

def home(request):
    popular_exercises = Exercise.objects.order_by("-view_count")[:3]

    bookmarks = []
    if request.user.is_authenticated:
        bookmarks = (
            Bookmark.objects.filter(user=request.user)
            .select_related("exercise")
            .order_by("-created_at")[:6]
        )
    
    context = {
        "popular_exercises": popular_exercises,
        "bookmarks": bookmarks,
    }
    return render(request, "dex/home.html", context)

def exercise_list(request):
    q = request.GET.get("q", "").strip()
    pm_ids = request.GET.getlist("primary_muscle")
    group_ids = request.GET.getlist("muscle_group")
    equipments = request.GET.getlist("equipment")

    exercises = Exercise.objects.all().prefetch_related(
        "primary_muscles__group"
    )

    if q:
        exercises = exercises.filter(
            Q(name__icontains=q)
            | Q(english_name__icontains=q)
            | Q(primary_muscles__name__icontains=q)
        )
    
    if pm_ids:
        exercises = exercises.filter(primary_muscles__id__in=pm_ids)
    
    if group_ids:
        exercises = exercises.filter(primary_muscles__group__id__in=group_ids)
    
    if equipments:
        exercises = exercises.filter(equipment__in=equipments)

    exercises = exercises.distinct()


    grouped = OrderedDict()
    uncategorized = []
    for ex in exercises:
        groups = []
        seen = set()
        for m in ex.primary_muscles.all():
            if m.group_id in seen:
                continue
            seen.add(m.group_id)
            groups.append(m.group)

        if not groups:
            uncategorized.append(ex)
            continue

        for g in sorted(groups, key=lambda x: (x.sort_order, x.name)):
            grouped.setdefault(g, []).append(ex)
    
    grouped_exercises = sorted(
        grouped.items(),
        key=lambda item: (item[0].sort_order, item[0].name)
    )

    muscle_groups = MuscleGroup.objects.order_by("sort_order", "name")
    primary_muscles = Muscle.objects.select_related("group").order_by("group__sort_order", "sort_order", "name")
    equipment_choices = Exercise._meta.get_field("equipment").choices


    context = {
        "grouped_exercises": grouped_exercises,
        "uncategorized": uncategorized,
        "q": q,
        "muscle_groups": muscle_groups,
        "primary_muscles": primary_muscles,
        "equipment_choices": equipment_choices,
        "selected_groups": group_ids,
        "selected_muscles": pm_ids,
        "selected_equipment": equipments,
    }
    return render(request, "dex/exercise_list.html", context)

def exercise_detail(request, slug):
    exercise = get_object_or_404(
        Exercise.objects.select_related("base_exercise").prefetch_related(
            "primary_muscles",
            "secondary_muscles",
            "videos",
            "comments__user",
        ),
        slug=slug,
    )

    # view_count increment
    Exercise.objects.filter(pk=exercise.pk).update(view_count=F("view_count") + 1)

    # variants (器具切替)
    if exercise.base_exercise:
        variant_qs = exercise.base_exercise.variants.exclude(pk=exercise.pk)
    else:
        variant_qs = exercise.variants.all()

    # alternatives (双方向)
    from_qs = ExerciseAlternative.objects.filter(from_exercise=exercise)
    to_qs = ExerciseAlternative.objects.filter(to_exercise=exercise)

    # 双方向の to_exercise / from_exercise を合成
    alt_ids = set()
    alternatives = []
    for alt in from_qs:
        if alt.to_exercise_id not in alt_ids:
            alternatives.append(alt.to_exercise)
            alt_ids.add(alt.to_exercise_id)
    for alt in to_qs:
        if alt.from_exercise_id not in alt_ids:
            alternatives.append(alt.from_exercise)
            alt_ids.add(alt.from_exercise_id)

    # comment form
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")  # 適宜URL名を調整
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.exercise = exercise
            comment.save()
            return redirect("exercise_detail", slug=exercise.slug)
    else:
        form = CommentForm()

    # videos: recommended first
    videos = sorted(
        exercise.videos.all(),
        key=lambda v: (not v.is_recommended, v.sort_order, v.id),
    )

    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(
            user=request.user, exercise=exercise
        ).exists()

    context = {
        "exercise": exercise,
        "primary_muscles": exercise.primary_muscles.all(),
        "secondary_muscles": exercise.secondary_muscles.all(),
        "videos": videos,
        "alternatives": alternatives,
        "variant_exercises": variant_qs,
        "comments": exercise.comments.all(),
        "comment_form": form,
        "is_bookmarked": is_bookmarked
    }
    return render(request, "dex/exercise_detail.html", context)

