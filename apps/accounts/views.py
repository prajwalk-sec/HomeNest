from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.properties.models import Property
from .models import User
from apps.tenants.models import Rental

def register_view(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")

        if not all([
            first_name,
            last_name,
            email,
            password,
            confirm_password,
            role,
        ]):
            messages.error(request, "All fields are required.")
            return redirect("register")

        if role not in ["OWNER", "TENANT"]:
            messages.error(request, "Invalid role selected.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(
                request,
                "An account with this email already exists."
            )
            return redirect("register")

        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )

        messages.success(
            request,
            "Account created successfully. Please login."
        )

        return redirect("login")

    return render(request, "accounts/register.html")


def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password,
        )

        if user is not None:

            login(request, user)

            if user.role == "OWNER":
                return redirect("owner_dashboard")

            elif user.role == "TENANT":
                return redirect("tenant_dashboard")

            logout(request)

            messages.error(request, "Invalid user role.")
            return redirect("login")

        messages.error(request, "Invalid email or password.")
        return redirect("login")

    return render(request, "accounts/login.html")


@login_required
def logout_view(request):

    logout(request)

    messages.success(request, "You have been logged out successfully.")

    return redirect("login")

@login_required
def owner_dashboard(request):
    if request.user.role != "OWNER":
        return redirect("login")

    owner = request.user

    total_properties = Property.objects.filter(owner=owner).count()
    available_properties = Property.objects.filter(owner=owner, status="AVAILABLE").count()
    rented_properties = Property.objects.filter(owner=owner, status="RENTED").count()

    pending_requests = Rental.objects.filter(property__owner=owner, status="PENDING").count()
    approved_requests = Rental.objects.filter(property__owner=owner, status="APPROVED").count()
    rejected_requests = Rental.objects.filter(property__owner=owner, status="REJECTED").count()

    properties = Property.objects.filter(owner=owner).prefetch_related("rental_requests")

    context = {
        "total_properties": total_properties,
        "available_properties": available_properties,
        "rented_properties": rented_properties,
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "rejected_requests": rejected_requests,
        "properties": properties,
    }

    return render(request, "owner/dashboard.html", context)


@login_required
def approve_rental_request(request, rental_id):

    if request.user.role != "OWNER":
        return redirect("login")

    rental = Rental.objects.get(
        id=rental_id,
        property__owner=request.user
    )

    rental.status = "APPROVED"
    rental.save()

    return redirect("owner_rental_requests")

@login_required
def reject_rental_request(request, rental_id):

    if request.user.role != "OWNER":
        return redirect("login")

    rental = Rental.objects.get(
        id=rental_id,
        property__owner=request.user
    )

    rental.status = "REJECTED"
    rental.save()

    return redirect("owner_rental_requests")