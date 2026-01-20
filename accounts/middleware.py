# from django.shortcuts import redirect
# from django.urls import reverse
#
#
# class RequireProfileMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         if request.user.is_authenticated:
#             if not hasattr(request.user, "scientist_profile"):
#                 allowed_paths = [
#                     reverse("profile-create"),
#                     reverse("logout"),
#                 ]
#                 if request.path not in allowed_paths:
#                     return redirect("profile-create")
#
#         return self.get_response(request)