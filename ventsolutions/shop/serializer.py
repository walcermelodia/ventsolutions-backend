from rest_framework import serializers
from .models import Category, Product, Image, Characteristic


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

        def get_photo_url(self, obj):
            request = self.context.get('request')
            photo_url = obj.fingerprint.url
            return request.build_absolute_uri(photo_url)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('path', 'is_main')

        def get_photo_url(self, obj):
            request = self.context.get('request')
            photo_url = obj.fingerprint.url
            return request.build_absolute_uri(photo_url)


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'part_number', 'name', 'price', 'discount', 'description', 'in_stock', 'images')

    def get_images(self, obj):
        images = Image.objects.filter(product=obj)
        return ImageSerializer(images, many=True).data


class ProductDetailSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField(read_only=True)
    characteristics = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ('part_number', 'name', 'price', 'discount', 'description', 'in_stock', 'images', 'characteristics')

    @staticmethod
    def get_images(obj):
        images = Image.objects.filter(product=obj)
        return ImageSerializer(images, many=True).data

    @staticmethod
    def get_characteristics(obj):
        characteristics = Characteristic.objects.filter(product=obj)
        return CharacteristicSerializer(characteristics, many=True).data


class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = ('name', 'value')


class ProductPaginationSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'part_number', 'name', 'price', 'discount', 'description', 'in_stock', 'main_image')

    @staticmethod
    def get_main_image(obj):
        main_image = Image.objects.filter(product=obj, is_main=True).first()
        return ImageSerializer(main_image).data
