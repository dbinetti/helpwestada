
# First-Party
from address.models import AddressField
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from hashid_field import HashidAutoField
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField

# Local
from .managers import UserManager


class Account(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    address = AddressField(
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    email = models.EmailField(
        blank=False,
    )
    phone = PhoneNumberField(
        blank=False,
    )
    is_public = models.BooleanField(
        default=False,
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

    # is_bilingual = models.BooleanField(
    #     default=False,
    # )
    # is_credential = models.BooleanField(
    #     default=False,
    # )
    # is_clear = models.BooleanField(
    #     default=False,
    # )
    # is_agree = models.BooleanField(
    #     default=False,
    # )


class School(models.Model):
    LEVEL = Choices(
        (100, 'elementary', 'Elementary'),
        (200, 'middle', 'Middle'),
        (300, 'high', 'High'),
    )
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=255,
        blank=False,
    )
    level = models.IntegerField(
        blank=True,
        null=True,
        choices=LEVEL,
    )
    nces_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
    )
    address = AddressField(
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    phone = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    website = models.URLField(
        blank=True,
        default='',
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    # search_vector = SearchVectorField(
    #     null=True,
    # )

    def __str__(self):
        return f"{self.name}"

    # class Meta:
    #     indexes = [
    #         GinIndex(fields=['search_vector'])
    #     ]


class Position(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    description = models.TextField(
        max_length=2000,
        blank=True,
        default='',
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


class Member(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    school = models.ForeignKey(
        'app.School',
        on_delete=models.CASCADE,
        related_name='members',
    )
    account = models.ForeignKey(
        'app.Account',
        on_delete=models.CASCADE,
        related_name='members',
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )


class Assignment(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    position = models.ForeignKey(
        'app.Position',
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    account = models.ForeignKey(
        'app.Account',
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )


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
        blank=True,
        null=True,
        editable=False,
    )
    picture = models.URLField(
        max_length=512,
        blank=True,
        default='https://www.helpwestada.com/static/app/unknown_small.png',
        verbose_name="Picture",
        editable=False,
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_admin = models.BooleanField(
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
