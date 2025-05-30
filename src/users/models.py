from uuid import uuid4
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from app.models import RandomSlugModel, TimeStampedModel
from .managers import UserManager


class Company(RandomSlugModel):
    """
        Company Data
    """
    customer_number = models.IntegerField()
    company_name = models.CharField(max_length=128)
    logo = models.ImageField(null=True, blank=True, upload_to='companies')
    
    def __str__(self):
        return self.company_name

    class Meta:
        ordering = ["company_name", ]


class User(AbstractBaseUser, PermissionsMixin):
    """
        User Model
    """
    company = models.ForeignKey('users.Company', on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    
    staff_companies = models.ManyToManyField('users.Company', blank=True, related_name='staff_companies',
                                             help_text='Compañías a las que puede acceder el usuario.')
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now, editable=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Token(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=20)
