from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product
from .serializer import CategorySerializer, ProductSerializer, ProductDetailSerializer, ProductPaginationSerializer, \
    CategoryDetailSerializer


# class CategoryAPIView(generics.ListAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer

def bin_search(l, r, data, id):
    while l < r:
        m = (l + r) // 2
        if id <= data[m]['id']:
            r = m
        else:
            l = m + 1
    return l


class CategoryAPIView(APIView):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all().order_by('id')
        serializer = CategorySerializer(categories, many=True, context={'request': self.request})
        response_data = []
        dict = {}
        for elem in serializer.data:
            if elem['id'] not in dict:
                dict[elem['id']] = elem
                elem['next'] = []

            if elem['parent_id'] is None:
                response_data.append(elem)
            else:
                position = bin_search(0, len(serializer.data), serializer.data, elem['parent_id'])
                dict[serializer.data[position]['id']]['next'].append(elem)

        return Response(response_data)


class ProductAPIView(generics.ListAPIView):
    # queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        ids = self.request.query_params['ids'].split(',')
        return Product.objects.filter(id__in=ids)


class ProductDetailAPIView(APIView):
    def get(self, request, *args, **kwargs):
        _id = self.kwargs['id']
        product = Product.objects.get(id=_id)
        serializer = ProductDetailSerializer(product, many=False, context={'request': self.request})
        return Response(serializer.data)


class CategoryDetailAPIView(APIView):
    def get(self, request, *args, **kwargs):
        _id = self.kwargs['id']
        category = Category.objects.get(id=_id)

        serializer = CategoryDetailSerializer(category, many=False, context={'request': self.request})
        return Response(serializer.data)


class ProductAPIListPagination(PageNumberPagination):
    page_size_query_param = 'pageSize'
    max_page_size = 150

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


class ProductPaginationAPIView(generics.ListAPIView):
    serializer_class = ProductPaginationSerializer
    pagination_class = ProductAPIListPagination

    def get_queryset(self):
        # category_ids = self.request.query_params['categoryIds'].split(',')
        category_ids_qp = None
        product_ids_qp = None
        if 'categoryIds' in self.request.query_params:
            category_ids_qp = self.request.query_params['categoryIds']

        if 'productIds' in self.request.query_params:
            product_ids_qp = self.request.query_params['productIds']

        if category_ids_qp is None and product_ids_qp is None:
            return Product.objects.all().order_by('-id')[:10:1]
        elif category_ids_qp is not None and product_ids_qp is not None:
            return Product.objects.filter(category__id__in=category_ids_qp.split(','), id__in=product_ids_qp.split(','))
        elif category_ids_qp is not None:
            return Product.objects.filter(category__id__in=category_ids_qp.split(','))
        elif product_ids_qp is not None:
            return Product.objects.filter(id__in=product_ids_qp.split(','))

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = {'request': self.request}
        return ProductPaginationSerializer(*args, **kwargs)
