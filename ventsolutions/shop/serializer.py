from rest_framework import serializers
from .models import Category, Product, Image, Characteristic


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'image_path', 'translation', 'parent_id')

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
        fields = ('id', 'part_number', 'name', 'translation', 'price', 'discount', 'description', 'in_stock', 'images',
                  'characteristics', 'category_id')

    def get_images(self, obj):
        images = Image.objects.filter(product=obj)

        return ImageSerializer(images, many=True, context={'request': self.context['request']}).data

    @staticmethod
    def get_characteristics(obj):
        characteristics = Characteristic.objects.filter(product=obj)
        return CharacteristicSerializer(characteristics, many=True).data


class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'image_path', 'translation', 'parent_id', 'description')

        def get_photo_url(self, obj):
            request = self.context.get('request')
            photo_url = obj.fingerprint.url
            return request.build_absolute_uri(photo_url)


class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = ('name', 'value')


class ProductPaginationSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'part_number', 'name', 'price', 'discount', 'in_stock', 'translation', 'main_image')

    def get_main_image(self, obj):
        main_image = Image.objects.filter(product=obj, is_main=True).first()
        return ImageSerializer(main_image, context={'request': self.context['request']}).data


class FeedbackSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, min_length=1)
    phone = serializers.RegexField(regex=r'(\+?7|8)\d{10}$', required=True)
    email = serializers.EmailField(required=True)
    question = serializers.CharField(required=False)


class OrderProductSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    count = serializers.IntegerField(required=True)


class OrderSerializer(serializers.Serializer):
    firstName = serializers.CharField(required=True)
    lastName = serializers.CharField(required=True)
    phone = serializers.RegexField(regex=r'(\+?7|8)\d{10}$', required=True)
    email = serializers.EmailField(required=True)
    inn = serializers.RegexField(regex=r'\d$', required=False, allow_null=True, allow_blank=True, min_length=10, max_length=12)
    organizationName = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    comment = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    delivery = serializers.CharField(required=True)
    products = serializers.ListField(child=OrderProductSerializer(), required=True, min_length=1)
