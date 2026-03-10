from django import forms
from django.contrib.auth import get_user_model

from .models import Message

User = get_user_model()


class ProjectMessageForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Message
        fields = ["recipients", "subject", "body"]
        labels = {
            "body": "Content",
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)

        if project:
            users = [
                m.scientist.user
                for m in project.memberships.select_related("scientist__user")
                if m.scientist and m.scientist.user
            ]

            self.fields["recipients"].queryset = User.objects.filter(
                id__in=[u.id for u in users]
            )

            self.fields["recipients"].label_from_instance = lambda user: (
                user.scientist_profile.full_name
                if hasattr(user, "scientist_profile")
                else user.email
            )