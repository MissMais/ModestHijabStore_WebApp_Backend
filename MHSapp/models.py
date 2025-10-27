from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import IntegrityError,models,transaction


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)
    
class CustomUser(AbstractUser):
    username=None
    email=models.EmailField(unique=True)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects=CustomUserManager()

    def __str__(self):
        return self.email

class Customers(models.Model):
    Customer_id= models.AutoField(primary_key=True )
    User_id=models.OneToOneField(CustomUser,on_delete=models.CASCADE  )
    Email=models.EmailField(max_length=25 , unique=True) 
    Contact=models.PositiveBigIntegerField()
    Profile_picture=models.ImageField(blank=True, null=True)

class Address(models.Model):
    Address_id = models.AutoField(primary_key=True )
    User_id=models.ForeignKey(Customers, on_delete=models.CASCADE,related_name="userid" )
    Address_type=models.CharField(max_length=50)
    Name=models.CharField(max_length=50)
    House_No=models.PositiveIntegerField()
    Area_Colony=models.CharField(max_length=75)
    Landmark=models.CharField(max_length=100)
    Pincode=models.PositiveIntegerField()
    City=models.CharField(max_length=25)
    State=models.CharField(max_length=25)
    Country=models.CharField(max_length=25)
    Contact = models.PositiveBigIntegerField()

class Cart(models.Model):
    Cart_id = models.AutoField(primary_key=True)
    customer_id=models.OneToOneField(Customers , models.CASCADE , related_name="cart")

class Product(models.Model):
    product_id = models.CharField(primary_key=True, max_length=50 , default="PR001")
    product_description = models.CharField(max_length=50, blank=True, null=True)
    Brand_id=models.ForeignKey('Brands',models.CASCADE,related_name="brandid")
    sub_category = models.ForeignKey('Subcategory', models.CASCADE , related_name="products")
    availability = models.CharField(max_length=50, blank=True, null=True)
    price = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'product'

    def save(self,*args, **kwargs):
        if not self.product_id:
            latest_obj = Product.objects.order_by('-product_id').first()
            print(latest_obj)
            print(r"\n\n\n")
            if latest_obj:
                latest_id = int(latest_obj.product_id[2:])
                self.product_id = 'PR{:03d}'.format(latest_id + 1)
            else:
                self.product_id = 'PR001'
        while True:
            try:
                with transaction.atomic():
                    super(Product,self).save(*args, **kwargs)
                break
            except IntegrityError:
                latest_id = int(self.product_id[2:])
                self.product_id = 'PR{:03d}'.format(latest_id + 1)


class Category(models.Model):
    category_id = models.CharField(primary_key=True, max_length=50 , default="C01")
    category_name = models.CharField(max_length=50, blank=True, null=True)
    category_image = models.ImageField( blank=True, null=True)

    class Meta:
        db_table = 'category'

    def save(self,*args, **kwargs):
        if not self.category_id:
            latest_obj = Category.objects.order_by('-category_id').first()
            if latest_obj:
                latest_id = int(latest_obj.category_id[1:])
                self.category_id = 'C{:02d}'.format(latest_id + 1)
            else:
                self.obj_id = 'C01'
        while True:
            try:
                with transaction.atomic():
                    super(Category,self).save(*args, **kwargs)
                break
            except IntegrityError:
                latest_id = int(self.category_id[1:])
                self.category_id = 'C{:02d}'.format(latest_id + 1)

class Subcategory(models.Model):
    sub_category_id = models.CharField(primary_key=True, max_length=50 , default="SC001")
    sub_category_name = models.CharField(max_length=50, blank=True, null=True)
    category_id = models.ForeignKey(Category, models.CASCADE , related_name="categoryid")

    class Meta:
        # managed = False
        db_table = 'subcategory'

    def __str__(self):
        return self.sub_category_name
    def save(self,*args, **kwargs):
        if not self.sub_category_id:
            latest_obj = Subcategory.objects.order_by('-sub_category_id').first()
            if latest_obj:
                latest_id = int(latest_obj.sub_category_id[2:])
                self.sub_category_id = 'SC{:03d}'.format(latest_id + 1)
            else:
                self.sub_category_id = 'SC001'
        while True:
            try:
                with transaction.atomic():
                    super(Subcategory,self).save(*args, **kwargs)
                break
            except IntegrityError:
                latest_id = int(self.sub_category_id[2:])
                self.sub_category_id = 'SC{:03d}'.format(latest_id + 1)


class Variation(models.Model):
    variation_id = models.CharField(primary_key=True, max_length=50 , default="V01")
    variation_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'variation'
    def save(self,*args, **kwargs):
        if not self.variation_id:
            latest_obj = Variation.objects.order_by('-variation_id').first()
            print(latest_obj)
            print(r"\n\n\n")
            if latest_obj:
                latest_id = int(latest_obj.variation_id[1:])
                self.variation_id = 'V{:02d}'.format(latest_id + 1)
            else:
                self.variation_id = 'V01'
        while True:
            try:
                with transaction.atomic():
                    super(Variation,self).save(*args, **kwargs)
                break
            except IntegrityError:
                latest_id = int(self.variation_id[1:])
                self.variation_id = 'V{:02d}'.format(latest_id + 1)

