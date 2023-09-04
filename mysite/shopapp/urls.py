from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    shop_index,
    ProductsListView,
    handle_file_upload,
    ProductCreateView,
    ProductDetailView,
    ProductUpdateView,
    ProductArchiveView,
    OrdersListView,
    OrderDetailView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    OrderExportView,
    ProductViewSet,
    OrderViewSet,
    LatestProductsFeed,
    UserOrderListView,
    UserOrderExportView,
)

app_name = 'shopapp'

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("order", OrderViewSet)

urlpatterns = [
    path("", shop_index, name="index"),
    path("api/", include(routers.urls)),
    path("products/", ProductsListView.as_view(), name='products_list'),
    path("products/<int:pk>/", ProductDetailView.as_view(), name='product_details'),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name='product_update'),
    path("products/<int:pk>/delete/", ProductArchiveView.as_view(), name='product_delete'),
    path("products/create", ProductCreateView.as_view(), name='product_create'),
    path("orders/", OrdersListView.as_view(), name='orders_list'),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name='order_details'),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name='order_update'),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name='order_delete'),
    path("orders/create/", OrderCreateView.as_view(), name='order_create'),
    path("orders/export/", OrderExportView.as_view(), name='order_export'),
    path("upload/", handle_file_upload, name='file_upload'),
    path("products/latest/feed/", LatestProductsFeed(), name="products_feed"),
    path("users/<int:user_id>/orders/", UserOrderListView.as_view(), name='user_orders_list'),
    path("users/<int:user_id>/orders/export/", UserOrderExportView.as_view(), name='user_orders_export'),
]
