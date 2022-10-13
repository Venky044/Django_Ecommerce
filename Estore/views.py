from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
import datetime

from .models import *
from .utils import cookieCart, cartData, guestOrder

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout

from .form import CustomUserCreationForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def userLogin(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('store')

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "username doesn't exit.")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store')

    return render(request, 'Estore/login_register.html', {'page':page})

def userLogout(request):
    logout(request)
    messages.success(request, "successfully logged out..")
    return redirect('login')


def userRegister(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            login(request, user)
            return redirect('store')

    context = {'page':page, 'form':form}
    return render(request, 'Estore/login_register.html', context)


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    page = 'store'

    # search product
    search_item = ''
    if request.GET.get('search_item'):
        search_item = request.GET.get('search_item')

    product = Product.objects.filter(name__icontains=search_item)

    # pagination
    pages = request.GET.get('page')
    pagination = Paginator(product, 6)

    try:
        product = pagination.page(pages)
    except EmptyPage:
        pages = pagination.num_pages
        product = pagination.page(pages)
    except PageNotAnInteger:
        pages = 1
        product = pagination.page(pages)

    leftIndex = (int(pages) - 1)
    if leftIndex < 1:
        leftIndex = 1
    
    rightIndex = (int(pages) + 1)
    if rightIndex > pagination.num_pages:
        rightIndex = pagination.num_pages
    
    pageIndex_range = range(leftIndex, rightIndex + 1)

    context = {'products':product, 'cartItems':cartItems, 'search_item':search_item, 'page':page, 'pagination':pagination, 'pageIndex_range':pageIndex_range}
    return render(request, 'Estore/store.html', context)


def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']


    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'Estore/cart.html' ,context)


def checkOut(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'Estore/check_out.html', context)

 
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)
        
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment complete', safe=False)

