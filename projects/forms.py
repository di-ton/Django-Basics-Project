from django import forms

from projects.models import ScientificEvent



class ScientificEventForm(forms.ModelForm):
    class Meta:
        model = ScientificEvent
        fields = "__all__"
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")

        if start and end and end < start:
            raise forms.ValidationError(
                "End date cannot be earlier than start date."
            )
        return cleaned