from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from carts.models import CartItem
from .forms import OrderForm,Order
import datetime
import requests,json
from django.views.decorators.csrf import csrf_protect
from .models import Payment,Order,OrderProduct
from store.models import Product
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from decouple import config


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
        'Authorization': config('KHALTI_SECRET_KET')
    }

    response = requests.post(url, payload, headers=headers)

    response_data = json.loads(response.text)
    status_code = str(response.status_code)

    if status_code == '400':
        response = JsonResponse({'status': 'false', 'message': response_data['detail']}, status=500)
        return response

    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(response_data)

    print(response_data)

    order = Order.objects.get(user=request.user, is_ordered=False, order_number=response_data['product_identity'])
    # print(order)
    # storeing the payment data in the database

    # print(request.user,order.order_total)
    # print(response_data['idx'])

    payment = Payment(
        user=request.user,
        payment_id=response_data['idx'],
        payment_method='With Khalti',
        amount_paid=order.order_total,
        status='completed',
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Moves the cart items to order product table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        # We did not do anything for variations ebacause it is many to many fields in cart model
        # in many to many fields we need to first save and then only assign the value
        cart_item = CartItem.objects.get(id=item.id)
        product__variations = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product__variations)
        orderproduct.save()

    # Reduce the quantity of the sold product
        product = Product.objects.get(id=item.product.id)
        product.stock = product.stock - item.quantity
        product.save()

    # Clear the cart
    CartItem.objects.filter(user=request.user).delete()

    # Send email to customer
    mail_subject = "Your order has been confirmed."
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()
    return JsonResponse(f"Payment Done !! Khalti.",safe=False)



    # Send order number and transaction id to frontend
    # return order_complete(request)
    # return render(request, 'orders/1.html')

#    return JsonResponse(f"Payment Done !! With IDX. {response_data['user']['idx']}",safe=False)
# return render(request,'orders/payments.html')





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
            data.save()  # Save the Order object to the database

            # Generate order number by adding the date to the user id
            yr = int(datetime.date.today().strftime('%y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%y%m%d")
            order_number = current_date + str(data.id)  # This will generate the unique order id with the xtra date and time at the end
            data.order_number = order_number
            data.save()  # Save the Order object again with the order number

            khalti_public_key=config('KHALTI_PUBLIC_KET')

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'khalti_public_key':khalti_public_key
            }

            return render(request, 'orders/payments.html', context)

    else:
        return redirect('checkout')


def order_complete(request):
    order = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at').first()
    payment=Payment.objects.filter(user=request.user).order_by("-created_at").first()
    context = {'order': order,'payment':payment}
    return render(request, 'orders/order_complete.html', context)
