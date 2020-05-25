from django.db import models

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=500)
    pub_date = models.DateField()
    image = models.ImageField(upload_to='shop/images', default="")

    def __str__(self):
        return str(self.id)+" : "+self.product_name

#here django create its own primary key named 'id' if we don't declare any primary key
#that's why we are using id instead of product_id everywhere 
#or make the product_id as primary key and then use it

class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=12, default="")
    desc = models.CharField(max_length=500, default="")
    date = models.DateField()

    def __str__(self):
        return self.name+" : "+self.date.strftime("%d-%b-%Y")

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=70)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=12, default="")
    date = models.DateField()

    def __str__(self):
        return "order id : "+str(self.order_id)+" : "+self.date.strftime("%d-%b-%Y")

class OrderUpdate(models.Model):
    update_id  = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=1000)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return "order:"+str(self.order_id)+" update:"+str(self.update_id)+" "+self.timestamp.strftime("%d-%b-%Y")