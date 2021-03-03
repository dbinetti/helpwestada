# Standard Libary
import csv

import geocoder
import requests
# First-Party
from auth0.v3.authentication import GetToken
from auth0.v3.exceptions import Auth0Error
from auth0.v3.management import Auth0
# Django
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django_rq import job

from .forms import SchoolForm
from .models import Account
from .models import User


# Auth0
def get_auth0_token():
    get_token = GetToken(settings.AUTH0_TENANT)
    token = get_token.client_credentials(
        settings.AUTH0_CLIENT_ID,
        settings.AUTH0_CLIENT_SECRET,
        f'https://{settings.AUTH0_TENANT}/api/v2/',
    )
    return token

def get_auth0_client():
    token = get_auth0_token()
    client = Auth0(
        settings.AUTH0_TENANT,
        token['access_token'],
    )
    return client

def get_user_data(user_id):
    client = get_auth0_client()
    data = client.users.get(user_id)
    return data

def put_auth0_payload(endpoint, payload):
    token = get_auth0_token()
    access_token = token['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.put(
        f'https://{settings.AUTH0_TENANT}/api/v2/{endpoint}',
        headers=headers,
        json=payload,
    )
    return response

@job
def update_auth0(user):
    if not user.username.startswith('auth0|'):
        return
    client = get_auth0_client()
    payload = {
        'name': user.name,
    }
    response = client.users.update(user.username, payload)
    return response

@job
def update_user_from_account(account):
    user = account.user
    if not user.username.startswith('auth0|'):
        return
    user.name = account.name
    user.save()
    return user

@job
def create_auth0_user(name, email):
    client = get_auth0_client()
    password = get_random_string()
    data = {
        'connection': 'Username-Password-Authentication',
        'name': name,
        'email': email,
        'password': password,
    }
    try:
        response = client.users.create(
            data,
        )
    except Auth0Error:
        return
    default = {
        'name': name,
        'email': email,
    }
    user, created= User.objects.update_or_create(
        username=response['user_id'],
        default=default,
    )
    return

@job
def update_user(user):
    data = get_user_data(user.username)
    user.data = data
    user.name = data.get('name', '')
    user.picture = data.get('picture', '')
    user.first_name = data.get('given_name', '')
    user.last_name = data.get('family_name', '')
    user.email = data.get('email', None)
    user.phone = data.get('phone_number', None)
    user.save()
    return user


@job
def delete_user(user_id):
    client = get_auth0_client()
    response = client.users.delete(user_id)
    return response

# User
def create_account(user):
    account = Account.objects.create(
        user=user,
        name=user.name,
        email=user.email,
    )
    return account


# Utility
def build_email(template, subject, from_email, context=None, to=[], cc=[], bcc=[], attachments=[], html_content=None):
    body = render_to_string(template, context)
    if html_content:
        html_rendered = render_to_string(html_content, context)
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email,
        to=to,
        cc=cc,
        bcc=bcc,
    )
    if html_content:
        email.attach_alternative(html_rendered, "text/html")
    for attachment in attachments:
        with attachment[1].open() as f:
            email.attach(attachment[0], f.read(), attachment[2])
    return email

@job
def send_email(email):
    return email.send()


@job
def send_confirmation(user):
    email = build_email(
        template='app/emails/confirmation.txt',
        subject='Welcome to Help West Ada!',
        from_email='David Binetti <dbinetti@helpwestada.com>',
        context={'user': user},
        to=[user.email],
    )
    return email.send()

@job
def account_outreach(account):
    email = build_email(
        template='app/emails/outreach.txt',
        subject='Help West Ada - Final Request',
        from_email='David Binetti <dbinetti@helpwestada.com>',
        to=[account.user.email],
    )
    return email.send()

@job
def delete_user_email(email_address):
    email = build_email(
        template='app/emails/delete.txt',
        subject='Help West Ada - Account Deleted',
        from_email='David Binetti <dbinetti@helpwestada.com>',
        to=[email_address],
    )
    return email.send()

def schools_list(filename='wasd.csv'):
    with open(filename) as f:
        reader = csv.reader(
            f,
            skipinitialspace=True,
        )
        next(reader)
        rows = [row for row in reader]
        t = len(rows)
        i = 0
        errors = []
        output = []
        level = {
            'Elementary': 100,
            'Middle': 200,
            'High': 300,
        }
        for row in rows:
            i += 1
            print(f"{i}/{t}")
            school = {
                'name': str(row[0]).strip().title(),
                'nces_school_id': int(row[5]),
                'phone': str(row[19]),
                'website': str(row[6].replace(" ", "")) if row[6] !='†' else '',
                'level': level[str(row[32])],
            }
            form = SchoolForm(school)
            if not form.is_valid():
                errors.append((row, form))
            output.append(school)
        if not errors:
            return output
        else:
            print('Error!')
            return errors

