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
from .serializers import UserSerializer,LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate



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
        user.is_active=True
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



def register(request):
    if request.method == "POST":
        form = RegestrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data[
                "first_name"
            ]  # when we use django form we need to use cleaned_data to extract form the frontend
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )  # this will call the create_user function which is under accounts/mode.py/MyAccountManager class
            user.phone_number = phone_number
            user.save()

            # User activation
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
            to_email = email
            send_email = EmailMessage(
                mail_subject, message, to=[to_email]
            )  # this is to send the email, what to send, where to send
            send_email.send()
            messages.success(
                request,
                "Regestration success. Please use the activation link to continue.",
            )

            return redirect(
                "/accounts/login/?command=verification&email=" + email
            )  # this will show if the user came from registration form or not
    else:
        form = RegestrationForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


class Login(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        
        if user is not None:
            token=get_tokens_for_user(user)
            try:
                # Here this try and except block is because when non-logged-in user adds something and then to checkout they login
                # the session must pass the cart id so that it can be added to the logged-in user's cart
                cart = Cart.objects.get(cart_id=_cart_id(request))
                print(cart)
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    product_variation = []

                    # Here we are getting the product variations by cart id
                    for item in cart_item:
                        variations = item.variations.all()
                        product_variation.append(list(variations))

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variations = item.variations.all()
                        ex_var_list.append(list(existing_variations))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()

                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

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
            return Response({"error":"Sorry worng username or password"},status=404)
            # return redirect("http://127.0.0.1:8000/accounts/login/")
                
    def get(self, request):
        return render(request, 'accounts/login.html')






def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:  # here this try and except block is because when non loggedin user add something and then to checkout they login
                # the session must pass the cart id so that it can be added to the user loggedin
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    product_variation = []

                    # here we are getting the product variations by cart id
                    for item in cart_item:
                        variations = item.variations.all()
                        product_variation.append(list(variations))

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variations = item.variations.all()
                        ex_var_list.append(list(existing_variations))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()

                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass
            authenticate.login(request, user)
            messages.success(request, "You are now logged in!")
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
                return redirect("dashboard")
        else:
            messages.error(request, "Invalid login details")
            return redirect("login")

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "You're logged out.")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulation! Your account is activated")
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link.")
        return redirect("register")


@login_required(login_url="https://127.0.0.1:8000/accounts/login/")
def dashboard(request):
    return render(request, "accounts/dashboard.html")


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
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
            return redirect("login")

        else:
            messages.error(request, "Account does not exist.")
            return redirect("forgotPassword")
    return render(request, "accounts/forgotPassword.html")


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please reset your password")
        return redirect("resetPassword")
    else:
        messages.error(request, "This link has been expired")
        return redirect("login")


def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(
                password
            )  # here set password is in build function in django which let us use save the updated password in database automatically in hased format
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")

        else:
            messages.error(request, "Password do not match")
            return redirect("resetPassword")

    return render(request, "accounts/resetPassword.html")


@login_required(login_url="login")
def my_orders(request):
    orders = (
        Order.objects.filter(user=request.user, is_ordered=True)
        .order_by("-order_number")
        .select_related("payment")
    )

    # print(orders)
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

    context = {"order_product_details": order_product_details, "orders": orders}

    # print("context", context)

    return render(request, "accounts/my_orders.html", context)


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
