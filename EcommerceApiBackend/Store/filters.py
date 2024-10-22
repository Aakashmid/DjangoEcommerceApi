import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    '''Custom product filter class'''
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='iexact')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['category','min_price','max_price']