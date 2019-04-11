from urllib.parse import urlencode
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_pagination_page_url(context , page=None):
    path = context['request'].path
    params = context['request'].GET.copy()

    if page:
        params['page'] = page
    else:
        params.pop('page', None)

    return '{}?{}'.format(path, urlencode(params))
