import json
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

    candles = Candle.objects.all()[:4]

    cart = {}
    if 'cart' in request.COOKIES:
        cart = json.loads(request.COOKIES['cart'])

    return render(request, 'index.html', {

        'candles': candles,
        'cart': cart,
        'CART_COUNT': get_cart_length(request),
    })


def order(request):
    upsells = Candle.objects.all()[4:6]
    cart = {}
    if 'cart' in request.COOKIES:
        cart = json.loads(request.COOKIES['cart'])
    total = 0
    for item in cart:
        total += cart[item]['quantity'] * cart[item]['price']


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
        # Get the candle_id from the POST request
        candle_id = request.POST.get('candle_id')

        if candle_id:
            # Fetch the candle object or return 404 if not found
            candle = get_object_or_404(Candle, id=candle_id)

            # Convert the price from Decimal to float before adding to the cart
            candle_price = float(candle.price)

            # Get the cart from the cookies or initialize it as an empty dictionary
            cart = {}
            if 'cart' in request.COOKIES:
                cart = json.loads(request.COOKIES['cart'])

            # Update the quantity of the item or add a new item to the cart
            if candle_id in cart:
                cart[candle_id]['quantity'] += 1
            else:
                cart[candle_id] = {
                    'id': candle_id,
                    'name': candle.name,
                    'price': candle_price,
                    'quantity': 1,
                }

            # Save the updated cart back into the cookies
            cart_json = json.dumps(cart)

            # Create a response to redirect back to the same page
            response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            # Set the updated cart cookie with a max-age of 7 days (604800 seconds)
            response.set_cookie('cart', cart_json, max_age=604800)

            return response
        else:
            # If no candle_id is provided, redirect back to the page
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # If the method is not POST, redirect back to the same page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
def remove_from_cart(request):
    global CART_COUNT
    if request.method == 'POST':
        # Get the item_id from the request body
        data = json.loads(request.body)
        item_id = data.get('item_id')
        print(item_id)
        # Get the cart from the cookies
        cart = {}
        if 'cart' in request.COOKIES:
            cart = json.loads(request.COOKIES['cart'])

        # Check if the item_id exists in the cart
        if item_id in cart:
            # Remove the item from the cart
            del cart[item_id]

            # Save the updated cart back to the cookies
            cart_json = json.dumps(cart)

            response = JsonResponse({'success': True})
            response.set_cookie('cart', cart_json, max_age=604800)  # Set the updated cart in cookies
            return response
        else:
            # If the item isn't found in the cart
            return JsonResponse({'success': False, 'message': 'Item not found'})

    # If the request method isn't POST, return an error
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
        print(f"Item: {name}, Price: {price}, Quantity: {quantity}")

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