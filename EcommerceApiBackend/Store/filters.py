import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    '''Custom product filter class'''
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='iexact')

    class Meta:
        model = Product
        fields = ['category','price']