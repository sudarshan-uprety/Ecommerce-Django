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




# Register your models here.
admin.site.register(Order,OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)