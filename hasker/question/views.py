from itertools import chain
from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Q
from django.views import generic, View
from django.views.generic.list import MultipleObjectMixin
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse, Http404, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Question, Answer, Tag
from .forms import QuestionCreateForm, AnswerForm
from .utils import new_answer_email_notify


class AskView(LoginRequiredMixin, generic.CreateView):
    form_class = QuestionCreateForm
    template_name = 'question/question_create.html'
    extra_context = {'title': 'Ask a question',
                     'max_tags_limit': settings.MAX_TAGS_LIMIT}

    def form_valid(self, form):
        question = form.save(commit=False)
        tags = form.cleaned_data['tags']
        question.author = self.request.user
        question.save(tags=tags)
        return redirect(question.url)


class QuestionView(MultipleObjectMixin, View):
    model = Question
    form_class = AnswerForm
    context_object_name = 'answers'
    paginate_by = settings.PAGINATE_ANSWERS
    template_name = 'question/question_detail.html'
    form = None

    def get(self, request, slug):
        self.form = self.form_class()
        self.question = get_object_or_404(self.model, slug=slug)
        return self.render_to_response(self.get_context_data())

    @method_decorator(login_required)
    def post(self, request, slug):
        self.form = form = self.form_class(request.POST)
        self.question = question = get_object_or_404(self.model, slug=slug)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()
            if request.user.pk != question.author.pk:
                new_answer_email_notify(request, question, answer)
            return redirect(question.url)
        return self.render_to_response(self.get_context_data())

    def get_queryset(self):
        return self.question.answer_set.popular()

    def get_context_data(self, **kwargs):
        object_list = self.get_queryset()
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update({
            'question': self.question,
            'form': self.form,
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        return render(self.request, self.template_name,
                      context, **response_kwargs)


class IndexView(generic.ListView):
    context_object_name = 'questions'
    paginate_by = settings.PAGINATE_QUESTIONS
    template_name = 'question/question_list.html'

    def get_queryset(self):
        sort = self.request.GET.get('sort')
        if sort == 'popular':
            return Question.objects.popular()
        else:
            return Question.objects.new()

    def get_context_data(self):
        title = 'New Questions'
        sort = self.request.GET.get('sort')
        if sort == 'popular':
            title = 'Hot Questions'

        context = super().get_context_data()
        context.update({
            'title': title
        })
        return context


class SearchView(generic.ListView):
    context_object_name = 'questions'
    paginate_by = settings.PAGINATE_QUESTIONS
    template_name = 'question/question_search.html'
    extra_context = {'title': 'Search result'}

    def get_queryset(self):
        search_query = self.request.GET.get('q')
        if not search_query:
            return Question.objects.none()
        search_query = search_query[:255]

        if search_query.startswith('tag:'):
            # search tags
            search_tag_query = search_query[len('tag:'):]
            if not search_tag_query:
                return Question.objects.none()
            query = Q(tags__name__icontains=search_tag_query)
        else:
            query = Q(title__icontains=search_query) | Q(text__icontains=search_query)
            words = search_query.split()
            if words:
                for word in words:
                    query |= Q(title__icontains=word) | Q(text__icontains=word)
        return Question.objects.filter(query).distinct().order_by('-rating', '-pub_date')


class AnswerMarkView(View):
    model = Answer

    def post(self, request, pk):
        if request.user.is_authenticated:
            answer = get_object_or_404(self.model, pk=pk)
            success = answer.mark(request.user)
            return JsonResponse({'success': success})
        else:
            return HttpResponseForbidden()


class BaseVoteView(View):
    model = None

    def post(self, request, pk):
        model = self.model
        if not model:
            raise ImproperlyConfigured("Field 'model' must be specified.")

        if request.user.is_authenticated:
            value = True if request.POST.get('value') == 'true' else False
            instance = get_object_or_404(model, pk=pk)
            instance.vote(request.user, value)
            return JsonResponse({'rating': instance.rating})
        else:
            return HttpResponseForbidden()


class QuestionVoteView(BaseVoteView):
    model = Question


class AnswerVoteView(BaseVoteView):
    model = Answer
