from django.contrib import admin
from django.urls import path
from sustainability.views import monitor_page, ajax_get_energy

urlpatterns = [
    path("admin/sustainability/monitor/", monitor_page, name="sustainability-monitor"),
    path("admin/sustainability/energy/", ajax_get_energy, name="sustainability-energy"),
    path("admin/", admin.site.urls),

]
