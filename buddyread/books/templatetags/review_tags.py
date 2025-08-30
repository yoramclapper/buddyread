from django.utils.safestring import mark_safe

from django import template

register = template.Library()

@register.filter
def stars(score):
    if score == "DNF":
        return "DNF"

    try:
        value = float(score)
    except ValueError:
        return ""

    full_stars = int(value)
    half_star = 1 if value % 1 >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    html = []
    html.extend(['<i class="bi bi-star-fill text-warning"></i>'] * full_stars)
    if half_star:
        html.append('<i class="bi bi-star-half text-warning"></i>')
    html.extend(['<i class="bi bi-star text-warning"></i>'] * empty_stars)

    return mark_safe("".join(html))

