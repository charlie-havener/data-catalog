from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Site Administration"
admin.site.site_title = "Catalog"
admin.site.index_title = "Admin"

urlpatterns = [
    path("", include("home.urls")),
    path("home/", include("home.urls")),
    path("catalog/", include("catalog.urls")),
    path('admin/', admin.site.urls),
]
