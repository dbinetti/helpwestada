# Django
# First-Party
from address.forms import AddressWidget
from address.models import AddressField
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from reversion.admin import VersionAdmin

# Local
from .forms import UserChangeForm
from .forms import UserCreationForm
from .models import Account
from .models import School
from .models import User


@admin.register(Account)
class AccountAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'name',
        'address',
        'email',
        'phone',
        'is_public',
        'notes',
    ]
    list_display = [
        'name',
        'is_public',
        'user',
    ]
    list_editable = [
    ]
    list_filter = [
        'is_public',
    ]
    search_fields = [
        'name',
    ]
    autocomplete_fields = [
        'user',
    ]
    inlines = [
    ]
    ordering = [
        'created',
    ]
    readonly_fields = [
    ]
    formfield_overrides = {
        AddressField: {
            'widget': AddressWidget(
                attrs={
                    'style': 'width: 300px;'
                }
            )
        }
    }


@admin.register(School)
class SchoolAdmin(VersionAdmin):
    fields = [
        'name',
        'kind',
        'level',
        'nces_id',
        'address',
        'phone',
        'website',
    ]
    list_display = [
        'name',
        'level',
        'nces_id',
        'address',
        'phone',
        'website',
        'created',
        'updated',
    ]
    list_filter = [
        'level',
    ]
    search_fields = [
        'name',
        'nces_id',
    ]
    inlines = [
    ]
    autocomplete_fields = [
    ]



@admin.register(User)
class UserAdmin(UserAdminBase):
    save_on_top = True
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    fieldsets = (
        (None, {
            'fields': [
                'username',
            ]
        }
        ),
        ('Data', {
            'fields': [
                'name',
                'email',
            ]
        }
        ),
        ('Permissions', {'fields': ('is_admin', 'is_active')}),
    )
    list_display = [
        # 'username',
        'name',
        'email',
        'created',
        'last_login'
    ]
    list_filter = [
        'is_active',
        'is_admin',
        'created',
        'last_login',
    ]
    search_fields = [
        'username',
        'name',
        'email',
    ]
    ordering = [
        '-created',
    ]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': [
                'username',
                'is_admin',
                'is_active',
            ]
        }
        ),
    )
    filter_horizontal = ()
    inlines = [
    ]
    readonly_fields = [
        'name',
        'email',
    ]
# Use Auth0 for login
admin.site.login = staff_member_required(
    admin.site.login,
    login_url=settings.LOGIN_URL,
)
