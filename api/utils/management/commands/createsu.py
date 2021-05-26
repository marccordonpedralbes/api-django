from django.core.management.base import BaseCommand
from api.users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):

        if not User.objects.filter(username="username").exists():
            User.objects.create_superuser(
                "username", "email@email.com", "passs123")
            print("Super user created")
