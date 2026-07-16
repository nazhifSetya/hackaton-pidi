from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product
from .serializers import ProductSerializer


class ProductListCreateView(APIView):
    """GET /products (list + search) and POST /products (create)."""

    def get(self, request):
        queryset = Product.objects.filter(is_delete=False)

        name = request.query_params.get("name")
        if name is not None:
            queryset = queryset.filter(name__icontains=name)

        location = request.query_params.get("location")
        if location is not None:
            queryset = queryset.filter(location__icontains=location)

        serializer = ProductSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response({"products": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailView(APIView):
    """GET / PUT / DELETE /products/{id}."""

    def get_object(self, id):
        try:
            # No is_delete filter: soft-deleted products remain reachable here.
            return Product.objects.get(id=id)
        except (Product.DoesNotExist, DjangoValidationError, ValueError):
            raise NotFound()

    def get(self, request, id):
        product = self.get_object(id)
        serializer = ProductSerializer(product, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        product = self.get_object(id)
        serializer = ProductSerializer(
            product, data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        product = self.get_object(id)
        product.is_delete = True
        product.save(update_fields=["is_delete", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
