from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view,permission_classes ,action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.views import APIView 
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework import status,viewsets , generics 
from .permissions import  IsAdminOrStaff,IsSellerOrReadOnly , IsOrderItemByBuyerOrAdmin , IsOrderItemPending,IsOrderPending, IsOrderByBuyerOrAdmin
import stripe
from .filters import ProductFilter,CustomSearchFilter
from .models import User, Product , Category , Cart , CartItem , Order, OrderItem , Review , Payment
from .serializers import UserSerializer,ProfileSerializer,ProductSerializer, CategorySeriazlizer , CartItemSerializer,OrderReadSerializer,OrderWriteSerializer, ReviewSerializer , PaymentSerializer , CartSerializer , OrderItemSerializer
# Create your views here.


@api_view(['GET', 'POST','PUT', 'DELETE', 'PATCH'])
def custom_404_handler(request, exception=None):
    response_data = {
        "error": "Endpoint not found",
        "status_code": status.HTTP_404_NOT_FOUND,
        "message": "The endpoint you requested does not exist. Please check the URL."
    }
    return Response(response_data, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def RegisterView(request):
    serialize=UserSerializer(data=request.data)
    if serialize.is_valid():
        user=serialize.save()
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': serialize.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({"error":serialize.errors})
    
    
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token , refresh token can't be further used to generate access token 
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            # print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

# profile view for getting and updating profile data
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class=ProfileSerializer
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        instance=self.get_object()
        name=request.data.get('name',None)
        if name:
            name=name.split(' ',1)
            instance.first_name=name[0].strip() or ''
            instance.last_name=name[1].strip() if len(name)>1 else ''

        # Use serializer to validate and update other fields
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # This will save the other fields
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSellerOrReadOnly]
    filter_backends=[DjangoFilterBackend,CustomSearchFilter]  # use search filter for searching , and DjangoFilterBackend for filtering products on basis of fields 
    search_fields=['name','category__name','description','author']
    filterset_class=ProductFilter
  
    def perform_create(self,serializer):
        serializer.save(seller=self.request.user)

     # Override the update method to handle partial updates with PUT
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)  # Set partial=True for PUT requests
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'],url_path='increment-views')
    def increase_views(self, request, pk=None):
        """Increase the views count of a specific product"""
        product = self.get_object()
        product.views += 1
        product.save()
        return Response({"status": "success", "views": product.views,'product_id':product.id}, status=status.HTTP_200_OK)


class CategoryViewset(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    permission_classes=[IsAdminOrStaff]
    serializer_class = CategorySeriazlizer


class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    def get_object(self):
        return get_object_or_404(Cart, buyer=self.request.user)

class CartViewset(viewsets.ModelViewSet): 
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(buyer=self.request.user)
        return CartItem.objects.filter(cart=cart)
    
    def get_object(self):
        queryset = self.get_queryset()
        item_id = self.kwargs.get('item_id')
        return get_object_or_404(queryset, id=item_id)  # Assuming 'id' is the primary key
    
    def perform_create(self, serializer):
        '''Add item to cart '''
        cart=get_object_or_404(Cart,buyer=self.request.user)
        serializer.save(cart=cart)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)  # Set partial=True for PUT requests
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False,methods=['delete'])
    def clear_cart(self,request):
        cart=get_object_or_404(Cart,buyer=self.request.user)
        cart.cart_items.all().delete()
        return Response({"status": "success", "message": "Cart cleared successfully"}, status=status.HTTP_200_OK)


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    CRUD order items that are associated with the current order id.
    """

    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsOrderItemByBuyerOrAdmin]

    def get_queryset(self):
        res = super().get_queryset()
        order_id = self.kwargs.get("order_id")
        return res.filter(order__id=order_id)

    def perform_create(self, serializer):
        order = get_object_or_404(Order, id=self.kwargs.get("order_id"))
        serializer.save(order=order)

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            self.permission_classes += [IsOrderItemPending]

        return super().get_permissions()


#### INcomplete 
# class OrderView(APIView):
#     '''handling two order case , through cart or without cart '''
#     def post(self,request,*args, **kwargs):
#         if 'product_id' in request.data:            
#             product_id = request.data.get('product_id',None)
#             # print(f"product_id: {int(product_id)}")
#             quantity = request.data.get('quantity', 1)
#             data = {'product':product_id, 'quantity':quantity}
#             # ItemSerializer= OrderItemSerializer(data=data)
#             # Prepare data for a single product order
#             # if ItemSerializer.is_valid():
#                 # item = ItemSerializer.save()
#             order_data = {
#                 'buyer': request.user.id,
#                 'billing_address': request.data.get('billing_address'),
#                 'shipping_address': request.data.get('shipping_address'),
#                 'order_items':[{
#                     'product':int(product_id),
#                     'quantity':int(quantity)
#                 }]
#             }

#             # else:
#             #     return Response(ItemSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
#             serializer = OrderWriteSerializer(data=order_data)
        
#         # elif 'cart_items' in request.data:
#         #     cart_items = request.data['cart_items']
#         #     order_items_data = []

#         #     # Prepare data for multiple cart items
#         #     for item in cart_items:
#         #         order_items_data.append({
#         #             'product': item['product_id'],  # Assuming cart item has product_id
#         #             'quantity': item.get('quantity', 1),
#         #         })

#         #     order_data = {
#         #         'buyer': request.user.id,
#         #         'billing_address': request.data.get('billing_address'),
#         #         'shipping_address': request.data.get('shipping_address'),
#         #         'order_items': order_items_data,
#         #     }
#         #     serializer = OrderWriteSerializer(data=order_data)

#         else:
#             return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
        
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#### incomplete 
# class CancelOrder(APIView):
#     def patch(self,request,*args, **kwargs):
#         '''handle cancel order action , will change status of order '''
#         pass
        

class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD orders of a user
    """
    queryset = Order.objects.all()
    permission_classes = [IsOrderByBuyerOrAdmin]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return OrderWriteSerializer

        return OrderReadSerializer

    def get_queryset(self):
        res = super().get_queryset()
        user = self.request.user
        return res.filter(buyer=user)

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            self.permission_classes += [IsOrderPending]

        return super().get_permissions()



# class OrderListView(generics.ListAPIView):
#     serializer_class=OrderReadSerializer
#     def get_queryset(self):
#         return Order.objects.filter(user=self.request.user)
    

# class OrderDetailView(generics.RetrieveAPIView):
#     serializer_class=OrderReadSerializer
#     def get_queryset(self):
#         return Order.objects.filter(user=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_id',None)
        if product_id is not None:
            return Review.objects.filter(user=self.request.user, product__id=product_id)
        raise ValidationError("Product id not specified !!")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




##### Payement  handling related views #####
##### Payement  handling related views #####

### incomplete view
class PaymentInitializeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            order = Order.objects.get(id=serializer.validated_data['order_id'])
            
            # Create a Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_price * 100),  # Amount in cents
                currency='usd',
                payment_method_types=['card']
            )
            
            # Create the Payment object in your DB
            payment = Payment.objects.create(
                user=request.user,
                order=order,
                amount=order.total_price,
                stripe_payment_intent_id=intent['id'],
                status='Pending'
            )
            
            response_data = StripePaymentIntentSerializer({
                'client_secret': intent['client_secret'],
                'payment_intent_id': intent['id']
            }).data

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)