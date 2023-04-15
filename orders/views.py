from django.shortcuts import render,redirect
from django.http import HttpResponse
from carts.models import CartItem
from .forms import OrderForm,Order
import datetime

# Create your views here.




def place_order(request,total=0,quantity=0):
    current_user=request.user

    #If the cart is empty then it will return to store home page to shop.
    cart_items=CartItem.objects.filter(user=current_user)
    cart_count=cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total=0
    tax=0
    for cart_item in cart_items:
        total=(cart_item.product.price*cart_item.quantity)
        quantity+=cart_item.quantity
    tax=0
    grand_total=total+tax


    
    if request.method=='POST':
        form=OrderForm(request.POST)
        if form.is_valid():
            data=Order()
            #store all the billing information insided Order table
            data.first_name=form.cleaned_data('first_name')
            data.last_name=form.cleaned_data('last_name')
            data.phone=form.cleaned_data('phone')
            data.email=form.cleaned_data('email')
            data.address_line_1=form.cleaned_data('address_line_1')
            data.address_line_2=form.cleaned_data('address_line_2')
            data.state=form.cleaned_data('state')
            data.city=form.cleaned_data('city')
            data.order_note=form.cleaned_data('order_note')
            data.order_total=grand_total
            data.tax=tax
            data.save()

            #Generate order number by adding the date to the user id
            yr=int(datetime.date.today().strftime('%y'))
            dt=int(datetime.date.today().strftime('%d'))
            mt=int(datetime.date.today().strftime('%m'))
            d=datetime.date(yr,mt,dt)
            current_date=d.strftime("%y%m%d")
            order_number=current_date + str(data.id) #This will generate the unique order id with the xtra date and time at the end
            data.order_number=order_number
            data.save()
            return redirect('checkout')
    
    else:
        return redirect('checkout')