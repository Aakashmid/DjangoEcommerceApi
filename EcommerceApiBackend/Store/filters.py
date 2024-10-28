import django_filters
from rest_framework.filters import SearchFilter
from django.db.models import Q
from .models import Product

class ProductFilter(django_filters.FilterSet):
    '''Custom product filter class'''
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='iexact')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['category','min_price','max_price']


class CustomSearchFilter(SearchFilter):
    def get_search_terms(self, request):
        # Override to allow searching for queries like "under 1000"
        query = request.query_params.get(self.search_param, '').lower().strip()
        terms = query.split()
        return terms

    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)
        category = None

        if "under" in search_terms:
            price=int(search_terms[search_terms.index('under')+1])
            queryset = queryset.filter(price__lte=price)
            print(queryset)
            category = search_terms[search_terms.index('under')-1]
        elif "above" in search_terms:
            price=int(search_terms[search_terms.index('above')+1])
            queryset = queryset.filter(price__gte=price)
            print(queryset)
            category = search_terms[search_terms.index('above')-1]
        
        if category is not None :
            queryset = queryset.filter(category__name__icontains=category)  # Filter products by category name``
        
        return queryset