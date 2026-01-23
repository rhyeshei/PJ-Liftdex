from django.db import models

class MuscleGroup(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
    
    def __str__(self):
        return self.name

class Muscle(models.Model):
    group = models.ForeignKey(
        MuscleGroup, on_delete=models.CASCADE, related_name="muscles"
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    structure_image = models.ImageField(
        upload_to="muscles,", blank=True, null=True
    )
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["group", "name"], name="uniq_muscle_group_name"
            )
        ]

    def __str__(self):
        return self.name