from django.shortcuts import render,redirect, get_object_or_404
from .models import Cart, CartItem
from store.models import Product
from django.core.exceptions import ObjectDoesNotExist
from store.models import Variation

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id) # get the product by id
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            
            try:
                variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation) # add variation to the list
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart by session id
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request)) # create a new cart if it doesn't exist
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart) # get the cart item for the product
        cart_item.quantity += 1 # increase the quantity if it exists
        cart_item.save()
    except CartItem.DoesNotExist:
        # create a new cart item if it doesn't exist
        cart_item = CartItem.objects.create(product=product, quantity=1,cart=cart)
        cart_item.save()
    return redirect('cart') # redirect to the cart view

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart by session id
    product = get_object_or_404(Product,id=product_id) # get the product by id
    cart_item = CartItem.objects.get(product=product, cart=cart) # get the cart item for the product
    if cart_item.quantity > 1:
        cart_item.quantity -= 1 # decrease the quantity if more than 1
        cart_item.save()
    else:
        cart_item.delete() # delete the cart item if quantity is 1
    return redirect('cart') # redirect to the cart view

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart by session id
    product = get_object_or_404(Product, id=product_id) # get the product by id
    cart_item = CartItem.objects.get(product=product, cart=cart) # get the cart item for the product
    cart_item.delete() # delete the cart item
    return redirect('cart') # redirect to the cart view
    
def cart(request,total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart by session id
        cart_items = CartItem.objects.filter(cart=cart, is_active=True) # get all active cart items
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity) # calculate total price
            quantity += cart_item.quantity # calculate total quantity
        tax = (2* total)/100 # calculate tax (2% of total)
        grand_total = total + tax # calculate grand total
    except ObjectDoesNotExist:
        pass # if cart does not exist, total and quantity remain 0

    context= {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html',context)
