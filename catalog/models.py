from django.db import models
from django.db.models import UniqueConstraint, CheckConstraint, F
from django.core.exceptions import ValidationError


class ObjectTypes(models.Model):
    type_name = models.CharField("name", max_length=50, unique=True)

    class Meta:
        verbose_name = "Object Types"
        verbose_name_plural = "Object Types"

    def __str__(self):
        return self.type_name


class Objects(models.Model):
    object_type = models.ForeignKey(ObjectTypes, on_delete=models.CASCADE)
    object_name = models.CharField("name", max_length=200)
    description = models.CharField(max_length=2000, null=True, blank=True)

    # ensure that the type + name combo is unique
    class Meta:
        verbose_name = "Objects"
        verbose_name_plural = "Objects"
        constraints = [
            UniqueConstraint(
                fields=["object_type", "object_name"],
                name="unique_object"
            )
        ]

    def __str__(self):
        return self.object_name

    def __repr__(self):
        return f"{self.object_name} ({self.object_type})"


class Columns(models.Model):
    parent = models.ForeignKey(Objects, on_delete=models.CASCADE)
    column_name = models.CharField("name", max_length=50)
    description = models.CharField(max_length=500, null=True, blank=True)
    data_type = models.CharField("type", max_length=50)

    class Meta:
        verbose_name = "Columns"
        verbose_name_plural = "Columns"
        constraints = [
            UniqueConstraint(
                fields=["parent", "column_name"],
                name="unique_object_column_names"
            )
        ]

    def __str__(self):
        return self.column_name


class Relationships(models.Model):
    parent = models.ForeignKey(
        Objects,
        on_delete=models.CASCADE,
        related_name='children'
    )
    child = models.ForeignKey(
        Objects,
        on_delete=models.CASCADE,
        related_name='parents'
    )

    class Meta:
        verbose_name = "Relationships"
        verbose_name_plural = "Relationships"
        constraints = [
            # the relationships must be unique
            UniqueConstraint(
                fields=['parent', 'child'],
                name="unique_relationship"
            ),
            # no self referential object
            CheckConstraint(
                check=~models.Q(parent=F('child')),
                name='parent_not_child'
            )
        ]

    def clean(self):
        if self.parent == self.child:
            raise ValidationError("an object cannot be a child of itself.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parent} -> {self.child}"


class OwnerTypes(models.Model):
    type_name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Owner Types"
        verbose_name_plural = "Owner Types"

    def __str__(self):
        return self.type_name


class Owners(models.Model):
    assigned_object = models.ForeignKey(Objects, on_delete=models.CASCADE, related_name="owned_objects")
    owner_type = models.ForeignKey(OwnerTypes, on_delete=models.CASCADE)
    owner_name = models.CharField("name", max_length=50)

    class Meta:
        verbose_name = "Owners"
        verbose_name_plural = "Owners"

    def __str__(self):
        return self.owner_name

    def __repr__(self):
        return f"{self.owner_name} ({self.owner_type})"
