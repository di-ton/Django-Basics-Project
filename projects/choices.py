from django.db import models


class ProjectStatusChoices(models.TextChoices):
    ONGOING = "ongoing", "Ongoing"
    COMPLETED = "completed", "Completed"
    PENDING = "pending", "Pending"
    CANCELLED = "cancelled", "Cancelled"


class JournalQuartileChoices(models.TextChoices):
    Q1 = "Q1", "Q1"
    Q2 = "Q2", "Q2"
    Q3 = "Q3", "Q3"
    Q4 = "Q4", "Q4"
    NA = "NA", "--"

class CategoryChoices(models.TextChoices):
    CHEM = "CHEM", "Chemical Sciences"
    PHYS = "PHYS", "Physical Sciences"
    ENG = "ENG", "Engineering and Technology"
    AGR = "AGR", "Agricultural and Veterinary Sciences"
    MED = "MED", "Medical and Health Sciences"
    MATH = "MATH", "Mathematics and Computer Science"
    BIO = "BIO", "Biological Sciences"
    EARTH = "EARTH", "Earth and Environmental Sciences"
    SOC = "SOC", "Social Sciences"
    HUM = "HUM", "Humanities and Arts"













