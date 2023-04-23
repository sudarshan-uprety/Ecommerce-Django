from .import views

from django.urls import path
from .import views

urlpatterns = [
    path('place_order/',views.place_order,name='place_order'),
    path('payments/',views.payment,name='payments'),
    # path('api/verify_payment',views.verify_payment,name='verify_payment'),
]
