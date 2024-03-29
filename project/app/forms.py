# Django
from django import forms
from django.contrib.auth.forms import UserChangeForm as UserChangeFormBase
from django.contrib.auth.forms import UserCreationForm as UserCreationFormBase

# Local
from .models import Account
from .models import User
from .widgets import AddressWidget


class DeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
    )


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'name',
            'email',
            'phone',
            'address',
            'ssn',
            'is_diploma',
            'is_certificate',
            'is_criminal',
            'criminal_notes',
            'is_offender',
            'is_wasd',
            'wasd_notes',
            'schools',
        ]
        labels = {
            "is_diploma": "Click if you have a High School Diploma or equivalent.",
            "is_certificate": "Click if you have an Idaho Teaching Certificate.",
            "is_criminal": "Click if you have ever been convicted of a criminal offense other than a minor traffic violation.",
            "is_offender": "Click if your name appears on any sex offender database in any state or country.",
            "is_wasd": "Click if you have ever worked for the West Ada School District.",
            "ssn": "Social Security Number",
        }
        widgets = {
            'criminal_notes': forms.Textarea(
                attrs={
                    'class': 'form-control h-25',
                    'placeholder': 'If you answered yes, explain giving dates.',
                    'rows': 5,
                }
            ),
            'wasd_notes': forms.Textarea(
                attrs={
                    'class': 'form-control h-25',
                    'placeholder': 'If you answered yes, state position, location, date left and reason for leaving.',
                    'rows': 5,
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control h-25',
                    'placeholder': 'Anything else we should know? (Optional)',
                    'rows': 5,
                }
            ),
            'address': AddressWidget(
                attrs={'style': "width: 600px;"}
            ),
        }

        help_texts = {
            'schools': "Enter your preferred schools, separated by commas.  If you are willing to substitute anywhere, please leave blank.",
            'ssn': "Your social security number will be required for background checks; again, this will not be shared without your express approval.",
            'address': "Your home address; again, this will not be shared without your express approval.",
        }


    def clean(self):
        pass

class UserCreationForm(UserCreationFormBase):
    """
    Custom user creation form for Auth0
    """

    # Bypass password requirement
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = [
            'username',
        ]


class UserChangeForm(UserChangeFormBase):
    """
    Custom user change form for Auth0
    """

    class Meta:
        model = User
        fields = [
            'username',
        ]
