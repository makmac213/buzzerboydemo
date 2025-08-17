from django.urls import path
from django.views.generic.base import RedirectView

from buzzerboy.apps.authorization.views import (
    DashboardView,
    LoginView,
    LogoutView,
    MyCompaniesView,
    MyProfileView,
    NewCompanyView,
    PasswordlessLoginView,
    SetLanguageView,
    SignupView,
)

app_name = 'authorization'

urlpatterns = [
    path('', RedirectView.as_view(url='login/', permanent=False), name='home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('passwordless-login/<uidb64>/', PasswordlessLoginView.as_view(), name='passwordless_login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('set-language/', SetLanguageView.as_view(), name='set_language'),

    path('companies/', MyCompaniesView.as_view(), name='my_companies'),
    path('companies/new/', NewCompanyView.as_view(), name='add_company'),

    path('my-profile/<int:profile_id>/', MyProfileView.as_view(), name='my_profile')
]
