from django import forms
from django.contrib.auth.models import User

from .models import Product, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount"


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "products", "delivery_address", "promocode"

    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.filter(archived=False),
        widget=forms.CheckboxSelectMultiple,
    )


class CSVImportFrom(forms.Form):
    csv_file = forms.FileField()
