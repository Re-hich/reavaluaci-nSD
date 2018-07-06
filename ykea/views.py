from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .models import *
from django.core.urlresolvers import reverse
from django.contrib import auth
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import ItemSerializer
from .permissions import *


def index(request):
    items_by_category = Item.CATEGORIES
    if request.user.is_authenticated:
        usermoneyAcount = WebUser.objects.filter(user=request.user.pk).values_list("money", flat=True)[0]
    else:
        usermoneyAcount = 0
    context = {
        'categories': items_by_category,
        'money' : usermoneyAcount,
    }
    return render(request, 'ykea/index.html', context)

def items(request, category=""):
    items_by_category = Item.objects.filter(category=category)
    categories = Item.CATEGORIES
    usermoneyAcount=0;
    if request.user.is_authenticated:
        usermoneyAcount = WebUser.objects.filter(user=request.user.pk).values_list("money", flat=True)[0]
    context = {
        'items': items_by_category,
        'category': category,
        'categories': categories,
        'money': usermoneyAcount,
    }
    return render(request, 'ykea/items.html', context)

def item(request, item_number=""):
    item_by_category = Item.objects.get(item_number=item_number)
    categories = Item.CATEGORIES
    if request.user.is_authenticated:
        usermoneyAcount = WebUser.objects.filter(user=request.user.pk).values_list("money", flat=True)[0]
    context = {
        'item':item_by_category,
        'number': item_number,
        'money' : usermoneyAcount,
        'categories' : categories,
    }
    return render(request, 'ykea/item.html', context)  

@login_required
def shoppingcart(request):
    if "selectedItem" in request.session:
        selectedItems = request.session["selectedItem"]
    else:
        selectedItems = []

    if request.user.is_authenticated:
        usermoneyAcount = WebUser.objects.filter(user=request.user.pk).values_list("money", flat=True)[0]

    items = ShoppingCart.objects.filter(user=request.user).filter(bought=0)
    price = 0
    for it in items:
        price += it.item.price
    
    if 'addshop' in request.POST:
        for key in request.POST:
            if key.startswith("checkbox"):
                item = Item.objects.get(item_number=request.POST[key])
                shop = ShoppingCart.objects.filter(item=item).filter(user=request.user).exists()
                if not shop:
                    shoppingcart = ShoppingCart(item=item, user=request.user, name=request.user.username)
                else :
                    shoppingcart = ShoppingCart.objects.filter(item=item).filter(user=request.user)[0]
                shoppingcart.save()
    elif 'delete' in request.POST:
        for key in request.POST:
            if key.startswith("checkbox"):
                item = Item.objects.get(item_number=request.POST[key])
                shoppingcart = ShoppingCart.objects.filter(item=item).filter(user=request.user)[0]
                shoppingcart.delete()
    elif 'buy' in request.POST:
        if price <= usermoneyAcount:
            user = WebUser.objects.get(user=request.user)
            user.money = usermoneyAcount-float(price)
            user.save()

            for it in items:
                ite = Item.objects.get(item_number=it.item.item_number)
                item = ShoppingCart.objects.filter(item=ite).filter(user=request.user)[0]
                item.bought = 1
                item.save()
            return HttpResponseRedirect(reverse('bought'))
        else:
            return HttpResponse('You don\'t have enough money')

    return HttpResponseRedirect(reverse('buy')) 

@login_required()
def buy(request):
    if not request.user.is_authenticated():
        return render(request, 'ykea/login_error.html')
    if request.user.is_authenticated:
        usermoneyAcount = WebUser.objects.filter(user=request.user.pk).values_list("money", flat=True)[0]
    items_shoppingcart = []
    numbers = ShoppingCart.objects.filter(user=request.user).filter(bought=0)
    categories = Item.CATEGORIES
    price = 0
    for num in numbers:
        price += num.item.price
        items_shoppingcart.append(num.item)
    
    context = {
        'item': items_shoppingcart,
        'price': price,
        'categories': categories,
        'money': usermoneyAcount,
    } 
    return render(request, 'ykea/buy.html', context)

@login_required()
def bought(request):
    if not request.user.is_authenticated():
        return render(request, 'ykea/login_error.html')
    if request.user.is_authenticated:
        usermoneyAcount = WebUser.objects.filter(user=request.user.pk).values_list("money", flat=True)[0]
    items_shoppingcart = []
    numbers = ShoppingCart.objects.filter(user=request.user).filter(bought=1)
    categories = Item.CATEGORIES
    for num in numbers:
        items_shoppingcart.append(num.item)
    
    context = {
        'item': items_shoppingcart,
        'categories': categories,
        'money': usermoneyAcount,
    } 
    return render(request, 'ykea/bought.html', context)

def login_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        # Correct password, and the user is marked "active"
        auth.login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect("/account/loggedin/")
    else:
        # Show an error page
        return HttpResponseRedirect("/account/invalid/")

def logout_view(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/account/loggedout/")

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })


class ItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Items to be viewed or edited.
    """
    queryset = Item.objects.all().order_by('item_number')
    permission_classes = [read_run_permission,Comercial_permission]
    serializer_class = ItemSerializer

def get_queryset(self):
    queryset = Item.objects.all()
    for p in self.request.query_params:
        if(p is not None):
            query_param = self.request.query_params.get(p, None)
            if(p == 'category'):
                queryset = queryset.filter(category=query_param)
            elif(p == 'new'):
                queryset = queryset.filter(is_new=query_param)
            elif(p == 'price'):
                queryset = queryset.filter(price__lt=query_param)
            #queryset = queryset.filter(price=query_param)
            
            return queryset

def comparator(request):
    
    cat = Item.objects.values('category').distinct()
    context = { 'category': cat }
    return render(request, 'ykea/comparator.html',context)

