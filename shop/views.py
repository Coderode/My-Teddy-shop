from django.shortcuts import render
from django.http import HttpResponse
from . models import Product,Contact,Order,OrderUpdate
from datetime import datetime
from django.contrib import messages
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum
MERCHANT_KEY = 'Your-Merchant-Key-Here'


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
        contact.save()
        # messages.warning(request,errors)
        messages.success(request, 'Your Query has been sent :-)')
    return render(request, 'shop/contact.html')

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Order.objects.filter(order_id=orderId, email=email)  #it returns in form of a array 
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse(1)
        except Exception as e:
            return HttpResponse(1)

    return render(request, 'shop/tracker.html')


def search(request):
    return render(request,'shop/search.html')

def productView(request,myid):
    #fetch the product using the id
    product = Product.objects.filter(id=myid)
    # print(product)
    return render(request,'shop/prodView.html',{'product':product[0]})

def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Order(items_json=items_json, name=name,amount=amount, email=email,address=address,city=city,state=state, zip_code=zip_code, phone=phone,date=datetime.today())
        order.save()
        id = order.order_id
        update = OrderUpdate(order_id=id, update_desc="The order has been placed")
        update.save()
        param_dict = {

                'MID': 'Your-Merchant-Id-Here',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'shop/paytm.html', {'param_dict': param_dict})
        # return render(request, 'shop/checkout.html', {'status':True, 'id': id})
    return render(request, 'shop/checkout.html')


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})

