import stripe
from .models import UserProfile
from django.conf import settings
from rest_framework import status
from django.shortcuts import redirect
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegistrationSerializer, UserLoginSerializer, UserProfileSerializer


stripe.api_key = settings.STRIPE_SECRET_KEY


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({
                'token': token,
                'msg': 'User created successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    authentication_classes =[JWTAuthentication]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                token = get_tokens_for_user(user)
                return Response({
                    'token': token,
                    'msg': 'Login successful',
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  
    authentication_classes =[JWTAuthentication]  

    def get(self, request):
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes =[JWTAuthentication]

    def post(self, request):
        YOUR_DOMAIN =  settings.YOUR_DOMAIN
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {'price': settings.STRIPE_RECURRING_PRICE_ID, 'quantity': 1}
            ],
            mode='subscription',
            success_url=f'{YOUR_DOMAIN}/api/payment/success/',
            cancel_url=f'{YOUR_DOMAIN}/api/payment/cancel/',
        )
        return redirect(checkout_session.url, code=303)


class PaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes =[JWTAuthentication]
    
    def get(self, request):
        profile = UserProfile.objects.get(user=request.user)
        profile.is_subscribed = True
        profile.save()
        return Response({'message': 'Payment successful!'}, status=status.HTTP_200_OK)


class PaymentCancelView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes =[JWTAuthentication]
    
    def get(self, request):
        return Response({'message': 'Payment cancelled!'}, status=status.HTTP_200_OK)