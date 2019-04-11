from datetime import timedelta

from django import template
from django.conf import settings
from django.utils import timezone
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _

from ..models import Question

register = template.Library()


@register.inclusion_tag('question/partials/trending_list.html')
def trending_questions_block():
    questions = Question.objects.popular()[:settings.TRENDING_QUESTIONS_LIMIT]
    return {'questions': questions}


@register.filter
def get_human_date(date):
    now = timezone.now()
    difference = now - date
    if difference <= timedelta(minutes=10):
        return _('just now')
    return _('{} ago').format(timesince(date).split(', ')[0])
