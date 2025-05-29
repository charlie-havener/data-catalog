from django import forms
from django.contrib import admin

from .models import Columns, Objects, ObjectTypes, Owners, OwnerTypes, Relationships

""" -------------------------
Owner Types in admin
------------------------- """

admin.site.register(OwnerTypes)

""" -------------------------
Object Types in admin
------------------------- """

admin.site.register(ObjectTypes)


""" -------------------------
Objects in admin
------------------------- """

class ColumnsInline(admin.StackedInline):

    # make the description field a textarea
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ColumnsInline, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'description':
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield

    model = Columns
    extra = 3
    classes = ['collapse']
    fieldsets = [
        (None, {"fields": ["column_name", "data_type", "description"]}),
    ]


class OwnersInline(admin.TabularInline):
    model = Owners
    extra = 1
    classes = ['collapse']
    fieldsets = [
        (None, {"fields": ["owner_name", "owner_type"]})
    ]

class RelationshipsInline(admin.TabularInline):
    model = Relationships
    extra = 1
    classes = ['collapse']
    fk_name = 'parent'


class ObjectsAdmin(admin.ModelAdmin):

    # make the description field a textarea
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ObjectsAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'description':
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield

    fieldsets = [
        ("Object", {"fields": ["object_name", "description", "object_type", "md"]})
    ]

    inlines = [ColumnsInline, OwnersInline, RelationshipsInline]

    list_display = ["object_name", "object_type"]

admin.site.register(Objects, ObjectsAdmin)
