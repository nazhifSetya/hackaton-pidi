import uuid

from django.db import models


class Product(models.Model):
    """A product listed on the OpenShop platform."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    description = models.TextField()
    shop = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.IntegerField()
    discount = models.IntegerField(default=0)
    category = models.CharField(max_length=255)
    stock = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    picture = models.TextField()
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
