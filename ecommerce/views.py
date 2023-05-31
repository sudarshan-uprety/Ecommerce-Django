from django.shortcuts import render
from store.models import Product
from carts.models import Cart,CartItem
from category.models import Category
from itertools import chain


def home(request):
    if request.user.is_authenticated:
        cart_items=CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            products=Product.objects.all().filter(is_available=True)
            context={
            'products':products,
            }
            return render(request,'home.html',context)
        else:
            product_id=cart_items.values_list('product',flat=True)
            categories=Category.objects.filter(product__in=product_id).distinct()
            recommended_products = Product.objects.filter(category__in=categories, is_available=True).distinct()
            all_products = Product.objects.all().filter(is_available=True).exclude(category__in=categories)
            products = list(recommended_products) + list(all_products)
            context={
                'recommended_products':recommended_products,
                'all_products':all_products,
            }
            return render(request,'home.html',context)
    else:
        products=Product.objects.all().filter(is_available=True)
        context={
            'products':products,
        }
        return render(request,'home.html',context)