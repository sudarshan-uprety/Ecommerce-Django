from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from carts.models import CartItem
from .forms import OrderForm,Order
import datetime
import requests,json
from django.views.decorators.csrf import csrf_protect
from .models import Payment

# Create your views here.
def payment(request):
   data = request.POST
   product_id = data['product_identity']
   token = data['token']
   print(token)
   amount = data['amount']
   url = "https://khalti.com/api/v2/payment/verify/"

   payload = {
  'token': token,
  'amount': amount
    }



   headers = {
  'Authorization': 'Key live_secret_key_1206ace4a52e414393b1fd1da1df1deb'
    }

   response = requests.post(url, payload, headers = headers)
   
   response_data = json.loads(response.text)
   status_code = str(response.status_code)

   if status_code == '400':
      response = JsonResponse({'status':'false','message':response_data['detail']}, status=500)
      return response

#    import pprint 
#    pp = pprint.PrettyPrinter(indent=4)
#    pp.pprint(response_data)

   print(response_data)
   

#    order=Order.objects.get(user=request.user,is_ordered=False,order_number='2jwzDS9wkxbkDFquJqfAEC')

   #storeing the payment data in the database

#    print(request.user,order.order_total)
#    print(response_data['idx'])


#    payment=Payment(
#        user=request.user,
#        payment_id=response_data['idx'],
#        payment_method='With Khalti',
#        amount_paid=order.order_total,
#        status='completed',
#    )
#    payment.save()

#    order.payment=payment
#    order.is_ordered=True
#    order.save()

#    return JsonResponse(f"Payment Done !! With IDX. {response_data['user']['idx']}",safe=False)
   return render(request,'orders/payments.html')





def place_order(request, total=0, quantity=0):
    current_user = request.user

    # If the cart is empty then it will return to store home page to shop.
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total = (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
        grand_total += total  # Add the total of each cart item to grand_total

    tax = 0
    grand_total += tax  # Add tax to grand_total

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            # store all the billing information insided Order table
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.save()

            # Generate order number by adding the date to the user id
            yr = int(datetime.date.today().strftime('%y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%y%m%d")
            order_number = current_date + str(data.id)  # This will generate the unique order id with the xtra date and time at the end
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }

            return render(request, 'orders/payments.html', context)

    else:
        return redirect('checkout')
