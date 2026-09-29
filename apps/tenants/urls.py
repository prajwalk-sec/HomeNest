from django.urls import path
from . import views

urlpatterns = [

# ================= TENANT DASHBOARD =================

path(
    "dashboard/",
    views.tenant_dashboard,
    name="tenant_dashboard"
),


# ================= AVAILABLE PROPERTIES =================

path(
    "properties/",
    views.available_properties,
    name="available_properties"
),


# ================= PROPERTY DETAILS =================

path(
    "property/<int:property_id>/",
    views.property_details,
    name="property_details"
),


# ================= RENTAL APPLICATION =================

path(
    "property/<int:property_id>/apply/",
    views.send_rental_request,
    name="send_rental_request"
),


# ================= TENANT RENTAL REQUESTS =================

path(
    "my-rental-requests/",
    views.my_rental_requests,
    name="my_rental_requests"
),


# ================= OWNER RENTAL REQUESTS =================

path(
    "owner/rental-requests/",
    views.owner_rental_requests,
    name="owner_rental_requests"
),

]
