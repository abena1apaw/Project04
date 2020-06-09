"""
Definition of views.
"""

from datetime import datetime
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpRequest
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.utils.encoding import force_text
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from .forms import RegisterForm
from .tokens import account_activation_token
from .forms import ContactForm


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title': 'Home Page',
            'year': datetime.now().year,
        }
    )


def activation_sent(request):
    return render(request, 'app/activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true
        user.is_active = True
        # set signup_confirmation true
        user.profile.signup_confirmation = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'app/activation_invalid.html')

#
# def contact(request):
#     """Renders the contact page."""
#     assert isinstance(request, HttpRequest)
#     return render(
#         request,
#         'app/contact.html',
#         {
#             'title': 'Contact Us',
#             'message': 'Let us know what you think',
#             'year': datetime.now().year,
#         }
#     )


def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title': 'About Paper Trader',
            'message': 'Application Description',
            'year': datetime.now().year,
        }
    )


def register_form(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.profile.email = form.cleaned_data.get('email')
            # user can't login until link confirmed
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            # load a template like get_template()
            # and calls its render() method immediately.
            message = render_to_string('app/activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
        return redirect('activation_sent')
    else:
        form = RegisterForm()
    return render(request, 'app/register_form.html', {'form': form})


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # send email code goes here
            sender_name = form.cleaned_data['name']
            sender_email = form.cleaned_data['email']

            message = "{0} has sent you a new message:\n\n{1}".format(sender_name, form.cleaned_data['message'])
            send_mail('New Enquiry', message, sender_email, ['akapaw@att.net'])

            return HttpResponse('Thanks for contacting us!')
    else:
        form = ContactForm()

    return render(request, 'app/contact.html', {'form': form})

