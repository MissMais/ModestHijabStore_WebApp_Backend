from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes ,authentication_classes
from MHSapp.serializers import *
from .models import * 
from django.contrib.auth.models import User 
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from django.urls import reverse
from MHSapp.views import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.core.mail import EmailMessage  
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
# from .serializers import SignupSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from django.core.mail import send_mail
import random as rn

class ChangePassword(APIView):
     permission_classes=[IsAuthenticated]
     def post(self,request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        com_password = request.data.get('confirm_password')
        if not user.check_password(old_password):
            return Response("Old password is incorrect")
        if new_password!=com_password:
             return Response("New password and confirm password do not match")
        user.set_password(new_password)
        user.save()
        return Response("Password changed successfully")
  
import random 
sent_otp=" "
stored_email = " "
otp_verified= False
@permission_classes([AllowAny])
class SendOTP(APIView):
     def post(self,request):              
          email=request.data['to']
          print("\n"*5)
          print(email)
          global stored_email , sent_otp , otp_verified
          otp=str(random.randint(1000, 9999) )
          otp_verified=False
          sent_otp=otp # store otp globlly
          stored_email=email # store email globlly
          print("OTP Is :",sent_otp)
          emailw=EmailMessage(
               'OTP for password reset',
               f'Your OTP is: {otp}',
               settings.EMAIL_HOST_USER,
               [email]
          )
          emailw.send(fail_silently=False)
          return Response({'status':True,'message':'OTP sent successfully'}) 
@permission_classes([AllowAny])
class VerifyOTP(APIView):
     def post(self,request):
          global otp_verified #for use 
          entered_otp=request.data.get("otp")
          if sent_otp == entered_otp:
                otp_verified = True 
                return Response('OTP verified successfully')
          return Response("Invalid OTP")
@permission_classes([AllowAny])
class forgetPassword(APIView):
     def post(self , request):
          global otp_verified , sent_otp , stored_email #for use
          new_password=request.data.get('new_password')
          confirm_password=request.data.get('confirm_password')
          if not otp_verified:
            return Response("OTP not verified")
          
          if new_password!= confirm_password:
                return Response('New Password and Confirm Password do not Match')
          try:
              user=CustomUser.objects.get(email=stored_email)
              user.set_password(new_password)
              user.save()
              otp_verified = False
              sent_otp = ""
              stored_email = ""
              return Response("Reset password successfully")
          except CustomUser.DoesNotExist:
               return Response("user not found")
        

@api_view(["POST"])
def LoginView(request):
    try:
        data = request.data
        email = data.get("email")
        password = data.get("password")

        user = authenticate(email=email, password=password)

        if user is None:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        # JWT token ke liye
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login Successfull",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# @permission_classes([AllowAny])
class LogoutView(APIView):
    #  permission_classes=[IsAuthenticated]
     def post(self,request):
          refresh_token_value=request.data.get("refresh")
          token=RefreshToken(refresh_token_value)
          token.blacklist()
          return Response("Logged out successfully.")

    

@api_view(["POST"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])  
def Customer_registration(request):
    try:
        data = request.data
        # Create CustomUser
        user = CustomUser.objects.create(
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"]
        )
        user.set_password(data["password"])
        user.save()

        # Create Customer
        customer = Customers.objects.create(
            User_id=user,
            Contact=data["contact"],
            Email=data["email"]  # optional, else skip this field
        )

        # Create Address
        Address.objects.create(
            User_id=customer,
            Address_type=data["address_type"],
            Name=data["first_name"],
            House_No=data["house_no"],
            Area_Colony=data["area_colony"],
            Landmark=data["landmark"],
            Pincode=data["pincode"],
            City=data["city"],
            State=data["state"],
            Country=data["country"],
            Contact=data["contact"],
        )

        # Create Cart
        Cart.objects.create(customer_id=customer)
        #Create Notification
        notification_message="Welcome to Modest Hijab Store ....Signup Successfully"
        Notifications.objects.create(
            notification_msg=notification_message,
            customer_id=customer
        )

        return Response({
            "message": "User, Customer, Address, Cart and Notification created successfully"
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET","POST","PATCH","DELETE"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])  
def UserView(request):
    if request.method=="GET":
        id = request.GET.get('id', None)
        if id:
            obj= CustomUser.objects.filter(id=id)
            serializer= UserSerializers(obj, many=True)
            return Response(serializer.data)
        users=CustomUser.objects.all()
        serializer=UserSerializers(users , many=True)
        return Response(serializer.data)
    
    elif request.method=="POST":
        post_data=request.data
        ser=UserSerializers(data=post_data)
        if ser.is_valid():
            ser.save()
            return Response("User Added")
        return Response(ser.errors)
        
    elif request.method=="PATCH":
        cart_id=request.data.get("id")
        cart_obj=CustomUser.objects.get(id=cart_id)
        ser=UserSerializers(cart_obj , data=request.data , partial=True)
        if ser.is_valid():
            ser.save()
            return Response("Updated Successfully")
        return Response(ser.errors)
    
    elif request.method == "DELETE":
        user_id = request.GET.get("id")
        print(user_id)
        obj = CustomUser.objects.get(id=user_id)
        obj.delete()
        return Response("User deleted")


@api_view(["GET","POST","PUT","DELETE"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])   
def CustomerView(request):
    if request.method=="GET":
        users=Customers.objects.all()
        ser=CustomerSerializers(users , many=True)
        return Response(ser.data)
    
    elif request.method=="POST":
        post_data=request.data
        ser=CustomerSerializers(data=post_data)
        if ser.is_valid():
            ser.save()
            return Response("Customer Added")
        return Response(ser.errors)
    
    elif request.method=="PUT":
        cart_id=request.data.get("id")
        cart_obj=Customers.objects.get(id=cart_id)
        ser=CustomerSerializers(cart_obj , data=request.data , partial=True)
        if ser.is_valid():
            ser.save()
            return Response("Updated Successfully")
        return Response(ser.errors)
    
    elif request.method=="DELETE":
        id=request.data["id"]
        obj=Customers.objects.get(id=id)
        obj.delete()
        return Response("Customer Deleted")
    

@api_view(["GET","POST","PUT","DELETE"]) 
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])  
def AddressView(request):
    if request.method == 'GET':
        id = request.GET.get('id', None) 
        if id:
            obj=Address.objects.filter(Address_id=id)
            serializer = AddressSerializer(obj, many=True)
            return Response(serializer.data)
    
        obj = Address.objects.all()
        serializer = AddressSerializer(obj, many=True)
        return Response(serializer.data)

    elif request.method=="POST":
        post_data=request.data
        ser=AddressSerializer(data=post_data)
        if ser.is_valid():
            ser.save()
            return Response("Address Added Successfully")
        return Response(ser.errors)
    
    elif request.method=="PUT":
        add_id=request.data.get("Address_id")
        add_obj=Address.objects.get(Address_id=add_id)
        ser=AddressSerializer(add_obj , data=request.data , partial=True)
        if ser.is_valid():
            ser.save()
            return Response("Updated Successfully")
        return Response(ser.errors) 
    
    elif request.method=="DELETE":
        add_id=request.data["Address_id"]
        add_obj=Address.objects.get(Address_id=add_id)
        add_obj.delete()
        return Response("Address Deleted Successfully")


@api_view(["GET","POST","PUT","DELETE"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])  
def CartView(request):
    if request.method=="GET":
        users=Cart.objects.all()
        ser=CartSerializer(users , many=True)
        return Response(ser.data)
    elif request.method=="POST":
        post_data=request.data
        ser=CartSerializer(data=post_data)
        if ser.is_valid():
            ser.save()
            return Response("Cart Added")
        return Response(ser.errors)
    elif request.method=="PUT":
        cart_id=request.data.get("Cart_id")
        cart_obj=Cart.objects.get(Cart_id=cart_id)
        ser=CartSerializer(cart_obj , data=request.data , partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors)
    elif request.method=="DELETE":
        id=request.data["Cart_id"]
        obj=Cart.objects.get(Cart_id=id)
        obj.delete()
        return Response("Cart Deleted")
    
@api_view(["GET","POST","PUT", "DELETE"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])  
def SubcategoryView(request):
    if request.method=='GET':
       obj=Subcategory.objects.all()
       ser=SubcategorySerializers(obj,many=True)
       return Response(ser.data)
    
    elif request.method=="POST":
        data= request.data
        print(data)
        serializer=SubcategorySerializers(data=data)
        
        if serializer.is_valid():
            serializer.save()
          
            return Response("Added Successfully")
        print(serializer.errors)
        return Response(serializer.errors)
    elif request.method=="PUT":
        id=request.data.get("sub_catgeory_id")
        obj= Subcategory.objects.get(sub_catgeory_id=id)
        serializer=SubcategorySerializers(obj , data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response("Updated Successfully")
        return Response(serializer.errors)
    elif request.method=="DELETE":
        id=request.data["sub_catgeory_id"]
        obj= Subcategory.objects.get(sub_catgeory_id=id)
        obj.delete()
        return Response({'message':"Sub category deleted"})


@api_view(["GET","POST","PUT","DELETE"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])  
def ProductView(request):
    if request.method=='GET':
        obj=Product.objects.all()
        ser=ProductSerializers(obj,many=True)
        return Response(ser.data)
    
    elif request.method=="POST":
        
        data= request.data
        print(data)
        serializer=ProductSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response("Product Added Successfully")
        print(serializer.errors)
        return Response(serializer.errors)
    elif request.method=="PUT":
        id=request.data.get("product_id")
        obj=Product.objects.get(product_id=id)
        serializer=ProductSerializers(obj,data=request.data,many=True)
        if serializer.is_valid():
            serializer.save()
            return Response("Product Updated Successfully")
        return Response(serializer.errors)
    
    elif request.method=="DELETE":
        id=request.data["product_id"]
        obj=Product.objects.get(product_id=id)
        obj.delete()
        return Response("Product Deleted Successfully")  


@api_view(["GET","POST","PUT","DELETE"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])  
def CategoryView(request):
    if request.method == 'GET':
        obj= Category.objects.all()
        serializer= CategorySerializers(obj , many=True, context={'request':request})
        return Response(serializer.data)

    elif request.method=="POST":
        data= request.data
        serializer=CategorySerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response("Category Added Successfully")
        print(serializer.errors)
        return Response(serializer.errors)

    elif request.method=="PUT":
        cat_id=request.data.get("category_id")
        obj_id=Category.objects.get(category_id=cat_id)
        ser=CategorySerializers(obj_id , data=request.data , partial= True)
        if ser.is_valid():
            ser.save()
            return Response("Category Updated Successfully")
        return Response(ser.errors)

    elif request.method=="DELETE":
        id=request.data["category_id"]
        obj=Category.objects.get(category_id=id)
        obj.delete()
        return Response("Category Delete Successfully")
    
@api_view(["GET","POST"])
def Homepageimage(request):
    if request.method == 'GET':
        obj= HomePageImage.objects.all()
        serializer= HomepageimageSerializer(obj , many=True, context={'request':request})
        return Response(serializer.data)

    elif request.method=="POST":
        data= request.data
        print(data)
        serializer=HomepageimageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors)


@api_view(["GET","POST","PUT","DELETE"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])  
def VariationView(request):
    if request.method=='GET':
        obj= Variation.objects.all()
        serializer= VariationSerializers(obj , many=True)
        return Response(serializer.data)

    elif request.method=="POST":
        data= request.data
        serializer=VariationSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    if request.method=="PUT":
        id=request.data.get("variation_id")
        obj_id=Variation.objects.get(variation_id=id)
        ser=VariationSerializers(obj_id , data=request.data , partial= True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors)

    elif request.method=="DELETE":
        data= request.data
        obj= Variation.objects.get(variation_id= data['variation_id'])
        obj.delete()
        return Response({'message':"variation deleted"})


@api_view(["GET","POST","PUT","DELETE"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])  
def VariationoptionView(request):
    if request.method=='GET':
        obj= Variationoption.objects.all()
        serializer= VariationoptionSerializers(obj , many=True)
        return Response(serializer.data)

    elif request.method=="POST":
        data= request.data
        serializer=VariationoptionSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors)
    
    elif request.method=="PUT":
        id=request.data.get("variation_option_id")
        obj_id=Variationoption.objects.get(variation_id=id)
        ser=VariationoptionSerializers(obj_id , data=request.data , partial= True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors)

    elif request.method=="DELETE":
        id=request.data["variation_option_id"]
        obj=Variationoption.objects.get(variation_id=id)
        obj.delete()
        return Response("Variationoption Delete Successfully")


