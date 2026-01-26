from django.db import models
from django.utils.text import slugify

from .choices import Difficulty, Equipment, ExerciseType
from .muscle import Muscle
from urllib.parse import urlparse, parse_qs

class Exercise(models.Model):
    name = models.CharField(max_length=200)
    english_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    difficulty = models.PositiveSmallIntegerField(choices=Difficulty.choices)
    equipment = models.CharField(max_length=30, choices=Equipment.choices)
    exercise_type = models.CharField(max_length=20, choices=ExerciseType.choices)

    primary_muscles = models.ManyToManyField(
        Muscle, related_name="primary_exercises", blank=True
    )
    secondary_muscles = models.ManyToManyField(
        Muscle, related_name="secondary_exercises", blank=True
    )

    tips_setup = models.TextField(blank=True)
    tips_negative = models.TextField(blank=True)
    tips_positive = models.TextField(blank=True)
    tips_points = models.TextField(blank=True)

    view_count = models.PositiveIntegerField(default=0)
    base_exercise = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="variants"
    )
    # 推奨レップ数-筋力
    strength_rep_min = models.PositiveSmallIntegerField(null=True, blank=True)
    strength_rep_max = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # 推奨レップ数-筋肥大
    hypertrophy_rep_min = models.PositiveSmallIntegerField(null=True, blank=True)
    hypertrophy_rep_max = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # 推奨レップ数-筋肉持久力
    endurance_rep_min = models.PositiveSmallIntegerField(null=True, blank=True)
    endurance_rep_max = models.PositiveSmallIntegerField(null=True, blank=True)

    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "equipment"], name="uniq_exercise_name_equipment"
            )
        ]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.english_name)
            slug = base_slug
            n = 2
            qs = Exercise.objects.all()
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            while qs.filter(slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ExerciseVideo(models.Model):
    exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, related_name="videos"
    )
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    is_recommended = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.title
    
    def get_embed_url(self):
        parsed = urlparse(self.url)
        host = parsed.netloc

        if "youtu.be" in host:
            video_id = parsed.path.lstrip("/")
        elif "youtube.com" in host:
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        else:
            return None

        if not video_id:
            return None

        return f"https://www.youtube-nocookie.com/embed/{video_id}"


class ExerciseAlternative(models.Model):
    from_exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, related_name="alternative_from"
    )
    to_exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, related_name="alternative_to"
    )
    note = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["from_exercise", "to_exercise"],
                name="uniq_exercise_alternative",
            )
        ]

    def __str__(self):
        return f"{self.from_exercise} -> {self.to_exercise}"