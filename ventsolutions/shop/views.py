import os

from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product, Image, NewProduct, SalesLeaderProduct
from .serializer import CategorySerializer, ProductSerializer, ProductDetailSerializer, ProductPaginationSerializer, \
    CategoryDetailSerializer, FeedbackSerializer, OrderProductSerializer, OrderSerializer
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


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
        product = Product.objects.get(translation=_id)
        serializer = ProductDetailSerializer(product, many=False, context={'request': self.request})
        return Response(serializer.data)


class CategoryDetailAPIView(APIView):
    def get(self, request, *args, **kwargs):
        _id = self.kwargs['id']
        category = Category.objects.get(translation=_id)

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


class ShowCase(generics.ListAPIView):
    serializer_class = ProductPaginationSerializer

    def get_queryset(self):
        type_query = self.request.query_params['type']
        if type_query == 'NEW':
            product_ids = list(map(lambda x: x.product.id, NewProduct.objects.all().order_by('order')))
        elif type_query == 'SALES_LEADER':
            product_ids = list(map(lambda x: x.product.id, SalesLeaderProduct.objects.all().order_by('order')))

        products_dict = dict(map(lambda x: (x.id, x), Product.objects.filter(id__in=product_ids)))
        result = []
        for product_id in product_ids:
            result.append(products_dict[product_id])
        return result

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = {'request': self.request}
        return ProductPaginationSerializer(*args, **kwargs)


class ProductPaginationAPIView(generics.ListAPIView):
    serializer_class = ProductPaginationSerializer
    pagination_class = ProductAPIListPagination

    def get_queryset(self):
        # category_ids = self.request.query_params['categoryIds'].split(',')
        category_ids_qp = None
        product_ids_qp = None
        categories = []
        if 'categoryIds' in self.request.query_params:
            category_ids_qp = self.request.query_params['categoryIds']
            for e in Category.objects.filter(translation__in=category_ids_qp.split(',')):
                categories.append(e.id)
        if 'productIds' in self.request.query_params:
            product_ids_qp = self.request.query_params['productIds']

        if category_ids_qp is None and product_ids_qp is None:
            return Product.objects.all().order_by('-id')[:10:1]
        elif category_ids_qp is not None and product_ids_qp is not None:
            return Product.objects.filter(category__id__in=categories, translation__in=product_ids_qp.split(','))
        elif category_ids_qp is not None:
            return Product.objects.filter(category__id__in=categories)
        elif product_ids_qp is not None:
            return Product.objects.filter(translation__in=product_ids_qp.split(','))

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = {'request': self.request}
        return ProductPaginationSerializer(*args, **kwargs)


class ProductSearchPaginationAPIView(generics.ListAPIView):
    serializer_class = ProductPaginationSerializer
    pagination_class = ProductAPIListPagination

    def get_queryset(self):
        q_search = self.request.query_params['q']
        return Product.objects.filter(name__icontains=q_search)

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = {'request': self.request}
        return ProductPaginationSerializer(*args, **kwargs)