@api_view(["GET","POST","PUT","DELETE"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])  
def ProductvariationView(request):
    if request.method=='GET':
        obj= Productvariation.objects.all()
        serializer= ProductvariationSerializers(obj , many=True)
        return Response(serializer.data)
    
    elif request.method=="POST":
        data= request.data
        serializer=ProductvariationSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    elif request.method=="PUT":
        id=request.data.get("product_variation_id")
        obj=Productvariation.objects.get(product_variation_id=id)
        serializer=ProductvariationSerializers(obj,data=request.data,many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    elif request.method=="DELETE":
        data= request.data
        obj= Productvariation.objects.get(product_id= data['product_variation_id'])
        obj.delete()
        return Response({'message':"ProductVariation deleted"})

@api_view(['GET'])
def CustomView(request):
    obj = Productvariation.objects.all()
    serializer = CustomSerializers(obj,many=True  , context={'request': request})
    return Response(serializer.data)


@api_view(["GET","POST","PUT","DELETE"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])  
def ProductImageView(request):
    if request.method=="GET":
        obj=ProductImages.objects.all()
        ser=ProductImagesSerializers(obj , many=True,  context={"request": request})
        return Response(ser.data)
    if request.method=="POST":
        post_data=request.data
        ser=ProductImagesSerializers(data=post_data, context={"request": request})
        if ser.is_valid():
            ser.save()
            return Response("ProductImage Added Successfully")
        return Response(ser.errors)
    if request.method=="PUT":
        pro_id=request.data.get("product_images_id")
        obj_id=ProductImages.objects.get(product_images_id=pro_id)
        ser=ProductImagesSerializers(obj_id , data=request.data , partial= True, context={"request": request})
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors)
    if request.method=="DELETE":
        id=request.data["product_images_id"]
        obj=ProductImages.objects.get(product_images_id=id)
        obj.delete()
        return Response("ProductImage Delete Successfully")
    

