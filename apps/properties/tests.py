from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from apps.accounts.models import User
from apps.properties.models import Property
from apps.tenants.models import Rental


class MaintenanceRequestPhotoUploadTests(TestCase):

    def test_tenant_can_submit_maintenance_request_with_optional_photo(self):
        owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="Password123!",
            role="OWNER",
        )
        tenant = User.objects.create_user(
            username="tenant",
            email="tenant@example.com",
            password="Password123!",
            role="TENANT",
        )

        property_obj = Property.objects.create(
            owner=owner,
            title="Sunny Villa",
            description="A nice place to live.",
            property_type="HOUSE",
            address="123 Main Street",
            city="Mumbai",
            rent=25000,
            bedrooms=2,
            bathrooms=2,
            status="AVAILABLE",
        )

        Rental.objects.create(
            tenant=tenant,
            property=property_obj,
            status="APPROVED",
        )

        image_buffer = BytesIO()
        Image.new("RGB", (10, 10), color="blue").save(image_buffer, format="PNG")
        image_buffer.seek(0)

        image = SimpleUploadedFile(
            "leak.png",
            image_buffer.read(),
            content_type="image/png",
        )

        self.client.login(username="tenant", password="Password123!")
        response = self.client.post(
            reverse("create_maintenance_request"),
            {
                "title": "Water leakage in bathroom",
                "description": "The bathroom ceiling is leaking.",
                "priority": "HIGH",
                "issue_image": image,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            property_obj.maintenance_requests.filter(
                tenant=tenant,
                title="Water leakage in bathroom",
            ).exists()
        )
        request = property_obj.maintenance_requests.get(
            tenant=tenant,
            title="Water leakage in bathroom",
        )
        self.assertTrue(request.issue_image.name.endswith("leak.png"))
