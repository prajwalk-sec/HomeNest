from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),


    path(
        "owner/dashboard/",
        views.owner_dashboard,
        name="owner_dashboard",
    ),

    path(
    "rental-requests/<int:rental_id>/approve/",
    views.approve_rental_request,
    name="approve_rental_request"
),

path(
    "rental-requests/<int:rental_id>/reject/",
    views.reject_rental_request,
    name="reject_rental_request"
),


]