from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile
from .serializers import RegisterSerializer, ProfileSerializer


# ──────────────────────────────────────────
# HTML VIEWS (session-based, for browser)
# ──────────────────────────────────────────

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user)
        messages.success(request, 'Account created. Please login.')
        return redirect('login')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'form_list'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.phone = request.POST.get('phone', '')
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        messages.success(request, 'Profile updated.')

    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']

        if request.user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password changed. Please login again.')
            return redirect('login')
        else:
            messages.error(request, 'Old password is incorrect')

    return render(request, 'accounts/change_password.html')


# ──────────────────────────────────────────
# REST API VIEWS (JWT-based)
# ──────────────────────────────────────────

class RegisterAPI(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Registration successful',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if request.user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save()
            return Response({'message': 'Password changed successfully'})
        return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)