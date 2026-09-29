from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.tenants.models import Rental

from .forms import MaintenanceRequestForm
from .models import MaintenanceRequest, Property


def home(request):
    """Public landing page — no login required."""
    properties = Property.objects.filter(
        status="AVAILABLE"
    ).order_by("-created_at")[:6]
 
    return render(request, "properties/home.html", {
        "properties": properties,
    })

@login_required
def add_property(request):

    if request.user.role != "OWNER":
        return redirect("login")

    if request.method == "POST":

        Property.objects.create(
            owner=request.user,
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            property_type=request.POST.get("property_type"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            rent=request.POST.get("rent"),
            bedrooms=request.POST.get("bedrooms"),
            bathrooms=request.POST.get("bathrooms"),
            image=request.FILES.get("image"),
        )

        return redirect("owner_dashboard")

    return render(
        request,
        "properties/add_property.html"
    )


@login_required
def my_properties(request):

    if request.user.role != "OWNER":
        return redirect("login")

    properties = Property.objects.filter(
        owner=request.user
    ).order_by("-created_at")

    return render(
        request,
        "properties/my_properties.html",
        {
            "properties": properties
        }
    )


@login_required
def edit_property(request, property_id):

    if request.user.role != "OWNER":
        return redirect("login")

    property = Property.objects.get(
        id=property_id,
        owner=request.user
    )

    if request.method == "POST":

        property.title = request.POST.get("title")
        property.description = request.POST.get("description")
        property.property_type = request.POST.get("property_type")
        property.address = request.POST.get("address")
        property.city = request.POST.get("city")
        property.rent = request.POST.get("rent")
        property.bedrooms = request.POST.get("bedrooms")
        property.bathrooms = request.POST.get("bathrooms")
        property.status = request.POST.get("status")

        # Update image only if a new image was selected
        if request.FILES.get("image"):
            property.image = request.FILES.get("image")

        property.save()

        return redirect("my_properties")

    return render(
        request,
        "properties/edit_property.html",
        {
            "property": property
        }
    )


@login_required
def delete_property(request, property_id):

    if request.user.role != "OWNER":
        return redirect("login")

    property = Property.objects.get(
        id=property_id,
        owner=request.user
    )

    if request.method == "POST":
        property.delete()
        return redirect("my_properties")

    return render(
        request,
        "properties/delete_property.html",
        {
            "property": property
        }
    )
@login_required
def owner_rental_requests(request):
    if request.user.role != "OWNER":
        return redirect("login")

    rentals = Rental.objects.filter(
        property__owner=request.user
    ).select_related(
        "tenant",
        "property"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "properties/owner_rental_requests.html",
        {
            "rentals": rentals,
        }
    )


@login_required
def owner_maintenance_requests(request):
    if request.user.role != "OWNER":
        return redirect("login")

    maintenance_requests = MaintenanceRequest.objects.filter(
        property__owner=request.user
    ).select_related(
        "tenant",
        "property"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "properties/owner_maintenance_requests.html",
        {
            "maintenance_requests": maintenance_requests,
        }
    )

@login_required
def approve_rental_request(request, rental_id):
    if request.method == "POST":
        rental = get_object_or_404(Rental, id=rental_id, property__owner=request.user)
        rental.status = "APPROVED"  # Change to "approved" if your model uses lowercase
        rental.save()  # <--- MUST SAVE DB INSTANCE
        messages.success(request, "Rental request accepted successfully.")
    return redirect("owner_rental_requests")

@login_required
def reject_rental_request(request, rental_id):
    if request.method == "POST":
        rental = get_object_or_404(Rental, id=rental_id, property__owner=request.user)
        rental.status = "REJECTED"  # Change to "rejected" if your model uses lowercase
        rental.save()  # <--- MUST SAVE DB INSTANCE
        messages.warning(request, "Rental request rejected.")
    return redirect("owner_rental_requests")


@login_required
def create_maintenance_request(request):

    rental = Rental.objects.filter(
        tenant=request.user,
        status="APPROVED",
    ).select_related("property").first()

    if not rental:
        messages.warning(
            request,
            "You do not have an active rental."
        )
        return redirect("tenant_dashboard")

    property_obj = rental.property

    if request.method == "POST":
        form = MaintenanceRequestForm(request.POST, request.FILES)

        if form.is_valid():
            maintenance_request = form.save(commit=False)

            maintenance_request.property = property_obj
            maintenance_request.tenant = request.user

            maintenance_request.save()

            messages.success(
                request,
                "Maintenance request submitted successfully."
            )

            return redirect("tenant_dashboard")

    else:
        form = MaintenanceRequestForm()

    return render(
        request,
        "properties/create_maintenance_request.html",
        {
            "form": form,
            "property": property_obj,
        },
    )