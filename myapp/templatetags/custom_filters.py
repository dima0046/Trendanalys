from django import template

register = template.Library()

@register.filter
def length_for_category(queryset, category):
    return sum(1 for item in queryset.object_list if item.category == category)