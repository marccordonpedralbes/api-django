"""Add circle mixin abstract."""

# Django REST Framework
from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404

# Models


# Utils


# class AddChatMixin(viewsets.GenericViewSet):
#     """Add circle mixin

#     Manages adding a circle object to views
#     that require it.
#     """

#     def dispatch(self, request, *args, **kwargs):
#         """Return the normal dispatch but adds the circle model."""

#         id = self.kwargs["slug_id"]

#         self.chat = get_object_or_404(Chat, id=id)

#         return super(AddChatMixin, self).dispatch(request, *args, **kwargs)


# class AddOrderMixin(viewsets.GenericViewSet):
#     """Add circle mixin

#     Manages adding a circle object to views
#     that require it.
#     """

#     def dispatch(self, request, *args, **kwargs):
#         """Return the normal dispatch but adds the circle model."""
#         try:
#             id = self.kwargs["order_id"]

#             self.order = get_object_or_404(Order, id=id)
#         except:
#             pass
#         return super(AddOrderMixin, self).dispatch(request, *args, **kwargs)
