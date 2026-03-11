from django.urls import path

from .views import favicon, healthz, login_page, student_login

urlpatterns = [
    path('', login_page, name='login-page'),
    path('healthz/', healthz, name='healthz'),
    path('favicon.ico', favicon, name='favicon'),
    path('icon.png', favicon, name='icon-png'),
    path('api/auth/student-login/', student_login, name='student-login'),
]
