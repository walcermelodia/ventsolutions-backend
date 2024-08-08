from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from shop.views import CategoryAPIView, ProductAPIView, ProductDetailAPIView, ProductPaginationAPIView, CategoryDetailAPIView

urlpatterns = [
    path('admin/', admin.site.urls),  # админка
    path('api/v1/categories', CategoryAPIView.as_view()),  # все категории
    path('api/v1/categories/<int:id>', CategoryDetailAPIView.as_view()),  # подробная информация по категории
    path('api/v1/products', ProductPaginationAPIView.as_view()),  # все товары по главной категории и ее подкатегориям
    path('api/v1/products/<int:id>', ProductDetailAPIView.as_view()),  # подробная информация о товаре

    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
