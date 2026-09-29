from django.urls import path
from . import views


urlpatterns = [

        
    path(
        "add/",
        views.add_property,
        name="add_property",
    ),

    path(
        "my-properties/",
        views.my_properties,
        name="my_properties",
    ),

    path(
        "edit/<int:property_id>/",
        views.edit_property,
        name="edit_property",
    ),

    path(
        "delete/<int:property_id>/",
        views.delete_property,
        name="delete_property",
    ),

   path(
    "rental-requests/",
    views.owner_rental_requests,
    name="owner_rental_requests"
),

path(
    "maintenance-requests/",
    views.owner_maintenance_requests,
    name="owner_maintenance_requests",
),

path(
    "maintenance/create/",
    views.create_maintenance_request,
    name="create_maintenance_request",
),

]
