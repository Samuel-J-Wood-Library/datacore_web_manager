# Data Core Web Manager
__A django app for managing institutional data cores__

```
Peter Oxley
Weill Cornell Medicine
Samuel J. Wood Library and C.V. Starr Biomedical Information Center
1300 York Ave
New York, NY 10065
```

## Scope
This app is for the collection, logging and auditing of infrastructure, project environments, users, software and data governance that are part of a data core. It is able to check that necessary governance conditions are being met in each project, flag pending expirations, and monitor project onboarding/migration. It also automatically generates operations emails, Data Core user agreements, and financial summaries. A search function allows simplified location of projects, users, or documentation.

This app is not being developed as a general-purpose app, but as a specific tool for use at the Samuel J. Wood library. The basic data structure should nevertheless be amenable to use in other data core projects. 

## Setup
This app will need to be installed into an existing Django project.

1. Copy this repository into the project directory
2. Rename the repository directory `dc_management`  
3. Add `dc_management.apps.DcManagementConfig` to INSTALLED_APPS in settings.py
4. From the project directory, run `python manage.py makemigrations dc_management`
5. run `python manage.py migrate`

### Apache configuration
As a quick guide for new Django projects, here is the basic apache configuration that can be used.

add the following configuration to `/etc/apache2/apache2.conf`

```
# set up the configuration for Django
# from https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/modwsgi/

Alias /media/ /var/www/media/
Alias /static/ /var/www/static/

<Directory /var/www/static>
   Require all granted
</Directory>

<Directory /var/www/media>
   Require all granted
</Directory>


WSGIScriptAlias / /path/to/my/django/project/project/wsgi.py
WSGIPythonHome  /path/to/my/python_host_env
WSGIPythonPath /path/to/my/django/project

# set the environment variables for settings.py
SetEnv SECRET_KEY <my_secret_key>
SetEnv DATABASE_NAME <datacore_db_name>
SetEnv DATABASE_USER <datacore_db_user_name>
SetEnv DATABASE_PASSWORD <password>
SetEnv OUTLOOK_APP_ID <outlook_id>
SetEnv OUTLOOK_APP_PW <outlook_pw>

<Directory /path/to/my/django/project>
<Files wsgi.py>
   Require all granted
</Files>
</Directory>


# add wsgi support:
LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so
```

If you wish to enable SSL encryption and https, you will need to create a certificate and install it on the server, and then add the following to `/etc/apache2/apache2.conf`

```
LoadModule ssl_module modules/mod_ssl.so

Listen 443
<VirtualHost *:443>
    ServerName mydomain.edu
    SSLEngine on
    SSLCertificateFile "/oac/certificates/my_certificate.cer"
    SSLCertificateKeyFile "/oac/certificates/my_certificate_key.key"
</VirtualHost>

```

## Dependencies

* Python >= 3.5
* Django >= 2.0
* django-autocomplete-light==3.3.2
* django-bootstrap3==11.0.0
* django-bootstrap4==0.0.7
* django-crispy-forms==1.7.2
* psycopg2==2.7.6.1
* requests==2.20.1

