import stripe
from .models import *
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
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

class ProductListView(View):
    def get(self, request):
        products = Product.objects.all()
        return render(request, 'api/product_list.html', {'products': products})

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        return render(request, "api/checkout.html", {'product': product})


@method_decorator(csrf_exempt, name='dispatch')
class CreatePaymentView(LoginRequiredMixin, View):

    def post(self, request, product_id):
        # YOUR_DOMAIN =  settings.YOUR_DOMAIN
        product = get_object_or_404(Product, id=product_id)
        order = Order.objects.create(user=request.user, product=product, amount=product.price)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {'price': settings.STRIPE_RECURRING_PRICE_ID, 'quantity': 1}
            ],
            mode='subscription',
            customer_email = request.user.email,
            # success_url=f'{YOUR_DOMAIN}/api/payment/success/',
            # cancel_url=f'{YOUR_DOMAIN}/api/payment/cancel/',
            
            success_url='http://localhost:8001/api/success/',
            cancel_url='http://localhost:8001/api/cancel/',
        )
        order.stripe_checkout_session_id = checkout_session.id
        order.save()
        
        # Implement is_subscribed = True
        # profile = UserProfile.objects.get(user=request.user)

        return redirect(checkout_session.url, code=303)




# class PaymentSuccessView(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes =[JWTAuthentication]
    
    # def get(self, request):
    #     profile = UserProfile.objects.get(user=request.user)
    #     profile.is_subscribed = True
    #     profile.save()
    #     return Response({'message': 'Payment successful!'}, status=status.HTTP_200_OK)


def success(request):
    profile = UserProfile.objects.get(user = request.user)
    profile.is_subscribed = True
    profile.save()
    return JsonResponse({"status": "Success"})


def cancel(request):
    return JsonResponse({"status": "Cancel"})


# class PaymentCancelView(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes =[JWTAuthentication]
    
    # def get(self, request):
    #     return Response({'message': 'Payment cancelled!'}, status=status.HTTP_200_OK)