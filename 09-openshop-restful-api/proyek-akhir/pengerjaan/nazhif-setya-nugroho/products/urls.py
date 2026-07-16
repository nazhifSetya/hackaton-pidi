from django.urls import re_path

from .views import ProductDetailView, ProductListCreateView

urlpatterns = [
    # Trailing slash optional so both `/products` and `/products/`
    # (and `/products/{id}` / `/products/{id}/`) work without a redirect.
    re_path(r"^products/?$", ProductListCreateView.as_view()),
    re_path(r"^products/(?P<id>[^/]+)/?$", ProductDetailView.as_view()),
]
