from django.urls import path

from . import views

app_name = "catalog"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:object_id>/", views.detail, name="detail"),
    path("api/lineage/", views.lineage, name="lineage"),
]
