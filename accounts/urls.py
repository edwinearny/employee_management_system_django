from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # HTML routes
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),

    # API routes
    path('api/register/', views.RegisterAPI.as_view(), name='api_register'),
    path('api/login/', views.LoginAPI.as_view(), name='api_login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', views.ProfileAPI.as_view(), name='api_profile'),
    path('api/change-password/', views.ChangePasswordAPI.as_view(), name='api_change_password'),
]