from django.shortcuts import render,redirect
from django.http import HttpResponse
from . models import Product,Contact,Order,OrderUpdate,Transaction
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.contrib import messages
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum
MERCHANT_KEY = 'Q74E7We%Bcdjw7dC'


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

def cartView(request):
    return render(request,'shop/cartview.html')

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query! :-("}
    return render(request, 'shop/search.html', params)

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
    if request.user.is_authenticated:
        if request.method=="POST":
            orderId = request.POST.get('orderId', '')
            email = request.user.email
            try:
                order = Order.objects.filter(order_id=orderId, email=email)  #it returns in form of a array 
                if len(order)>0:
                    update = OrderUpdate.objects.filter(order_id=orderId)
                    updates = []
                    for item in update:
                        updates.append({'text': item.update_desc, 'time': item.timestamp})
                        response = json.dumps({"status":"success","updates": updates, "itemsJson": order[0].items_json}, default=str)
                    return HttpResponse(response)
                else:
                    return HttpResponse('{"status":"noitem"}')   #if no item is there
            except Exception as e:
                return HttpResponse('{"status":"error"}')  #if some error occur

        return render(request, 'shop/tracker.html')
    return render(request,'shop/errorpage.html')

def productView(request,myid):
    #fetch the product using the id
    product = Product.objects.filter(id=myid)
    # print(product)
    return render(request,'shop/prodView.html',{'product':product[0]})

def myorders(request):
    if request.user.is_authenticated:
        email = request.user.email
        Orders={}
        try:
            orders = Order.objects.filter(email=email)  #it returns in form of a array 
            allOrders=[]
            for item in orders:
                allOrders.append({'order_id':item.order_id,'amount':item.amount,'date':item.date})
            Orders={'allOrders':allOrders}
        except Exception as e:
            Orders = {'allOrders':[]}
        return render(request,'shop/myorders.html',Orders)  #if some error occur
    else:
        return render(request,'shop/errorpage.html')

def checkout(request):
    if request.user.is_authenticated:
        user = request.user
        name = user.first_name+user.last_name
        email = user.email
        userDetails={'name':name,'email':email}

        if request.method=="POST":
            items_json = request.POST.get('itemsJson', '')
            amount = request.POST.get('amount', '')
            address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
            city = request.POST.get('city', '')
            state = request.POST.get('state', '')
            zip_code = request.POST.get('zip_code', '')
            phone = request.POST.get('phone', '')
            order = Order(items_json=items_json, name=name,amount=amount, email=email,address=address,city=city,state=state, zip_code=zip_code, phone=phone,date=datetime.today())
            order.save()
            id = order.order_id
            update = OrderUpdate(order_id=id, update_desc="The order requested")
            update.save()
            # Request paytm to transfer the amount to your account after payment by user
            param_dict = {
                    'MID': 'xFCBbJ94852181573190',
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
        return render(request, 'shop/checkout.html',{'userDetails':userDetails})
    return render(request,'shop/errorpage.html')

#authentication APIs
def handleSignup(request):
    if request.method == 'POST':
        #get the post parameter
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        #checks for user inputs
        # username length and alphanumeric
        errors = []
        if len(username) > 10 or len(username) < 3 or not username.isalnum(): 
            errors.append('Username length should be between 3 and 10 and it should be alphanumeric!')
        if len(password1) < 5 or len(password1) > 30:
            errors.append('Password length should be between 4 and 30!')
        if len(fname) <3:
            errors.append('Please enter a valid name!')
        if password1 != password2:
            errors.append('Passwords should Match!')

        #if any error occures redirect to home
        if len(errors) > 0 :
            for error in errors:
                messages.error(request,error)
            return redirect('home')

        #else create the user
        #create the user
        try:
            myuser = User.objects.create_user(username,email,password1)
            myuser.first_name = fname
            myuser.last_name = lname
            myuser.save()
            messages.success(request,'Your  Account has been successfully created! Now can login Now :-)')
        except:
            messages.error(request,'Username already exist please enter another unique username!')
        return redirect('/')
    else:
        return render(request,'shop/errorpage.html')

def handleLogin(request):
    if request.method == 'POST':
        #get the post parameters
        username = request.POST['loginusername']
        password = request.POST['loginpassword']

        user = authenticate(username= username, password= password)
        if user is not None:
            login(request,user)
            messages.success(request, 'Welcome '+username+', You are successfully logged In!')
            return redirect('/')
        else:
            messages.error(request,'Invalid credentials, Please try again! or signup before login if not registered!')
            return redirect('/')
    else:
        return render(request,'shop/errorpage.html')

def handleLogout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You are successfully logged out!')
    return redirect('/')

@csrf_exempt
def handlerequest(request):
    if request.method == "POST":
        # paytm will send you post request here
        form = request.POST
        response_dict = {}
        for i in form.keys():
            response_dict[i] = form[i]
            if i == 'CHECKSUMHASH':
                checksum = form[i]

        verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
        if verify:
            id = response_dict['ORDERID']
            if response_dict['RESPCODE'] == '01':
                update = OrderUpdate(order_id=id, update_desc="Transaction has been made and The order has been placed successfully!")
                update.save()
                transaction = Transaction(order_id = id, txn = response_dict)
                transaction.save()
            else:
                update = OrderUpdate(order_id=id, update_desc="Transaction Pending...")
                update.save()
        return render(request, 'shop/paymentstatus.html', {'response': response_dict})
    else:
        return render(request,'shop/errorpage.html')

