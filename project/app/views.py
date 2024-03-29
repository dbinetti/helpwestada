import csv
import datetime
import json
import logging

import jwt
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as log_in
from django.contrib.auth import logout as log_out
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import HttpResponse
# from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import AccountForm
from .forms import DeleteForm
from .models import Account
from .models import User
from .tasks import send_email

log = logging.getLogger(__name__)

# Root
def index(request):
    accounts = Account.objects.filter(
    ).order_by('-created')
    total = Account.objects.count()
    return render(
        request,
        'app/pages/index.html',
        {'accounts': accounts, 'total': total,},
    )

# Authentication
def login(request):
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    next_url = request.GET.get('next', '/account')
    state = f"{get_random_string()}|{next_url}"
    request.session['state'] = state
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'response_type': 'code',
        'scope': 'openid profile email',
        'state': state,
        'redirect_uri': redirect_uri,
        'screen_hint': 'signup',
    }
    url = requests.Request(
        'GET',
        f'https://{settings.AUTH0_DOMAIN}/authorize',
        params=params,
    ).prepare().url
    return redirect(url)


def callback(request):
    # Reject if state doesn't match
    browser_state = request.session.get('state')
    server_state = request.GET.get('state')
    if browser_state != server_state:
        del request.session['state']
        log.error('state mismatch')
        messages.error(
            request,
            "Sorry, there was a problem.  Please try again or contact support."
        )
        return redirect('index')
    next_url = server_state.partition('|')[2]
    # Get Auth0 Code
    code = request.GET.get('code', None)
    if not code:
        log.error('no code')
        return HttpResponse(status=400)
    token_url = f'https://{settings.AUTH0_DOMAIN}/oauth/token'
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    token_payload = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'client_secret': settings.AUTH0_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
    }
    token = requests.post(
        token_url,
        json=token_payload,
    ).json()
    payload = jwt.decode(
        token['id_token'],
        options={
            'verify_signature': False,
        }
    )
    payload['username'] = payload.pop('sub')
    if not 'email' in payload:
        log.error("no email")
        messages.error(
            request,
            "Email address is required.  Please try again.",
        )
        return redirect('index')
    user = authenticate(request, **payload)
    if user:
        log_in(request, user)
        # if not getattr(user, 'is_verified', None):
        #     return redirect('verify')
        # Always redirect first-time users to account page
        if (user.last_login - user.created) < datetime.timedelta(minutes=1):
            messages.success(
                request,
                "Welcome and thanks for helping West Ada!"
            )
            messages.warning(
                request,
                "Next, review the below and click 'Save'.  We will inform you when the program officially begins."
            )
            return redirect('account')
        # Otherwise, redirect to next_url, defaults to 'account'
        return redirect(next_url)
    log.error('callback fallout')
    return HttpResponse(status=403)

def logout(request):
    log_out(request)
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'return_to': request.build_absolute_uri(reverse('index')),
    }
    logout_url = requests.Request(
        'GET',
        f'https://{settings.AUTH0_DOMAIN}/v2/logout',
        params=params,
    ).prepare().url
    messages.success(
        request,
        "You Have Been Logged Out!",
    )
    return redirect(logout_url)

# Account
@login_required
def account(request):
    account = request.user.account
    if request.POST:
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            account = form.save()
            messages.success(
                request,
                "Saved!",
            )
            return redirect('thanks')
    else:
        form = AccountForm(instance=account)
    accounts = Account.objects.filter(
    ).order_by('-created')
    total = Account.objects.count()
    return render(
        request,
        'app/pages/account.html',
        context={
            'form': form,
            'accounts': accounts,
            'total': total,
        },
    )

# Delete
@login_required
def delete(request):
    if request.method == "POST":
        form = DeleteForm(request.POST)
        if form.is_valid():
            user = request.user
            user.delete()
            messages.error(
                request,
                "Account Deleted!",
            )
            return redirect('index')
    else:
        form = DeleteForm()
    return render(
        request,
        'app/pages/delete.html',
        {'form': form,},
    )
