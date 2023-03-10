from django.shortcuts import render
from django.http import HttpResponse
from .models import Cart,CartItem
from ..store.models import Product
# Create your views here.

def _cart_id(request): #this function will get the cart id and will use that cart id in add_cart function
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart


def add_cart(request,product_id): #this function is when we click add to cart then this should run
    product=Product.Object.get(id=product_id) #this function will get the product
    try:
        cart=Cart.Object.get(cart_id=_cart_id(request)) #get the cart using the cart_id present in the session
    except Cart.DoesnotExist:
        cart=Cart.Object.create(cart_id=_cart_id(request))
    cart.save()

    try:
        cart_item=CartItem.objects.get


def cart(request):
    return render(request,'store/cart.html')