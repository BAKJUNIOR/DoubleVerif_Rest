import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm, LoginForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View


class RegisterView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Inscription réussie, {user.get_full_name()}! Veuillez vous connecter.")
            return redirect('login')
        return render(request, 'register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                contact = email
                method = "email"
                response = requests.post(
                    f"{settings.TWO_FA_SERVICE_URL}/api/2fa/sendCode",
                    data={'contact': contact, 'method': method}
                )
                if response.status_code == 200:
                    request.session['contact'] = contact  # Store the contact in session
                    return redirect('validate_2fa')
                messages.error(request, 'Erreur lors de l\'envoi du code.')
                return render(request, 'login.html', {'form': form})
            messages.error(request, 'Les informations d\'identification sont invalides.')
            return render(request, 'login.html', {'form': form})
        return render(request, 'login.html', {'form': form})


class Validate2FAView(View):
    def get(self, request):
        return render(request, 'validate_2fa.html')

    def post(self, request):
        code = request.POST.get('code')
        contact = request.session.get('contact')  # Retrieve the contact from session
        response = requests.post(
            f"{settings.TWO_FA_SERVICE_URL}/api/2fa/validateCode",
            data={'contact': contact, 'code': code}
        )
        if response.json() is True:
            return redirect('home')
        messages.error(request, 'Le code est invalide.')
        return render(request, 'validate_2fa.html')


class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Vous avez été déconnecté avec succès.')
        return redirect('login')
