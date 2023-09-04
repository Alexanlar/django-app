from django.contrib.auth.models import User
from django.core.management import BaseCommand
from shopapp.models import Product, Order


class Command(BaseCommand):
    """
    Create orders
    """
    def handle(self, *args, **options):
        self.stdout.write("Create order")
        user = User.objects.get(username="user")
        order = Order.objects.get_or_create(
            delivery_address="Chaikinoi st., 29",
            promocode="sale20",
            user=user
        )
        self.stdout.write(f"Order created {order}")
        self.stdout.write(
            self.style.SUCCESS("Orders created")
        )