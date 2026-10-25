from io import BytesIO, StringIO
from unittest import skipUnless
from unittest.mock import patch

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import (
    SimpleTestCase,
    TestCase,
    TransactionTestCase,
    override_settings,
)
from django.urls import reverse
from PIL import Image
from cloudinary.exceptions import Error as CloudinaryError

from apps.accounts.models import User
from apps.properties.forms import PropertyForm
from apps.properties.models import (
    MaintenanceRequest,
    MaintenanceRequestHistory,
    Property,
)
from apps.tenants.models import Rental


@skipUnless(settings.CLOUDINARY_URL, "Cloudinary is not configured.")
class PropertyCloudinaryStorageTests(SimpleTestCase):

    def setUp(self):
        from config.storage import HomeNestMediaCloudinaryStorage

        self.storage = HomeNestMediaCloudinaryStorage()

    def test_legacy_property_path_uses_root_cloudinary_public_id(self):
        image_url = self.storage.url(
            "properties/047c6f68fa70f1901dd609a1d9ece210.jpg"
        )

        self.assertTrue(
            image_url.endswith(
                "/image/upload/047c6f68fa70f1901dd609a1d9ece210"
            )
        )
        self.assertNotIn("/media/", image_url)
        self.assertNotIn("/properties/", image_url)
        self.assertNotIn("/v1/", image_url)

    def test_property_image_field_uses_root_cloudinary_urls(self):
        image_url = Property._meta.get_field("image").storage.url(
            "properties/047c6f68fa70f1901dd609a1d9ece210.jpg"
        )

        self.assertTrue(
            image_url.endswith(
                "/image/upload/047c6f68fa70f1901dd609a1d9ece210"
            )
        )

    def test_new_property_upload_uses_root_public_id(self):
        image_content = b"uploaded image bytes"
        with patch.object(
            self.storage,
            "_upload",
            return_value={
                "public_id": "new-property-image",
                "version": 1792745196,
            },
        ) as upload:
            saved_name = self.storage.save(
                "properties/new-property-image.jpg",
                ContentFile(image_content),
            )

        self.assertEqual(saved_name, "properties/v1792745196/new-property-image")
        self.assertEqual(upload.call_args.args[0], "new-property-image.jpg")
        self.assertEqual(
            upload.call_args.args[1].name,
            "new-property-image.jpg",
        )
        self.assertEqual(
            upload.call_args.args[1].read(),
            image_content,
        )
        self.assertTrue(
            self.storage.url(saved_name).startswith(
                "https://res.cloudinary.com/"
            )
        )
        self.assertTrue(
            self.storage.url(saved_name).endswith(
                "/image/upload/v1792745196/new-property-image"
            )
        )

    def test_upload_failure_logs_safe_exception_type_and_traceback(self):
        file_contents = b"private image contents"
        with patch.object(
            self.storage,
            "_upload",
            side_effect=CloudinaryError("private diagnostic value"),
        ):
            with self.assertLogs("config.storage", level="ERROR") as logs:
                with self.assertRaises(CloudinaryError):
                    self.storage.save(
                        "properties/private-name.jpg",
                        ContentFile(file_contents),
                    )

        output = "\n".join(logs.output)
        self.assertIn("exception_type=Error", output)
        self.assertIn("_save", output)
        self.assertNotIn("private diagnostic value", output)
        self.assertNotIn(file_contents.decode(), output)

    def test_other_media_paths_keep_the_configured_media_prefix(self):
        image_url = self.storage.url("maintenance/repair.jpg")

        self.assertIn("/media/maintenance/repair.jpg", image_url)

    def test_edit_form_binds_upload_and_preserves_image_when_empty(self):
        property_obj = Property(
            image="properties/existing-image",
            title="Existing property",
            description="Existing description",
            property_type="HOUSE",
            address="1 Existing Road",
            city="Mumbai",
            rent="25000",
            bedrooms=2,
            bathrooms=1,
            status="AVAILABLE",
        )
        form_data = {
            "title": "Updated property",
            "description": "Updated description",
            "property_type": "HOUSE",
            "address": "2 New Road",
            "city": "Mumbai",
            "rent": "26000",
            "bedrooms": "2",
            "bathrooms": "1",
            "status": "AVAILABLE",
        }
        form = PropertyForm(form_data, {}, instance=property_obj)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.save(commit=False).image.name,
            "properties/existing-image",
        )

        image_buffer = BytesIO()
        Image.new("RGB", (10, 10), color="blue").save(
            image_buffer,
            format="JPEG",
        )
        upload = SimpleUploadedFile(
            "new-image.jpg",
            image_buffer.getvalue(),
            content_type="image/jpeg",
        )
        upload_form = PropertyForm(
            form_data,
            {"image": upload},
            instance=property_obj,
        )

        self.assertTrue(upload_form.is_valid(), upload_form.errors)
        self.assertEqual(
            upload_form.save(commit=False).image.name,
            "new-image.jpg",
        )


