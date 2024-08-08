from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product, Image
from .serializer import CategorySerializer, ProductSerializer, ProductDetailSerializer, ProductPaginationSerializer, \
    CategoryDetailSerializer


class CategoryAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


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
        serializer = ProductDetailSerializer(product, many=False)
        return Response(serializer.data)


class CategoryDetailAPIView(APIView):
    def get(self, request, *args, **kwargs):
        _id = self.kwargs['id']
        category = Category.objects.get(id=_id)
        serializer = CategoryDetailSerializer(category, many=False)
        return Response(serializer.data)


class ProductAPIListPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 10


class ProductPaginationAPIView(generics.ListAPIView):
    serializer_class = ProductPaginationSerializer
    pagination_class = ProductAPIListPagination

    def get_queryset(self):
        category_ids = self.request.query_params['categoryIds'].split(',')
        return Product.objects.filter(category__id__in=category_ids)
