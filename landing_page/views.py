import json
from unicodedata import decimal

from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from landing_page.models import *
from decimal import Decimal

from . import spreadsheet


# Create your views here.
def get_cart_length(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
        length = 0
        for item in cart:
            length += cart[item]['quantity']
        return length
    except:
        return 0
def home(request):

    candles = Candle.objects.all()
    upsells = Upsells.objects.all()
    cart = {}
    if 'cart' in request.COOKIES:
        cart = json.loads(request.COOKIES['cart'])
    total = 0
    for item in cart:



        quantity = int(cart[item]['quantity'])
        price = Decimal(cart[item]['price'])  # Ensure it's converted to a Decimal
        total += quantity * price
    return render(request, 'index.html', {

        'candles': candles,
        'cart': cart,
        'CART_COUNT': get_cart_length(request),
        'upsells': upsells,
        'total': total,
    })


def order(request):
    upsells = Upsells.objects.all()
    cart = {}
    if 'cart' in request.COOKIES:
        cart = json.loads(request.COOKIES['cart'])
        print(cart)
    total = 0
    for item in cart:



        quantity = int(cart[item]['quantity'])
        price = Decimal(cart[item]['price'])  # Ensure it's converted to a Decimal
        total += quantity * price
    print('total', total)

    return render(request, 'place_order.html',{
        'upsells': upsells,
        'cart': cart,
        'total': str(total),
        'CART_COUNT': get_cart_length(request),
    })

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
import json
from .models import Candle

def add_to_cart(request):
    if request.method == 'POST':
        candle_id = request.POST.get('candle_id')
        candle_name = request.POST.get('candle_name')
        referer = request.META.get('HTTP_REFERER', '')

        if candle_id:
            if '/order' in referer:
                candle = get_object_or_404(Upsells, id=candle_id)
                item_type = 'upsell'
            else:
                candle = get_object_or_404(Candle, id=candle_id)
                item_type = 'candle'

            candle_price = float(candle.price)

            cart = {}
            if 'cart' in request.COOKIES:
                cart = json.loads(request.COOKIES['cart'])

            cart_key = f"{item_type}_{candle_id}"

            # Update the quantity or add the item to the cart
            if cart_key in cart:
                cart[cart_key]['quantity'] += 1
            else:
                cart[cart_key] = {
                    'id': candle_id,
                    'type': item_type,
                    'name': candle.name,
                    'price': candle_price,
                    'quantity': 1,
                }

            cart_json = json.dumps(cart)
            messages.success(request, f"Добавихте {candle.name} в количката", extra_tags='show_cart_modal')
            response = redirect(request.META.get('HTTP_REFERER'))
            response.set_cookie('cart', cart_json, max_age=604800)  # Save updated cart

            return response
        else:
            return redirect('home')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
def remove_from_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')


        cart = {}
        if 'cart' in request.COOKIES:
            cart = json.loads(request.COOKIES['cart'])

        # If the item exists in the cart, remove it
        if item_id in cart:
            del cart[item_id]

            cart_json = json.dumps(cart)

            response = redirect(request.META.get('HTTP_REFERER', '/'))
            response.set_cookie('cart', cart_json, max_age=604800)  # Save updated cart

            return response
        else:
            return JsonResponse({'success': False, 'message': 'Item not found in cart'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def get_cart_items(request):
    # Retrieve the cart from cookies, or initialize an empty dictionary if not present
    cart = {}
    if 'cart' in request.COOKIES:
        cart = json.loads(request.COOKIES['cart'])

    # Iterate through the cart and extract item details
    for candle_id, item in cart.items():
        name = item.get('name')
        price = item.get('price')
        quantity = item.get('quantity')
        # Do whatever you need with these values


    # You can return the cart or any necessary information
    return cart


def order_complete(request):
    if request.method == "POST":
        # Get customer details from the form
        customer_name = request.POST.get("name")
        customer_phone = request.POST.get("phone")
        customer_address = request.POST.get("address")

        # Get cart items and calculate total
        cart = get_cart_items(request)
        total_price = sum(int(item["quantity"]) * float(item["price"]) for item in cart.values())
        total_price = f"{total_price:.2f}"
        response = render(request, "order_complete.html", {
            "cart": cart,
            "total_price": total_price,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "customer_address": customer_address,
        })
        SPREADSHEET_ROW = [customer_name, customer_phone, customer_address]
        ordered_items = ''
        for item in cart:
            ordered_items += f"{cart[item]['name']} × {cart[item]['quantity']}\n"
        ordered_items += f"Общо: {total_price}"
        SPREADSHEET_ROW.append(ordered_items)
        SPREADSHEET_ROW.append("НЕ")
        SPREADSHEET_ROW.append('НЕ')
        # Clear cart after placing order
        # request.session["cart"] = {}
        spreadsheet.append_to_sheet(SPREADSHEET_ROW)
        # Clear the cart after the order is completed
        response.delete_cookie("cart")

        return response

    return redirect("home")


def lichni_danni(request):
    return render(request,'lichni-danni.html')

def biscuits(request):
    return render(request,'Biscuits.html')
def tos(request):
    return render(request,'tos.html')
