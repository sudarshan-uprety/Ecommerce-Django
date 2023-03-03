from django.db import models

# Create your models here.
class Category(models.Model):
    category_name=models.CharField(max_length=50,unique=True)
    slug=models.CharField(max_length=100,unique=True)
    description=models.TextField(max_length=255,blank=True)
    cat_image=models.ImageField(upload_to='photos/categories',blank=True)

    class Meta: #while in python when a module is created then at the end the 's come this class makes sure that it doesnot appear
        verbose_name='category'
        verbose_name_plural='categories'

    def __str__(self):
        return self.category_name