@api_view(["GET"])
def OrderHistory1(request,value):
    if request.method=="GET":
        filter=OrderHistory.objects.all().filter(customer_id=value)
        ser=OrderHistorySerializer(filter,many=True,context={"request": request})
        return Response(ser.data)


@api_view(["GET","POST"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])  
def OrderHistoryView(request):
    if request.method=="GET":
        id = request.GET.get('id', None)
        if id:
            obj= OrderHistory.objects.filter(customer_id=id)
            serializer= OrderHistorySerializer(obj, many=True,context={"request": request})
            return Response(serializer.data)
        orders=OrderHistory.objects.all()
        serializer=OrderHistorySerializer(orders , many=True,context={"request": request})
        return Response(serializer.data)

    
    elif request.method=="POST":
        post_data=request.data
        ser=OrderHistorySerializer(data=post_data,context={"request": request})
        if ser.is_valid():
            ser.save()
            return Response("Order History Added")
        return Response(ser.errors)
    

@api_view(["GET","POST","PUT","DELETE"])
def BrandView(request):
    if request.method=="GET":
        obj=Brands.objects.all()
        ser=BrandsSerializers(obj,many=True,context={"request": request})
        return Response(ser.data)
    elif request.method=="POST":
        post_data=request.data
        ser=BrandsSerializers(data=post_data,context={"request": request})
        if ser.is_valid():
            ser.save()
            return Response({"message":"Brand Post Successful"})
        return Response(ser.errors)
    elif request.method=="PUT":
        id=request.data.get("Brand_id")
        obj=Brands.objects.get(Brand_id=id)
        ser=BrandsSerializers(obj,data=request.data,partial=True)
        if ser.is_valid():
            ser.save()
            return Response("Brand Changed Successfully")
        return Response(ser.errors)
    elif request.method=="DELETE":
        id=request.data["Brand_id"]
        obj=Brands.objects.get(Brand_id=id)
        obj.delete()
        return Response("Delete Successfully")
        

