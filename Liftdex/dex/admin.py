from django.contrib import admin

from .models import (
    Bookmark,
    Comment,
    Exercise,
    ExerciseAlternative,
    ExerciseVideo,
    Muscle,
    MuscleGroup,
)


class ExerciseVideoInline(admin.TabularInline):
    model = ExerciseVideo
    extra = 1
    fields = ("title", "url", "is_recommended", "sort_order")


class ExerciseAlternativeInline(admin.TabularInline):
    model = ExerciseAlternative
    fk_name = "from_exercise"
    extra = 1
    fields = ("to_exercise", "note", "sort_order")


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("user", "url", "content", "created_at")
    readonly_fields = ("created_at",)
    can_delete = True


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "english_name",
        "equipment",
        "difficulty",
        "exercise_type",
        "view_count",
    )
    list_filter = ("equipment", "difficulty", "exercise_type")
    search_fields = ("name", "english_name", "slug")
    ordering = ("name",)
    filter_horizontal = ("primary_muscles", "secondary_muscles")
    inlines = (ExerciseVideoInline, ExerciseAlternativeInline, CommentInline)
    fieldsets = (
        (None, {"fields": ("name", "english_name", "slug")}),
        ("分類", {"fields": ("equipment", "difficulty", "exercise_type")}),
        ("筋肉", {"fields": ("primary_muscles", "secondary_muscles")}),
        ("レップ推奨", {"fields": (
            ("strength_rep_min", "strength_rep_max"),
            ("hypertrophy_rep_min", "hypertrophy_rep_max"),
            ("endurance_rep_min", "endurance_rep_max"),
        )}),
        ("Tips", {"fields": (
            "tips_setup",
            "tips_negative",
            "tips_positive",
            "tips_points",
        )}),
        ("統計", {"fields": ("view_count",)}),
    )


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order")
    search_fields = ("name", "slug")
    ordering = ("sort_order", "name")


@admin.register(Muscle)
class MuscleAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "slug", "sort_order")
    list_filter = ("group",)
    search_fields = ("name", "slug")
    ordering = ("sort_order", "name")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user_username", "exercise", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "exercise__name")

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = "ユーザー名"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user_username", "exercise", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "exercise__name", "content")

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = "ユーザー名"