class Variationoption(models.Model):
    variation_option_id = models.CharField(primary_key=True, max_length=50 , default="VO001")
    variation_id = models.ForeignKey(Variation, models.CASCADE , related_name="variationid")
    value = models.CharField(max_length=50, blank=True, null=True)
    ColorCode = models.CharField(max_length=50 , blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'variationoption'
    def save(self,*args, **kwargs):
        if not self.variation_option_id:
            latest_obj = Variationoption.objects.order_by('-option_id').first()
            print(latest_obj)
            print(r"\n\n\n")
            if latest_obj:
                latest_id = int(latest_obj.option_id[1:])
                self.option_id = 'VO{:03d}'.format(latest_id + 1)
            else:
                self.option_id = 'VO001'
        while True:
            try:
                with transaction.atomic():
                    super(Variationoption,self).save(*args, **kwargs)
                break
            except IntegrityError:
                latest_id = int(self.option_id[1:])
                self.option_id = 'VO{:03d}'.format(latest_id + 1)


class Productvariation(models.Model):
    product_variation_id = models.CharField(primary_key=True, max_length=50 , default="PV0001")
    product_id = models.ForeignKey(Product, models.CASCADE , related_name='productid')
    variation_option_id = models.ForeignKey('Variationoption', models.CASCADE, related_name='variationoptionid')
    stock = models.PositiveIntegerField(blank=True, null=True)
    avg_rating=models.FloatField(null=True,blank=True)

    class Meta:
        db_table = 'productvariation'

    def save(self,*args, **kwargs):
        if not self.product_variation_id:
            latest_obj = Productvariation.objects.order_by('-product_variation_id').first()
            print(latest_obj)
            print(r"\n\n\n")
            if latest_obj:
                latest_id = int(latest_obj.product_variation_id[2:])
                self.product_variation_id = 'PV{:04d}'.format(latest_id + 1)
            else:
                self.product_variation_id = 'PV0001'
        while True:
            try:
                with transaction.atomic():
                    super(Productvariation,self).save(*args, **kwargs)
                break
            except IntegrityError:
                latest_id = int(self.product_variation_id[2:])
                self.product_variation_id = 'PV{:04d}'.format(latest_id + 1)


class Cart_item(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    Cart_id = models.ForeignKey(Cart , models.CASCADE , related_name="cartid")
    product_variation_id=models.ForeignKey(Productvariation ,  models.CASCADE , related_name="productvariationid" )
    Quantity=models.PositiveIntegerField()
    Sub_Total=models.PositiveIntegerField()


class Size(models.Model):
    size_id = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    size_value = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'size'

class ProductImages(models.Model):
    product_images_id= models.AutoField(primary_key=True)
    image_url = models.ImageField(null=True , blank=True) 
    product_variation_id = models.ForeignKey(Productvariation, models.CASCADE , related_name="images" )  

    class Meta:
        managed=True
        db_table = 'mhs_app_product_img' 


class Quotes(models.Model):
    quote_id=models.AutoField(primary_key=True)
    quote=models.CharField(max_length=100,null=True)

    class Meta:
        db_table = 'Quotes' 


class Order(models.Model):
    Order_id = models.AutoField(primary_key=True)
    Order_Date=models.DateTimeField(auto_now_add=True)
    Delivery_Address=models.ForeignKey(Address , models.CASCADE,related_name="delivery")
    Cart_id=models.ForeignKey(Cart , models.CASCADE,related_name="order")
    payment_id=models.ForeignKey("Payment",models.CASCADE,related_name="paymentid")
    payment_confirmation=models.CharField(max_length=20,null=True)
    order_status=models.CharField(max_length=20, null=True)

class OrderHistory(models.Model):
    order_history_id=models.AutoField(primary_key=True)
    order_id=models.ForeignKey(Order , models.CASCADE,related_name="orderid")
    customer_id=models.ForeignKey(Customers , models.CASCADE,related_name="customerid")
    cart_item_id=models.ForeignKey(Cart_item ,models.CASCADE,related_name="cartitemid")


class Payment(models.Model):
    Payment_id=models.AutoField(primary_key=True)
    Payment_mode=models.CharField(max_length=50,null=True)


class Brands(models.Model):
    Brand_id=models.AutoField(primary_key=True)
    Brand_name=models.CharField(max_length=50, null=True)
    Brand_image=models.ImageField(null=True , blank=True)

class HomePageImage(models.Model):
    homepageimage_id=models.AutoField(primary_key=True)
    category=models.ForeignKey(Category,models.CASCADE,related_name="homepage_images")
    image = models.ImageField(upload_to="homepage_images/")

    class Meta:
        db_table = "homepage_image"

    def __str__(self):
        return f"Image for {self.category.category_name}"
    
class Wishlist(models.Model):
    wishlist_id=models.AutoField(primary_key=True)
    customer_id=models.ForeignKey(Customers,models.CASCADE,related_name="customid")
    product_variation_id=models.ForeignKey(Productvariation,models.CASCADE,related_name="prodid")
   

class Notifications(models.Model):
    notification_id=models.AutoField(primary_key=True)
    notification_msg=models.CharField(max_length=100,null=True)
    customer_id=models.ForeignKey(Customers,models.CASCADE,related_name="notification")

class Varieties(models.Model):
    Variety_id=models.AutoField(primary_key=True)
    Variety_image=models.ImageField(upload_to="variety_images/")
    Brand_id=models.ForeignKey(Brands, models.CASCADE,related_name="brands")
    Variation_option_id=models.ForeignKey(Variationoption ,models.CASCADE, related_name="variation_options")


class Customer_rating(models.Model):
    customer_rating_id=models.AutoField(primary_key=True)
    customer_id=models.ForeignKey(Customers,models.CASCADE,related_name="customer")
    product_variation_id=models.ForeignKey(Productvariation,models.CASCADE,related_name="product")
    rating=models.IntegerField(null=True, blank=True)