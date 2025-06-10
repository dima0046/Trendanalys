from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def query_string(context, **kwargs):
    request = context['request']
    query = request.GET.copy()
    for key, value in kwargs.items():
        if key == 'sort_by' and query.get('sort_by') == value:
            query['sort_direction'] = 'desc' if query.get('sort_direction', 'asc') == 'asc' else 'asc'
        query[key] = value
    return urlencode(query)