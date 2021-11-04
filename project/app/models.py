
# First-Party
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_fsm import FSMIntegerField
from hashid_field import HashidAutoField
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField

# Local
from .managers import UserManager


class Account(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    STATE = Choices(
        (0, 'new', 'New'),
    )
    state = FSMIntegerField(
        choices=STATE,
        default=STATE.new,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    address = models.CharField(
        max_length=512,
        blank=False,
        default='',
    )
    email = models.EmailField(
        blank=False,
    )
    phone = PhoneNumberField(
        blank=False,
    )
    ssn = models.CharField(
        max_length=100,
        blank=False,
    )
    is_diploma = models.BooleanField(
        default=False,
    )
    is_certificate = models.BooleanField(
        default=False,
    )
    is_criminal = models.BooleanField(
        default=False,
    )
    criminal_notes = models.TextField(
        blank=True,
    )
    is_offender = models.BooleanField(
        default=False,
    )
    is_wasd = models.BooleanField(
        default=False,
    )
    wasd_notes = models.TextField(
        blank=True,
    )
    schools = ArrayField(
        models.CharField(
            max_length=255,
        ),
        default=list,
        blank=True,
    )
    notes = models.TextField(
        max_length=2000,
        blank=True,
        default='',
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    user = models.OneToOneField(
        'app.User',
        on_delete=models.CASCADE,
        related_name='account',
        null=True,
        unique=True,
    )

    def __str__(self):
        return f"{self.name}"



class User(AbstractBaseUser):
    id = HashidAutoField(
        primary_key=True,
    )
    username = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        unique=True,
    )
    data = models.JSONField(
        null=True,
        editable=False,
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        default='(Unknown)',
        verbose_name="Name",
        editable=False,
    )
    email = models.EmailField(
        blank=False,
        editable=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_admin = models.BooleanField(
        default=False,
    )
    is_verified = models.BooleanField(
        default=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [
    ]

    objects = UserManager()

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return str(self.name)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
