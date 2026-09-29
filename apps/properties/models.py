from django.conf import settings
from django.db import models


class Property(models.Model):

    PROPERTY_TYPE_CHOICES = (
        ("HOUSE", "House"),
        ("APARTMENT", "Apartment"),
        ("VILLA", "Villa"),
        ("ROOM", "Room"),
        ("PG", "PG"),
    )

    STATUS_CHOICES = (
        ("AVAILABLE", "Available"),
        ("RENTED", "Rented"),
    )

    image = models.ImageField(
        upload_to="properties/",
        null=True,
        blank=True,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="properties",
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPE_CHOICES,
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    rent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    bedrooms = models.PositiveIntegerField(
        default=1
    )

    bathrooms = models.PositiveIntegerField(
        default=1
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="AVAILABLE",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title


class MaintenanceRequest(models.Model):

    PRIORITY_CHOICES = (
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("URGENT", "Urgent"),
    )

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("REJECTED", "Rejected"),
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="maintenance_requests",
    )

    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="maintenance_requests",
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    issue_image = models.ImageField(
        upload_to="maintenance/",
        null=True,
        blank=True,
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="MEDIUM",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    owner_note = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.title} - {self.property.title}"