
from django.contrib import admin
from django.urls import path,include
import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("tickets.urls", namespace="tickets")),
    path("account/", include("account.urls", namespace="account")),
    path("employee/", include("employee.urls", namespace="employee")),
    # path("expenses/", include("expenses.urls", namespace="expenses")),
    path("dailyexpense/", include("dailyexpense.urls", namespace="dailyexpense")),
    path("vehicle/", include("vehicle.urls", namespace="vehicle")),
    path("generator/", include("generator.urls", namespace="generator")),
    path("common/", include("common.urls", namespace="common")),
    path("disaster/", include("disaster.urls", namespace="disaster")),
    path("adhocman/", include("adhocman.urls", namespace="adhocman")),
]



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
