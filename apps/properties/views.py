# ============================================================
# DJANGO IMPORTS
# ============================================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render


# ============================================================
# APPLICATION IMPORTS
# ============================================================

# Rental model is used for rental requests and
# checking whether a tenant has an active rental.
from apps.tenants.models import Rental

# Custom decorator that allows only OWNER users
# to access owner-only views.
from apps.accounts.decorators import owner_required

# Form used to create maintenance requests.
from .forms import MaintenanceRequestForm

# Models used by this application.
from .models import MaintenanceRequest, Property


# ============================================================
# HOME PAGE
# ============================================================

def home(request):
    """
    Public landing page.

    This page does not require authentication.
    It displays the latest available properties.
    """

    # Get only properties that are currently available.
    #
    # order_by("-created_at") means newest properties
    # appear first.
    #
    # [:6] limits the result to the first 6 properties.
    properties = Property.objects.filter(
        status="AVAILABLE"
    ).order_by("-created_at")[:6]

    return render(
        request,
        "properties/home.html",
        {
            "properties": properties,
        },
    )


# ============================================================
# ADD PROPERTY
# ============================================================

@owner_required
def add_property(request):
    """
    Allows an OWNER to create a new property.

    The owner is automatically taken from request.user,
    so the property is linked to the currently logged-in owner.
    """

    # Check whether the add-property form was submitted.
    if request.method == "POST":

        # Create a new property in the database.
        Property.objects.create(
            # IMPORTANT:
            # Associate the property with the logged-in owner.
            owner=request.user,

            title=request.POST.get("title"),
            description=request.POST.get("description"),
            property_type=request.POST.get("property_type"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            rent=request.POST.get("rent"),
            bedrooms=request.POST.get("bedrooms"),
            bathrooms=request.POST.get("bathrooms"),

            # request.FILES is used for uploaded files/images.
            image=request.FILES.get("image"),
        )

        # After successfully creating the property,
        # return to the owner dashboard.
        return redirect("owner_dashboard")

    # For a GET request, display the add-property form.
    return render(
        request,
        "properties/add_property.html",
    )


# ============================================================
# MY PROPERTIES
# ============================================================

@owner_required
def my_properties(request):
    """
    Displays only the properties belonging to the
    currently logged-in OWNER.
    """

    # IMPORTANT:
    # owner=request.user ensures that an owner can see
    # only their own properties.
    properties = Property.objects.filter(
        owner=request.user
    ).order_by("-created_at")

    return render(
        request,
        "properties/my_properties.html",
        {
            "properties": properties,
        },
    )


# ============================================================
# EDIT PROPERTY
# ============================================================

@owner_required
def edit_property(request, property_id):
    """
    Allows an OWNER to edit one of their own properties.
    """

    # get_object_or_404() does two things:
    #
    # 1. Finds the requested property.
    # 2. Returns a proper 404 response if it does not exist
    #    or does not belong to the logged-in owner.
    #
    # This also provides object-level authorization.
    property_obj = get_object_or_404(
        Property,
        id=property_id,
        owner=request.user,
    )

    # Process the submitted edit form.
    if request.method == "POST":

        # Update the property's basic information.
        property_obj.title = request.POST.get("title")
        property_obj.description = request.POST.get("description")
        property_obj.property_type = request.POST.get("property_type")
        property_obj.address = request.POST.get("address")
        property_obj.city = request.POST.get("city")
        property_obj.rent = request.POST.get("rent")
        property_obj.bedrooms = request.POST.get("bedrooms")
        property_obj.bathrooms = request.POST.get("bathrooms")
        property_obj.status = request.POST.get("status")

        # Only replace the existing image if the owner
        # selected a new image.
        if request.FILES.get("image"):
            property_obj.image = request.FILES.get("image")

        # Save all changes to the database.
        property_obj.save()

        # Return to the owner's property list.
        return redirect("my_properties")

    # Display the existing property information
    # inside the edit form.
    return render(
        request,
        "properties/edit_property.html",
        {
            "property": property_obj,
        },
    )


# ============================================================
# DELETE PROPERTY
# ============================================================

@owner_required
def delete_property(request, property_id):
    """
    Allows an OWNER to delete one of their own properties.

    The actual deletion happens only on POST.
    """

    # Only retrieve a property belonging to the
    # currently logged-in owner.
    property_obj = get_object_or_404(
        Property,
        id=property_id,
        owner=request.user,
    )

    # Delete only when the confirmation form is submitted.
    if request.method == "POST":

        property_obj.delete()

        return redirect("my_properties")

    # For GET requests, display the confirmation page.
    return render(
        request,
        "properties/delete_property.html",
        {
            "property": property_obj,
        },
    )


# ============================================================
# OWNER MAINTENANCE REQUESTS
# ============================================================

@owner_required
def owner_maintenance_requests(request):
    """
    Displays maintenance requests submitted by tenants
    for properties owned by the logged-in OWNER.
    """

    # property__owner=request.user means:
    #
    # MaintenanceRequest
    #       ↓
    # Property
    #       ↓
    # owner = currently logged-in user
    #
    # Therefore an owner can see only maintenance requests
    # related to their own properties.
    maintenance_requests = MaintenanceRequest.objects.filter(
        property__owner=request.user
    ).select_related(
        "tenant",
        "property",
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "properties/owner_maintenance_requests.html",
        {
            "maintenance_requests": maintenance_requests,
        },
    )


# ============================================================
# OWNER RENTAL REQUESTS
# ============================================================

@owner_required
def owner_rental_requests(request):
    """
    Displays rental requests for properties owned by
    the currently logged-in OWNER.
    """

    # Only retrieve rental requests associated with
    # the logged-in owner's properties.
    #
    # select_related() helps reduce unnecessary database
    # queries when accessing tenant and property information.
    rental_requests = Rental.objects.filter(
        property__owner=request.user
    ).select_related(
        "tenant",
        "property",
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "owner/rental_requests.html",
        {
            "rental_requests": rental_requests,
        },
    )


# ============================================================
# APPROVE RENTAL REQUEST
# ============================================================

@owner_required
def approve_rental_request(request, rental_id):
    """
    Approves a rental request.

    This action is performed only through POST.
    """

    # State-changing operations should use POST rather than GET.
    if request.method != "POST":
        return redirect("owner_rental_requests")

    # Retrieve only a rental request belonging to
    # a property owned by the logged-in OWNER.
    #
    # This prevents one owner from approving another
    # owner's rental request.
    rental = get_object_or_404(
        Rental,
        id=rental_id,
        property__owner=request.user,
    )

    # Change the rental status.
    rental.status = "APPROVED"

    # Save the change to the database.
    rental.save()

    # Show a success message to the owner.
    messages.success(
        request,
        "Rental request accepted successfully.",
    )

    return redirect("owner_rental_requests")


# ============================================================
# REJECT RENTAL REQUEST
# ============================================================

@owner_required
def reject_rental_request(request, rental_id):
    """
    Rejects a rental request.

    This action is performed only through POST.
    """

    # Only allow POST for this state-changing operation.
    if request.method != "POST":
        return redirect("owner_rental_requests")

    # Retrieve only a rental request belonging to
    # a property owned by the logged-in OWNER.
    rental = get_object_or_404(
        Rental,
        id=rental_id,
        property__owner=request.user,
    )

    # Change the rental status.
    rental.status = "REJECTED"

    # Save the change to the database.
    rental.save()

    # Show a warning message to the owner.
    messages.warning(
        request,
        "Rental request rejected.",
    )

    return redirect("owner_rental_requests")


# ============================================================
# CREATE MAINTENANCE REQUEST
# ============================================================

@login_required
def create_maintenance_request(request):
    """
    Allows a logged-in TENANT with an approved rental
    to submit a maintenance request.
    """

    # Find an approved rental belonging to the logged-in tenant.
    #
    # select_related("property") allows us to access the
    # related property without an additional database query.
    rental = Rental.objects.filter(
        tenant=request.user,
        status="APPROVED",
    ).select_related(
        "property",
    ).first()

    # If the tenant does not have an approved rental,
    # they cannot submit a maintenance request.
    if not rental:
        messages.warning(
            request,
            "You do not have an active rental.",
        )

        return redirect("tenant_dashboard")

    # Get the property associated with the approved rental.
    property_obj = rental.property

    # Process the maintenance form.
    if request.method == "POST":

        # request.FILES is required because the maintenance
        # request can contain an uploaded photo.
        form = MaintenanceRequestForm(
            request.POST,
            request.FILES,
        )

        # Validate the submitted form.
        if form.is_valid():

            # commit=False creates the object in memory
            # without immediately saving it to the database.
            maintenance_request = form.save(
                commit=False
            )

            # Set values controlled by the server.
            #
            # We do NOT allow the browser to decide which
            # property or tenant owns the maintenance request.
            maintenance_request.property = property_obj
            maintenance_request.tenant = request.user

            # Now save the completed object.
            maintenance_request.save()

            # Tell the tenant that the request was created.
            messages.success(
                request,
                "Maintenance request submitted successfully.",
            )

            # Return to the tenant dashboard.
            return redirect("tenant_dashboard")

    else:
        # Display an empty form for GET requests.
        form = MaintenanceRequestForm()

    # Display the maintenance request form.
    return render(
        request,
        "properties/create_maintenance_request.html",
        {
            "form": form,
            "property": property_obj,
        },
    )
