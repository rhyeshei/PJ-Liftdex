from django.conf import settings
from django.db import models

from .exercise import Exercise


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks"
    )
    exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, related_name="bookmarked_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "exercise"], name="uniq_bookmark")
        ]

    def __str__(self):
        return f"{self.user} - {self.exercise}"


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, related_name="comments"
    )
    url = models.URLField(blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.exercise}"
