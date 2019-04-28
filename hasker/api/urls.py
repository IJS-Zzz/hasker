from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views


app_name = 'api'

urlpatterns = [
    # API Root
    path('', views.api_root, name='api-root'),

    # Question
    path('questions/', views.QuestionsListView.as_view(), name='questions-list'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question-detail'),
    path('questions/<int:pk>/answers/', views.AnswersListView.as_view(), name='question-answers-list'),
    path('questions/<int:pk>/vote/', views.QuestionVoteView.as_view(), name='question-vote'),

    # Answer
    path('answers/<int:pk>/', views.AnswerDetailView.as_view(), name='answer-detail'),
    path('answers/<int:pk>/vote/', views.AnswerVoteView.as_view(), name='answer-vote'),

    # Tag
    path('tags/', views.TagsListView.as_view(), name='tags-list'),
    path('tags/<int:pk>/questions', views.TagQuestionsListView.as_view(), name='tag-questions-list'),

    # Search
    path('search/', views.SearchListView.as_view(), name='search'),

    # Trending Questions
    path('trending/', views.TrendingQuestionsListView.as_view(), name='trending-questions'),

    # Auth
    path('api-token-auth/', obtain_auth_token, name='api-token-auth'),
    # obtain_auth_token - use post metod with data (username and password) for generate api token
    # example:
    # curl -X POST http://localhost:8000/api/v1/api-token-auth/ -d "username=admin&password=admin"
    # -H Authorization: Token {token}
]
