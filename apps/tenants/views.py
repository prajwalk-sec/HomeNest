from django.shortcuts import render,redirect
from django.contrib import messages
from django .contrib.auth.decorators import login_required
from .models import Tenant,Rental
from apps.properties.models import Property

# Create your views here.
@login_required
def tenant_dashboard(request):

    if request.user.role != "TENANT":
        return render(request, "tenants/dashboard.html")

    tenant, created = Tenant.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        "tenants/dashboard.html",
        {
            "tenant": tenant,
        }
    )

@login_required
def available_properties(request):

    # Start with all available properties
    properties = Property.objects.filter(
        status="AVAILABLE"
    ).order_by("-created_at")

    # Get search/filter values
    city = request.GET.get("city", "").strip()
    property_type = (request.GET.get("property_type") or request.GET.get("type") or "").strip()
    max_rent = request.GET.get("max_rent", "").strip()

    # Filter by city
    if city:
        properties = properties.filter(
            city__icontains=city
        )

    # Filter by property type
    if property_type:
        properties = properties.filter(
            property_type=property_type
        )

    # Filter by maximum rent
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
        }
    )

# Property Details
@login_required
def property_details(request, property_id):

    property = Property.objects.get(
        id=property_id,
        status="AVAILABLE"
    )

    return render(
        request,
        "tenants/property_details.html",
        {
            "property": property,
        }
    )

@login_required
def property_details(request, property_id):

    property = Property.objects.get(
        id=property_id,
        status="AVAILABLE"
    )

    return render(
        request,
        "tenants/property_details.html",
        {
            "property": property,
        }
    )

# Send Rental Request
@login_required
def send_rental_request(request, property_id):

    if request.user.role != "TENANT":
        return redirect("login")

    property = Property.objects.get(
        id=property_id,
        status="AVAILABLE"
    )

    Rental.objects.create(
        tenant=request.user,
        property=property,
        status="PENDING"
    )

    messages.success(
        request,
        "Your rental application has been submitted successfully. The owner will review your request and update its status."
    )

    return redirect(
        "property_details",
        property_id=property.id
    )


@login_required
def my_rental_requests(request):

    if request.user.role != "TENANT":
        return redirect("login")

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
        }
    )

def owner_rental_requests(request):

    owner = request.user

    rental_requests = Rental.objects.filter(
        property__owner=owner
    ).select_related(
        "tenant",
        "property"
    ).order_by(
        "-created_at"
    )

    context = {
        "rental_requests": rental_requests,
    }

    return render(
        request,
        "owner/rental_requests.html",
        context
    )