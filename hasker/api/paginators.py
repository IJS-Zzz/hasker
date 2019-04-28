from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class QuestionListPagination(PageNumberPagination):
    page_size = settings.PAGINATE_QUESTIONS
    page_size_query_param = 'page_size'
    max_page_size = 100


class AnswerListPagination(PageNumberPagination):
    page_size = settings.PAGINATE_ANSWERS
    page_size_query_param = 'page_size'
    max_page_size = 100


class TagListPagination(PageNumberPagination):
    page_size = settings.PAGINATE_TAGS
    page_size_query_param = 'page_size'
    max_page_size = 100
