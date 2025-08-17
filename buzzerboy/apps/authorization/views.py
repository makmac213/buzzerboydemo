# django imports
from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import translation
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View

# authorization
from .forms import CompanyForm, SignupForm
from .models import Company, UserProfile

User = get_user_model()


class SignupView(View):
    template_name = 'auth/signup.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.POST)
        context = {}
        if form.is_valid():
            instance = form.save()
            company_name = form.cleaned_data.get('company')
            company = Company.objects.create(name=company_name)
            profile = UserProfile.objects.get(user=instance)
            profile.company = company
            profile.save()
            return redirect("authorization:login")
        else:
            context = {
                "error": "Error",
                "has_error": True,
                "form": form,
            }
        return render(request, self.template_name, context)


class LoginView(DjangoLoginView):
    template_name = 'auth/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("authorization:dashboard")
        context = {}
        return render(request, self.template_name, context)

    def post(self, request):
        email = request.POST.get('email')

        # Validate email input
        if not email:
            return self.form_invalid(self.get_form())
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            context = {
                'error': 'User does not exist.',
                'has_error': True,
            }
            return render(request, self.template_name, context)

        # Generate a simple token (for demo, use uidb64, in production use a secure token)
        # For real-life applications we can create a more secure token
        # by building a custom token generator and a model to store it
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        login_url = request.build_absolute_uri(
            reverse('authorization:passwordless_login', kwargs={'uidb64': uid})
        )
        send_mail(
            'Your login link',
            f'Click the link to login: {login_url}',
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'no-reply@example.com',
            [email],
            fail_silently=False,
        )

        context = {
            'message': 'A login link has been sent to your email.',
            'has_email': True,
        }
        return render(request, self.template_name, context)


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('authorization:login')


class PasswordlessLoginView(View):

    def get(self, request, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return HttpResponse('Invalid or expired login link.', status=400)
        # login and set the active profile on session
        login(request, user)
        active_profile = user.profiles.filter(is_default=True).first()
        request.session['active_profile'] = active_profile.id
        # We need to set the cookie first or translation.activate will not work
        translation.activate(active_profile.default_language)
        response = redirect('authorization:dashboard')
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, active_profile.default_language)
        return response


class DashboardView(LoginRequiredMixin, View):
    template_name = 'auth/dashboard.html'

    def get(self, request):
        return render(request, self.template_name, {'user': request.user})
    

class SetLanguageView(LoginRequiredMixin, View):
    """Language switcher for logged in users"""

    def post(self, request):
        language = request.POST.get('language')
        response = redirect('authorization:dashboard')
        if language:
            profile_id = request.session.get('active_profile')
            if profile_id:
                profile = get_object_or_404(UserProfile, id=profile_id, user=request.user)
                profile.default_language = language
                profile.save()
                request.session['active_profile'] = profile.id
                translation.activate(language)
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        return response


class MyCompaniesView(LoginRequiredMixin, View):
    template_name = 'auth/companies/list.html'
    
    def get(self, request):
        return render(request, self.template_name, {})


class NewCompanyView(LoginRequiredMixin, View):
    template_name = 'auth/companies/form.html'

    def get(self, request):
        context = {"form": CompanyForm()}
        return render(request, self.template_name, context)

    def post(self, request):
        form = CompanyForm(request.POST)
        if form.is_valid():
            instance = form.save()
            UserProfile.objects.create(
                user=request.user,
                company=instance
            )
            return redirect("authorization:my_companies")
        context = {
            "form": form
        }
        return render(request, self.template_name, context)


class MyProfileView(LoginRequiredMixin, View):
    template_name = 'auth/my_profile.html'

    def get(self, request, *args, **kwargs):
        # should only get my own profiles
        profile_id = kwargs.get('profile_id')
        instance = get_object_or_404(UserProfile, id=profile_id, user=request.user)
        context = {
            "instance": instance,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Only the switch functionality for now
        profile_id = request.POST.get('profile_id')
        request.session['active_profile'] = profile_id
        return redirect("authorization:dashboard")
