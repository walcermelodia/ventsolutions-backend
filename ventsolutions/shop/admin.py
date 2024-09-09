from django.contrib import admin
from django import forms

from .models import Category, Product, Image, Characteristic, NewProduct, SalesLeaderProduct
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.safestring import mark_safe


class ProductAdminForm(forms.ModelForm):
    description = forms.CharField(label="Описание", widget=CKEditorUploadingWidget())

    class Meta:
        model = Product
        fields = '__all__'


class CategoryAdminForm(forms.ModelForm):
    description = forms.CharField(label="Описание", widget=CKEditorUploadingWidget(), required=False)

    class Meta:
        model = Category
        fields = '__all__'


class ImageInline(admin.TabularInline):
    model = Image
    verbose_name = 'Карточка товара'
    verbose_name_plural = 'Карточки товара'
    extra = 0
    readonly_fields = ('get_image',)

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.path.url} width="50" height="60">')

    get_image.short_description = 'Изображение товара'


class CharacteristicInline(admin.TabularInline):
    model = Characteristic
    extra = 0
    verbose_name = 'Характеристика товара'
    verbose_name_plural = 'Характеристики товара'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'get_main_image', 'part_number', 'price', 'discount', 'in_stock', 'translation', 'category',)
    list_display_links = ('name',)
    list_editable = ('in_stock', 'price', 'discount', 'translation', 'part_number')
    search_fields = ('id', 'name', 'translation')
    form = ProductAdminForm
    inlines = [ImageInline, CharacteristicInline]
    save_on_top = True
    save_as = True
    autocomplete_fields = ('category',)

    def get_main_image(self, obj):
        images = Image.objects.filter(product__id=obj.id, is_main=True)
        if len(images) < 1:
            return None
        else:
            return mark_safe(f'<img src={images[0].path.url} width="50" height="60">')

    get_main_image.short_description = 'Карточка товара'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_main_image', 'translation', 'parent')
    list_display_links = ('name',)
    search_fields = ('id', 'name', 'translation')
    form = CategoryAdminForm

    autocomplete_fields = ('parent',)

    def get_main_image(self, obj):
        return mark_safe(f'<img src={obj.image_path.url} width="50" height="60">')

    get_main_image.short_description = 'Изображение категории'


@admin.register(NewProduct)
class NewProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'get_main_image')
    list_display_links = ('product',)

    autocomplete_fields = ('product',)

    def get_main_image(self, obj):
        images = Image.objects.filter(product__id=obj.product.id, is_main=True)
        if len(images) < 1:
            return None
        else:
            return mark_safe(f'<img src={images[0].path.url} width="50" height="60">')

    get_main_image.short_description = 'Карточка товара'


@admin.register(SalesLeaderProduct)
class SalesLeaderProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'get_main_image',)
    list_display_links = ('product',)

    autocomplete_fields = ('product',)

    def get_main_image(self, obj):
        images = Image.objects.filter(product__id=obj.product.id, is_main=True)
        if len(images) < 1:
            return None
        else:
            return mark_safe(f'<img src={images[0].path.url} width="50" height="60">')

    get_main_image.short_description = 'Карточка товара'


admin.site.site_title = 'ООО \"Вент-Решения\"'
admin.site.site_header = 'ООО \"Вент-Решения\"'
