# accounts/views.py
import random
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, OTP
from .serializers import UserSerializer, OTPRequestSerializer, OTPVerifySerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registration successful. Please verify your email.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user, created = User.objects.get_or_create(email=email)
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            OTP.objects.create(user=user, otp=otp)
            # Mock email service by printing the OTP instead of sending an actual email
            print(f'OTP for {email}: {otp}')
            return Response({'message': 'OTP sent to your email.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({'message': 'Invalid email.'}, status=status.HTTP_400_BAD_REQUEST)
            otp_record = OTP.objects.filter(user=user, otp=otp, created_at__gte=timezone.now() - timedelta(minutes=10)).first()
            if not otp_record:
                return Response({'message': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            return Response({'message': 'Login successful.', 'token': str(refresh.access_token)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
