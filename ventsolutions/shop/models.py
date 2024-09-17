from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField('Название', max_length=256)
    image = models.ImageField('Изображение', name='image_path', upload_to='categories/')
    description = models.TextField('Описание', null=True, blank=True)
    translation = models.CharField('Транслитерация названия', max_length=256, unique=True)
    parent = models.ForeignKey('self', verbose_name='Родительская категория', on_delete=models.SET_NULL, blank=True,
                               null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    part_number = models.CharField('Артикул', max_length=24)
    name = models.CharField('Название', max_length=256)
    price = models.DecimalField('Цена', decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal('0.0'))])
    discount = models.PositiveIntegerField('Скидка', validators=[MinValueValidator(0)])
    description = models.TextField('Описание')
    translation = models.CharField('Транслитерация названия', max_length=256, unique=True)
    in_stock = models.BooleanField('Наличие товара', default=True)
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Image(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    path = models.ImageField('Изображение', name='path', upload_to='products/images/')
    is_main = models.BooleanField('Главное изображение товара', default=True)
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'


class Characteristic(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField('Название', max_length=128)
    value = models.CharField('Значение', max_length=128)
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = 'Характеристика товара'
        verbose_name_plural = 'Характеристики товаров'


class NewProduct(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', null=False, default=1)
    product = models.OneToOneField(Product, verbose_name='Товар', on_delete=models.CASCADE, null=False, unique=True)

    class Meta:
        verbose_name = 'Новинка'
        verbose_name_plural = 'Новинки'
        db_table = 'shop_new_product'


class SalesLeaderProduct(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', null=False, default=1)
    product = models.OneToOneField(Product, verbose_name='Товар', on_delete=models.CASCADE, null=False, unique=True)

    class Meta:
        verbose_name = 'Лидер продаж'
        verbose_name_plural = 'Лидеры продаж'
        db_table = 'shop_sales_leader_product'
