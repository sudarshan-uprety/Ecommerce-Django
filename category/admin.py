from django.contrib import admin
from .models import Category

# Register your models here.
admin.site.register(Category) #we have imported the model in admin pannel so that the admin can use it
