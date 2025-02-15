# users/urls.py

from django.urls import path
from .views import RegisterView, LoginView, Validate2FAView, HomeView, auth_views 

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('validate-2fa/', Validate2FAView.as_view(), name='validate_2fa'),
    path('Accueil/', HomeView.as_view(), name='home'),
    path('logout/', auth_views.as_view(), name='logout'),

]
