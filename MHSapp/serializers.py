from rest_framework import serializers
from MHSapp.models import *
from rest_framework.serializers import *
from rest_framework import serializers

class UserSerializers(serializers.ModelSerializer):
    class Meta: 
        model=CustomUser
        fields= ['id','first_name' , 'last_name'  , 'email']
        
class CustomerSerializers(serializers.ModelSerializer):
    class Meta: 
        model=Customers              
        fields= "__all__" 

class AddressSerializer(serializers.ModelSerializer):
    # user_id = serializers.SerializerMethodField()
    class Meta:
        model = Address
        fields= "__all__" 
    #     fields = [
    #         "Address_id", "Address_type", "Name", "House_No", "Area_Colony",
    #         "Landmark", "Pincode", "City", "State", "Country", "Contact",
    #         "user_id"
    #     ]

    # def get_user_id(self, obj):
    #     return obj.User_id.User_id.id 

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cart
        fields="__all__"

class ProductSerializers(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields="__all__"

class CategorySerializers(serializers.ModelSerializer):
    homepage_images = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ["category_id", "category_name", "homepage_images"]

    def get_homepage_images(self, obj):
        request = self.context.get("request")
        return [request.build_absolute_uri(img.image.url) for img in obj.homepage_images.all()]
        
class HomepageimageSerializer(serializers.ModelSerializer):
    class Meta:
        model=HomePageImage
        fields="__all__"

class SubcategorySerializers(serializers.ModelSerializer):    
    class Meta:
        model=Subcategory
        fields="__all__"

class VariationSerializers(serializers.ModelSerializer):
    class Meta:
        model=Variation
        fields="__all__"
        depth=1

class VariationoptionSerializers(serializers.ModelSerializer):
    class Meta:
        model=Variationoption
        fields="__all__"
        
class ProductvariationSerializers(serializers.ModelSerializer):
    class Meta:
        model=Productvariation
        fields=['product_variation_id', 'product_id', 'variation_option_id', 'stock', 'avg_rating']


class BrandsSerializers(serializers.ModelSerializer):
    class Meta:
        model=Brands
        fields=["Brand_id", "Brand_name", "Brand_image"]

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart_item
        fields = ['cart_item_id', 'Cart_id', 'product_variation_id', 'Quantity', 'Sub_Total']
        
class SizeSerializers(serializers.ModelSerializer):
    class Meta:
        model=Size
        fields="__all__"

class ProductImagesSerializers(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = ProductImages
        fields = ["product_images_id", "image_url", "product_variation_id"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if request and obj.image_url:
            return request.build_absolute_uri(obj.image_url.url)
        return None

class QuotesSerializers(serializers.ModelSerializer):    
    class Meta:
        model=Quotes
        fields="__all__"

class PaymentSerializers(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields="__all__"

class CustomSerializers(serializers.ModelSerializer):
    Product_id = serializers.CharField(source="product_id.product_id")
    category_name = serializers.CharField(source='product_id.sub_category.category_id.category_name')
    sub_category_name = serializers.CharField(source='product_id.sub_category.sub_category_name')
    product_description = serializers.CharField(source='product_id.product_description')
    availability = serializers.CharField(source='product_id.availability')
    price = serializers.CharField(source='product_id.price')
    brand=BrandsSerializers(source="product_id.Brand_id")
    product_variation = ProductvariationSerializers(source="*")
    variation_type = serializers.CharField(source='variation_option_id.variation_id.variation_name')
    variation_name = serializers.CharField(source='variation_option_id.value')
    ColorCode = serializers.CharField(source='variation_option_id.ColorCode')
    images = serializers.SerializerMethodField()
    class Meta:
        model = Productvariation
        fields = [
            'Product_id', 'category_name', 'sub_category_name',
            'product_description', 'availability', 'price', 'brand',
            'product_variation', 'variation_type', 'variation_name',
            'ColorCode', 'images'
        ]

    def get_images(self, obj):
            request = self.context.get('request')
            base_url = request.build_absolute_uri('/')[:-1] if request else ""
            image_urls = []
            images = obj.images.all()  
            for index, image in enumerate(images):
                image_urls.append(base_url+image.image_url.url)
            return image_urls

class CustomSerializers1(serializers.ModelSerializer):
    Product_id = serializers.CharField(source="product_id.product_id")
    product_description = serializers.CharField(source='product_id.product_description')
    price = serializers.CharField(source='product_id.price')
    variation_type = serializers.CharField(source='variation_option_id.variation_id.variation_name')
    variation_name = serializers.CharField(source='variation_option_id.value')
    ColorCode = serializers.CharField(source='variation_option_id.ColorCode')
    images = serializers.SerializerMethodField()
    class Meta:
        model = Productvariation
        fields = [
            'Product_id', 
            'product_description', 'price',
            'variation_type', 'variation_name',
            'ColorCode', "images"
        ]

    def get_images(self, obj):
            request = self.context.get('request')
            base_url = request.build_absolute_uri('/')[:-1] if request else ""
            image_urls = []
            images = obj.images.all()  
            for index, image in enumerate(images):
                image_urls.append(base_url+image.image_url.url)
            return image_urls

class CartItemSerializer1(serializers.ModelSerializer):
    product_variation = CustomSerializers1(source="product_variation_id", read_only=True)
    class Meta:
        model = Cart_item
        fields = ["cart_item_id", "Quantity", "product_variation"]

class OrderHistorySerializer(serializers.ModelSerializer): 
    Order_status=serializers.CharField(source="order_id.order_status")
    Order_date=serializers.CharField(source="order_id.Order_Date")
    cart_item = CartItemSerializer1(source="cart_item_id", read_only=True)
    class Meta:
        model = OrderHistory
        fields = ["order_history_id", "order_id", "customer_id", "cart_item","Order_status","Order_date"]

class WishlistSerializers(serializers.ModelSerializer):
    class Meta:
        model=Wishlist
        fields="__all__"

class NotificationSerializers(serializers.ModelSerializer):
    class Meta:
        model=Notifications
        fields="__all__"

class VarietySerializer(serializers.ModelSerializer):
    class Meta:
        model=Varieties
        fields="__all__"

class Customer_ratingSerializers(serializers.ModelSerializer):
    class Meta:
        model=Customer_rating
        fields="__all__"
        