
from django.urls import path
from .views import RegistrationView, LoginView, UserProfileView, CreateCheckoutSessionView, PaymentSuccessView, PaymentCancelView

urlpatterns = [
    path('authentication/signup/', RegistrationView.as_view(), name='signup'),
    path('authentication/login/', LoginView.as_view(), name='login'),
    path('user_profile/get_user_profile/', UserProfileView.as_view(), name='get_user_profile'),
    path('payment/create_checkout/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('payment/success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/cancel/', PaymentCancelView.as_view(), name='payment_cancel'),
]
