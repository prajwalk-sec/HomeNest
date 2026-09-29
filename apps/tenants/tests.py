from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.properties.models import Property


class RentalRequestMessageTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owneruser",
            email="owner@example.com",
            password="StrongPass123!",
            role="OWNER",
        )
        self.tenant = User.objects.create_user(
            username="tenantuser",
            email="tenant@example.com",
            password="StrongPass123!",
            role="TENANT",
        )
        self.property = Property.objects.create(
            owner=self.owner,
            title="Sunset Apartment",
            description="A bright apartment near the city center.",
            property_type="APARTMENT",
            address="12 Market Street",
            city="Nairobi",
            rent="25000.00",
            bedrooms=2,
            bathrooms=1,
            status="AVAILABLE",
        )

    def test_success_message_after_rental_application_submission(self):
        self.client.login(username="tenantuser", password="StrongPass123!")

        response = self.client.post(
            reverse("send_rental_request", args=[self.property.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Your rental application has been submitted successfully. The owner will review your request and update its status.",
        )


class TenantPropertySearchTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="ownersearch",
            email="ownersearch@example.com",
            password="StrongPass123!",
            role="OWNER",
        )
        self.tenant = User.objects.create_user(
            username="tenantsearch",
            email="tenantsearch@example.com",
            password="StrongPass123!",
            role="TENANT",
        )

        self.matching_property = Property.objects.create(
            owner=self.owner,
            title="Lake View Apartment",
            description="A bright apartment near the lake.",
            property_type="APARTMENT",
            address="5 Lake Road",
            city="Nairobi",
            rent="28000.00",
            bedrooms=3,
            bathrooms=2,
            status="AVAILABLE",
        )

        self.other_property = Property.objects.create(
            owner=self.owner,
            title="City House",
            description="A townhouse in another area.",
            property_type="HOUSE",
            address="8 Town Lane",
            city="Mombasa",
            rent="32000.00",
            bedrooms=4,
            bathrooms=3,
            status="AVAILABLE",
        )

    def test_available_properties_search_filters_by_city_type_and_budget(self):
        self.client.login(username="tenantsearch", password="StrongPass123!")

        response = self.client.get(
            reverse("available_properties"),
            {"city": "Nairobi", "property_type": "APARTMENT", "max_rent": "30000"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lake View Apartment")
        self.assertNotContains(response, "City House")
        self.assertEqual(list(response.context["properties"]), [self.matching_property])
