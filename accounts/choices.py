from django.db import models

class AcademicDegreeChoices(models.TextChoices):
    PHD_STUDENT = "PHD_STUDENT", "PhD Student"
    PHD = "PHD", "PhD"
    DSC = "DSC", "DSc"


class AcademicPositionChoices(models.TextChoices):
    NONE = "NONE", "—"
    POSTDOC = "POSTDOC", "Postdoctoral Researcher"
    ASSISTANT_PROF = "ASSISTANT_PROF", "Assistant Professor"
    ASSOCIATE_PROF = "ASSOCIATE_PROF", "Associate Professor"
    PROFESSOR = "PROFESSOR", "Professor"

