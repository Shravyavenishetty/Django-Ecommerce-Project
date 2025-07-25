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


    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists() # check if the product is already in the cart
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart) # get the cart item for the product
        # existing_variations -> database
        # current_variation -> product_variation
        # item_id -> id of the variation
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variations = item.variations.all()
            ex_var_list.append(list(existing_variations))
            id.append(item.id)
        print(ex_var_list)

        if product_variation in ex_var_list:
            # increase the quantity if the product already exists in the cart
            index = ex_var_list.index(product_variation) # get the index of the product variation
            item_id = id[index] # get the id of the cart item
            item = CartItem.objects.get(product=product, id = item_id)
            item.quantity += 1 # increase the quantity
            item.save()
        else:
            # create a new cart item if the product does not exist in the cart
            item = CartItem.objects.create(product=product, quantity=1, cart=cart) # create a new cart item
            if len(product_variation) > 0:
                item.variations.clear() # clear existing variations
                item.variations.add(*product_variation)
        # cart_item.quantity += 1 # increase the quantity if it exists
                item.save()
    else:
        # create a new cart item if it doesn't exist
        cart_item = CartItem.objects.create(product=product, quantity=1,cart=cart)
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation) # add variations to the cart item
        cart_item.save()
    return redirect('cart') # redirect to the cart view

def remove_cart(request, product_id,cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart by session id
    product = get_object_or_404(Product,id=product_id) # get the product by id
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart,id=cart_item_id) # get the cart item for the product
        if cart_item.quantity > 1:
            cart_item.quantity -= 1 # decrease the quantity if more than 1
            cart_item.save()
        else:
            cart_item.delete() # delete the cart item if quantity is 1
    except:
        pass
    return redirect('cart') # redirect to the cart view

def remove_cart_item(request, product_id,cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart by session id
    product = get_object_or_404(Product, id=product_id) # get the product by id
    cart_item = CartItem.objects.get(product=product, cart=cart,id=cart_item_id) # get the cart item for the product
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