# def geocode_address(raw):
#     result = geocoder.google(raw)
#     if not result.ok:
#         raise Exception
#     value = result.json
#     mapping = {
#         'raw': value.get('raw', ''),
#         'street_number': value.get('housenumber', ''),
#         'route': value.get('street', ''),
#         'locality': value.get('city', ''),
#         'postal_code': value.get('postal', ''),
#         'state_code': value.get('state', ''),
#         'country_code': value.get('country', ''),
#         'latitude': value.get('lat', ''),
#         'longitude': value.get('lng', ''),
#     }
# dict_keys(['accuracy', 'address', 'bbox', 'city', 'confidence', 'country', 'county', 'housenumber', 'lat', 'lng', 'ok', 'place', 'postal', 'quality', 'raw', 'state', 'status', 'street'])
# {'street_number': '912',
#  'route': 'East Covey Run Court',
#  'raw': '912 East Covey Run Court, Eagle, ID, USA',
#  'formatted': '912 E Covey Run Ct, Eagle, ID 83616, USA',
#  'latitude': 43.7110071,
#  'longitude': -116.3427846,
#  'locality': 'Eagle',
#  'postal_code': '83616',
#  'state': 'Idaho',
#  'state_code': 'ID',
#  'country': 'United States',
#  'country_code': 'US'}

# In [20]: raw
# Out[20]:
# {'address_components': [{'long_name': '912',
#    'short_name': '912',
#    'types': ['street_number']},
#   {'long_name': 'East Covey Run Court',
#    'short_name': 'E Covey Run Ct',
#    'types': ['route']},
#   {'long_name': 'Eagle',
#    'short_name': 'Eagle',
#    'types': ['locality', 'political']},
#   {'long_name': 'Ada County',
#    'short_name': 'Ada County',
#    'types': ['administrative_area_level_2', 'political']},
#   {'long_name': 'Idaho',
#    'short_name': 'ID',
#    'types': ['administrative_area_level_1', 'political']},
#   {'long_name': 'United States',
#    'short_name': 'US',
#    'types': ['country', 'political']},
#   {'long_name': '83616', 'short_name': '83616', 'types': ['postal_code']},
#   {'long_name': '4197',
#    'short_name': '4197',
#    'types': ['postal_code_suffix']}],
#  'formatted_address': '912 E Covey Run Ct, Eagle, ID 83616, USA',
#  'geometry': {'bounds': {'northeast': {'lat': 43.7111357, 'lng': -116.3425882},
#    'southwest': {'lat': 43.7109158, 'lng': -116.3429569}},
#   'location': {'lat': 43.7110071, 'lng': -116.3427845},
#   'location_type': 'ROOFTOP',
#   'viewport': {'northeast': {'lat': 43.71237473029149,
#     'lng': -116.3414235697085},
#    'southwest': {'lat': 43.70967676970849, 'lng': -116.3441215302915}}},
#  'place_id': 'ChIJO3a6u3YAr1QRfGGPw6f6iyw',
#  'types': ['premise'],
#  'street_number': {'long_name': '912', 'short_name': '912'},
#  'route': {'long_name': 'East Covey Run Court',
#   'short_name': 'E Covey Run Ct'},
#  'locality': {'long_name': 'Eagle', 'short_name': 'Eagle'},
#  'political': {'long_name': 'United States', 'short_name': 'US'},
#  'administrative_area_level_2': {'long_name': 'Ada County',
#   'short_name': 'Ada County'},
#  'administrative_area_level_1': {'long_name': 'Idaho', 'short_name': 'ID'},
#  'country': {'long_name': 'United States', 'short_name': 'US'},
#  'postal_code': {'long_name': '83616', 'short_name': '83616'},
#  'postal_code_suffix': {'long_name': '4197', 'short_name': '4197'}}

# In [21]: raw.keys()
# Out[21]: dict_keys(['address_components', 'formatted_address', 'geometry', 'place_id', 'types', 'street_number', 'route', 'locality', 'political', 'administrative_area_level_2', 'administrative_area_level_1', 'country', 'postal_code', 'postal_code_suffix'])


#     return mapping
