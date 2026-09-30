# ============================================================
# DJANGO IMPORTS
# ============================================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render


# ============================================================
# APPLICATION IMPORTS
# ============================================================

from .models import Tenant, Rental
from apps.properties.models import MaintenanceRequest, Property


# ============================================================
# TENANT DASHBOARD
# ============================================================

@login_required
def tenant_dashboard(request):
    """
    Displays the dashboard for the currently logged-in TENANT.

    Only users with the TENANT role should access this page.
    """

    # Prevent OWNER users from accessing the tenant dashboard.
    if request.user.role != "TENANT":
        return redirect("owner_dashboard")

    # Get the tenant profile.
    #
    # If the profile does not exist yet, Django creates it.
    tenant, created = Tenant.objects.get_or_create(
        user=request.user
    )

    maintenance_requests = MaintenanceRequest.objects.filter(
        tenant=request.user
    ).select_related(
        "property"
    ).prefetch_related(
        "history__updated_by",
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "tenants/dashboard.html",
        {
            "tenant": tenant,
            "maintenance_requests": maintenance_requests,
        },
    )


# ============================================================
# AVAILABLE PROPERTIES
# ============================================================

@login_required
def available_properties(request):
    """
    Displays all currently available properties.

    Tenants can filter properties by:
    - City
    - Property type
    - Maximum rent
    """

    # Start with only available properties.
    #
    # Newest properties appear first.
    properties = Property.objects.filter(
        status="AVAILABLE"
    ).order_by(
        "-created_at"
    )

    # --------------------------------------------------------
    # GET FILTER VALUES
    # --------------------------------------------------------

    city = request.GET.get(
        "city",
        ""
    ).strip()

    # Support both parameter names so existing templates
    # using either "property_type" or "type" continue working.
    property_type = (
        request.GET.get("property_type")
        or request.GET.get("type")
        or ""
    ).strip()

    max_rent = request.GET.get(
        "max_rent",
        ""
    ).strip()

    # --------------------------------------------------------
    # FILTER BY CITY
    # --------------------------------------------------------

    if city:
        properties = properties.filter(
            city__icontains=city
        )

    # --------------------------------------------------------
    # FILTER BY PROPERTY TYPE
    # --------------------------------------------------------

    if property_type:
        properties = properties.filter(
            property_type=property_type
        )

    # --------------------------------------------------------
    # FILTER BY MAXIMUM RENT
    # --------------------------------------------------------

    if max_rent:
        properties = properties.filter(
            rent__lte=max_rent
        )

    return render(
        request,
        "tenants/available_properties.html",
        {
            "properties": properties,
            "city": city,
            "property_type": property_type,
            "max_rent": max_rent,
        },
    )


# ============================================================
# PROPERTY DETAILS
# ============================================================

@login_required
def property_details(request, property_id):
    """
    Displays details of a property that is currently available.
    """

    # get_object_or_404() returns a proper 404 page if:
    #
    # 1. The property does not exist.
    # 2. The property is no longer available.
    #
    # This is safer than using Property.objects.get().
    property_obj = get_object_or_404(
        Property,
        id=property_id,
        status="AVAILABLE",
    )

    return render(
        request,
        "tenants/property_details.html",
        {
            "property": property_obj,
        },
    )


# ============================================================
# SEND RENTAL REQUEST
# ============================================================

@login_required
def send_rental_request(request, property_id):
    """
    Allows a TENANT to submit a rental request
    for an available property.

    The request is created only through POST.
    """

    # Only TENANT users can send rental requests.
    if request.user.role != "TENANT":
        return redirect("login")

    # State-changing operations should use POST.
    if request.method != "POST":
        return redirect(
            "property_details",
            property_id=property_id,
        )

    # Retrieve only an available property.
    property_obj = get_object_or_404(
        Property,
        id=property_id,
        status="AVAILABLE",
    )

    # --------------------------------------------------------
    # PREVENT DUPLICATE RENTAL REQUESTS
    # --------------------------------------------------------

    existing_request = Rental.objects.filter(
        tenant=request.user,
        property=property_obj,
    ).exists()

    if existing_request:
        messages.warning(
            request,
            "You have already submitted a rental request for this property.",
        )

        return redirect(
            "property_details",
            property_id=property_obj.id,
        )

    # --------------------------------------------------------
    # CREATE RENTAL REQUEST
    # --------------------------------------------------------

    Rental.objects.create(
        tenant=request.user,
        property=property_obj,
        status="PENDING",
    )

    # Show a success message to the tenant.
    messages.success(
        request,
        "Your rental application has been submitted successfully. "
        "The owner will review your request and update its status.",
    )

    return redirect(
        "property_details",
        property_id=property_obj.id,
    )


# ============================================================
# MY RENTAL REQUESTS
# ============================================================

@login_required
def my_rental_requests(request):
    """
    Displays all rental requests submitted by
    the currently logged-in TENANT.
    """

    # Only TENANT users should access this page.
    if request.user.role != "TENANT":
        return redirect("owner_dashboard")

    # Retrieve only requests belonging to the current tenant.
    #
    # select_related("property") avoids extra database
    # queries when the template accesses rental.property.
    rentals = Rental.objects.filter(
        tenant=request.user
    ).select_related(
        "property"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "tenants/my_rental_requests.html",
        {
            "rentals": rentals,
        },
    )

