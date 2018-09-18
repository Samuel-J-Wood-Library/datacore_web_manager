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
This app is for the collection, logging and auditing of infrastructure, project environments, users, software and data governance that are part of a data core. This app is not being developed as a general-purpose app, but as a specific tool for use at the Samuel J. Wood library. The basic data structure should nevertheless be amenable to use in other data core projects. 

## Setup
This app will need to be installed into an existing Django project.

1. Copy this repository into the project directory
2. Rename the repository directory `dc_management`  
3. Add `dc_management.apps.DcManagementConfig` to INSTALLED_APPS in settings.py
4. From the project directory, run `python manage.py makemigrations dc_management`
5. run `python manage.py migrate`

## Dependencies

```
Django >= 2.0
python >=3.6
django-autocomplete-light==3.3.0rc1
django-bootstrap3==9.1.0
django-bootstrap4==0.0.7
django-crispy-forms==1.7.0
django-shibboleth-remoteuser==0.9a1
```