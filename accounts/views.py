# -*- encoding: utf-8 -*-
############################################################################################
#
#    Zoook e-sale for OpenERP, Open Source Management Solution	
#    Copyright (C) 2011 Zikzakmedia S.L. (<http://www.zikzakmedia.com>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################################

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.core.validators import email_re

from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login

from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login

from django.core.mail import EmailMessage

from recaptcha.client import captcha

from accounts.models import *
from base.models import *

from settings import *
from tools.conn import connection, xmlrpc

import xmlrpclib

def is_valid_email(email):
    """Email validation"""

    return True if email_re.match(email) else False

def login(request):
    """Login Page and authenticate. If exists session, redirect profile"""

    if request.user.is_authenticated(): #redirect profile
        return HttpResponseRedirect("/accounts/profile/")

    title = _('Login')
    metadescription = _('Account frontpage of %(site)s') % {'site':SITE_TITLE}

    if 'username' in request.POST and 'password1' in request.POST:
        username = request.POST['username']
        password = request.POST['password1']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return HttpResponseRedirect("/accounts/profile/")
            else:
                error = _('Sorry. Your user is not active.')
        else:
            error = _('Sorry. Your username or password is not valid.')

    form = UserCreationForm()
    return render_to_response("accounts/login.html", locals(), context_instance=RequestContext(request))