class SetProperty2ImageCommandTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(
            username="image-command-owner",
            email="image-command-owner@example.com",
            password="test-password",
            role="OWNER",
        )
        self.target = Property.objects.create(
            pk=2,
            owner=owner,
            title="Target property",
            description="Target description.",
            property_type="HOUSE",
            address="2 Target Road",
            city="Mumbai",
            rent=25000,
            image="properties/target.jpg",
        )
        self.other = Property.objects.create(
            pk=3,
            owner=owner,
            title="Other property",
            description="Other description.",
            property_type="HOUSE",
            address="3 Other Road",
            city="Mumbai",
            rent=25000,
            image="properties/other.jpg",
        )

    def test_updates_only_property_id_2(self):
        call_command("set_property_2_image", stdout=StringIO())

        self.target.refresh_from_db()
        self.other.refresh_from_db()
        self.assertEqual(
            self.target.image.name,
            "https://res.cloudinary.com/drt0y3ldh/image/upload/"
            "v1792835619/bhouse.jpg",
        )
        self.assertEqual(self.target.title, "Target property")
        self.assertEqual(self.target.description, "Target description.")
        self.assertEqual(self.other.image.name, "properties/other.jpg")


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
        self.assertTrue(request.issue_image.name.lower().endswith(".png"))
        self.assertTrue(request.issue_image.storage.exists(request.issue_image.name))
        history = request.history.get()
        self.assertEqual(history.status, "PENDING")
        self.assertEqual(history.updated_by, tenant)


@skipUnless(settings.CLOUDINARY_URL, "Cloudinary is not configured.")
@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "config.storage.HomeNestMediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)
class PropertyEditCloudinaryFailureTests(TransactionTestCase):

    def test_failed_image_upload_keeps_existing_property_unchanged(self):
        owner = User.objects.create_user(
            username="property-owner",
            email="property-owner@example.com",
            password="test-password",
            role="OWNER",
        )
        property_obj = Property.objects.create(
            owner=owner,
            title="Original title",
            description="Original description",
            property_type="HOUSE",
            address="1 Existing Road",
            city="Mumbai",
            rent=25000,
            bedrooms=2,
            bathrooms=1,
            status="AVAILABLE",
            image="properties/existing-image",
        )
        image_buffer = BytesIO()
        Image.new("RGB", (10, 10), color="blue").save(
            image_buffer,
            format="JPEG",
        )
        upload = SimpleUploadedFile(
            "replacement.jpg",
            image_buffer.getvalue(),
            content_type="image/jpeg",
        )

        self.client.force_login(owner)
        with patch(
            "config.storage.HomeNestMediaCloudinaryStorage._upload",
            side_effect=CloudinaryError("Cloudinary unavailable"),
        ):
            response = self.client.post(
                reverse("edit_property", args=[property_obj.pk]),
                {
                    "title": "Changed title",
                    "description": "Changed description",
                    "property_type": "HOUSE",
                    "address": "2 New Road",
                    "city": "Mumbai",
                    "rent": "26000",
                    "bedrooms": "3",
                    "bathrooms": "2",
                    "status": "AVAILABLE",
                    "image": upload,
                },
            )

        self.assertEqual(response.status_code, 200)
        property_obj.refresh_from_db()
        self.assertEqual(property_obj.title, "Original title")
        self.assertEqual(property_obj.description, "Original description")
        self.assertEqual(property_obj.image.name, "properties/existing-image")
        self.assertContains(response, "The image could not be uploaded")


