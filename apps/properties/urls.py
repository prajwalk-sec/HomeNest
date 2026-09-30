from django.urls import path
from . import views


urlpatterns = [

    # ========================================================
    # ADD PROPERTY
    # ========================================================

    path(
        "add/",
        views.add_property,
        name="add_property",
    ),


    # ========================================================
    # MY PROPERTIES
    # ========================================================

    path(
        "my-properties/",
        views.my_properties,
        name="my_properties",
    ),


    # ========================================================
    # EDIT PROPERTY
    # ========================================================

    path(
        "edit/<int:property_id>/",
        views.edit_property,
        name="edit_property",
    ),


    # ========================================================
    # DELETE PROPERTY
    # ========================================================

    path(
        "delete/<int:property_id>/",
        views.delete_property,
        name="delete_property",
    ),


    # ========================================================
    # OWNER RENTAL REQUESTS
    # ========================================================

    path(
        "rental-requests/",
        views.owner_rental_requests,
        name="owner_rental_requests",
    ),


    # ========================================================
    # APPROVE RENTAL REQUEST
    # ========================================================

    path(
        "rental-requests/<int:rental_id>/approve/",
        views.approve_rental_request,
        name="approve_rental_request",
    ),


    # ========================================================
    # REJECT RENTAL REQUEST
    # ========================================================

    path(
        "rental-requests/<int:rental_id>/reject/",
        views.reject_rental_request,
        name="reject_rental_request",
    ),


    # ========================================================
    # OWNER MAINTENANCE REQUESTS
    # ========================================================

    path(
        "maintenance-requests/",
        views.owner_maintenance_requests,
        name="owner_maintenance_requests",
    ),


    # ========================================================
    # CREATE MAINTENANCE REQUEST
    # ========================================================

    path(
        "maintenance/create/",
        views.create_maintenance_request,
        name="create_maintenance_request",
    ),
]

