from django.shortcuts import render
from django.http import HttpResponse
from . models import Product,Contact
from datetime import datetime
from django.contrib import messages
from math import ceil

# Create your views here.
def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
        
    params = {'allProds':allProds}
    return render(request,'shop/index.html',params)

def about(request):
    return render(request,'shop/about.html')

def contact(request):
    if request.method=="POST":
        # print(request)
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        # print(name,email,phone,desc)
        contact = Contact(name=name, email=email, phone=phone, desc=desc,date=datetime.today())
        print(contact.save())
        # messages.warning(request,errors)
        messages.success(request, 'Your Query has been sent :-)')
    return render(request, 'shop/contact.html')

def tracker(request):
    return render(request,'shop/tracker.html')

def search(request):
    return render(request,'shop/search.html')

def productView(request,myid):
    #fetch the product using the id
    product = Product.objects.filter(id=myid)
    # print(product)
    return render(request,'shop/prodView.html',{'product':product[0]})

def checkout(request):
    return render(request,'shop/checkout.html')
    # return HttpResponse("we are at checkout page")

