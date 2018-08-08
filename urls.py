from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path

from . import views

app_name = 'dc_management'
urlpatterns = [
    # index showing dashboard of high priority items:
    url(r'^$', views.IndexView.as_view(), name='index'),

    # index views of projects, users, servers, software and gov docs:
    path('project', views.IndexProjectView.as_view(), name='idx-project'),
    path('server', views.IndexServerView.as_view(), name='idx-server'),
    path('user', views.IndexUserView.as_view(), name='idx-user'),
    path('softwareidx', views.IndexSoftwareView.as_view(), name='idx-software'),
    path('govdoc', views.IndexGovdocView.as_view(), name='idx-govdoc'),
    
    # autocomplete functions:
    url(r'autocomplete-user/$', 
        views.DCUserAutocomplete.as_view(), 
        name='autocomplete-user',
        ),
    url(r'autocomplete-project/$', 
        views.ProjectAutocomplete.as_view(),
        name='autocomplete-project',
        ),
    url(r'autocomplete-node/$', 
        views.NodeAutocomplete.as_view(),
        name='autocomplete-node',
        ),

    url(r'autocomplete-software/$', 
        views.SoftwareAutocomplete.as_view(),
        name='autocomplete-software',
        ),
    url(r'autocomplete-govdoc/$', 
        views.GovdocAutocomplete.as_view(),
        name='autocomplete-govdoc',
        ),

    # outlook email:
    url(r'outlook/$', views.OutlookConnection.as_view(), name='outlook'),
    url(r'outlook/gettoken/$', views.GetToken.as_view(), name='gettoken'),
    url(r'outlook/sendtest/$', views.SendMail.as_view(), name='sendtest'),
    url(r'outlook/reset/$', views.ResetOutlookTokens.as_view(), name='reset-outlook'),
    
    # index showing all items:
    url(r'^dcuser/all/$', views.AllDCUserView.as_view(), name='all_users'),
    url(r'^project/all/$', views.AllProjectsView.as_view(), name='all_projects'),
    path('node/all', views.AllServersView.as_view(), name='all_servers'),
    
    # detail views of projects, nodes and users:
    url(r'^project/(?P<pk>[0-9]+)/$', views.ProjectView.as_view(), name='project'),
    url(r'^node/(?P<pk>[0-9]+)/$', views.ServerView.as_view(), name='node'),
    url(r'^dcuser/(?P<pk>[0-9]+)/$', views.DCUserView.as_view(), name='dcuser'),
    url(r'^govdoc/(?P<pk>[0-9]+)/$', views.pdf_view, name='govdoc'),
    path('govdoc/meta/<int:pk>', views.GovernanceView.as_view(), name='govdocmeta'),
    
    # add, modify, remove user
    url(r'^dcuser/add/$', views.DC_UserCreate.as_view(), name='dc_user-add'),
    url(r'^dcuser/update/(?P<pk>[0-9]+)/$', 
        views.DC_UserUpdate.as_view(), 
        name='dc_user-update',
    ),
    path('dcuser/add/bulk', views.BulkUserUpload.as_view(), name='bulkuserupload'),
    
    # views related to onboarding:
    url(r'onboarding/dcua_generator/$', views.CreateDCAgreementURL.as_view(), 
        name='url_generator',
    ),
    path('onboarding/dcua_url/<int:pk>', views.ViewDCAgreementURL.as_view(), 
        name='url_result',
    ),
    path('server/add', views.ServerCreate.as_view(), name='server-add'),
    path('server/update/<int:pk>/', views.ServerUpdate.as_view(), name='server-update'),
    path('project/add/', views.ProjectCreate.as_view(), name='project-add'),
    path('project/update/<int:pk>/', 
            views.ProjectUpdate.as_view(), 
            name='project-update'
    ),
    path('project/<int:ppk>/storage/change/',
            views.StorageChange.as_view(),
            name='storage-change',
    ),
    
    path('govdoc/meta/add', views.GovernanceCreate.as_view(), name='govdocmeta-add'),
    path('govdoc/meta/update/<int:pk>', 
            views.GovernanceUpdate.as_view(), 
            name='govdocmeta-update'
    ),
    
    # forms for adding user - project relationship:
    url(r'^dcuser/(?P<pk>[0-9]+)/connect$', 
        views.AddThisUserToProject.as_view(), 
        name='thisusertoproject-add',
    ),
    url(r'^dcuser/any/connect$', 
        views.AddUserToProject.as_view(), 
        name='usertoproject-add',
    ),
    
    # removing user - project relationship:
    url(r'^project/(?P<pk>[0-9]+)/userconnect$', 
        views.AddUserToThisProject.as_view(), 
        name='usertothisproject-add',
    ),
    url(r'^project/(?P<pk>[0-9]+)/userremove$', 
        views.RemoveUserFromThisProject.as_view(), 
        name='usertothisproject-remove',
    ),

    # software views:
    path('software/<int:pk>', views.SoftwareView.as_view(), name='software-detail'),
    url(r'^software/$', views.UpdateSoftware.as_view(), name='change_software'),
    url(r'^software/email/$', 
        views.EmailResults.as_view(), 
        name='email_results'),
        
    # finance views:
    url(r'finances/$', views.ActiveProjectFinances.as_view(), name='finances-active'),
    
    # log views:
    path('logs/filetransfer/<int:pk>', 
            views.FileTransferView.as_view(), 
            name='file-transfer-view',
    ),
    path('logs/filetransfer/create', 
            views.FileTransferCreate.as_view(), 
            name='file-transfer-add',
    ),
    path('logs/migration/<int:pk>/update', 
            views.MigrationUpdate.as_view(), 
            name='migration-update',
    ),
    path('logs/migration/<int:ppk>/create', 
            views.MigrationCreate.as_view(), 
            name='migration-add',
    ),
    path('logs/migration/<int:pk>', 
            views.MigrationDetailView.as_view(), 
            name='migration-info',
    ),
    
    # search view:
    path('search/all', views.FullSearch.as_view(), name="full-search"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


