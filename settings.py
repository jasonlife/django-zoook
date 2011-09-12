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

from config import *

import os
import re

TEMPLATE_DEBUG = DEBUG

PAGINATOR_TOTAL = 9
PAGINATOR_ITEMS = [9,18,36]
PAGINATOR_ORDER_TOTAL = 5
PAGINATOR_INVOICE_TOTAL = 5

CATALOG_ORDERS = ['price','name']

ADMIN_URI = '/manager/'
USER_ADD_APP = [
    {'app':'content.content','url':'/content/add/','string':'Add Content'},
    {'app':'cms.modules','url':'/cms/modules/list/','string':'All Modules'},
]

USER_LENGHT = 8
KEY_LENGHT = 6

LOGIN_URL = '/partner/'
LOGIN_REDIRECT_URL = '/'

ADMINS = (
    ('Zikzakmedia','zikzak@zikzakmedia.com'),
)

MANAGERS = ADMINS

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

PROJECT_PATH = os.path.dirname(__file__)
PATH = os.path.abspath(os.path.dirname(__file__).decode("utf-8"))

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PATH, "static")

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'c=ylnmu)78-olf-96npet^tdrds-e+3jm=_hm(w*85e6yd^z@a'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'localeurl.middleware.LocaleURLMiddleware',
)

ROOT_URLCONF = 'zoook.urls'

TEMPLATE_DIRS = (
    os.path.join(PATH, "templates"+"/"+BASE_TEMPLATE),
    os.path.join(PROJECT_PATH,'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'localeurl',
    'inplaceeditform',
    'base',
    'partner',
    'content',
    'contact',
    'catalog',
#    'search',
    'sale',
    'check',
    'cashondelivery',
    'tools.filemanager',
    'tools.cms',
)

AUTH_PROFILE_MODULE = "partner.AuthProfile"

LOCALE_INDEPENDENT_PATHS = (
    re.compile('^/static/'),
    re.compile('^/media/'),
    re.compile('^/manager/'),
    re.compile('^/filemanager/'),
    re.compile('^/inplaceeditform/'),
)
