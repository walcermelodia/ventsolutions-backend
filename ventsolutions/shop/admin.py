from django.contrib import admin
from django import forms

from .models import Category, Product, Image, Characteristic
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class ProductAdminForm(forms.ModelForm):
    description = forms.CharField(label="Описание", widget=CKEditorUploadingWidget())

    class Meta:
        model = Product
        fields = '__all__'


class CategoryAdminForm(forms.ModelForm):
    description = forms.CharField(label="Описание", widget=CKEditorUploadingWidget())

    class Meta:
        model = Category
        fields = '__all__'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'part_number', 'name', 'price', 'discount', 'description', 'in_stock', 'translation')
    list_editable = ('part_number', 'name', 'price', 'discount', 'description', 'in_stock')
    form = ProductAdminForm


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'translation', 'parent')
    # list_editable = ('name', 'image', 'description', 'translation', 'parent')
    form = CategoryAdminForm


# admin.site.register(Category)
# admin.site.register(Product, ProductAdminForm)
admin.site.register(Image)
admin.site.register(Characteristic)
