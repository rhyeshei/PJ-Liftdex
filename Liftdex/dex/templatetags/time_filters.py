from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def short_ago(value):
    if not value:
        return ""

    now = timezone.now()
    delta = now - value
    minutes = int(delta.total_seconds() // 60)

    # 最低 1分前
    if minutes < 1:
        minutes = 1

    if minutes < 60:
        return f"{minutes}分前"

    hours = minutes // 60
    if hours < 24:
        return f"{hours}時間前"

    days = hours // 24
    if days < 30:
        return f"{days}日前"

    months = days // 30
    if months < 12:
        return f"{months}ヶ月前"

    years = months // 12
    return f"{years}年前"
