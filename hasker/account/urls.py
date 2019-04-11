from django.urls import path

from . import views


app_name = 'account'
urlpatterns = [
    # Auth
    path('singup/', views.SingUpView.as_view(), name='singup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User
    path('settings', views.UserEditView.as_view(), name='edit'),
    path('profile/<slug:username>/', views.UserProfileView.as_view(), name='profile')
]
