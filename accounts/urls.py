from django.urls import path
from . import views

#for django_rest_framework 
from .views import Register,Login

urlpatterns = [
    # path("register/", views.register, name="register"),
    #for drf
    
    path('register/',Register.as_view(),name='register'),

    # path("login/", views.login, name="login"),
    path('login/',Login.as_view(),name='login'),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("activate/<uidb64>/<token>/", views.ActivateAccountAPIView.as_view(), name="activate"),
    path("forgotPassword/", views.ForgetPasswordAPI.as_view(), name="forgotPasswords"),
    path(
        "resetpassword_validate/<uidb64>/<token>/",
        views.ResetPasswordValidateAPI.as_view(),
        name="resetpassword_validate",
    ),
    path("resetPassword/", views.ResetPasswordAPI.as_view(), name="resetPassword"),
    path("my_orders/", views.MyOrders.as_view(), name="my_orders"),
    path("change_password/", views.change_password, name="change_password"),
    path("order_detail/<int:order_id>/", views.order_detail, name="order_detail"),
]
