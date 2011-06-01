Installation Instructions
=========================

The current installation documentation is somewhat technical, aimed at
system administrators setting up the Co-operative Membership System on a
server. In the future we hope to have packaging options that will make some of
these steps unnecessary.

Requirements
------------

Major software components:

- Python 2.6
- Django 1.3
- Postgresql 8.4
- Apache 2.2

Other software components:

- psycopg2 (database adaptor)
- sphinx (to generate documentation, if needed)
- virtualenv (not necessary, but highly recommended)



System Setup Walkthrough
------------------------

These are the steps taken to set up the system. These are the steps are taken on
a ubuntu/debian linux system.


- apt-get install build-essentials apache2 postgresql virtualenv mercurial
- virtualenv --no-site-packages coop
- cd coop
- source bin/activate
- pip install django
- pip install psycopg2
- createuser -U postgres --no-superuser --no-createdb --no-createrole coop
- createdb -U postgres -O coop coop
- psql -U postgres -d coop -c "CREATE OR REPLACE FUNCTION to_ascii(bytea, name) RETURNS text STRICT AS 'to_ascii_encname' LANGUAGE internal;"
- django-admin.py startproject membership
- cd membership
- hg clone https://bitbucket.org/timtoo/generic-co-operative-membership coop
- # set up django. See "Setting Up Django" section below
- python manage.py syncdb
- # create superuser account when prompted
- python manage.py runserver
- # you should see a message stating the server is running at 127.0.0.1:8000



Setting Up Django
-----------------

To set up Django, two files must be modified in the project folder:
settings.py and urls.py.

If everything is set up exactly as described above, you can just copy
the sample settings.py and url.py from the coop/misc/ folder,
overwriting the default versions in the Django project folder.

The following documents the changes made to the default files.

settings.py
```````````

- set DEBUG = False (you might want to leave this at True until the installation is up and running)
- uncomment and set ADMINS (list email addresses of admins -- used in case of problems)
- set DATABASE
    - ENGINE: django.db.backends.postgresql_psycopg2
    - NAME: coop
    - USER: coop
- set TIME_ZONE and LANGUAGE_CODE as appropriate
- add: LOGIN_URL = '/coop/login'
- add: LOGIN_REDIRECT_URL = '/coop'
- modify INSTALLED_APPS so 'django.contrib.humanize' is at the end of the list
- modify INSTALLED_APPS so 'coop' is at the end of the list
- uncomment (remove the # from the beginning of the line) 'django.contrib.admin' in the INSTALLED_APPS list
- add TEMPLATE_CONTEXT_PROCESSORS as follows (we have to list all of the default processors, so as to put ours at the end):

::

    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'django.contrib.messages.context_processors.messages',
        'coop.appsettings.context_processor',
    )

urls.py
```````

- uncomment (remove the # from the start of the line): url(r'^admin/', include(admin.site.urls)),
- add: url(r'^coop/', include('coop.urls')),


Sample Configuration Code
`````````````````````````

For reference, some examples of the results of the above described edits:

::

  INSTALLED_APPS = (
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'django.contrib.sessions',
      'django.contrib.sites',
      'django.contrib.messages',
      'django.contrib.staticfiles',
      # Uncomment the next line to enable the admin:
      'django.contrib.admin',
      # Uncomment the next line to enable admin documentation:
      # 'django.contrib.admindocs',
      'django.contrib.humanize',
      'coop',
  )

::

  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', }
          'NAME': 'coop',                      # Or path to database file if using sqlite3.
          'USER': 'coop',                      # Not used with sqlite3.
          'PASSWORD': '',                  # Not used with sqlite3.
          'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.                       'PORT': '',                      # Set to empty string for default. Not used with sqlite3.                     }                                                                                                              }

::

ADMINS = (
    ('Tim Middleton', 'tim@vaults.ca'),
)

::

An example urls.py:

::

urlpatterns = patterns('',
    url(r'^coop/', include('coop.urls')),
    url(r'^admin/', include(admin.site.urls)),
)


