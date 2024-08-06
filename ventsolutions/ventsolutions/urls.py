from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from shop.views import CategoryAPIView, ProductAPIView, ProductDetailAPIView, ProductPaginationAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/categories', CategoryAPIView.as_view()),
    path('api/v1/products', ProductAPIView.as_view()),
    path('api/v1/products/<int:id>', ProductDetailAPIView.as_view()),
    path('api/v1/categoies/<int:category_id>/products', ProductPaginationAPIView.as_view())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
