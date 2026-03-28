from django.shortcuts import redirect
from django.urls import reverse


# class ProfileRequiredMixin:
#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return redirect("login")
#
#         # OneToOne existence check
#         if not request.user.scientist_profile:
#             return redirect("profile-create")
#
#         return super().dispatch(request, *args, **kwargs)


class ProfileRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect("login")

        # If user has NO profile -> force profile creation
        if not hasattr(user, 'scientist_profile'):
            allowed_url = reverse("profile-create")

            # only 'profile-create' is allowed
            if request.path != allowed_url:
                return redirect("profile-create")

        return super().dispatch(request, *args, **kwargs)
