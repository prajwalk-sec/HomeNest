# ============================================================
# DJANGO AUTHENTICATION
# ============================================================

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect


# ============================================================
# APPLICATION IMPORTS
# ============================================================

# Property model used by the owner dashboard.
from apps.properties.models import Property

# Rental model used by the owner dashboard.
from apps.tenants.models import Rental

# Custom User model.
from .models import User

# Custom decorator that allows only OWNER users.
from apps.accounts.decorators import owner_required


# ============================================================
# USER REGISTRATION
# ============================================================

def register_view(request):
    """
    Creates a new HomeNest user account.

    Only OWNER and TENANT roles are allowed.
    """

    # Process the registration form.
    if request.method == "POST":

        # Get values submitted from the registration form.
        first_name = request.POST.get(
            "first_name",
            ""
        ).strip()

        last_name = request.POST.get(
            "last_name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        password = request.POST.get(
            "password",
            ""

        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        role = request.POST.get(
            "role",
            ""
        ).strip().upper()

        # ----------------------------------------------------
        # REQUIRED FIELD VALIDATION
        # ----------------------------------------------------

        if not all([
            first_name,
            last_name,
            email,
            password,
            confirm_password,
            role,
        ]):
            messages.error(
                request,
                "All fields are required.",
            )

            return redirect("register")

        # ----------------------------------------------------
        # ROLE VALIDATION
        # ----------------------------------------------------

        # HomeNest has only two application roles:
        # OWNER and TENANT.
        if role not in ["OWNER", "TENANT"]:
            messages.error(
                request,
                "Invalid role selected.",
            )

            return redirect("register")

        # ----------------------------------------------------
        # PASSWORD VALIDATION
        # ----------------------------------------------------

        if password != confirm_password:
            messages.error(
                request,
                "Passwords do not match.",
            )

            return redirect("register")

        # ----------------------------------------------------
        # DUPLICATE EMAIL CHECK
        # ----------------------------------------------------

        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "An account with this email already exists.",
            )

            return redirect("register")

        # ----------------------------------------------------
        # CREATE USER
        # ----------------------------------------------------

        # create_user() automatically hashes the password.
        #
        # We use the email as the username because the
        # current authentication flow authenticates using
        # username=email.
        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )

        # Tell the user that registration was successful.
        messages.success(
            request,
            "Account created successfully. Please login.",
        )

        return redirect("login")

    # Display registration page for GET requests.
    return render(
        request,
        "accounts/register.html",
    )


# ============================================================
# USER LOGIN
# ============================================================

def login_view(request):
    """
    Authenticates a HomeNest user.

    OWNER users are sent to the owner dashboard.
    TENANT users are sent to the tenant dashboard.
    """

    # Process login form.
    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        password = request.POST.get(
            "password",
            ""
        )

        # Authenticate using Django's authentication system.
        #
        # username=email works because registration stores
        # the user's email as the username.
        user = authenticate(
            request,
            username=email,
            password=password,
        )

        # Authentication successful.
        if user is not None:

            # Create the authenticated session.
            login(
                request,
                user,
            )

            # Redirect OWNER users.
            if user.role == "OWNER":
                return redirect(
                    "owner_dashboard"
                )

            # Redirect TENANT users.
            if user.role == "TENANT":
                return redirect(
                    "tenant_dashboard"
                )

            # Safety fallback if an unexpected role exists.
            logout(request)

            messages.error(
                request,
                "Invalid user role.",
            )

            return redirect("login")

        # Authentication failed.
        messages.error(
            request,
            "Invalid email or password.",
        )

        return redirect("login")

    # Display login page for GET requests.
    return render(
        request,
        "accounts/login.html",
    )


# ============================================================
# LOGOUT
# ============================================================

@login_required
def logout_view(request):
    """
    Logs the current user out of HomeNest.
    """

    # End the Django authentication session.
    logout(request)

    # Show confirmation message.
    messages.success(
        request,
        "You have been logged out successfully.",
    )

    return redirect("login")


# ============================================================
# OWNER DASHBOARD
# ============================================================

@owner_required
def owner_dashboard(request):
    """
    Displays statistics and properties belonging to
    the currently logged-in OWNER.
    """

    # Get the currently logged-in owner.
    owner = request.user

    # --------------------------------------------------------
    # PROPERTY STATISTICS
    # --------------------------------------------------------

    # Total number of properties owned by this user.
    total_properties = Property.objects.filter(
        owner=owner
    ).count()

    # Number of available properties.
    available_properties = Property.objects.filter(
        owner=owner,
        status="AVAILABLE",
    ).count()

    # Number of rented properties.
    rented_properties = Property.objects.filter(
        owner=owner,
        status="RENTED",
    ).count()

    # --------------------------------------------------------
    # RENTAL REQUEST STATISTICS
    # --------------------------------------------------------

    # Pending rental requests.
    pending_requests = Rental.objects.filter(
        property__owner=owner,
        status="PENDING",
    ).count()

    # Approved rental requests.
    approved_requests = Rental.objects.filter(
        property__owner=owner,
        status="APPROVED",
    ).count()

    # Rejected rental requests.
    rejected_requests = Rental.objects.filter(
        property__owner=owner,
        status="REJECTED",
    ).count()

    # --------------------------------------------------------
    # OWNER PROPERTIES
    # --------------------------------------------------------

    # Retrieve only properties belonging to this owner.
    #
    # prefetch_related("rental_requests") reduces additional
    # database queries when rental requests are accessed
    # from the dashboard template.
    properties = Property.objects.filter(
        owner=owner
    ).prefetch_related(
        "rental_requests"
    )

    # --------------------------------------------------------
    # TEMPLATE CONTEXT
    # --------------------------------------------------------

    context = {
        "total_properties": total_properties,
        "available_properties": available_properties,
        "rented_properties": rented_properties,
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "rejected_requests": rejected_requests,
        "properties": properties,
    }

    return render(
        request,
        "owner/dashboard.html",
        context,
    )

