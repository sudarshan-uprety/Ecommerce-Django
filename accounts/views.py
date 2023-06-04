from django.shortcuts import render, get_object_or_404
from .forms import RegestrationForm
from .models import Account
from django.contrib import messages, auth
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct
from accounts.models import Account

# verrifications email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests
from carts.views import _cart_id


#inmports for django_rest_framweorks
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer,LoginSerializer,MyOrdersSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate,logout



# Create your views here.


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

#Generating token manually
class Register(generics.GenericAPIView):
    serializer_class=UserSerializer

    def post(self,request):
        serializer=UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password=serializer.validated_data['password']
        password2=serializer.validated_data['password2']
        if password!=password2:
            return Response({"error":"passsword and confirm password do not match"},status=401)
        validated_data=serializer.validated_data
        validated_data.pop('password2')
        user=Account(**validated_data)
        user.set_password(password)
        # user.is_active=True
        user.save()
        # return Response({"ststus":"User registered successfully"},status=201)



        #User activation
        current_site = get_current_site(request)
        mail_subject = "Please activate your account"
        message = render_to_string(
                "accounts/account_verification_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(
                        force_bytes(user.pk)
                    ),  # this is to encode the uid by the encoder so that no other person can see the uid
                    "token": default_token_generator.make_token(user),
                },
        )
        to_email = validated_data['email']
        send_email = EmailMessage(
            mail_subject, message, to=[to_email]
        )  # this is to send the email, what to send, where to send
        send_email.send()
        messages.success(
            request,
                "Registration success. Please use the activation link to continue.",
        )

        # return redirect("/accounts/login/?command=verification&email=" + email)
        return Response({"success":"You have been registered"})

    def get(self,request):
        return render(request, "accounts/register.html")




class Login(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            user_cart=Account.objects.filter(email=email).values('id')
            print(user_cart)
            token=get_tokens_for_user(user)
            try:
                # Here this try and except block is because when non-logged-in user adds something and then to checkout they login
                # the session must pass the cart id so that it can be added to the logged-in user's cart
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()

            except:
                pass

            # auth.login(request, user)
            # messages.success(request, "You are now logged in!")
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                # query = next=/cart/checkout/
                params = dict(x.split("=") for x in query.split("&"))
                # params = {'next': '/cart/checkout/'}
                if "next" in params:
                    nextpage = params["next"]
                    return redirect(nextpage)

            except:
                return Response({"success":"you are now loggedin","token":token})
                # return redirect("dashboard")
        else:
            # messages.error(request, "Invalid login details")
            return Response({"error":"Sorry worng email or password"},status=404)
            # return redirect("http://127.0.0.1:8000/accounts/login/")
                
    def get(self, request):
        return render(request, 'accounts/login.html')





class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pass


class ActivateAccountAPIView(generics.GenericAPIView):
    permission_classes=[]

    def get(self,request,uidb64,token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Congratulation! Your account is activated")
            return Response({"message":"Your account has been activated"})
        else:
            messages.error(request, "Invalid activation link.")
            return redirect("register")


# def forgotPassword(request):
#     if request.method == "POST":
#         email = request.POST["email"]
#         if Account.objects.filter(email=email).exists():
#             user = Account.objects.get(
#                 email__exact=email
#             )  # if the email is being enter is exact similar to email in our database

#             # resetpassword email
#             current_site = get_current_site(request)
#             mail_subject = "Reset Your Password"
#             message = render_to_string(
#                 "accounts/reset_password_email.html",
#                 {
#                     "user": user,
#                     "domain": current_site,
#                     "uid": urlsafe_base64_encode(
#                         force_bytes(user.pk)
#                     ),  # this is to encode the uid by the encoder so that no other person can see the uid
#                     "token": default_token_generator.make_token(user),
#                 },
#             )
#             to_email = email
#             send_email = EmailMessage(
#                 mail_subject, message, to=[to_email]
#             )  # this is to send the email, what to send, where to send
#             send_email.send()

#             messages.success(
#                 request, "Password reset email has been sent to your email address."
#             )
#             return redirect("login")

#         else:
#             messages.error(request, "Account does not exist.")
#             return redirect("forgotPassword")
#     return render(request, "accounts/forgotPassword.html")


class ForgetPasswordAPI(generics.GenericAPIView):
    def post(self,request):
        email = request.data.get("email")
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(
                email__exact=email
            )  # if the email is being enter is exact similar to email in our database

            # resetpassword email
            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(
                        force_bytes(user.pk)
                    ),  # this is to encode the uid by the encoder so that no other person can see the uid
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(
                mail_subject, message, to=[to_email]
            )  # this is to send the email, what to send, where to send
            send_email.send()

            messages.success(
                request, "Password reset email has been sent to your email address."
            )
            return Response({"message":"we have sent you a mail with reset password link."})

        else:
            messages.error(request, "Account does not exist.")
            return Response({"message":"sorry no such account exists"})




class ResetPasswordValidateAPI(generics.GenericAPIView):
    def get(self,request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            request.session["uid"] = uid
            return Response({"message":"You will be redirected to a react app where you can reset password"})
        else:
            return Response({"message":"Sorry the link has expired"})

class ResetPasswordAPI(generics.GenericAPIView):
    def post(self,request):
            password = request.POST["password"]
            confirm_password = request.POST["confirm_password"]

            if password == confirm_password:
                uid = request.session.get("uid")
                user = Account.objects.get(pk=uid)
                user.set_password(
                    password
                )  # here set password is in build function in django which let us use save the updated password in database automatically in hased format
                user.save()
                return Response({"message":"Your password has been reset"})

            else:
                return Response({"message":"password do not match"})

class MyOrders(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=MyOrdersSerializer

    def get_queryset(self):
        user = self.request.user
        orders = (
            Order.objects.filter(user=user, is_ordered=True)
            .order_by("-order_number")
            .select_related("payment")
        )
        order_products = (
            OrderProduct.objects.filter(order__in=orders)
            .prefetch_related("variations", "product")
            .order_by("-order")
        )

        order_product_details = []

        for order_product in order_products:
            order_product_detail = {
                "order_number": order_product.order.order_number,
                "product_name": order_product.product.product_name,
                "product_quantity": order_product.quantity,
                "price": order_product.order.order_total,
                "created_at": order_product.order.created_at,
            }
            order_product_details.append(order_product_detail)

        return order_product_details

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
 

@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        user = Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password changed successfully")
                return redirect("change_password")
            else:
                messages.error(request, "Please enter valid current password")
                return redirect("change_password")
        else:
            messages.error(request, "Password do not match")
            return redirect("change_password")
    return render(request, "accounts/change_password.html")


@login_required(login_url="login")
def order_detail(request, order_id):
    order_details = OrderProduct.objects.filter(
        order__order_number=order_id, user=request.user
    )
    order = Order.objects.get(order_number=order_id)
    subtotal = 0

    for i in order_details:
        subtotal += i.product_price * i.quantity

    context = {
        "order_detail": order_details,
        "order": order,
        "subtotal": subtotal,
    }
    return render(request, "accounts/order_detail.html", context)
