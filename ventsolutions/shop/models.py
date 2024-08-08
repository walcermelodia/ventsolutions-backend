from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField('Название', max_length=256)
    image = models.ImageField('Изображение', name='image_path', upload_to='categories/')
    description = models.TextField('Описание', null=True)
    translation = models.CharField('Транслитерация названия', max_length=256)
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
    part_number = models.CharField('Артикул', max_length=10)
    name = models.CharField('Название', max_length=256)
    price = models.DecimalField('Цена', decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal('0.0'))])
    discount = models.PositiveIntegerField('Скидка', validators=[MinValueValidator(0)])
    description = models.TextField('Описание')
    translation = models.CharField('Транслитерация названия', max_length=256)
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
    is_main = models.BooleanField('Главное изображение карточки товара', default=True)
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
