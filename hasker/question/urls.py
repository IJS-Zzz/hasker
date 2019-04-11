from django.urls import path

from . import views

app_name = 'question'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('ask/', views.AskView.as_view(), name='ask'),
    path('question/<slug:slug>/', views.QuestionView.as_view(), name='question'),

    path('vote/question/<int:pk>/', views.QuestionVoteView.as_view(), name='question-vote'),
    path('vote/answer/<int:pk>/', views.AnswerVoteView.as_view(), name='answer-vote'),
    path('mark/answer/<int:pk>/', views.AnswerMarkView.as_view(), name='answer-mark'),
    path('search/', views.SearchView.as_view(), name='search'),
]