@api_view(["GET","POST"])
def PaymentView(request):
    if request.method=="GET":
        obj=Payment.objects.all()
        ser=PaymentSerializers(obj,many=True)
        return Response(ser.data)
    if request.method=="POST":
        post_data=request.data
        ser=PaymentSerializers(data=post_data)
        if ser.is_valid():
            ser.save()
            return Response({"message":"Payment Post Successful"})
        return Response(ser.errors)  

@permission_classes([AllowAny])
class AddToCartAPIView(APIView): 
    def get(self, request):
        try:
            # 1. Authentication check
            if request.user.is_anonymous:
                return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            customer = Customers.objects.get(User_id=request.user)
            cart = Cart.objects.get(customer_id=customer)
            cart_items = Cart_item.objects.filter(Cart_id=cart)  
            if not cart_items.exists():
                return Response({"message": "Cart is empty"}, status=status.HTTP_200_OK)
            serializer = CartItemSerializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Customers.DoesNotExist:
            return Response({"error": "Customer profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Cart.DoesNotExist:
            return Response({"message": "Cart is empty"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        try:      
            if request.user.is_anonymous:
                return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)  
            customer = Customers.objects.get(User_id=request.user)
            cart, _ = Cart.objects.get_or_create(customer_id=customer)
            quantity = int(request.data.get("quantity", 1))
            product_variation = Productvariation.objects.get(pk=request.data['product_variation_id'])
   
            #Subtotal Calculation
            price = product_variation.product_id.price
            subtotal = price * quantity

            #  Add or update cart item
            cart_item = Cart_item.objects.create(
                Cart_id=cart,
                product_variation_id=product_variation,
                Quantity=quantity,
                Sub_Total=subtotal
            )

            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        except Customers.DoesNotExist:
            return Response({"error": "Customer profile not found"}, status=status.HTTP_404_NOT_FOUND)

        except Productvariation.DoesNotExist:
            return Response({"error": "Product variation not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
    def patch(self, request):
        try:
            if request.user.is_anonymous:
                return Response({"error": "Authentication required"}, status=401)
            customer = Customers.objects.get(User_id=request.user)
            cart = Cart.objects.get(customer_id=customer)
            cart_item_id = request.data.get("cart_item_id")
            quantity = int(request.data.get("quantity", 1))
            item = Cart_item.objects.get(Cart_id=cart, cart_item_id=cart_item_id)
            item.Quantity = quantity
            item.Sub_Total = quantity * item.product_variation_id.product_id.price
            item.save()
            return Response({"message": "Cart item updated"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    def delete(self, request):
        try:
            if request.user.is_anonymous:
                return Response({"error": "Authentication required"}, status=401)
            customer = Customers.objects.get(User_id=request.user)
            cart = Cart.objects.get(customer_id=customer)
            cart_item_id = request.data.get("cart_item_id", None)
            if cart_item_id:
                Cart_item.objects.get(Cart_id=cart, cart_item_id=cart_item_id).delete()
                return Response({"message": "Cart item deleted"}, status=200)
            else:
                Cart_item.objects.filter(Cart_id=cart).delete()
                return Response({"message": "All cart items deleted"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

from django.db import transaction
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
# from .utils import send_whatsapp_message

import re
@permission_classes([AllowAny])
class PlaceOrderAPIView(APIView):

    def get(self, request):
        try:
            if request.user.is_anonymous:
                return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            customer = Customers.objects.get(User_id=request.user)
            orders = Order.objects.filter(Cart_id__customer_id=customer)
            orders_data = [
                {
                    "order_id": order.Order_id,
                    "order_date": order.Order_Date,
                    "status": getattr(order, "order_status", "Unknown"),
                    "delivery_address": str(order.Delivery_Address),
                    "payment_id": order.payment_id.pk
                }
                for order in orders
            ]
            return Response({"orders": orders_data}, status=status.HTTP_200_OK)
        except Customers.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            if request.user.is_anonymous:
                return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            customer = Customers.objects.get(User_id=request.user)
            cart = Cart.objects.get(customer_id=customer)    
            cart_item_id_list = []
            for l in request.data['cart_item_id']:
                cart_item_id_list.append(l['cart_item_id'])

            payment_id=request.data.get("payment_id")
            payment=Payment.objects.filter(pk=payment_id).first()
            delivery_address_id = request.data.get("Delivery_Address")
            payment_confirmation = request.data.get("payment_confirmation", "Pending")
            order_status = "Placed"
            delivery_address = Address.objects.get(pk=delivery_address_id)
            payment = Payment.objects.get(pk=payment_id)
            first = Order.objects.filter(Cart_id__customer_id=customer).first() is None
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    Delivery_Address=delivery_address,
                    Cart_id=cart,
                    payment_id=payment,
                    payment_confirmation=payment_confirmation,
                    order_status=order_status
                )
                message="Order has been placed Successfully"
                Notifications.objects.create(
                    customer_id=customer,notification_msg=message
                )
                # Save items to OrderHistory
                cart_items = Cart_item.objects.filter(cart_item_id__in=cart_item_id_list)

                # for item in cart_item_id_list:  
                # for Out of Stock
                for item in cart_items: 
                    product_variation = item.product_variation_id
                    quantity = item.Quantity
                    product_variation.stock -= quantity
                    product_variation.save()
                    if product_variation.stock is None or product_variation.stock < quantity:
                        return Response("is Out of Stock")
                    # cart_item = Cart_item.objects.get(cart_item_id=item)
                    OrderHistory.objects.create(
                            order_id=order,
                            customer_id=customer,
                            cart_item_id=item,
                            )
            user=request.user
            if order.Cart_id:
                # cart_item = order.Cart_id.cartid.all()
                cart_item = Cart_item.objects.filter(cart_item_id__in=cart_item_id_list)
                sub_total = sum(i.Quantity * i.product_variation_id.product_id.price for i in cart_item)
            if first:
                discount = sub_total * 0.5
                final_total = sub_total - discount
            else:
                discount = 0
                final_total = sub_total

                context = {
                    "order": [order],     
                    "customer_name": user.first_name +"  "+ user.last_name,        
                    "cart_item": [
                        {  
                            "product_name": i.product_variation_id.product_id.product_description,
                            "quantity": i.Quantity,
                            "total_price": i.Quantity * i.product_variation_id.product_id.price
                            }
                            for i in cart_item
                            ],
                            # "sub_total_price": sum(i.Quantity * i.product_variation_id.product_id.price for i in cart_item),
                            "sub_total_price": sub_total,
                            "discount": discount,
                            "final_total": final_total,
                            }
                html_message = render_to_string("receipt.html", context , request=request,)
                msg = EmailMultiAlternatives(
                    subject="Order Confirmation",
                    body="Your order has been successfully placed.",
                    from_email="saklen660@gmail.com",
                    to=[user.email],
                    )
                msg.attach_alternative(html_message, "text/html")
                msg.send(fail_silently=False)
                send_mail(
                    subject="New Order Placed",
                    message=f"A new order has been placed by {user.email}.",
                    from_email="saklen660@gmail.com",
                    recipient_list=["mohdshaik639379@gmail.com"], 
                    fail_silently=False,
                    )

            return Response(
                {"message": "Order placed successfully", "order_id": order.Order_id,
                "order_id": order.Order_id,
                "first": first,
                "sub_total": sub_total,
                "discount": discount,
                "final_total": final_total
                },

                status=status.HTTP_201_CREATED
            )
  
        except Customers.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Address.DoesNotExist:
            return Response({"error": "Delivery address not found"}, status=status.HTTP_404_NOT_FOUND)
        except Payment.DoesNotExist:
            return Response({"error": "Payment record not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:

            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, order_id):
        
        try:
            if request.user.is_anonymous:
                return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

            customer = Customers.objects.get(User_id=request.user)
            order = Order.objects.get(Order_id=order_id, Cart_id__customer_id=customer)
            order_status = request.data.get("order_status")
            payment_confirmation = request.data.get("payment_confirmation")
            if order_status:
                order.order_status = order_status
            if payment_confirmation:
                order.payment_confirmation = payment_confirmation
            order.save()
            return Response({"message": "Order updated successfully"}, status=status.HTTP_200_OK)
        except Customers.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, order_id):
       
        try:
            if request.user.is_anonymous:
                return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            customer = Customers.objects.get(User_id=request.user)
            order = Order.objects.get(Order_id=order_id, Cart_id__customer_id=customer)
            order.delete()
            return Response({"message": "Order cancelled successfully"}, status=status.HTTP_200_OK)
        except Customers.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET","POST","PUT","DELETE"])
def WishlistView(request):
    if request.method=="GET":
        id = request.GET.get('id', None)
        if id:
            obj= Wishlist.objects.filter(wishlist_id=id)
            serializer= WishlistSerializers(obj, many=True)
            return Response(serializer.data)

        obj=Wishlist.objects.all()
        ser=WishlistSerializers(obj,many=True)
        return Response(ser.data)
    elif request.method=="POST":
        post_data=request.data
        customer=post_data["customer_id"]
        ser=WishlistSerializers(data=post_data)
        if ser.is_valid():
            ser.save()
            customer=Customers.objects.get(User_id=customer)
            message="You just added and item in your wishlist..."
            Notifications.objects.create(customer_id=customer,notification_msg=message)
            return Response({"message":"Wishlist Added Successfully"})
        return Response(ser.errors)
    
    elif request.method=="PUT":
        wish_id=request.data.get("wishlist_id")
        # print(wish_id)
        obj=Wishlist.objects.get(wishlist_id=wish_id)
        ser=WishlistSerializers(obj,data=request.data,partial=True)
        if ser.is_valid():
            ser.save()
            return Response({"message":"Updated Successfully"})
        return Response(ser.errors)
    
    elif request.method=="DELETE":
        id=request.data["wishlist_id"]
        # id =request.data.GET.get
        print(id)
        obj=Wishlist.objects.get(wishlist_id=id)
        obj.delete()
        return Response("Wishlist Deleted")


@api_view(["GET"])
def Subcategoryfilter(request, value):
    sub = Subcategory.objects.filter(sub_category_name=value).first()
    print(sub)
    var = Productvariation.objects.filter(product_id__sub_category=sub)
    ser = CustomSerializers(var, many=True, context={'request': request})
    return Response(ser.data)

@api_view(["GET","POST","PUT","DELETE"])
def NotificationView(request):
    if request.method=="GET":
        id=request.GET.get("id",None)
        if id:
            obj=Notifications.objects.filter(notification_id=id)
            ser=NotificationSerializers(obj,many=True)
            return Response(ser.data)
        obj=Notifications.objects.all()
        ser=NotificationSerializers(obj,many=True)
        return Response(ser.data)  
    elif request.method=="POST":
        post_data=request.data
        ser=NotificationSerializers(data=post_data)
        if ser.is_valid():
            ser.save()
            return Response({"message":"Post Successful"})
        return Response(ser.errors)  
    elif request.method=="PUT":
        notif_id=request.data.get("notification_id")
        obj=Notifications.objects.get(notification_id=notif_id)
        ser=NotificationSerializers(obj,data=request.data,partial=True)
        if ser.is_valid():
            ser.save
            return Response(ser.data)
        return Response(ser.errors) 
    elif request.method=="DELETE":
        id=request.GET.get("notification_id")
        obj=Notifications.objects.get(notification_id=id)
        obj.delete()
        return Response({"message":"Notification deleted"})
    
@api_view(["GET","POST","DELETE"])
def QuotesView(request):
    if request.method=="GET":
        obj=Quotes.objects.all()
        ser=QuotesSerializers(obj,many=True)
        return Response(ser.data)
    
    elif request.method=="POST":
        post_data=request.data
        ser=QuotesSerializers(data=post_data)
        if ser.is_valid():
            ser.save()
            return Response({"message":"Quote Post Successfully"})
        return Response(ser.errors)
    
    elif request.method=="DELETE":
        id=request.GET.get("quote_id")
        obj=Quotes.objects.get(quote_id=id)
        obj.delete()
        return Response({"message":"Deleted Quotes"})
    
@api_view(["GET","POST","PUT","DELETE"])
def VarietyView(request):
    if request.method=="GET":
        obj=Varieties.objects.all()
        ser=VarietySerializer(obj , many=True , context={"request":request})
        return Response(ser.data)
    elif request.method=="POST":
        post_data=request.data
        ser=VarietySerializer(data=post_data)
        if ser.is_valid():
            ser.save()
            return Response("Variety Added Successfully")
        return Response(ser.errors)
    elif request.method=="PUT":
        id=request.data.get("Variety_id")
        obj=Varieties.objects.get(Variety_id=id)
        ser=VarietySerializer(obj , data=request.data , partial=True)
        if ser.is_valid():
            ser.save()
            return Response("Updated Successfully")
        return Response(ser.errors)
    elif request.method=="DELETE":
        id=request.data["Variety_id"]
        obj=Varieties.objects.get(Variety_id=id)
        obj.delete()
        return Response("Variety Deleted Successfully")
    

@api_view(["GET","POST","PUT","DELETE"])
def Customer_ratingView(request):
    if request.method=="GET":
        obj=Customer_rating.objects.all()
        ser=Customer_ratingSerializers(obj,many=True)
        return Response(ser.data)
    
    elif request.method=="POST":
        data=request.data
        product=data["product_variation_id"]
        ser=Customer_ratingSerializers(data=data)
        if ser.is_valid():
            ser.save()
            pv_id=Customer_rating.objects.filter(product_variation_id=product)
            rate=[i.rating for i in list(pv_id)]
            avg=sum(rate)/len(rate)
            obj=Productvariation.objects.get(product_variation_id=product)
            obj.avg_rating=avg
            obj.save()
            return Response("Added Customer_Rating...")
        return Response(ser.errors)
    
    elif request.method=="PUT":
        id=request.data.get("customer_rating_id")
        obj=Customer_rating.objects.get(customer_rating_id=id)
        ser=Customer_ratingSerializers(obj,data=data,partial=True)
        if ser.is_valid():
            ser.save()
            return Response ("Customer_Rating Updated")
        return Response(ser.errors)
    
    elif request.method=="DELETE":
        id=request.data["customer_rating_id"]
        obj=Customer_rating.objects.get(customer_rating_id=id)
        obj.delete()
        return Response ({"message":"Rating Deleted"})



# --------------------------------------------Stripe

import stripe
from django.http import JsonResponse

@csrf_exempt
def create_payment(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        intent = stripe.PaymentIntent.create(
            amount=5000,
            currency="inr",
            payment_method_types=["card"],
        )
        return JsonResponse({"clientSecret": intent.client_secret})
    except Exception as e:
        return JsonResponse({"error": str(e)})
    

