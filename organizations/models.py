from django.db import models
from django.utils.text import slugify


class ScientificOrganization(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if self.website and not self.website.startswith(("http://", "https://")):
            self.website = "https://" + self.website

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

