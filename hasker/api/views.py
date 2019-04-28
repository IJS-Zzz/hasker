from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse

from hasker.question.models import Answer, Question, Tag
from .serializers import (AnswerSerializer, QuestionSerializer,
                          QuestionsListSerializer, TagSerializer,
                          VoteSerializer)
from .paginators import (AnswerListPagination,
                         QuestionListPagination,
                         TagListPagination)
from .permissions import IsAuthorOrReadOnly


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'questions': reverse('api:questions-list', request=request, format=format),
        'trending': reverse('api:trending-questions', request=request, format=format),
        'search': reverse('api:search', request=request, format=format),
        'tags': reverse('api:tags-list', request=request, format=format),
    })


class QuestionsListView(generics.ListAPIView):
    serializer_class = QuestionsListSerializer
    model = Question
    pagination_class = QuestionListPagination

    def get_queryset(self):
        sort = self.request.GET.get('sort')
        if sort == 'popular':
            return self.model.objects.popular()
        return self.model.objects.new()


class QuestionDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsAuthorOrReadOnly,)


class AnswersListView(generics.ListAPIView):
    serializer_class = AnswerSerializer
    model = Answer
    pagination_class = AnswerListPagination

    def get_queryset(self):
        try:
            question = Question.objects.get(id=self.kwargs.get('pk'))
        except Question.DoesNotExist:
            raise NotFound()
        return question.answer_set.popular()


class AnswerDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsAuthorOrReadOnly,)


class TagsListView(generics.ListAPIView):
    serializer_class = TagSerializer
    queryset = Tag.objects.all().order_by('id')
    pagination_class = TagListPagination


class TagQuestionsListView(generics.ListAPIView):
    serializer_class = QuestionsListSerializer
    model = Tag
    pagination_class = QuestionListPagination

    def get_queryset(self):
        try:
            tag = self.model.objects.get(id=self.kwargs.get('pk'))
        except self.model.DoesNotExist:
            raise NotFound()
        return tag.question_tags.popular()


class SearchListView(generics.ListAPIView):
    serializer_class = QuestionsListSerializer
    model = Question
    pagination_class = QuestionListPagination

    def get_queryset(self):
        search_query = self.request.GET.get('q')
        if not search_query:
            return self.model.objects.none()
        search_query = search_query[:255]

        if search_query.startswith('tag:'):
            # search tags
            search_tag_query = search_query[len('tag:'):]
            if not search_tag_query:
                return self.model.objects.none()
            query = Q(tags__name__icontains=search_tag_query)
        else:
            query = Q(title__icontains=search_query) | Q(text__icontains=search_query)
            words = search_query.split()
            if words:
                for word in words:
                    query |= Q(title__icontains=word) | Q(text__icontains=word)
        return self.model.objects.filter(query).distinct().order_by('-rating', '-pub_date')


class TrendingQuestionsListView(generics.ListAPIView):
    serializer_class = QuestionsListSerializer
    queryset = Question.objects.popular()[:settings.TRENDING_QUESTIONS_LIMIT]


class BaseVoteView(APIView):
    serializer_class = VoteSerializer
    permission_classes = (permissions.IsAuthenticated,)
    model = None

    def post(self, request, pk):
        model = self.model
        if not model:
            raise ImproperlyConfigured("Field 'model' must be specified.")

        value = True if request.POST.get('value') == 'true' else False
        try:
            instance = model.objects.get(id=pk)
        except model.DoesNotExist:
            raise NotFound()
        vote = instance.vote(request.user, value)
        return Response({'rating': instance.rating, 'vote': vote}, status=status.HTTP_201_CREATED)


class QuestionVoteView(BaseVoteView):
    model = Question


class AnswerVoteView(BaseVoteView):
    model = Answer
