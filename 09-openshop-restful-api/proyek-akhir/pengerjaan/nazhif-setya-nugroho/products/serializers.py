from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serialize a Product, including HATEOAS `_links`.

    All writable fields are required (except `is_delete`) so that a request
    missing any of them fails `is_valid()` and returns HTTP 400.
    """

    _links = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "shop",
            "price",
            "sku",
            "description",
            "location",
            "discount",
            "category",
            "stock",
            "is_available",
            "picture",
            "is_delete",
            "_links",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "name": {"required": True, "allow_blank": False},
            "sku": {"required": True, "allow_blank": False},
            "description": {"required": True, "allow_blank": False},
            "shop": {"required": True, "allow_blank": False},
            "location": {"required": True, "allow_blank": False},
            "price": {"required": True},
            "discount": {"required": True},
            "category": {"required": True, "allow_blank": False},
            "stock": {"required": True},
            "is_available": {"required": True},
            "picture": {"required": True, "allow_blank": False},
            "is_delete": {"required": False, "default": False},
        }

    def get__links(self, obj):
        request = self.context.get("request")

        def uri(path):
            return request.build_absolute_uri(path) if request else path

        detail = f"/products/{obj.id}/"
        return [
            {
                "rel": "self",
                "href": uri("/products"),
                "action": "POST",
                "types": ["application/json"],
            },
            {
                "rel": "self",
                "href": uri(detail),
                "action": "GET",
                "types": ["application/json"],
            },
            {
                "rel": "self",
                "href": uri(detail),
                "action": "PUT",
                "types": ["application/json"],
            },
            {
                "rel": "self",
                "href": uri(detail),
                "action": "DELETE",
                "types": ["application/json"],
            },
        ]
