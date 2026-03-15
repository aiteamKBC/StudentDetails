from django.urls import path

from .views import brand_logo, favicon, healthz, login_page, student_login

urlpatterns = [
    path('', login_page, name='login-page'),
    path('healthz/', healthz, name='healthz'),
    path('favicon.ico', favicon, name='favicon'),
    path('icon.png', favicon, name='icon-png'),
    path('Kent-Business-College-e1768393206822.webp', brand_logo, name='brand-logo'),
    path('api/auth/student-login/', student_login, name='student-login'),
]
