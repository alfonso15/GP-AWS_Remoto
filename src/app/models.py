from django.db import models
from django.utils.text import slugify
from .utils import generate_random_slug


class RandomSlugModel(models.Model):
    """
        Abstract Class with auto-generated random slug
    """
    SLUG_LENGTH = 8
    random_slug = models.SlugField(editable=False, primary_key=True)

    def save(self, *args, **kwargs):
        if not self.random_slug:
            self.random_slug = generate_random_slug(model=self._meta.model,
                                                    size=self.SLUG_LENGTH)
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """
        Abstract Class with create and update dates
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class SlugModel(models.Model):
    """
        Abstract Class with slugified field
    """
    slug = models.CharField(max_length=256, unique=True)
    SLUG_FIELD = ''

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.slug = slugify(getattr(self, self.SLUG_FIELD))
        return super().save(*args, **kwargs)
