from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.properties.models import Property


class Command(BaseCommand):
    help = "Set the image URL for Property ID 2 only."

    def handle(self, *args, **options):
        with transaction.atomic():
            updated = Property.objects.filter(pk=2).update(
                image=(
                    "https://res.cloudinary.com/drt0y3ldh/image/upload/"
                    "v1792835619/bhouse.jpg"
                )
            )

            if updated != 1:
                raise CommandError("Property ID 2 does not exist.")

        self.stdout.write(
            self.style.SUCCESS("Updated image for Property ID 2.")
        )
