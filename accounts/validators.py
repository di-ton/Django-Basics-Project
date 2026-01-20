import re
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

@deconstructible
class OrcidIdValidator:
    regex = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")

    def __call__(self, value):
        if not self.regex.match(value):
            raise ValidationError(
                "Invalid ORCID format. Expected format: 0000-0000-0000-000X"
            )


@deconstructible
class ScopusIDValidator:
    def __call__(self, value):
        if not value.isdigit():
            raise ValidationError(
                "Scopus ID must contain only digits."
            )

        if len(value) < 6:
            raise ValidationError(
                "Scopus ID appears to be too short."
            )