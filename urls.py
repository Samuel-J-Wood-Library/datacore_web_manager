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
    url(r'autocomplete-dataset/$', 
        views.DatasetAutocomplete.as_view(), 
        name='autocomplete-dataset',
        ),
    url(r'autocomplete-storage/$', 
        views.StorageAutocomplete.as_view(), 
        name='autocomplete-storage',
        ),
    url(r'autocomplete-dataaccess/$',
        views.DataAccessAutocomplete.as_view(),
        name='autocomplete-dataaccess'
        ),
    url(r'autocomplete-djuser/$',
        views.DjangoUserAutocomplete.as_view(),
        name='autocomplete-djuser',
        ),
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
    path('project/<int:pk>', views.ProjectView.as_view(), name='project'),
    path('node/<int:pk>', views.ServerView.as_view(), name='node'),
    path('dcuser/<int:pk>', views.DCUserView.as_view(), name='dcuser'),
    path('govdoc/<int:pk>', views.pdf_view, name='govdoc'),
    path('govdoc/meta/<int:pk>', views.GovernanceView.as_view(), name='govdocmeta'),
    path('govdoc/projectlist/<int:pk>', 
         views.AllProjectGovDocsView.as_view(), 
         name='prjgovdocs'
    ),

    # add, modify, view sftp connections:
    path('sftp', views.IndexSFTPView.as_view(), name='idx-sftp'),
    path('sftp/<int:pk>', views.SFTPView.as_view(), name='sftp'),
    path('sftp/add', views.SFTPCreate.as_view(), name='sftp-add'),
    path('sftp/update/<int:pk>', views.SFTPUpdate.as_view(), name = 'sftp-update'),

    # add, modify, view storage:
    path('storage/<int:pk>', views.StorageView.as_view(), name='storage'),
    path('storage/add', views.StorageCreate.as_view(), name='storage-add'),
    path('storage/update/<int:pk>/', 
         views.StorageUpdate.as_view(), 
         name='storage-update',
         ),
    path('storage/attach/<int:pk>/', 
         views.StorageAttach.as_view(), 
         name='storage-attach',
         ),
    path('storage/all', views.AllStorageView.as_view(), name='all_storage'),
    
    
    # add, modify, remove user
    url(r'^dcuser/add/$', views.PersonCreate.as_view(), name='person-add'),
    url(r'^dcuser/update/(?P<pk>[0-9]+)/$', 
        views.PersonUpdate.as_view(), 
        name='person-update',
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
    
    # Data Core user views
    path('myproject/<int:pk>/', 
         views.UserProjectView.as_view(), 
         name='user-project-view'
    ),
    path('myprojects/', views.UserProjectListView.as_view(), name='user-project-list'),
    
    
    # forms for adding user - project relationship:
    url(r'^dcuser/(?P<pk>[0-9]+)/connect$', 
        views.AddThisUserToProject.as_view(), 
        name='thisusertoproject-add',
    ),
    url(r'^dcuser/any/connect$', 
        views.AddUserToProject.as_view(), 
        name='usertoproject-add',
    ),
    path('dcua/view/<int:pk>/', views.DCUAView.as_view(),name='dcua'),
    path('dcua/sign/<int:pk>/', views.SignDCUA.as_view(),name='sign-dcua'),
    path('dcua/prep/', views.PrepDCUA.as_view(),name='prep-dcua'),

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
    path('finances/<int:pk>',
         views.ProjectMonthlyBillView.as_view(),
         name='project-bill',
    ),
    path('finances/create',
         views.ProjectMonthlyBillCreate.as_view(),
         name='project-bill-add',
    ),
    path('finances/update/<int:pk>',
         views.ProjectMonthlyBillUpdate.as_view(),
         name='project-bill-update',
    ),
    
    path('finances/generate/<int:ppk>',
         views.ProjectMonthlyBillGenerate.as_view(),
         name='project-charge',
    ),
    
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
    
    # comment views
    path('comment/add/<int:inst_pk>/<str:model_type>/<str:comment_type>', 
            views.CommentView.as_view(), 
            name='add_comment'),
    
    # search view:
    path('search/all', views.FullSearch.as_view(), name="full-search"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


