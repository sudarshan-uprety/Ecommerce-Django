from django.contrib import admin
from .models import Category

# Register your models here.
class CategoryAdmin(admin.ModelAdmin): #here this class is used to make sure that the cateogry name is automatically set to slug name as both of them are same while adding categories
    prepopulated_fields={'slug':('category_name',)}
    list_display=('category_name','slug')

admin.site.register(Category,CategoryAdmin) #we have imported the model in admin pannel so that the admin can use it