def register(request):
    """Registration page. If exists session, redirect profile"""

    if request.user.is_authenticated(): #redirect profile
        return HttpResponseRedirect("/accounts/profile/")

    title = _('Create an Account')
    metadescription = _('Create an Account of %(site)s') % {'site':SITE_TITLE}

    if request.method == "POST":
        error = []
        users = ''
        emails = ''

        form = UserCreationForm(request.POST)
        data = request.POST.copy()

        username = data['username']
        email = data['email']
        password = data['password1']

        if data['password1'] == data['password2']:
            if form.is_valid():
                if len(username) < USER_LENGHT:
                    msg = _('Username is short. Minimum %(size)s characters') % {'size': USER_LENGHT}
                    error.append(msg)
                if len(password) < KEY_LENGHT:
                    msg = _('Password is short. Minimum %(size)s characters') % {'size': KEY_LENGHT}
                    error.append(msg)

                if is_valid_email(email):
                    # check if user not exist
                    users = User.objects.filter(username__exact=username)
                    emails = User.objects.filter(email__exact=email)
                else:
                    msg = _('Sorry. This email is not valid. Try again')
                    error.append(msg)

                check_captcha = captcha.submit(request.POST['recaptcha_challenge_field'], request.POST['recaptcha_response_field'], RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR'])
                if check_captcha.is_valid is False: # captcha not valid
                    msg = _('Error with captcha number. Copy same number.')
                    error.append(msg)

                if users:
                    msg = _('Sorry. This user are exists. Use another username')
                    error.append(msg)
                if emails:
                    msg = _('Sorry. This email are exists. Use another email or remember password')
                    error.append(msg)

                if not error:
                    # create user
                    user = User.objects.create_user(username, email, password)
                    user.is_staff = False
                    user.save()
                    # send email
                    subject = _('New user added - %(name)s') % {'name':SITE_TITLE}
                    body = _("This is email automatically from %(site)s\n\nUsername: %(username)s\nPassword: %(password)s\n\n%(live_url)s\n\nPlease, don't answer this email") % {'site':SITE_TITLE,'username':username,'password':password,'live_url':LIVE_URL}
                    email = EmailMessage(subject, body, to=[email])
                    email.send()
                    # authentification / login user
                    user = authenticate(username=username, password=password)
                    auth_login(request, user)
                    return HttpResponseRedirect("/accounts/profile/")
            else:
                msg = _("Sorry. Error form values. Try again")
                error.append(msg)
        else:
            msg = _("Sorry. Passwords don't match. Try again")
            error.append(msg)

    form = UserCreationForm()
    html_captcha = captcha.displayhtml(RECAPTCHA_PUB_KEY)

    return render_to_response("accounts/register.html", locals(), context_instance=RequestContext(request))

def remember(request):
    """Remember password"""

    error = []

    title = _('Remember')
    metadescription = _('Remember account of %(site)s') % {'site':SITE_TITLE}

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        data = request.POST.copy()

        email = data['email']

        check_captcha = captcha.submit(request.POST['recaptcha_challenge_field'], request.POST['recaptcha_response_field'], RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR'])
        if check_captcha.is_valid is False: # captcha not valid
            msg = _('Error with captcha number. Copy same number.')
            error.append(msg)
        else:
            if is_valid_email(email):
                # check if user  exist
                users = User.objects.filter(email__exact=email)
                if len(users) > 0:
                    #create new password
                    key = User.objects.make_random_password(length=KEY_LENGHT)
                    # update password
                    user = User.objects.get(id=users[0].id)
                    user.set_password(key)
                    user.save()
                    # send email
                    subject = _('Remember username - %(name)s') % {'name':SITE_TITLE}
                    body = _("This is email automatically from %(site)s\n\nUsername: %(username)s\nPassword: %(password)s\n\n%(live_url)s\n\nPlease, don't answer this email") % {'site':SITE_TITLE,'username':user.username,'password':key,'live_url':LIVE_URL}
                    email = EmailMessage(subject, body, to=[user.email])
                    email.send()
                    email = ''
                    msg = _('A new password are you send it to %(email)s') % {'email':user.email}
                    error.append(msg)
                else:
                    msg = _('Sorry. This email not exist. Try again')
                    error.append(msg)
            else:
                msg = _('Sorry. This email is not valid. Try again')
                error.append(msg)

    form = UserCreationForm()
    html_captcha = captcha.displayhtml(RECAPTCHA_PUB_KEY)

    return render_to_response("accounts/remember.html", locals(), context_instance=RequestContext(request))

@login_required
def profile(request):
    """Profile page"""

    full_name = request.user.get_full_name()
    if not full_name:
        full_name = request.user

    title = _('Profile %(full_name)s') % {'full_name':full_name}
    metadescription = _('Account frontpage of %(site)s') % {'site':SITE_TITLE}

    #saas module

    return render_to_response("accounts/profile.html", locals(), context_instance=RequestContext(request))

@login_required
def changepassword(request):
    """Change Password page"""

    title = _('Change password')
    metadescription = _('Change password of %(site)s') % {'site':SITE_TITLE}

    if request.method == "POST":
        error = ''

        form = UserCreationForm(request.POST)
        data = request.POST.copy()

        if data['password1'] == data['password2']:
            if len(data['password1']) >= KEY_LENGHT:
                # update password
                request.user.set_password(data['password1'])
                request.user.save()
                if request.user.email:
                    # send email
                    subject = _('New password added - %(name)s') % {'name':SITE_TITLE}
                    body = _("This is email automatically from %(site)s\n\nNew password: %(password)s\n\n%(live_url)s\n\nPlease, don't answer this email") % {'site':SITE_TITLE,'password':data['password1'],'live_url':LIVE_URL}
                    email = EmailMessage(subject, body, to=[request.user.email])
                    email.send()
                error = _("New password added")
            else:
                error = _("Sorry. Passwords need %(size)s characters or more. Try again") % {'size':KEY_LENGHT}
        else:
            error = _("Sorry. Passwords don't match. Try again")

    form = UserCreationForm()
    return render_to_response("accounts/changepassword.html", locals(), context_instance=RequestContext(request))

@login_required
def partner(request):
    """Partner page"""

    # OERP Connection
    o = connection()
    uid = xmlrpc()

    if not o or not uid:
        error = _('Error connecting with our ERP. Try again or cantact us')
        return render_to_response("accounts/error.html", locals(), context_instance=RequestContext(request))

    user_id = request.user.id

    partner = Partner.objects.filter(user=user_id)
    if partner:
        partner = Partner.objects.get(user=user_id)

    title = _('Partner Profile')
    metadescription = _('Partner profile of %(site)s') % {'site':SITE_TITLE}

    vat_code = VAT_CODE

    country_default = COUNTRY_DEFAULT

#    countries = o.ResCountry.all()
    countries =  Country.objects.all().order_by('name')
    countries = countries.filter(status=True)

    #form send
    if request.method == 'POST':
        form = PartnerForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            addr_name = form.cleaned_data['addr_name']
            addr_street = form.cleaned_data['addr_street']
            addr_zip = form.cleaned_data['addr_zip']
            addr_city = form.cleaned_data['addr_city']
            addr_addr_country_id = form.cleaned_data['addr_country_id']
            addr_email = form.cleaned_data['addr_email']
            addr_phone = form.cleaned_data['addr_phone']

            #TODO: save_all() Last OOOP commit have bug and we don't use save_all()
            #check if this vat exists
            vat = form.cleaned_data['vat_code']+form.cleaned_data['vat']
            server_object = '%s:%s/xmlrpc/object' % (OOOP_CONF['uri'],OOOP_CONF['port'])
            sock = xmlrpclib.ServerProxy(server_object)
            check_vat = sock.execute(OOOP_CONF['dbname'], uid, OOOP_CONF['password'], 'res.partner', 'dj_check_vat', vat)

            if not check_vat:
                message = _('Vat not valid. Check if vat is correct')
                return render_to_response("accounts/partner.html", locals(), context_instance=RequestContext(request))
            #partner
            if not partner:
                n = o.ResPartner.new()
                n.name = name
                n.vat = vat
                n.dj_username = request.user.username
                n.dj_email = request.user.email
                partner_id = n.save()

                partner_oerp = o.ResPartner.get(partner_id)
                addr = o.ResPartnerAddress.new()
                addr.partner_id = partner_oerp
            else:
                partner_oerp = o.ResPartner.get(partner.partner_id)
                addr = o.ResPartnerAddress.get(partner.address_id)

            #address
            addr.name = addr_name
            addr.street = addr_street
            addr.zip = addr_zip
            addr.city = addr_city
            #        addr.country_id = addr_addr_country_id
            addr.email = addr_email
            addr.phone = addr_phone
            address_id = addr.save()

            #Save into django table id partner/partner_address
            if not partner:
                partner = Partner.objects.create(user=request.user,partner_id=partner_id,address_id=address_id) #save partner
                partner = Partner.objects.get(id=partner.id) #get info partner
            message = _('Your details are updated successfully')
            full_name = request.user.get_full_name()
            return render_to_response("accounts/profile.html", locals(), context_instance=RequestContext(request))
        else:
            message = _('Error validation form. Try again')

    #show form partner values
    if partner:
        partner_oerp = o.ResPartner.get(partner.partner_id)
        addr_oerp = o.ResPartnerAddress.get(partner.address_id)

    return render_to_response("accounts/partner.html", locals(), context_instance=RequestContext(request))
