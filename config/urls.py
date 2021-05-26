from django.conf import settings
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path("api/", include(("api.users.urls", "users"), namespace="users")),
    path("api/", include(("api.products.urls", "products"), namespace="products")),
    path("api/", include(("api.recipes.urls", "recipes"), namespace="recipes")),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
