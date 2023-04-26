from django.contrib import admin
from .models import Payment,Order,OrderProduct


class OrderProductInLine(admin.TabularInline):
    model=OrderProduct
    readonly_fields=('payment','user','product','quantity','product_price','ordered')
    extra=0

class OrderAdmin(admin.ModelAdmin):
    list_display=['order_number','full_name','email','phone','city','order_total','status','is_ordered','created_at']
    list_filter=['status','is_ordered']
    search_fields=['email','phone','order_number']
    list_per_page=20
    inlines=[OrderProductInLine]

class OrderProductAdmin(admin.ModelAdmin):
    list_display=['order','user','product_price','product','quantity','ordered','created_at']

class OrderPaymentAdmin(admin.ModelAdmin):
    list_display=['user','payment_id','amount_paid','status','created_at']


# Register your models here.
admin.site.register(Order,OrderAdmin)
admin.site.register(Payment,OrderPaymentAdmin)
admin.site.register(OrderProduct,OrderProductAdmin)