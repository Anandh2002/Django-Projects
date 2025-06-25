from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('captcha/', views.CaptchaView.as_view(), name='captcha'),
    path('otp/', views.OTPView.as_view(), name='otp'),
    path('passbook/', views.PassbookView.as_view(), name='passbook'),
]
