import itertools
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


class QuestionManager(models.Manager):
    def new(self):
        return self.all().order_by('-pub_date')

    def popular(self):
        return self.all().order_by('-rating', '-pub_date')


class AnswerManager(models.Manager):
    def popular(self):
        return self.all().order_by('-rating', '-pub_date')


class VoteMixin:
    def vote(self, user, value=False):
        if self.author == user:
            return False
        with transaction.atomic():
            try:
                vote = self.votes.get(user=user)
                if vote.vote != value:
                    vote.delete()
                else:
                    return False
            except ObjectDoesNotExist:
                self.votes.create(user=user, vote=value)
            self.rating += 1 if value else -1
            self.save()
            return True


class Question(VoteMixin, models.Model):
    title = models.CharField(_('Title'), max_length=255)
    text = models.TextField(_('Question'))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    slug = models.SlugField(unique=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag', related_name='question_tags')
    votes = GenericRelation('Vote', related_query_name='questions')
    rating = models.IntegerField(default=0)

    correct_answer = models.ForeignKey(
        'Answer',
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='correct_answer'
    )

    # Manager
    objects = QuestionManager()

    def __str__(self):
        return self.title

    @property
    def has_answer(self):
        return self.correct_answer is not None

    def get_absolute_url(self):
        return reverse("question:question", kwargs={'slug': self.slug})

    def get_vote_url(self):
        return reverse("question:question-vote", kwargs={'pk': self.pk})

    @property
    def url(self):
        return self.get_absolute_url()

    def get_slug_max_length(self):
        return self._meta.get_field('slug').max_length

    @classmethod
    def is_slug_exists(cls, slug):
        return cls.objects.filter(slug=slug).exists()

    def slugify(self, string):
        max_length = self.get_slug_max_length()
        slug = orig = slugify(string)[:max_length]
        for x in itertools.count(1):
            if not self.is_slug_exists(slug):
                break
            slug = '{}-{}'.format(orig[:max_length - len(str(x)) - 1], x)
        return slug

    def save(self, tags=(), *args, **kwargs):
        if not self.pk:
            self.slug = self.slugify(self.title)
        super().save(*args, **kwargs)
        tag_objects = []
        for tag in tags:
            tag_object, _ = Tag.objects.get_or_create(name=tag)
            tag_objects.append(tag_object)
        self.tags.add(*tag_objects)


class Answer(VoteMixin, models.Model):
    text = models.TextField(_('Answer'))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    votes = GenericRelation('Vote', related_query_name='answers')
    rating = models.IntegerField(default=0)

    # Manager
    objects = AnswerManager()

    def mark(self, user):
        with transaction.atomic():
            question = self.question
            if question.author != user or self.author == user:
                return False
            if question.has_answer:
                if question.correct_answer == self:
                    question.correct_answer = None
                else:
                    question.correct_answer = self
            else:
                question.correct_answer = self
            question.save()
            return True

    def get_vote_url(self):
        return reverse('question:answer-vote', kwargs={'pk': self.pk})

    def get_mark_url(self):
        return reverse('question:answer-mark', kwargs={'pk': self.pk})


class Tag(models.Model):
    name = models.CharField(_('Name'), max_length=50, unique=True)

    def __str__(self):
        return self.name

    def get_search_url(self):
        return '{}?{}'.format(reverse("question:search"), urlencode({'q': 'tag:' + self.name}))

    @property
    def url(self):
        return self.get_search_url()


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