class MaintenanceRequestWorkflowTests(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="maintenance-owner",
            email="owner-maintenance@example.com",
            password="Password123!",
            role="OWNER",
        )
        self.other_owner = User.objects.create_user(
            username="other-maintenance-owner",
            email="other-owner@example.com",
            password="Password123!",
            role="OWNER",
        )
        self.tenant = User.objects.create_user(
            username="maintenance-tenant",
            email="tenant-maintenance@example.com",
            password="Password123!",
            role="TENANT",
        )
        self.other_tenant = User.objects.create_user(
            username="other-maintenance-tenant",
            email="other-tenant@example.com",
            password="Password123!",
            role="TENANT",
        )
        self.property = Property.objects.create(
            owner=self.owner,
            title="Maintenance Home",
            description="A home for maintenance tests.",
            property_type="HOUSE",
            address="1 Main Street",
            city="Mumbai",
            rent=25000,
            bedrooms=2,
            bathrooms=1,
            status="RENTED",
        )
        self.other_property = Property.objects.create(
            owner=self.other_owner,
            title="Other Owner Home",
            description="Another home.",
            property_type="HOUSE",
            address="2 Main Street",
            city="Mumbai",
            rent=25000,
            bedrooms=2,
            bathrooms=1,
            status="RENTED",
        )
        self.tenant_request = MaintenanceRequest.objects.create(
            property=self.property,
            tenant=self.tenant,
            title="Leaking tap",
            description="The kitchen tap leaks.",
            priority="HIGH",
        )
        self.other_tenant_request = MaintenanceRequest.objects.create(
            property=self.property,
            tenant=self.other_tenant,
            title="Broken window",
            description="The window will not close.",
        )
        self.foreign_request = MaintenanceRequest.objects.create(
            property=self.other_property,
            tenant=self.other_tenant,
            title="Faulty heater",
            description="The heater is not working.",
        )
        for maintenance_request in [
            self.tenant_request,
            self.other_tenant_request,
            self.foreign_request,
        ]:
            MaintenanceRequestHistory.objects.create(
                maintenance_request=maintenance_request,
                status=maintenance_request.status,
                updated_by=maintenance_request.tenant,
            )

    def test_tenant_dashboard_shows_only_their_maintenance_requests(self):
        self.client.login(username="maintenance-tenant", password="Password123!")

        response = self.client.get(reverse("tenant_dashboard"))

        self.assertEqual(response.status_code, 200)
        requests = list(response.context["maintenance_requests"])
        self.assertEqual([item.id for item in requests], [self.tenant_request.id])
        self.assertContains(response, "Your maintenance request is currently pending review.")
        self.assertContains(response, self.property.title)
        self.assertContains(response, self.tenant_request.title)
        self.assertContains(response, "High")
        self.assertContains(response, "Submitted")

    def test_owner_can_advance_status_and_reply(self):
        self.client.login(username="maintenance-owner", password="Password123!")
        update_url = reverse(
            "update_maintenance_request",
            args=[self.tenant_request.id],
        )

        response = self.client.post(
            update_url,
            {"status": "IN_PROGRESS", "owner_note": "Repair is scheduled."},
        )
        self.assertEqual(response.status_code, 302)
        self.tenant_request.refresh_from_db()
        self.assertEqual(self.tenant_request.status, "IN_PROGRESS")
        self.assertEqual(self.tenant_request.owner_note, "Repair is scheduled.")

        self.client.post(
            update_url,
            {"status": "IN_PROGRESS", "owner_note": "The replacement part arrived."},
        )
        self.tenant_request.refresh_from_db()
        self.assertEqual(self.tenant_request.owner_note, "The replacement part arrived.")

        self.client.post(
            update_url,
            {"status": "RESOLVED", "owner_note": "The tap has been repaired."},
        )
        self.tenant_request.refresh_from_db()
        self.assertEqual(self.tenant_request.status, "RESOLVED")
        self.assertEqual(self.tenant_request.owner_note, "The tap has been repaired.")
        self.assertIsNotNone(self.tenant_request.completed_at)
        history = list(self.tenant_request.history.all())
        self.assertEqual(
            [entry.status for entry in history],
            ["PENDING", "IN_PROGRESS", "IN_PROGRESS", "RESOLVED"],
        )
        self.assertEqual(
            [entry.owner_note for entry in history],
            ["", "Repair is scheduled.", "The replacement part arrived.", "The tap has been repaired."],
        )
        self.assertTrue(all(entry.updated_by == self.owner for entry in history[1:]))

        owner_response = self.client.get(reverse("owner_maintenance_requests"))
        owner_content = owner_response.content.decode()
        self.assertLess(
            owner_content.index("Repair is scheduled."),
            owner_content.index("The replacement part arrived."),
        )
        self.assertLess(
            owner_content.index("The replacement part arrived."),
            owner_content.index("The tap has been repaired."),
        )

        self.client.logout()
        self.client.login(username="maintenance-tenant", password="Password123!")
        response = self.client.get(reverse("tenant_dashboard"))
        self.assertContains(response, "Resolved")
        self.assertContains(response, "The tap has been repaired.")
        tenant_content = response.content.decode()
        self.assertLess(
            tenant_content.index("Repair is scheduled."),
            tenant_content.index("The replacement part arrived."),
        )
        self.assertLess(
            tenant_content.index("The replacement part arrived."),
            tenant_content.index("The tap has been repaired."),
        )

    def test_closed_request_rejects_all_later_updates(self):
        self.client.login(username="maintenance-owner", password="Password123!")

        for closed_status in ["RESOLVED", "REJECTED"]:
            with self.subTest(status=closed_status):
                self.tenant_request.status = closed_status
                self.tenant_request.owner_note = "Closed request note."
                self.tenant_request.save()
                history_count = self.tenant_request.history.count()

                response = self.client.post(
                    reverse("update_maintenance_request", args=[self.tenant_request.id]),
                    {"status": "", "owner_note": "A later update."},
                )

                self.assertEqual(response.status_code, 302)
                self.tenant_request.refresh_from_db()
                self.assertEqual(self.tenant_request.status, closed_status)
                self.assertEqual(self.tenant_request.owner_note, "Closed request note.")
                self.assertEqual(self.tenant_request.history.count(), history_count)

    def test_owner_can_reject_only_after_work_is_in_progress(self):
        self.tenant_request.status = "IN_PROGRESS"
        self.tenant_request.save(update_fields=["status"])
        self.client.login(username="maintenance-owner", password="Password123!")

        response = self.client.post(
            reverse("update_maintenance_request", args=[self.tenant_request.id]),
            {"status": "REJECTED", "owner_note": "The issue is not covered."},
        )

        self.assertEqual(response.status_code, 302)
        self.tenant_request.refresh_from_db()
        self.assertEqual(self.tenant_request.status, "REJECTED")

    def test_owner_cannot_skip_pending_directly_to_resolved(self):
        self.client.login(username="maintenance-owner", password="Password123!")

        self.client.post(
            reverse("update_maintenance_request", args=[self.tenant_request.id]),
            {"status": "RESOLVED", "owner_note": "Skipping a step."},
        )

        self.tenant_request.refresh_from_db()
        self.assertEqual(self.tenant_request.status, "PENDING")

    def test_owner_cannot_update_request_for_another_owners_property(self):
        self.client.login(username="maintenance-owner", password="Password123!")

        response = self.client.post(
            reverse(
                "update_maintenance_request",
                args=[self.foreign_request.id],
            ),
            {"status": "IN_PROGRESS", "owner_note": "Unauthorized update."},
        )

        self.assertEqual(response.status_code, 404)
        self.foreign_request.refresh_from_db()
        self.assertEqual(self.foreign_request.status, "PENDING")

    def test_owner_list_is_limited_to_owned_properties(self):
        self.client.login(username="maintenance-owner", password="Password123!")

        response = self.client.get(reverse("owner_maintenance_requests"))

        self.assertEqual(response.status_code, 200)
        requests = list(response.context["maintenance_requests"])
        self.assertEqual(
            {item.id for item in requests},
            {self.tenant_request.id, self.other_tenant_request.id},
        )

    def test_tenant_can_remove_their_own_request(self):
        self.client.login(username="maintenance-tenant", password="Password123!")

        response = self.client.post(
            reverse("delete_maintenance_request", args=[self.tenant_request.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            MaintenanceRequest.objects.filter(id=self.tenant_request.id).exists()
        )
        self.assertTrue(
            MaintenanceRequestHistory.objects.filter(
                maintenance_request__isnull=True,
                updated_by=self.tenant,
            ).exists()
        )
        self.assertContains(response, "Your maintenance request was removed.")

    def test_tenant_cannot_remove_another_tenants_request(self):
        self.client.login(username="maintenance-tenant", password="Password123!")

        response = self.client.post(
            reverse("delete_maintenance_request", args=[self.other_tenant_request.id]),
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            MaintenanceRequest.objects.filter(id=self.other_tenant_request.id).exists()
        )

    def test_removal_requires_post(self):
        self.client.login(username="maintenance-tenant", password="Password123!")

        response = self.client.get(
            reverse("delete_maintenance_request", args=[self.tenant_request.id]),
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(
            MaintenanceRequest.objects.filter(id=self.tenant_request.id).exists()
        )

    def test_submission_shows_confirmation_message(self):
        Rental.objects.create(
            tenant=self.tenant,
            property=self.property,
            status="APPROVED",
        )
        self.client.login(username="maintenance-tenant", password="Password123!")

        response = self.client.post(
            reverse("create_maintenance_request"),
            {
                "title": "Bedroom light",
                "description": "The bedroom light is out.",
                "priority": "MEDIUM",
            },
            follow=True,
        )

        self.assertContains(
            response,
            "Your maintenance request has been received successfully.",
        )
