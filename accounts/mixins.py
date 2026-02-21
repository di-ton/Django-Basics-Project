from django.shortcuts import redirect


class ProfileRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        # OneToOne existence check
        if not request.user.scientist_profile:
            return redirect("profile-create")

        return super().dispatch(request, *args, **kwargs)