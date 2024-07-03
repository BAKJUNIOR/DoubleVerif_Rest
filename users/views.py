# users/views.py

import requests
from django.conf import settings
from django.contrib.auth import authenticate, login
from requests import request

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
                    return redirect('validate_2fa')
                return render(request, 'login.html', {'form': form, 'error': 'Erreur lors de envoi du code '})
            return render(request, 'login.html', {'form': form, 'error': 'les informations identification invalides'})
        return render(request, 'login.html', {'form': form})


class Validate2FAView(View):
    def get(self, request):
        return render(request, 'validate_2fa.html')

    def post(self, request):
        code = request.POST.get('code')
        response = requests.post(
            f"{settings.TWO_FA_SERVICE_URL}/api/2fa/validateCode",
            data={'code': code}
        )
        if response.json() is True:
            return redirect('home')
        return render(request, 'validate_2fa.html', {'error': 'le Code est invalide'})


class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')


class auth_views(View):
    def get(self, request):
        return render(request, 'login.html')