class Feedback(APIView):
    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with open('resources/feedback_template.html', mode='r', encoding='utf-8') as f:
            html_template = f.read()
        html_template = html_template.replace('{question}', request.data['question']).replace('{name}', request.data[
            'name']).replace('{email}', request.data['email']).replace('{phone}', request.data['phone'])
        send_feedback_message(html_template)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Order(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with open('resources/order_email_template.html', mode='r', encoding='utf-8') as f:
            email_template = f.read()

        product_ids = list(map(lambda x: x['id'], request.data['products']))
        dict_products = dict(map(lambda x: (x.translation, x), list(Product.objects.filter(translation__in=product_ids))))
        html_products = []
        total_amount = 0.0
        for product in request.data['products']:
            main_image = Image.objects.filter(product_id=dict_products[product['id']].id, is_main=True).first()
            total_amount += product['count'] * float(dict_products[product['id']].price)
            item_prod_html = f'''
                              <tr>
                    <td class="item-col item">
                      <table cellspacing="0" cellpadding="0" width="100%">
                        <tr>
                          <td class="mobile-hide-img">
                            <img width="110" height="92" src="{request.build_absolute_uri(main_image.path.url)}" alt="{dict_products[product['id']].translation}">
                          </td>
                          <td class="product">
                            <span style="color: #4d4d4d; font-weight:bold;">{product['name']}</span><br>
                            <a href="{request.build_absolute_uri(dict_products[product['id']].translation)}">Перейти на сайт</a>
                          </td>
                        </tr>
                      </table>
                    </td>
                    <td class="item-col quantity">{product['count']}</td>
                    <td class="item-col">{float(dict_products[product['id']].price) * product['count']} ₽</td>
                  </tr>
            '''
            html_products.append(item_prod_html)

        if request.data['delivery'] == 'COURIER':
            delivery_price = 1000
        else:
            delivery_price = 0
        total_amount += delivery_price
        html_products.append(f'''
        <tr>
                    <td class="item-col item">
                    </td>
                    <td class="item-col quantity" style="text-align:right; padding-right: 10px; border-top: 1px solid #cccccc;">
                      <span class="total-space">Стоимость доставки</span> <br />
                      <span class="total-space" style="font-weight: bold; color: #4d4d4d">Итого</span>
                    </td>
                    <td class="item-col price" style="text-align: left; border-top: 1px solid #cccccc;">
                      <span class="total-space">{delivery_price} ₽</span> <br />
                      <span class="total-space" style="font-weight:bold; color: #4d4d4d">{total_amount} ₽</span>
                    </td>
                  </tr>
        ''')
        email_template = email_template.replace('{products}', '\n'.join(html_products))

        html_contacts = []
        contact_template = '''                <tr>
                  <td class="item-col item">
                    <strong>{key}: </strong> {value}
                  </td>
                </tr>
        '''
        html_contacts.append(
            contact_template.replace('{value}', request.data['lastName'] + ' ' + request.data['firstName']).replace(
                '{key}', 'ФИО'))
        html_contacts.append(
            contact_template.replace('{key}', 'email').replace('{value}', request.data['email']))
        html_contacts.append(
            contact_template.replace('{key}', 'phone').replace('{value}', request.data['phone']))
        if 'inn' in request.data and request.data['inn'] is not None:
            html_contacts.append(
                contact_template.replace('{key}', 'ИНН').replace('{value}', request.data['inn']))
        if 'organizationName' in request.data and request.data['organizationName'] is not None:
            html_contacts.append(contact_template.replace('{key}', 'Название организации').replace('{value}',
                                                                                                   request.data[
                                                                                                       'organizationName']))

        if request.data['delivery'] == 'SELF_CALL':
            html_contacts.append(contact_template.replace('{key}', 'Способ доставки').replace('{value}', ' Самовывоз'))
        elif request.data['delivery'] == 'COURIER':
            html_contacts.append(contact_template.replace('{key}', 'Способ доставки').replace('{value}', ' Курьером'))
        elif request.data['delivery'] == 'TERMINAL':
            html_contacts.append(
                contact_template.replace('{key}', 'Способ доставки').replace('{value}', ' До терминала ТК в СПБ'))

        if 'comment' in request.data and request.data['comment'] is not None:
            html_contacts.append(
                contact_template.replace('{key}', 'Комментарий').replace('{value}', request.data['comment']))

        email_template = email_template.replace('{contacts}', '\n'.join(html_contacts))

        send_order_message(email_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def send_feedback_message(html_template):
    from_address = os.environ.get('EMAIL_SENDER')
    to_address = os.environ.get('EMAIL_RECIPIENT')
    password = os.environ.get('SMTP_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = 'Обратная связь'

    msg.attach(MIMEText(html_template, 'html'))

    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    server.login(from_address, password)
    text = msg.as_string()
    server.sendmail(from_address, to_address, text)
    server.quit()


def send_order_message(email_template):
    from_address = os.environ.get('EMAIL_SENDER')
    to_address = os.environ.get('EMAIL_RECIPIENT')
    password = os.environ.get('SMTP_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = 'Новый заказ'

    msg.attach(MIMEText(email_template, 'html'))

    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    server.login(from_address, password)
    text = msg.as_string()
    server.sendmail(from_address, to_address, text)
    server.quit()
