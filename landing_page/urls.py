from django.urls import path

from . import admin
from .views import home, order, add_to_cart, remove_from_cart, order_complete

from django.contrib import admin  # ✅ Ensure this is imported from django.contrib
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),  # ✅ Correct syntax
    path("", home, name="home"),
    path('order', order, name="order"),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/', remove_from_cart, name='remove_from_cart'),
    path('order_complete/', order_complete, name='order_complete'),
]

