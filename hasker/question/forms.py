import re

from django.conf import settings
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Question, Answer


class QuestionCreateForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text=_('Enter tags, separated by commas. Maximum {} tags'.format(settings.MAX_TAGS_LIMIT)),
    )

    class Meta:
        model = Question
        fields = ('title', 'text', 'tags',)

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        tags = [t.strip() for t in tags.split(',')] if tags else []

        if len(tags) > settings.MAX_TAGS_LIMIT:
            raise ValidationError(_('The maximum number of tags is {}'.format(settings.MAX_TAGS_LIMIT)))

        for tag in tags:
            if not re.match(r'^[\w\@\.\+\-]+$', tag):
                raise ValidationError(_('Tag value may contain only English letters, numbers and @/./+/-/_ characters.'))

        return tags


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        labels = {
            'text': _('Your answer'),
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder':'Enter your answer here...',
            }),
        }
