from csv import DictReader
from io import TextIOWrapper

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from shopapp.models import Product, Order
from .forms import CSVImportFrom


class OrderInline(admin.TabularInline):
    model = Product.orders.through


@admin.action(description="Archive products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = [
        mark_archived,
        mark_unarchived,
    ]
    inlines = [
        OrderInline,
    ]
    list_display = "pk", "name", "description", "price", "discount", "archived"
    list_display_links = "pk", "name"
    list_filter = ("price", "name")
    search_fields = "name", "description"
    fieldsets = [
        (None, {
            "fields": ("name", "description"),
        }),
        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("wide",),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
        })
    ]


class ProductInline(admin.TabularInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "shopapp/orders_changelist.html"
    inlines = [
        ProductInline,
    ]
    list_display = "pk", "delivery_address", "promocode", "created_at", "user"

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'GET':
            form = CSVImportFrom()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportFrom(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)
        csv_file = TextIOWrapper(
            form.files["csv_file"].file,
            encoding=request.encoding,
        )
        reader = DictReader(csv_file)
        orders = []
        for row in reader:
            instance = Order.objects.create(delivery_address=row['delivery_address'],
                                            promocode=row['promocode'],
                                            user=request.user,
                                            )
            products = Product.objects.filter(id__in=[int(i) for i in row['products'].split(' ')])
            instance.user = request.user
            instance.products.set(products)

        self.message_user(request, "Data from CSV was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-orders-csv/",
                self.import_csv,
                name="import-orders-csv",
            )
        ]
        return new_urls + urls
