
from django.urls import path
from api.views import * 
urlpatterns = [
    path('', RootView.as_view(), name='root'),
    path('authentication/signup/', RegistrationView.as_view(), name='signup'),
    path('authentication/login/', LoginView.as_view(), name='login'),
    path('user_profile/get_user_profile/', UserProfileView.as_view(), name='get_user_profile'),


    path("product_list/", ProductListView.as_view(), name='product_list'),
    path("checkout/<int:product_id>/", CheckoutView.as_view(), name='checkout'),
    path("create_payment/<int:product_id>/", CreatePaymentView.as_view(), name='create_payment'),
    path("success/", success, name='success'),
    path("cancel/", cancel, name="cancel"),
    # path('payment/success/', PaymentSuccessView.as_view(), name='success'),
    # path('payment/cancel/', PaymentCancelView.as_view(), name='cancel'),
]
