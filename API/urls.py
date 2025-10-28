from MHSapp.views import *
from django.urls import path
from rest_framework.settings import settings
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
     path("changepassword/",ChangePassword.as_view(),name="changepassword"),
     path("mail/",SendOTP.as_view(),name="mail"),
     path("verify/",VerifyOTP.as_view(),name="Verify"),
     path("forget/",forgetPassword.as_view(),name="forget"),
     path("register/",Customer_registration),
     path("user/",UserView),
     path("customer/",CustomerView),
     path("address/",AddressView),
     path("cart/",CartView),
     path('login/', LoginView),
     path("logout/",LogoutView.as_view() , name='logout_password'),
     path('custom/', CustomView),
     path('subcategory/', SubcategoryView),
     path('product/', ProductView),
     path('category/', CategoryView),
     path("homeimage/",Homepageimage),
     path('variation/', VariationView),
     path('varoption/', VariationoptionView),
     path('productvar/', ProductvariationView),
     path("images/",ProductImageView),
     path("history/",OrderHistoryView),
     path('access/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
     path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('history/<int:value>/',OrderHistory1),
     path("add/",AddToCartAPIView.as_view()),
     path("add/<int:cart_item_id>/",AddToCartAPIView.as_view()),
     path("place/",PlaceOrderAPIView.as_view()),
     path('place/<int:order_id>/', PlaceOrderAPIView.as_view()),
     path("wishlist/",WishlistView),
     path("filter/<str:value>/",Subcategoryfilter),
     path("notif/",NotificationView),
     path("quote/",QuotesView),
     path("payment/",PaymentView),
     path("brand/",BrandView),
     path("test/", create_payment, name="create-payment"),
     path("variety/",VarietyView),
     path("rating/",Customer_ratingView),
     path("chat/",chat)
 ] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


