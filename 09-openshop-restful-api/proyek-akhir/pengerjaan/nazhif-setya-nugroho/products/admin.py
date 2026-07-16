from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "shop", "price", "stock", "is_available", "is_delete")
    search_fields = ("name", "sku", "shop", "location", "category")
    list_filter = ("is_available", "is_delete", "category")
