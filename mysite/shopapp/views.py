import json
from timeit import default_timer

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.core.cache import cache
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from myauth.models import Profile
from .forms import ProductForm, OrderForm
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer


def shop_index(request: HttpRequest):
    context = {
        'time_running': default_timer()
    }
    return render(request, 'shopapp/shop-index.html', context=context)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived"
    ]
    ordering_fields = [
        "name",
        "description",
        "price",
        "discount",
    ]


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_fields = [
        "user",
        "created_at",
        "promocode",
    ]
    ordering_fields = [
        "user",
        "created_at",
        "promocode",
    ]

# ================================Products=============================================
class ProductsListView(ListView):
    queryset = Product.objects.filter(archived=False)
    template_name = "shopapp/products-list.html"
    context_object_name = "products"


class ProductDetailView(DetailView):
    template_name = "shopapp/product-details.html"
    model = Product
    context_object_name = "product"


class ProductCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = "shopapp.add_product"
    template_name = "shopapp/product-create.html"
    model = Product
    context_object_name = "product"
    fields = "name", "price", "description", "discount"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        model_instance = form.save(commit=False)
        model_instance.created_by = self.request.user
        model_instance.save()
        form.save()
        return super().form_valid(form)


class ProductUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = "shopapp.change_product"
    model = Product
    template_name = "shopapp/product-update.html"
    context_object_name = "product"
    fields = "name", "price", "description", "discount"

    def form_valid(self, form):
        if self.request.user != form.created_by:
            raise PermissionError
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk}
        )


class ProductArchiveView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = "shopapp/product_confirm_delete.html"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class LatestProductsFeed(Feed):
    title = "Products (latest)"
    description = "Updates on products"
    link = reverse_lazy("shopapp:index")

    def items(self):
        return (
            Product.objects.filter(archived=False)
            .order_by("-created_at")[:5]
        )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description

# ================================Orders=============================================
class OrdersListView(ListView):
    model = Order
    template_name = "shopapp//orders-list.html"
    context_object_name = "orders"


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    model = Order
    template_name = "shopapp/order-details.html"
    context_object_name = "order"


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    template_name = "shopapp/order-create.html"
    context_object_name = "order"
    form_class = OrderForm
    success_url = reverse_lazy("shopapp:orders_list")

    def form_valid(self, form):
        model_instance = form.save(commit=False)
        model_instance.user = self.request.user
        model_instance.save()
        form.save()
        return super().form_valid(form)


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    template_name = "shopapp/order-update.html"
    context_object_name = "order"
    form_class = OrderForm

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk}
        )


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = "shopapp/order_confirm_delete.html"
    success_url = reverse_lazy("shopapp:orders_list")


class OrderExportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> HttpResponse:
        data = dict()
        data["orders"] = list()
        for order in Order.objects.all():
            order_dict = {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user_id,
                "products": [product.pk for product in order.products.all()],
            }
            data["orders"].append(order_dict)
        return HttpResponse(json.dumps(data))


class UserOrderExportView(LoginRequiredMixin, TemplateView):
    serializer_class = OrderSerializer

    def get(self, request: HttpRequest, user_id) -> HttpResponse:
        cached_key = "orders_data_export" + user_id
        data = cache.get(cached_key)
        if data is None:
            data = dict()
            data["orders"] = list()
            self.owner = get_object_or_404(User, id=user_id)
            for order in Order.objects.filter(user_id=self.owner):
                order_dict = {
                    "pk": order.pk,
                    "delivery_address": order.delivery_address,
                    "promocode": order.promocode,
                    "user_id": order.user_id,
                    "products": [product.pk for product in order.products.all()],
                }
                data["orders"].append(order_dict)
            cache.set(cached_key, data, 300)
        return HttpResponse(json.dumps(data))


class UserOrderListView(ListView, LoginRequiredMixin):
    model = Order
    template_name = "shopapp//orders-list.html"
    context_object_name = "orders"

    def get_queryset(self) -> HttpResponse:
        self.owner = get_object_or_404(User, id=self.kwargs['user_id'])
        return Order.objects.filter(user_id=self.owner)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context


# ================================Other=============================================
def handle_file_upload(request: HttpRequest):
    big_file = False
    filename = "null"
    if request.method == "POST" and request.FILES.get("myfile"):
        myfile = request.FILES["myfile"]
        filesize = myfile.size
        if filesize > 1024*1024:
            big_file = True
            print("File too big!", filesize)
        else:
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            print("saved file", filename)
    context = {
        "big_file": big_file,
        "filename": filename
    }
    return render(request, 'shopapp/file-upload.html', context=context)


