"""
URL configuration for HomeNest.

This file connects the main project URLs
with the different Django applications.
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from apps.properties import views


# ============================================================
# MAIN URL PATTERNS
# ============================================================

urlpatterns = [

    # --------------------------------------------------------
    # HOME PAGE
    # --------------------------------------------------------

    path(
        "",
        views.home,
        name="home",
    ),


    # --------------------------------------------------------
    # DJANGO ADMIN
    # --------------------------------------------------------

    path(
        "admin/",
        admin.site.urls,
    ),


    # --------------------------------------------------------
    # ACCOUNTS
    # --------------------------------------------------------

    path(
        "accounts/",
        include("apps.accounts.urls"),
    ),


    # --------------------------------------------------------
    # PROPERTIES
    # --------------------------------------------------------

    path(
        "properties/",
        include("apps.properties.urls"),
    ),


    # --------------------------------------------------------
    # TENANTS
    # --------------------------------------------------------

    path(
        "tenants/",
        include("apps.tenants.urls"),
    ),
]


# ============================================================
# DEVELOPMENT MEDIA FILES
# ============================================================

# During development, Django serves uploaded media files
# from MEDIA_ROOT when DEBUG=True.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

