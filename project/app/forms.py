# Django
from django import forms
from django.contrib.auth.forms import UserChangeForm as UserChangeFormBase
from django.contrib.auth.forms import UserCreationForm as UserCreationFormBase

# Local
from .models import Account
from .models import School
from .models import User


class DeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
    )


class AccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Required fields override
        # self.fields['address'].required = True

    class Meta:
        model = Account
        fields = [
            'name',
            'email',
            'phone',
            'address',
            'is_public',
            'notes',
        ]
        labels = {
            "is_public": "Make My Name Public",
        }
        widgets = {
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control h-25',
                    'placeholder': 'Anything else we should know? (Optional)',
                    'rows': 5,
                }
            ),
        }

        # help_texts = {
        #     'is_bilingual': "If you speak Spanish, please click here.",
        # }


    def clean(self):
        pass

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = [
            'name',
            'nces_id',
            'phone',
        ]


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
