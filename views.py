import json
import os
import re
from datetime import date, timedelta
import time
from urllib.parse import quote
from mimetypes import guess_type
import numpy as np

from dal import autocomplete

from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist

from django.core.mail import send_mail

from django.urls import reverse

from django.http import HttpResponse, Http404, FileResponse

from django.urls import reverse_lazy
from django.shortcuts import render, redirect

from django.db.models import Q, Sum
from django.db.utils import IntegrityError, DataError

from dc_management.authhelper import get_signin_url, get_token_from_code
from dc_management.outlookservice import get_me

from .models import Server, Project, Access_Log, Governance_Doc
from .models import Software, Software_Log, Storage_Log, Storage
from .models import UserCost, SoftwareCost, StorageCost, DCUAGenerator, DatabaseCost
from .models import FileTransfer, MigrationLog, CommentLog
from .models import ProjectBillingRecord, ExtraResourceCost
from .models import DataCoreUserAgreement, SFTP

from persons.models import Person
from datacatalog.models import Dataset, DataUseAgreement, DataAccess

from .forms import AddUserToProjectForm, RemoveUserFromProjectForm
from .forms import ExportFileForm, CreateDCAgreementURLForm
from .forms import AddSoftwareToProjectForm, ProjectForm, ProjectUpdateForm
from .forms import StorageChangeForm, BulkUserUploadForm, GovernanceDocForm
from .forms import FileTransferForm, ServerUpdateForm, ServerForm, MigrationForm
from .forms import CommentForm, StorageForm, StorageAttachForm
from .forms import DCUAForm, DCUAPrepForm, ProjectBillingForm, SFTPForm

#######################
#### Comment views ####
#######################

class CommentView(LoginRequiredMixin, CreateView):
    template_name = 'dc_management/comment_form.html'
    form_class = CommentForm
    
    def get_success_url(self):
        if self.kwargs['model_type'] ==  'project':
            return reverse('dc_management:project', args=(self.kwargs['inst_pk'],))
        if self.kwargs['model_type'] ==  'server':
            return reverse('dc_management:node', args=(self.kwargs['inst_pk'],))
        if self.kwargs['model_type'] ==  'person':
            return reverse('dc_management:dcuser', args=(self.kwargs['inst_pk'],))
        if self.kwargs['model_type'] ==  'software':
            return reverse('dc_management:software-detail',
                             args=(self.kwargs['inst_pk'],)
                            )
        if self.kwargs['model_type'] ==  'governance_doc':
            return reverse('dc_management:govdoc', args=(self.kwargs['inst_pk'],))
            
    def form_valid(self, form, ):
        self.object = form.save(commit=False)
        # get model instance comment is connected with:
        inst_pk = self.kwargs['inst_pk']            #  pk of object to attach comment to
        model_type = self.kwargs['model_type']      #  type of object comment is attached
        comment_parent = self.kwargs['comment_type']  #  pk of parent comment, or "new"
        
        # get the user who posted
        self.object.record_author = self.request.user
        
        # check if reply, then save parent if so:
        if comment_parent == 'new':
            pass
        else:
            self.object.parent_comment = CommentLog.objects.get(
                                                pk=int(comment_parent)
                                                            )
        self.object.save()
        
        # connect comment to model instance:
        if model_type == 'project':
            inst = Project.objects.get(pk=inst_pk)
        elif model_type == 'server':
            inst = Server.objects.get(pk=inst_pk)
        elif model_type == 'person':
            inst = Person.objects.get(pk=inst_pk)
        elif model_type == 'software':
            inst = Software.objects.get(pk=inst_pk)
        elif model_type == 'governance_doc':
            inst = Governance_Doc.objects.get(pk=inst_pk) 
        
        inst.dynamic_comments.add(self.object)
        inst.save()
        
        
        return super(CommentView, self).form_valid(form)

####################################
######  AUTOCOMPLETE  VIEWS   ######
####################################
class DjangoUserAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.all()

        if self.q:
            qs = qs.filter(
                            Q(username__istartswith=self.q) |
                            Q(first_name__istartswith=self.q) |
                            Q(last_name__istartswith=self.q)
                            )
            #qs = qs.filter(cwid__istartswith=self.q)

        return qs

class DCUserAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Person.objects.all()

        if self.q:
            qs = qs.filter(
                            Q(cwid__istartswith=self.q) | 
                            Q(first_name__istartswith=self.q) |
                            Q(last_name__istartswith=self.q)
                            )
            #qs = qs.filter(cwid__istartswith=self.q)

        return qs

class ProjectAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Project.objects.all()

        if self.q:
            qs =  qs.filter(
                            Q(dc_prj_id__icontains=self.q) | 
                            Q(nickname__icontains=self.q) 
                            )
        return qs

class SoftwareAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Software.objects.all()

        if self.q:
            qs =  qs.filter(
                            Q(name__icontains=self.q) | 
                            Q(vendor__icontains=self.q) |
                            Q(version__icontains=self.q)
                            )
        return qs

class NodeAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Server.objects.all()

        if self.q:
            qs =  qs.filter(
                            Q(node__icontains=self.q) | 
                            Q(ip_address__icontains=self.q) |
                            Q(comments__icontains=self.q)
                            )
        return qs

class GovdocAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Governance_Doc.objects.all()

        if self.q:
            qs =  qs.filter(
                            Q(doc_id__icontains=self.q) | 
                            Q(project__dc_prj_id__icontains=self.q) |
                            Q(project__nickname__icontains=self.q) |
                            Q(comments__icontains=self.q) |
                            Q(pk=self.q)
                            )
        return qs

class StorageAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Storage.objects.all()

        if self.q:
            qs = qs.filter(
                            Q(name__icontains=self.q) | 
                            Q(description__icontains=self.q)
                            )
        return qs

class DataAccessAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = DataAccess.objects.all()

        if self.q:
            qs = qs.filter(
                            Q(name__icontains=self.q) |
                            Q(storage_type__name__icontains=self.q) |
                            Q(filepaths__icontains=self.q)
                            )
        return qs

class DatasetAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Dataset.objects.all()

        if self.q:
            qs = qs.filter(
                            Q(ds_id__icontains=self.q) | 
                            Q(title__icontains=self.q)
                            )
        return qs

#######################
#### Outlook views ####
#######################

class ResetOutlookTokens(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dc_management/email_reset.html'
    def get_context_url(self, **kwargs):
        self.request.session['outlook_access_token'] = ""
        self.request.session['outlook_user_email'] = ""
        self.request.session['outlook_token_expires'] = ""
        self.request.session['outlook_refresh_token'] = ""
        context = super(ResetOutlookTokens, self).get_context_data(**kwargs)
        context.update({'reset':"TRUE"})
        return context
        
class OutlookConnection(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dc_management/email_outlook.html'
    
    
    def get_context_data(self, **kwargs):
        redirect_uri = self.request.build_absolute_uri(reverse('dc_management:gettoken'))
        sign_in_url = get_signin_url(redirect_uri)
                
        context = super(OutlookConnection, self).get_context_data(**kwargs)
        context.update({'sign_in_url': sign_in_url,
                        'redirect_uri': redirect_uri,
        })
        return context

class GetToken(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dc_management/email_token.html'
    def get_context_data(self, **kwargs):
        auth_code = self.request.GET['code']
        redirect_uri = self.request.build_absolute_uri(reverse('dc_management:gettoken'))
        token = get_token_from_code(auth_code, redirect_uri)
        access_token = token['access_token']
        user = get_me(access_token)
        
        # get token refresh details
        refresh_token = token['refresh_token']
        expires_in = token['expires_in']

        # expires_in is in seconds
        # Get current timestamp (seconds since Unix Epoch) and
        # add expires_in to get expiration time
        # Subtract 5 minutes to allow for clock differences
        expiration = int(time.time()) + expires_in - 300


        # Save the token in the session
        self.request.session['outlook_access_token'] = access_token
        self.request.session['outlook_user_email'] = user['mail']
        self.request.session['outlook_token_expires'] = expiration
        self.request.session['outlook_refresh_token'] = refresh_token

        context = super(GetToken, self).get_context_data(**kwargs)
        context.update({'gettoken': "Get Token",
                        'auth_code': auth_code,
                        'user': user,
                        'email': user['mail'],
        })
        return context

class SendMail(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dc_management/email_result.html'
    def get_context_data(self, **kwargs):
        # disabling until SSL can be configured.
        #access_token = get_access_token(
        #                    self.request,
        #                    self.request.build_absolute_uri(
        #                                reverse('dc_management:gettoken'))
        #                                )
        access_token = 'disabled temporarily'
        user_email = "disabled@disabled"  #self.request.session['outlook_user_email']
        
        # get email parameters from session info (saved as json)
        email_details = json.loads(self.request.session['email_json'])
        
        payload = {
                  "Message": {
                    "Subject": email_details['subject'],
                    "Body": {
                      "ContentType": "Text",
                      "Content": email_details['body']
                    },
                    "ToRecipients": [
                      {
                        "EmailAddress": {
                          "Address": email_details['to_email']
                        }
                      }
                    ],
                    #"Attachments": [
                    #  {
                    #    "@odata.type": "#Microsoft.OutlookServices.FileAttachment",
                    #    "Name": "menu.txt",
                    #    "ContentBytes": "bWFjIGFuZCBjaGVlc2UgdG9kYXk="
                    #  }
                    #]
                  },
                  "SaveToSentItems": "true"
                  }

        context = super(SendMail, self).get_context_data(**kwargs)
        context.update({'email_details':email_details,
                        'gettoken': access_token,
                        'sendtest': "Email has been temporarily disabled." #send_message(access_token,user_email,payload),
        })
        return context

#######################
#### Basic views ####
#######################
class IndexProjectView(PermissionRequiredMixin, generic.ListView):
    template_name = 'dc_management/index_projects.html'
    context_object_name = 'project_list'
    permission_required = 'dc_management.view_project'
    
    def get_queryset(self):
        """Return  all active projects."""
        return  Project.objects.filter(
                    Q(status="RU") |
                    Q(status="ON")
                ).order_by('dc_prj_id'
                )

    def get_context_data(self, **kwargs):
        context = super(IndexProjectView, self).get_context_data(**kwargs)
        context.update({
            'empty_list'    : [],
        })
        return context
        
class IndexUserView(PermissionRequiredMixin, generic.ListView):
    template_name = 'dc_management/index_users.html'
    context_object_name = 'user_list'
    permission_required = 'dc_management.view_project'

    def get_queryset(self):
        """Return  all active projects."""
        return  Person.objects.filter(project_pi__isnull=False,
                                        ).distinct().order_by('first_name')

    def get_context_data(self, **kwargs):
        context = super(IndexUserView, self).get_context_data(**kwargs)
        context.update({
            'empty_list'     : [],
        })
        return context
    
class IndexServerView(LoginRequiredMixin, generic.ListView):
    template_name = 'dc_management/index_servers.html'
    context_object_name = 'server_list'

    def get_queryset(self):
        """Return  all active production servers."""
        return  Server.objects.filter(status="ON"
                                        ).filter(
                                            function="PR"
                                        ).order_by('node')

    def get_context_data(self, **kwargs):
        context = super(IndexServerView, self).get_context_data(**kwargs)
        context.update({
            'empty_list'     : [],
        })
        return context

class IndexSoftwareView(LoginRequiredMixin, generic.ListView):
    template_name = 'dc_management/index_software.html'
    context_object_name = 'sw_list'

    def get_queryset(self):
        """Return  all software."""
        swqs = Software.objects.all()
        swqs = sorted(swqs, key=lambda i: i.seatcount(), reverse=True)
        return  swqs

    def get_context_data(self, **kwargs):
        context = super(IndexSoftwareView, self).get_context_data(**kwargs)
        context.update({
            'empty_list'     : [],
        })
        return context

class IndexGovdocView(LoginRequiredMixin, generic.ListView):
    template_name = 'dc_management/index_gov_docs.html'
    context_object_name = 'govdoc_list'

    def get_queryset(self):
        """Return  all software."""
        return Governance_Doc.objects.all()

    def get_context_data(self, **kwargs):
        context = super(IndexGovdocView, self).get_context_data(**kwargs)
        context.update({
            'empty_list'     : [],
        })
        return context

class IndexSFTPView(PermissionRequiredMixin, generic.ListView):
    template_name = 'dc_management/index_sftp.html'
    context_object_name = 'sftp_list'
    permission_required = 'dc_management.view_project'

    def get_queryset(self):
        """Return  all software."""
        return SFTP.objects.all().order_by('project')

    def get_context_data(self, **kwargs):
        context = super(IndexSFTPView, self).get_context_data(**kwargs)
        context.update({
            'empty_list'     : [],
        })
        return context

class IndexView(PermissionRequiredMixin, generic.ListView):
    
    template_name = 'dc_management/index.html'
    context_object_name = 'project_list'
    permission_required = 'dc_management.view_project'
    
    def get_queryset(self):
        """Return  all active projects."""
        return Project.objects.filter(status="RU").order_by('dc_prj_id')
    
    def get_context_data(self, **kwargs):
        # all projects running and without a completed date
        still_running = Project.objects.filter(status='RU',
                                                completion_date__isnull=True,
                                                ).order_by('expected_completion'
                                                )
        # for the expiring list
        expiring_soon = [ p for p in still_running if p.days_to_completion() <= 60 ]
        
        # all projects with valid IRB documentation
        irb_valid_projects = Project.objects.filter(
                                Q(governance_doc__governance_type='IR',
                                  governance_doc__expiry_date__gte=date.today()) |
                                Q(governance_doc__governance_type='IX')
                                            )
        irb_invalid_projects = still_running.difference(irb_valid_projects)
        
        # get all projects with expired DUAs that DON'T have currently valid DUAs
        dua_invalid_projects = Project.objects.filter(
                                    ~Q(governance_doc__expiry_date__gte=date.today()) &
                                    Q(governance_doc__governance_type='DU')
                                ).exclude(
                                    governance_doc__expiry_date__gte=date.today(),
                                    governance_doc__governance_type='DU'
                                ).exclude(
                                    status='CO',
                                ).distinct()
        
        swqs = Software.objects.all()
        swqs = sorted(swqs, key=lambda i: i.seatcount(), reverse=True)
        
        context = super(IndexView, self).get_context_data(**kwargs)
        context.update({
            'expiring_list'     : expiring_soon,  
            'onboarding_list'   : MigrationLog.objects.filter(
                                        Q(access_date__isnull=True) |
                                        Q(envt_date__isnull=True)   |
                                        Q(data_date__isnull=True)
                                        ).filter(
                                        project__status='ON'
                                        ).order_by('record_creation'),
            'migration_list'    : MigrationLog.objects.filter(
                                        Q(access_date__isnull=True) |
                                        Q(envt_date__isnull=True) |
                                        Q(data_date__isnull=True)
                                        ).exclude(
                                            project__status='ON'
                                        ).exclude(
                                            project__status='SU'
                                        ).order_by('record_creation'),
            'onboarding_prj_list': Project.objects.filter(
                                        status='ON',
                                        migrationlog=None,
                                        ).order_by('requested_launch'),                            
            'irb_invalid'       : irb_invalid_projects,
            'dua_invalid'       : dua_invalid_projects,
            'undocumented_list' : Project.objects.filter(
                                        governance_doc__isnull=True,
                                        ).order_by('dc_prj_id'),                           
            'shutting_list'     : Project.objects.filter(
                                        status='SD',
                                        completion_date__isnull=True,
                                        ).order_by('expected_completion'),                            
            # for finding users assigned more than once:
            'server_list'       : Server.objects.filter(
                                        status="ON"
                                        ).filter(
                                            function="PR"
                                        ).order_by('node'),
            'unsigned_user_list':[],
            'undoc_user_list'   :Person.objects.exclude(
                governance_doc__date_issued__gte=date.today()-timedelta(days=360),
                                        ).filter(
                project__status__in=['RU', 'SD'],
                                        ).distinct(
                                        ).order_by('first_name'
                                        ),
        })
        return context

class AllDCUserView(LoginRequiredMixin, generic.ListView):
    template_name = 'dc_management/all_users.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        """Return  all active projects."""
        return Person.objects.all().order_by('first_name')
       
class DCUserView(LoginRequiredMixin, generic.DetailView):
    model = Person
    template_name = 'dc_management/dcuser.html'

class PersonCreate(LoginRequiredMixin, CreateView):
    model = Person
    fields = ['first_name', 'last_name', 'cwid', 'affiliation', 'role', 'comments']
    success_url = reverse_lazy("dc_management:index" )
    def form_valid(self, form):
        self.object = form.save(commit=False)
        #self.object.user = self.request.user
        #self.object.post_date = datetime.now()
        self.object.save()
        return super(PersonCreate, self).form_valid(form)

class PersonUpdate(LoginRequiredMixin, UpdateView):
    model = Person
    fields = ['first_name', 
                'last_name', 
                'cwid', 
                'affiliation', 
                'role', 
                'email', 
                'department',
                'comments'
                ]  

#############################
######  PROJECT VIEWS  ######
#############################

class ProjectView(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = 'dc_management/project.html'

    def get_context_data(self, **kwargs):
        # get project cost
        project_costs = []
        
        # get all software installed on the node, and thus available to the prj
        node=self.object.host
        if node:
            available_sw = node.software_installed.exclude(
                                            pk__in=self.object.software_installed.all()
            )
        else:
            available_sw = []            
        
        # pull all governance docs from datasets on attached storage:
        prj_governance = DataUseAgreement.objects.filter(datasets__dataaccess__dc_project=self.object.pk,
                                ).distinct()
        
        # create other lists for display:
        current_gov_docs = self.object.governance_doc_set.all(
                                ).exclude(superseded_by__isnull=False
                                ).exclude(defers_to_doc__isnull=False
                                )
        irb_users = Person.objects.filter(Q(governance_doc__governance_type='IR') &
                                         Q(governance_doc__project=self.object.pk)
                                ).distinct()
        dcua_users = Person.objects.filter(Q(governance_doc__governance_type='DC') &
                                         Q(governance_doc__project=self.object.pk)
                                ).distinct()
        dua_users = Person.objects.filter(Q(governance_doc__governance_type='DU') &
                                         Q(governance_doc__project=self.object.pk)
                                ).distinct()
        
        project_bills = ProjectBillingRecord.objects.filter(project=self.object.pk
                                ).order_by('-billing_date')
        # calculate monthly bill totals and zip them with the monthly bill.
        bill_zip = zip(project_bills, [ pb.monthly_total() for pb in project_bills ])
        
        try:
            latest_bill = project_bills.latest('billing_date')
        except ProjectBillingRecord.DoesNotExist:
            latest_bill = None
        
        if latest_bill:
            bill_total = latest_bill.monthly_total()
        else:
            bill_total = 0
        
        if current_gov_docs.filter(governance_type='IX').count() >= 1:
            fully_validated = dcua_users
        elif current_gov_docs.filter(governance_type='DU').count() == 0:
            fully_validated = irb_users & dcua_users
        else:
            fully_validated = irb_users & dua_users & dcua_users
        
        partially_validated = dcua_users | dua_users | irb_users
        unconnected_users = fully_validated.exclude(pk__in=self.object.users.all())
        
        ## update context        
        context = super(ProjectView, self).get_context_data(**kwargs)
        context.update({
                        'project_costs': project_costs,
                        'available_software':available_sw,
                        'prj_governance':prj_governance,
                        'current_gov_docs':current_gov_docs,
                        'fully_validated':fully_validated,
                        'partially_validated':partially_validated,
                        'irb_users':irb_users,
                        'dua_users':dua_users,
                        'dcua_users':dcua_users,
                        'unconnected_users':unconnected_users,
                        'bill':latest_bill,
                        'bill_total':bill_total,
                        'all_bills':project_bills,
                        'bill_zip':bill_zip,
        })
        return context

class AllProjectGovDocsView(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = 'dc_management/gov_docs_all.html'

class AllProjectsView(LoginRequiredMixin, generic.ListView):
    template_name = 'dc_management/projects_all.html'
    context_object_name = 'project_list'
    
    def get_queryset(self):
        """Return  all projects."""
        return Project.objects.all().order_by('dc_prj_id')

class BulkUserUpload(LoginRequiredMixin, FormView):
    template_name = 'dc_management/bulkuseruploadform.html'
    form_class = BulkUserUploadForm
    success_url = reverse_lazy('dc_management:index')
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        post_data = self.request.POST
        
        # Check if user in project, then connect user to project
        users_csv_field = form.cleaned_data['users_csv']
        users_csv = self.request.FILES['users_csv']
        extra_comment = form.cleaned_data['comment']
        
        #form.instance.record_author = self.request.user

        # read file and create users.
        chunks = users_csv.chunks() # open(users_csv, "r")
        for handle in chunks:
            for line in str(handle).split('\\n'):
                print(line)
                if len(line.strip().split(',')) == 6:
                    fn,ln,cw,af,ro,co = line.strip().split(',')
                    print("First:{}\nLast:{}\nCWID:{}\nAffil:{}\nRole:{}\nComments:{}".format(fn,ln,cw,af,ro,co))
                    if fn[:2] == "b'":      # from conversion of bytes to str
                        fn = fn[2:]
                    try:
                        u = Person(first_name=fn.strip(), 
                                    last_name=ln.strip(), 
                                    cwid=cw.strip(), 
                                    affiliation=af.strip(), 
                                    role=ro.strip(),
                                    comments="\n".join([co,extra_comment]),
                                    )
                        u.save()
                    except DataError:       # eg role has more than 2 chars
                        print("USER DATA ERROR ENCOUNTERED FOR {}. SKIPPING".format(cw))
                    except IntegrityError:  # eg CWID already exists
                        print("USER INTEGRITY ERROR ENCOUNTERED FOR {}. SKIPPING".format(cw))               
                        
        return super(BulkUserUpload, self).form_valid(form)    
  
class ProjectCreate(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "dc_management/basic_crispy_form.html"
    
    #success_url = reverse_lazy("dc_management:index" )
    # default success_url should be to the object page defined in model.
    def form_valid(self, form):
        self.object = form.save(commit=False)
        return super(ProjectCreate, self).form_valid(form)

class ProjectUpdate(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectUpdateForm
    template_name = "dc_management/basic_crispy_form.html"

    #success_url = reverse_lazy("dc_management:index" )
    #default success_url should be to the object page defined in model.
    def form_valid(self, form):
        print(self.object.host)
        self.object = form.save(commit=False)
        return super(ProjectUpdate, self).form_valid(form)

class StorageChange(LoginRequiredMixin, CreateView):
    model = Storage_Log
    template_name = 'dc_management/storage_change_form.html'
    form_class = StorageChangeForm
        
    """
    # keeping this in case I need it somewhere else later
    # pass the project pk from the url to the form's kwargs for queryset populating
    def get_form_kwargs(self):
        kwargs = super(StorageChange, self).get_form_kwargs()
        kwargs.update({'ppk': self.kwargs['ppk']})  
    return kwargs
    """
    
    def get_initial(self):
        initial = super(StorageChange, self).get_initial()
        # get the project from the url
        chosen_project = Project.objects.get(pk=self.kwargs['ppk'])
        # update initial field defaults with custom set default values:
        initial.update({'project': chosen_project, })
        return initial

    def get_success_url(self):
        if self.update_server == True:
            return reverse_lazy('dc_management:sendtest',)
        else:
            return reverse('dc_management:project', args=[self.project_pk])
                
    def form_valid(self, form):
        # clear email fields in session
        email_details = {   'subject'       :"na",
                            'body'          :"na",
                            'to_email'      :"na",
                            'subject_html'  :"na",
                            'body_html'     :"na",
        }
        self.request.session['email_json'] = json.dumps(email_details)

        log = form.save(commit=False)
        
        log.record_author = self.request.user
        
        # update the project storage:
        project = log.project
        
        # match storage type to project (this needs to be more robust)
        s_type = log.storage_type.storage_type
        assess_server = False
        existing_project_storage = None
        new_project_storage = None

        if re.search('direct', s_type.lower()):
            existing_project_storage = project.direct_attach_storage
            if not existing_project_storage:
                existing_project_storage = 0
            new_project_storage = log.storage_amount
            project.direct_attach_storage = new_project_storage
            existing_server_storage = project.host.other_storage
            assess_server = True
        elif re.search('archiv', s_type.lower()):
            project.backup_storage = log.storage_amount
        elif re.search('primary', s_type.lower()):
            project.fileshare_storage = log.storage_amount
        elif re.search('derivative', s_type.lower()):
            project.fileshare_derivative = log.storage_amount
        else:
            raise Http404()

        project.save()
        log.save()
        
        ## TODO: 
        # assess if this project change requires a server change
        self.update_server = False
        self.project_pk = project.pk
        
        if assess_server == True:
            # was project biggest user of resources on node?
            # get all other projects on node:
            shared_prjs = Project.objects.filter(host=project.host).exclude(pk=project.pk)
            # get the highest resource of the other projects:
            mounted_storage = [p.direct_attach_storage for p in shared_prjs if p.direct_attach_storage]
            if len(shared_prjs) == 0 or len(mounted_storage) == 0:  
            # ie, this is the only project on the node with storage assigned
                new_server_amount = new_project_storage
            elif max(mounted_storage) == 0:
                new_server_amount = new_project_storage
            else:
                highest_resource = max([p.direct_attach_storage for p in shared_prjs if p.direct_attach_storage])
            
                if new_project_storage > highest_resource:
                    new_server_amount = new_project_storage 

                elif existing_project_storage > highest_resource and \
                     new_project_storage <= highest_resource:
                        # change server direct_attach to highest of other projects
                        new_server_amount = highest_resource
                else:   # new amt < others, old amt <= others
                    # no change necessary to server storage.
                    new_server_amount = None  # not to be confused with 0
                
            if new_server_amount:
                self.update_server = True
                # update server storage amount:
                host = project.host
                host.other_storage = new_server_amount
                host.save()
                
                # send email requesting change to server
                if log.sn_ticket:
                    ticket_redirect = "Re: incident {} ".format(log.sn_ticket)
                else:
                    ticket_redirect = ""
                subject_str = '{}Change {} E: drive to {} GB'
                body_str = '''Dear OPs, 
        
Please change the E: drive storage on node {0} to {1} GB.

{2}

Kind regards,
{3}'''
                subj_msg = subject_str.format(ticket_redirect,
                                                project.host.node, 
                                                new_server_amount
                )
                body_msg = body_str.format(project.host.node,
                                    new_server_amount,
                                    log.comments,
                                    self.request.user.get_short_name(),
                )

                email_dict = {  'subject'       :subj_msg,
                                'body'          :body_msg,
                                'to_email'      :"dcore-ticket@med.cornell.edu",
                                'subject_html'  :quote(subj_msg),
                                'body_html'     :quote(body_msg),
                }
        
                self.request.session['email_json'] = json.dumps(email_dict)

        return super(StorageChange, self).form_valid(form)

#############################
######  STORAGE VIEWS  ######
#############################

class StorageView(PermissionRequiredMixin, generic.DetailView):
    model = Storage
    template_name = 'dc_management/storage.html'
    permission_required = 'dc_management.view_project'
    
    def get_context_data(self, **kwargs):
        # get a non-redundant list of all projects using this storage
        storage_projects =  Project.objects.filter(storage=self.kwargs['pk']
                        ).order_by('dc_prj_id').distinct()
        storage_governance = DataUseAgreement.objects.filter(
                                datasets__storage=self.kwargs['pk']
                        ).order_by('governance_type').distinct()
        
        context = super(StorageView, self).get_context_data(**kwargs)
        context.update({
                        'storage_projects': storage_projects,
                        'storage_governance': storage_governance,
        })
        return context

class AllStorageView(PermissionRequiredMixin, generic.ListView):
    template_name = 'dc_management/storage_all.html'
    context_object_name = 'storage_list'
    permission_required = 'dc_management.view_project'
    
    def get_queryset(self):
        """Return  all storage."""
        return DataAccess.objects.all().order_by('name')

class StorageCreate(PermissionRequiredMixin, CreateView):
    model = Storage
    form_class = StorageForm
    template_name = "dc_management/basic_crispy_form.html"
    permission_required = 'dc_management.view_project'
    
    # default success_url should be to the object page defined in model.
    def form_valid(self, form):
        self.object = form.save(commit=False)
        # update who last edited record
        self.object.record_author = self.request.user
        
        self.object.save()
        return super(StorageCreate, self).form_valid(form)

class StorageUpdate(PermissionRequiredMixin, UpdateView):
    model = Storage
    form_class = StorageForm
    template_name = "dc_management/basic_form.html"
    permission_required = 'dc_management.view_project'
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        # update who last edited record
        self.object.record_author = self.request.user
        
        self.object.save()
        return super(StorageUpdate, self).form_valid(form)

class StorageAttach(PermissionRequiredMixin, UpdateView):
    """
    Storage attach is really just a project update with only one field to update.
    """
    model = Project
    form_class = StorageAttachForm
    template_name = "dc_management/basic_crispy_form.html"
    permission_required = 'dc_management.view_project'
    
    #success_url = reverse_lazy("dc_management:index" )
    #default success_url should be to the object page defined in model.
    def form_valid(self, form):
        print(self.object.host)
        self.object = form.save(commit=False)
        return super(StorageAttach, self).form_valid(form)

#############################
######  SERVER VIEWS  ######
#############################

class ServerView(LoginRequiredMixin, generic.DetailView):
    model = Server
    template_name = 'dc_management/server.html'

    def get_context_data(self, **kwargs):
        # get a non-redundant list of all users on the server
        server_users =  Person.objects.filter(project__host=self.kwargs['pk']
                        ).order_by('first_name').distinct()
        
        # get a list of all software installed for various projects:

        qs = Software_Log.objects.all()
        qs_node = qs.filter(applied_to_node=self.kwargs['pk'] 
                            ).order_by('software_changed','-change_date')
        current_swl = ''
        installed_sw = []
        for swl in qs_node:
            if swl == current_swl:
                continue
            else:
                current_swl = swl
                if swl.change_type == "AA":   # last change was to add software to node
                    installed_sw.append(swl.software_changed) 
 
        context = super(ServerView, self).get_context_data(**kwargs)
        context.update({
                        'server_users': server_users,
                        'installed_software_bylogs':installed_sw,
                        'self_server_list':[self.object,],
        })
        return context

class AllServersView(LoginRequiredMixin, generic.ListView):
    template_name = 'dc_management/server_all.html'
    context_object_name = 'server_list'
    
    def get_queryset(self):
        """Return  all servers."""
        return Server.objects.all().order_by('node')

class ServerCreate(LoginRequiredMixin, CreateView):
    model = Server
    form_class = ServerForm
    template_name = "dc_management/basic_form.html"
    
    # default success_url should be to the object page defined in model.
    def form_valid(self, form):
        self.object = form.save(commit=False)
        return super(ServerCreate, self).form_valid(form)

class ServerUpdate(LoginRequiredMixin, UpdateView):
    model = Server
    form_class = ServerUpdateForm
    template_name = "dc_management/basic_form.html"
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        return super(ServerUpdate, self).form_valid(form)

####################
#### sFTP VIEWS ####
####################
class SFTPView(PermissionRequiredMixin, generic.DetailView):
    model = SFTP
    template_name = 'dc_management/sftp_detail.html'
    permission_required = 'dc_management.view_project'

class SFTPCreate(PermissionRequiredMixin, CreateView):
    model = SFTP
    form_class = SFTPForm
    template_name = "dc_management/basic_crispy_form.html"
    permission_required = 'dc_management.view_project'

    # default success_url should be to the object page defined in model.
    def form_valid(self, form):
        self.object = form.save(commit=False)
        # update who last edited record
        self.object.record_author = self.request.user

        self.object.save()
        return super(SFTPCreate, self).form_valid(form)

class SFTPUpdate(PermissionRequiredMixin, UpdateView):
    model = SFTP
    form_class = SFTPForm
    template_name = "dc_management/basic_form.html"
    permission_required = 'dc_management.view_project'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # update who last edited record
        self.object.record_author = self.request.user

        self.object.save()
        return super(SFTPUpdate, self).form_valid(form)

# ############################# #
# #####  UPDATE SOFTWARE  ##### #
# ############################# #


class UpdateSoftware(LoginRequiredMixin, FormView):
    template_name = 'dc_management/updatesoftwareform.html'
    form_class = AddSoftwareToProjectForm
    #success_url = reverse_lazy('dc_management:email_results')
    success_url = reverse_lazy('dc_management:sendtest')

    def email_change_project_software(self, changestr, prj, sw):
        """
        send request to add/remove software to node:
        """
        sbj_str = '{} software {} to {}'
        body_str = 'Please {} {} for project {} (node {}, {}).'
        sbj_msg  = sbj_str.format(changestr, sw, prj.dc_prj_id)
        body_msg = body_str.format(changestr,
                                     sw, 
                                     prj.dc_prj_id,
                                     prj.host.node,
                                     prj.host.ip_address,
                                    )

        email_dict = {'subject': sbj_msg,
                      'body': body_msg,
                      'to_email': "dcore-ticket@med.cornell.edu",
                      'subject_html': quote(sbj_msg),
                      'body_html': quote(body_msg),
                      }
        
        self.request.session['email_json'] = json.dumps(email_dict)
    
    def email_change_node_software(self, changestr, node, sw):
        """
        send request to add/remove software to node:
        """
        sbj_str = '{} software {} to {}'
        body_str = 'Please install {} on node {} ({}).'
        sbj_msg = sbj_str.format(changestr, sw, node.node)
        body_msg = body_str.format(sw, 
                                   node.node,
                                   node.ip_address,
                                   )

        email_dict = {'subject': sbj_msg,
                      'body': body_msg,
                      'to_email': "dcore-ticket@med.cornell.edu",
                      'subject_html': quote(sbj_msg),
                      'body_html': quote(body_msg),
                      }
        
        self.request.session['email_json'] = json.dumps(email_dict)

    def form_valid(self, form):
        # clear email fields in session
        email_details = {'subject': "na",
                         'body': "na",
                         'to_email': "na",
                         'subject_html': "na",
                         'body_html': "na",
                         }
        self.request.session['email_json'] = json.dumps(email_details)
        
        # Check if user in project, then connect user to project
        sw = form.cleaned_data['software_changed']
        prj = form.cleaned_data['applied_to_prj']
        user = form.cleaned_data['applied_to_user']
        node = form.cleaned_data['applied_to_node']
        change = form.cleaned_data['change_type']
        
        form.instance.record_author = self.request.user
        
        if change == "AA":
            changestr = "install" # set language for emails:
            
            # if project specified, and not already installed:
            if prj and prj.host and not sw in prj.software_installed.all():
                # add sw to prj
                prj.software_installed.add(sw)
                prj.software_requested.add(sw)

                self.email_change_project_software(changestr, prj, sw)
            
                # add to node if not already:
                # check to see if any changes have been applied to the node:
                node = prj.host
                if sw not in node.software_installed.all():
                    form.instance.applied_to_node = node
                    node.software_installed.add(sw)  
            # if node specified (and not a project), and not already on node:
            elif node and not prj:
                # check to see if any changes have been applied to the node:
                if sw not in node.software_installed.all():                    
                    self.email_change_node_software(changestr, node, sw)
                    node.software_installed.add(sw)
            else:
                return redirect('dc_management:index')
                
        elif change == "RA":
            changestr = "uninstall" # set language for emails:
            # if project specified, and not already uninstalled:
            if prj and prj.host and sw in prj.software_installed.all():
                # remove sw to prj
                prj.software_installed.remove(sw)
                prj.software_requested.remove(sw)

                self.email_change_project_software(changestr, prj, sw)
            
                # remove from node if only project requiring it, and it is licensed.
                node = prj.host
                qs = Project.objects.all()
                qs_wsw = qs.filter(software_requested=sw)
                                        
                if not qs_wsw or len(qs_wsw) == 0:  
                    form.instance.applied_to_node = node
                    node.software_requested.remove(sw)
        
            # if node specified (and not a project), and sw still on node:
            if node and not prj:
                if sw in node.software_installed.all():
                    self.email_change_node_software(changestr, node, sw)
                    node.software_requested.remove(sw)

        else:
            changestr = "confirm presence of" # innocuous, not intended to be used.
                     
        form.save()                
                
        return super(UpdateSoftware, self).form_valid(form)    


class EmailResults(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dc_management/email_result.html'


class SoftwareView(LoginRequiredMixin, generic.DetailView):
    model = Software
    template_name = 'dc_management/software.html'

# ############################# #
# #####  USER PAGE VIEWS  ##### #
# ############################# #


class UserProjectView(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = 'dc_management/userview_project_detail.html'

    def get_context_data(self, **kwargs):
        
        project_dcuas = DataCoreUserAgreement.objects.filter(project=self.kwargs['pk'])
        dcua_attestees = [ d.attestee for d in project_dcuas ]
        project_govdocs = DataUseAgreement.objects.filter()
        
        context = super(UserProjectView, self).get_context_data(**kwargs)
        context.update({
                        'project_dcuas': project_dcuas,
                        'dcua_attestees':dcua_attestees,
        })
        return context    

class UserProjectListView(LoginRequiredMixin, generic.ListView):
    template_name = 'dc_management/userview_project_list.html'
    context_object_name = 'project_list'
    
    def get_queryset(self):
        """Return all projects associated with the viewer"""
        viewer = self.request.user
        try:
            viewer_person = Person.objects.get(cwid=viewer.username)
        except:
            viewer_person = None
            viewers_projects = None
        else:
            viewers_projects = Project.objects.filter(  Q(pi=viewer_person) |
                                        Q(users__id=viewer_person) |
                                        Q(prj_admin=viewer_person)
                             ).order_by('dc_prj_id'
                             )
        
        return viewers_projects
        
#################################################
######  UPDATE USER - PROJECT RELATIONSHIP ######
#################################################

class AddUserToProject(LoginRequiredMixin, FormView):
    template_name = 'dc_management/addusertoproject.html'
    form_class = AddUserToProjectForm
    success_url = reverse_lazy('dc_management:sendtest')
    
    def form_valid(self, form):
        # clear email fields in session
        email_details = {   'subject'       :"na",
                            'body'          :"na",
                            'to_email'      :"na",
                            'subject_html'  :"na",
                            'body_html'     :"na",
        }
        self.request.session['email_json'] = json.dumps(email_details)
             
        # Check if user in project, then connect user to project
        
        prj = form.cleaned_data['project']
        newusers = form.cleaned_data['dcusers']
        email_comment = form.cleaned_data['email_comment']
        locations_allowed = form.cleaned_data['locations_allowed']
        oldusers = prj.users.all()
        record_author = self.request.user
        
        userlist = []
        for newuser in newusers:
            if newuser in oldusers:
                # report user is already added to project
                pass
            else:
                prj.users.add(newuser)
                userlist.append(newuser)
                
                # save access log instance
                self.logger = Access_Log(
                            record_author=record_author,
                            date_changed=date.today(),
                            dc_user=newuser,
                            prj_affected=prj,
                            change_type="AA",
                )
                self.logger.save()
                
                # create DCUA for signing by user
                new_dcua = DataCoreUserAgreement(
                                    record_creation=date.today(),
                                    record_update=date.today(),
                                    record_author=record_author,
                                    attestee=newuser,
                                    project=prj,
                                    start_date=date.today(),
                                    end_date=date.today()+timedelta(days=365), 
                                    locations_allowed=locations_allowed,
                            )
                new_dcua.save()
                
        # send email
        if prj.host:
            node = prj.host.node
            ip = prj.host.ip_address
        else:
            node = "not mounted"
            ip = ""
        subject_str = 'Add users to {}'
        body_str = '''Dear OPs, 
        
This ticket refers to SOP "HowTo: Add or remove a user to a Data Core project"
https://nexus.weill.cornell.edu/display/ops/HowTo%3A+Add+or+remove+a+user+to+a+Data+Core+project+group

For the following {4} users, please add them to the AD group for project {0} ({1}, {2}) and create their corresponding fileshare directory (permissions indicated):

{3}

{6}

Kind regards,
{5}'''
        subj_msg = subject_str.format(str(prj))
        body_msg = body_str.format(prj.dc_prj_id,
                            node,
                            ip,
                            '\n'.join(["{} ; WorkArea-{} ; (RWX)".format(u,u.cwid) for u in userlist]),
                            len(userlist),
                            self.request.user.get_short_name(),
                            email_comment,
                            )

        email_dict = {  'subject'       :subj_msg,
                        'body'          :body_msg,
                        'to_email'      :"dcore-ticket@med.cornell.edu",
                        'subject_html'  :quote(subj_msg),
                        'body_html'     :quote(body_msg),
        }
        
        self.request.session['email_json'] = json.dumps(email_dict)
                
        return super(AddUserToProject, self).form_valid(form)

class AddThisUserToProject(AddUserToProject):
    template_name = 'dc_management/addusertoproject.html'
    form_class = AddUserToProjectForm
    success_url = reverse_lazy('dc_management:all_projects')
    #chosen_user = Person.objects.get(pk=self.kwargs['pk'])
    #success_url = reverse_lazy('dc_management:dcuser', self.kwargs['pk'])
    
    def get_initial(self):
        initial = super(AddThisUserToProject, self).get_initial()
        # get the user from the url
        chosen_user = Person.objects.get(pk=self.kwargs['pk'])
        # update initial field defaults with custom set default values:
        initial.update({'dcuser': chosen_user, })
        return initial

class AddUserToThisProject(AddUserToProject):
    template_name = 'dc_management/addusertoproject.html'
    form_class = AddUserToProjectForm
    success_url = reverse_lazy('dc_management:sendtest')
    
    def get_initial(self):
        initial = super(AddUserToThisProject, self).get_initial()
        # get the user from the url
        chosen_project = Project.objects.get(pk=self.kwargs['pk'])
        # update initial field defaults with custom set default values:
        initial.update({'project': chosen_project, })
        return initial

class DCUAView(LoginRequiredMixin, generic.DetailView):
    model = DataCoreUserAgreement
    template_name = 'dc_management/dcua_doc.html'

class PrepDCUA(PermissionRequiredMixin, CreateView):
    model = DataCoreUserAgreement
    form_class = DCUAPrepForm
    template_name = "dc_management/basic_crispy_form.html"
    permission_required = 'dc_management.view_project'

    def form_valid(self, form):
        """
        On successful submission, update the record author.
        """
        self.object = form.save(commit=False)

        # update who last edited record
        self.object.record_author = self.request.user

        # save migration log changes
        self.object.save()
        return super(PrepDCUA, self).form_valid(form)

class SignDCUA(PermissionRequiredMixin, UpdateView):
    model = DataCoreUserAgreement
    form_class = DCUAForm
    template_name = "dc_management/basic_crispy_form.html"
    permission_required = 'dc_management.view_project'

    def has_permission(self):
        if self.request.user == self.get_object().attestee:
            return True
        else:
            return False

    def form_valid(self, form):
        """
        On successful submission, update the node for the project.
        """
        self.object = form.save(commit=False)

        # update who last edited record
        self.object.record_author = self.request.user

        # save migration log changes
        self.object.save()
        return super(SignDCUA, self).form_valid(form)

######### Removing users from projects ###########

class RemoveUserFromProject(LoginRequiredMixin, FormView ):
    template_name = 'dc_management/removeuserfromproject.html'
    form_class = RemoveUserFromProjectForm
    success_url = reverse_lazy('dc_management:sendtest')
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        post_data = self.request.POST
        
        # clear email fields in session
        email_details = {   'subject'       :"na",
                            'body'          :"na",
                            'to_email'      :"na",
                            'subject_html'  :"na",
                            'body_html'     :"na",
        }
        self.request.session['email_json'] = json.dumps(email_details)
                
        # Check if user in project, then remove user from project
        prj = form.cleaned_data['project']
        newusers = form.cleaned_data['dcusers']
        oldusers = prj.users.all()
        record_author = self.request.user
        email_comment = form.cleaned_data['email_comment']
        
        userlist = []
        for newuser in newusers:
            if newuser not in oldusers:
                # report user is not in project
                pass
            else:
                prj.users.remove(newuser)
                userlist.append(newuser)
                
                # save access log instance
                self.logger = Access_Log(
                            record_author=record_author,
                            date_changed=date.today(),
                            dc_user=newuser,
                            prj_affected=prj,
                            change_type="RA",
                )
                self.logger.save()

        # send email
        if prj.host:
            node = prj.host.node
            ip = prj.host.ip_address
        else:
            node = "not mounted"
            ip = ""

        subject_str = 'Remove users from {}'
        body_str = '''Dear OPs, 
        
This ticket refers to SOP "HowTo: Add or remove a user to a Data Core project"
https://nexus.weill.cornell.edu/display/ops/HowTo%3A+Add+or+remove+a+user+to+a+Data+Core+project+group

Please remove the following users from project {0} ({1}, {2}):

{3}

{5}

Kind regards,
{4}'''
        subj_msg = subject_str.format(str(prj))
        body_msg = body_str.format(prj.dc_prj_id,
                            node,
                            ip,
                            '\n'.join([str(u) for u in userlist]),
                            self.request.user.get_short_name(),
                            email_comment,
                            )
        
        email_dict = {  'subject'       :subj_msg,
                        'body'          :body_msg,
                        'to_email'      :"dcore-ticket@med.cornell.edu",
                        'subject_html'  :quote(subj_msg),
                        'body_html'     :quote(body_msg),
        }
        
        self.request.session['email_json'] = json.dumps(email_dict)


        return super(RemoveUserFromProject, self).form_valid(form)

class RemoveUserFromThisProject(RemoveUserFromProject):
    template_name = 'dc_management/removeuserfromproject.html'
    form_class = RemoveUserFromProjectForm
    success_url = reverse_lazy('dc_management:sendtest')
    
    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(RemoveUserFromThisProject, self).get_form_kwargs()
        kwargs['project_users'] =   Project.objects.get(
                                                        pk=self.kwargs['pk']
                                    ).users.all()
        return kwargs

    def get_initial(self):
        initial = super(RemoveUserFromThisProject, self).get_initial()
        # get the user from the url
        chosen_project = Project.objects.get(pk=self.kwargs['pk'])
        # update initial field defaults with custom set default values:
        initial.update({'project': chosen_project, })
        return initial

###### Onboarding views #######

class CreateDCAgreementURL(LoginRequiredMixin, CreateView):
    model = DCUAGenerator
    template_name = 'dc_management/dcua_url_generator_form.html'
    form_class = CreateDCAgreementURLForm
    #success_url = reverse_lazy('dc_management/dcua_url_generator_result.html')
    #success_url = reverse_lazy('dc_management:url_result')

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        post_data = self.request.POST 
        link_object = form.save(commit=False)
        
        
        # create the personalized URL:
        ticket = form.cleaned_data['ticket']
        startdate = form.cleaned_data['startdate']
        enddate = form.cleaned_data['enddate']
        
        # create a string of folders:
        folders = ""
        folderlist = []
        for f in range(1,7,1):
            folder = "".join(["folder",str(f)])
            foldername = form.cleaned_data[ folder ]
            if foldername and foldername != "":
                folders += "&{}={}".format(folder, foldername)
                folderlist.append(foldername)
        
        # create the qualtrics link with embedded data:
        qualtrics_link = "https://weillcornell.az1.qualtrics.com/jfe/form/SV_eL1OCCGkNZWnX93"
        
        qualtrics_link += "?startdate={}&enddate={}".format(startdate,enddate)
        qualtrics_link += "{}".format(folders)
        if ticket and re.search("INC\d{6,8}", ticket):
            qualtrics_link += "&ticket={}".format(ticket)
        
        # add qualtrics link to model instance and save:
        link_object.url = qualtrics_link
        link_object.save()
        
        return super(CreateDCAgreementURL, self).form_valid(form)

    # the following has been deprecated. Being maintained during bug testing.
    def form_valid_old(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        post_data = self.request.POST 
        
        # create the personalized URL:
        ticket = form.cleaned_data['ticket']
        startdate = form.cleaned_data['startdate']
        enddate = form.cleaned_data['enddate']
        
        folders = ""
        folderlist = []
        for f in range(1,7,1):
            folder = "".join(["folder",str(f)])
            foldername = form.cleaned_data[ folder ]
            if foldername != "":
                folders += "&{}={}".format(folder, foldername)
                folderlist.append(foldername)
        
        qualtrics_link = "https://weillcornell.az1.qualtrics.com/jfe/form/SV_eL1OCCGkNZWnX93"
        
        qualtrics_link += "?startdate={}&enddate={}".format(startdate,enddate)
        qualtrics_link += "{}".format(folders)
        if re.search("INC\d{6,8}", ticket):
            qualtrics_link += "&ticket={}".format(ticket)
            self.request.session['ticket'] = ticket
        else:
            self.request.session['ticket'] = ""
        
        # add to session info for passing to results page
        # NB - all session info fields must be updated, otherwise old info will be passed!
        self.request.session['qualtrics_link'] = qualtrics_link
        self.request.session['startdate'] = startdate
        self.request.session['enddate'] = enddate
        self.request.session['folders'] = folderlist

        return super(CreateDCAgreementURL, self).form_valid(form)


class ViewDCAgreementURL(LoginRequiredMixin, generic.DetailView):
    template_name = 'dc_management/dcua_url_generator_result.html'
    model = DCUAGenerator

###### Export requests #######


class ExportRequest(LoginRequiredMixin, FormView):
    template_name = 'dc_management/export_request_form.html'
    form_class = ExportFileForm
    success_url = reverse_lazy('dc_management:all_projects')
    
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        post_data = self.request.POST

        # Check if user in project, then connect user to project
        
        prj = form.cleaned_data['project']
        requestor = form.cleaned_data['dcuser']
        files_requested = form.cleaned_data['files_requested']
        internal_destination = form.cleaned_data['internal_destination']
        record_author = self.request.user
        
        # if internal_destination supplied, request internal transfer
        # otherwise, use transfer.med to transfer to user directly.
        if internal_destination:
            pass
        else:
            pass
            
        # save access log instance
        self.logger = Access_Log(
                    record_author=record_author,
                    date_changed=date.today(),
                    dc_user=form.cleaned_data['dcuser'],
                    prj_affected=form.cleaned_data['project'],
                    change_type="AA",
        )
        self.logger.save()
        
        # send email
        send_mail(
            'Transfer files from {} to {}'.format(requestor, str(prj)),
            'Please add {} to project {} ({}) (name: {} IP:{}).'.format(requestor,
                                                                 str(prj),
                                                                 prj.host,
                                                                 prj.host.node,
                                                                 prj.host.ip_address,
                                                                 ),
            'from@example.com',
            ['oxpeter@gmail.com'],
            fail_silently=True,
        )
        return super(AddUserToProject, self).form_valid(form)


class ExportFromThisProject(ExportRequest):
    template_name = 'dc_management/addusertoproject.html'
    form_class = ExportFileForm
    success_url = reverse_lazy('dc_management:all_projects')
    
    def get_initial(self):
        initial = super(AddThisUserToProject, self).get_initial()
        # get the user from the url
        chosen_user = Person.objects.get(pk=self.kwargs['pk'])
        # update initial field defaults with custom set default values:
        initial.update({'dcuser': chosen_user, })
        return initial
    
########################################
######  GOVERNANCE RELATED VIEWS  ######
########################################


@login_required()
def pdf_view(request, pk):
    gov_doc = Governance_Doc.objects.get(pk=pk)
    # check to see if file is associated:
    try:
        gd_file = gov_doc.documentation.file
    except (FileNotFoundError, ValueError):
        raise Http404()

    # get standardized extension name to evaluate how to display:
    extension_raw = os.path.splitext(gov_doc.documentation.name)
    extension = extension_raw[1][1:].lower()

    # serve pdfs for viewing in the browser
    if extension == "pdf":
        try:
            return FileResponse(gov_doc.documentation.file,
                                content_type='application/pdf',
                                )
        except FileNotFoundError:
            raise Http404()

    # viewing of docx files
    elif extension == "docx":
        try:
            with open(str(gov_doc.documentation.file), 'rb') as fh:
                response = HttpResponse(fh.read(),
                                        content_type="application/vnd.ms-word",
                                        )
                response['Content-Disposition'] = f'inline; filename={os.path.basename(str(gov_doc.documentation.file))}'
                return response
            
        except FileNotFoundError:
            raise Http404()

    # download all other files for handling by the user.
    else:
        mime_type = guess_type(gov_doc.documentation.name)
        with open(str(gov_doc.documentation.file), 'rb') as fh:
            response = HttpResponse(fh.read(),
                                    content_type=mime_type,
                                    )
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(str(gov_doc.documentation.file))}'
            return response


class GovernanceView(LoginRequiredMixin, generic.DetailView):
    model = Governance_Doc
    template_name = 'dc_management/governance_meta.html'


class GovernanceCreate(LoginRequiredMixin, CreateView):
    model = Governance_Doc
    form_class = GovernanceDocForm
    template_name = 'dc_management/governance_form.html'

    def form_valid(self, form):
        # add the logged in user as the record author
        form.instance.record_author = self.request.user
        
        self.object = form.save(commit=False)
        return super(GovernanceCreate, self).form_valid(form)


class GovernanceUpdate(LoginRequiredMixin, UpdateView):
    model = Governance_Doc
    form_class = GovernanceDocForm
    template_name = 'dc_management/governance_form.html'

    def form_valid(self, form):
        # add the logged in user as the record author
        form.instance.record_author = self.request.user
        
        self.object = form.save(commit=False)
        return super(GovernanceUpdate, self).form_valid(form)

###############################
######  FINANCE  VIEWS   ######
###############################

class ProjectMonthlyBillView(LoginRequiredMixin, generic.DetailView):
    model = ProjectBillingRecord
    template_name = 'dc_management/project_billing.html'

class ProjectMonthlyBillGenerate(PermissionRequiredMixin, CreateView):
    model = ProjectBillingRecord
    form_class = ProjectBillingForm 
    permission_required = 'dc_management.add_projectbillingrecord'
    
    template_name = "dc_management/basic_crispy_form.html"
    
    def get_form_kwargs(self):
        kwargs = super( ProjectMonthlyBillGenerate, self).get_form_kwargs()
        # update the kwargs for the form init method with yours
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params
        return kwargs
    
    #success_url = reverse_lazy("dc_management:index" )
    # default success_url should be to the object page defined in model.
    def form_valid(self, form):
        self.object = form.save(commit=False)
        # update who last edited record
        self.object.record_author = self.request.user
        prj = Project.objects.get(pk=self.kwargs['ppk'])
        self.object.project = prj
        self.object.save()
        return super(ProjectMonthlyBillGenerate, self).form_valid(form)

class ProjectMonthlyBillGenerateOld(LoginRequiredMixin, CreateView):
    model = ProjectBillingRecord
    template_name = 'dc_management/basic_form.html'

    fields=['project',
            'billing_date',
            'base_value',
            'base_rate',
            'base_expense',
            'storage_1_type',
            'storage_1_value',
            'storage_1_rate',
            'storage_1_expense',
            'storage_2_type',
            'storage_2_value',
            'storage_2_rate',
            'storage_2_expense',
            'storage_3_type',
            'storage_3_value',
            'storage_3_rate',
            'storage_3_expense',
            'storage_4_type',
            'storage_4_value',
            'storage_4_rate',
            'storage_4_expense',
            'sw_value',
            'sw_rates',
            'sw_expense',
            'hosting_value',
            'hosting_rate',
            'hosting_expense',
            'db_value',
            'db_rate',
            'db_expense',
            'db_setup',
            'multiplier',
            'comments',
            ]
    def get_initial(self):
        initial = super(ProjectMonthlyBillGenerateOld, self).get_initial()
        # get the project
        chosen_project = Project.objects.get(pk=self.kwargs['pk'])
        
        # get the billable number of users
        user_number = chosen_project.billable_users().count()
        user_rate = UserCost.objects.get(user_quantity=user_number).user_cost
        
        # get the storage charges
        st1 = StorageCost.objects.get(storage_type__icontains="fileshare")
        st1_type = st1.storage_type
        st1_value = chosen_project.fileshare_storage
        st1_rate = st1.st_cost_per_gb 
        st1_expense = st1_rate * st1_value / 100
        
        st2 = StorageCost.objects.get(storage_type__icontains="backup")
        st2_type = st2.storage_type
        st2_value = chosen_project.backup_storage
        st2_rate = st2.st_cost_per_gb 
        st2_expense = st2_rate * st2_value / 100

        st3 = StorageCost.objects.get(storage_type__icontains="direct")
        st3_type = st3.storage_type
        st3_value = chosen_project.direct_attach_storage
        st3_rate = st3.st_cost_per_gb 
        st3_expense = st3_rate * st3_value / 100
        
        # get software expenses
        sw_str = "; ".join([sw.name for sw in chosen_project.software_requested.all()])
        
        sw_costs = []
        for sw in chosen_project.software_requested.all():
            sw_rate = SoftwareCost.objects.get(software=sw.pk).software_cost
            sw_cost = sw_rate * user_number
            sw_costs.append(sw_cost)
        x = np.array(sw_costs)
        sw_total = x[x != np.array(None)].sum()
        
        # get extra computation costs
        prj_erc = chosen_project.requested_cpu - 4
        erc = ExtraResourceCost.objects.get(extra_cpu=prj_erc)
        erc_cost = erc.cpu_cost
        
        # get db costs
        if chosen_project.db:
            db_value = 1
            db_rate = DatabaseCost.objects.get(pk=1).db_cost
        else:
            db_value = 0
            db_rate = 0
            
        # update initial field defaults with custom set default values:
        initial.update({'project': chosen_project, 
                        'billing_date':date.today(),
                        'base_value': user_number,
                        'base_rate': user_rate,
                        'base_expense': user_rate,
                        'storage_1_type':st1_type,
                        'storage_1_value':st1_value,
                        'storage_1_rate':st1_rate,
                        'storage_1_expense':st1_expense,
                        'storage_2_type':st2_type,
                        'storage_2_value':st2_value,
                        'storage_2_rate':st2_rate,
                        'storage_2_expense':st2_expense,
                        'storage_3_type':st3_type,
                        'storage_3_value':st3_value,
                        'storage_3_rate':st3_rate,
                        'storage_3_expense':st3_expense,
                        'sw_value':sw_str,
                        'sw_rates':"; ".join(["${:.2f}".format(c) for c in sw_costs]),
                        'sw_expense':sw_total,
                        'hosting_value':prj_erc,
                        'hosting_rate':erc_cost,
                        'hosting_expense':erc_cost,
                        'db_value':db_value,
                        'db_rate':db_rate,
                        'db_expense':db_rate,
                        'db_setup':0,
                        'multiplier':1,
                        'comments':"automatically generated.",  
        
        })
        return initial
    def form_valid(self, form):
        # add the logged in user as the record author
        form.instance.record_author = self.request.user
        
        self.object = form.save(commit=False)
        return super(ProjectMonthlyBillGenerateOld, self).form_valid(form)

class ProjectMonthlyBillCreate(LoginRequiredMixin, CreateView):
    model = ProjectBillingRecord
    template_name = 'dc_management/basic_form.html'
    fields=['project',
            'billing_date',
            'base_value',
            'base_rate',
            'base_expense',
            'storage_1_type',
            'storage_1_value',
            'storage_1_rate',
            'storage_1_expense',
            'storage_2_type',
            'storage_2_value',
            'storage_2_rate',
            'storage_2_expense',
            'storage_3_type',
            'storage_3_value',
            'storage_3_rate',
            'storage_3_expense',
            'storage_4_type',
            'storage_4_value',
            'storage_4_rate',
            'storage_4_expense',
            'sw_value',
            'sw_rates',
            'sw_expense',
            'hosting_value',
            'hosting_rate',
            'hosting_expense',
            'db_value',
            'db_rate',
            'db_expense',
            'db_setup',
            'multiplier',
            'comments',
            ]
    #template_name = 'dc_management/governance_form.html'
    # default success_url should be to the object page defined in model.
    def form_valid(self, form):
        # add the logged in user as the record author
        form.instance.record_author = self.request.user
        
        self.object = form.save(commit=False)
        return super(ProjectMonthlyBillCreate, self).form_valid(form)

class ProjectMonthlyBillUpdate(LoginRequiredMixin, CreateView):
    model = ProjectBillingRecord
    template_name = 'dc_management/basic_form.html'
    fields=['project',
            'billing_date',
            'base_value',
            'base_rate',
            'base_expense',
            'storage_1_type',
            'storage_1_value',
            'storage_1_rate',
            'storage_1_expense',
            'storage_2_type',
            'storage_2_value',
            'storage_2_rate',
            'storage_2_expense',
            'storage_3_type',
            'storage_3_value',
            'storage_3_rate',
            'storage_3_expense',
            'storage_4_type',
            'storage_4_value',
            'storage_4_rate',
            'storage_4_expense',
            'sw_value',
            'sw_rates',
            'sw_expense',
            'hosting_value',
            'hosting_rate',
            'hosting_expense',
            'db_value',
            'db_rate',
            'db_expense',
            'db_setup',
            'multiplier',
            'comments',
            ]
    #template_name = 'dc_management/governance_form.html'
    # default success_url should be to the object page defined in model.
    def form_valid(self, form):
        # add the logged in user as the record author
        form.instance.record_author = self.request.user
        
        self.object = form.save(commit=False)
        return super(ProjectMonthlyBillCreate, self).form_valid(form)

class ActiveProjectFinances(LoginRequiredMixin, generic.ListView):
    template_name = 'dc_management/finances_global.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        """Return  all active projects."""
        return Project.objects.all().order_by('dc_prj_id')
    
    def get_context_data(self, **kwargs):
        all_prjs = Project.objects.all().order_by('dc_prj_id')
        user_costs = UserCost.objects.all()
        sw_costs = SoftwareCost.objects.all()
        storage_costs = StorageCost.objects.all()
        
        # lists for passing to template:
        sw_list = []
        compute_list = []

        # get user costs before cycling through all projects, so we only touch this 
        # table once:
        #maxquant = user_costs.aggregate(Max('user_quantity'))
        max_rego = user_costs.order_by('-user_quantity')[0]
        set_cost = max_rego.user_cost
        set_cnt = max_rego.user_quantity

        # get the cost of adding additional users beyond the maximum number priced
        try:
            xtr_cost = user_costs.get(user_quantity=0).user_cost    
        except ObjectDoesNotExist:
            xtr_cost = 0
        
        for prj in all_prjs:
            # get costs for Primary data storage
            try:
                fs_rate = storage_costs.get(
                                storage_type__icontains="primary"
                                            ).st_cost_per_gb
            except ObjectDoesNotExist:
                fs_rate = 0          
            if prj.fileshare_storage:
                fss = prj.fileshare_storage
            else:
                fss = 0
            prj.fileshare_cost = fss * fs_rate

            # get costs for derivative data storage
            try:
                bkp_rate = storage_costs.get(
                                storage_type__icontains="derivative"
                                            ).st_cost_per_gb
            except ObjectDoesNotExist:
                bkp_rate = 0          
        
            if prj.fileshare_derivative:
                bs = prj.fileshare_derivative
            else:
                bs = 0
            prj.backup_cost = bs * bkp_rate
            
            # completed projects only have storage costs, ie no compute costs:
            if prj.status == 'CO':
                prj.direct_attach_cost = 0
                prj.user_cost = 0
                prj.software_cost = 0
                prj.db_cost = 0
                prj.host_cost = 0
                sw_list.append([]) # to keep the sw list in sync
                compute_list.append(((0, 'CPUs', 0.0), (0, 'GB RAM', 0.0)))
            else:
                # get cost for users.
                user_num = len(prj.users.all())
                
                # if a classroom, rate is set at the zero user rate for all users after PI
                if prj.env_type == 'CL':
                    # get the PI cost
                    try:
                        pi_cost = user_costs.get(user_quantity=1).user_cost    
                    except ObjectDoesNotExist:
                        pi_cost = 0
                    
                    # calculate total user cost for classroom:
                    ucost = (user_num - 1) * xtr_cost + pi_cost
                
                else:  # not a classroom
                    try:
                        ucost = user_costs.get(user_quantity=user_num).user_cost
                    except ObjectDoesNotExist:
                    
                        ucost = set_cost + xtr_cost * set_cnt
                
                prj.user_cost = ucost
            
                    
                # get cost for storage
                # direct attach
                try:
                    direct_rate = storage_costs.get(
                                    storage_type__icontains="direct"
                                                ).st_cost_per_gb
                except ObjectDoesNotExist:
                    direct_rate = 0          
            
                if not prj.direct_attach_storage:
                    das = 0
                else:
                    das = prj.direct_attach_storage
                prj.direct_attach_cost = das * direct_rate
            
                
            
                # get costs for software:
                prj_sw_list = []
                prj_sw_total = 0
                for sw in prj.software_installed.all():
                    try:
                        sw_cost = sw_costs.get(software=sw).software_cost
                    except ObjectDoesNotExist:
                        sw_cost = 0
                    prj_sw_list.append((sw.name, sw_cost * user_num))
                    prj_sw_total += sw_cost * user_num
                prj.software_cost = prj_sw_total
                sw_list.append(prj_sw_list)
            
            
                # db cost
                try:
                    db_rate = storage_costs.get(
                                    storage_type__icontains="db"
                                                ).st_cost_per_gb
                except ObjectDoesNotExist:
                    db_rate = 0          
            
                if prj.db:
                    db_size = prj.db.processor_num / 2
                else:
                    db_size = 0
                            
                prj.db_cost = db_size * db_rate

                # server cost
                try:
                    server_CPU_rate = storage_costs.get(
                                    storage_type__icontains="CPU"
                                                ).st_cost_per_gb
                except ObjectDoesNotExist:
                    server_CPU_rate = 0
                try:
                    server_RAM_rate = storage_costs.get(
                                    storage_type__icontains="RAM"
                                                ).st_cost_per_gb
                except ObjectDoesNotExist:
                    server_RAM_rate = 0          
            
                if prj.host and prj.requested_cpu:
                    xtra_cpu = prj.requested_cpu - 4
                    if xtra_cpu < 0:
                        xtra_cpu = 0
                else:
                    xtra_cpu = 0
                if prj.host and prj.requested_ram:
                    xtra_ram = prj.requested_ram - 16
                    if xtra_ram < 0:
                        xtra_ram = 0
                    total_xtra_ram = xtra_ram
                    xtra_ram = xtra_ram - xtra_cpu * 4 
                else: 
                    xtra_ram = 0
                    total_xtra_ram = 0
                prj.host_cost = max(xtra_cpu / 2 *
                                    server_CPU_rate,
                                    total_xtra_ram / 8 * 
                                    server_RAM_rate
                                )
                compute_list.append(((  xtra_cpu, 
                                        "CPUs", 
                                        xtra_cpu / 2 * server_CPU_rate
                                        ),
                                    (total_xtra_ram, 
                                    "GB RAM", 
                                    total_xtra_ram / 8 * server_RAM_rate),
                                    )
                )
                
            # update total cost:
            prj.project_total_cost = (  prj.backup_cost + 
                                         prj.fileshare_cost +
                                         prj.direct_attach_cost +
                                         prj.user_cost +
                                         prj.software_cost +
                                         prj.db_cost +
                                         prj.host_cost
            )
            
            #### SAVE ####
            
            prj.save()
           
        prj_data = list(zip(all_prjs, sw_list, compute_list))
        grand_total = list(Project.objects.all().aggregate(
                                            Sum('project_total_cost')
                        ).values())[0]   
        context = super(ActiveProjectFinances, self).get_context_data(**kwargs)
        context.update({
            'prj_data': prj_data,
            'grand_total_cost': grand_total,
        })
        return context

###########################
######  LOG  VIEWS   ######
###########################

class FileTransferView(LoginRequiredMixin, generic.DetailView):
    model = FileTransfer
    template_name = 'dc_management/file_transfer.html'

class FileTransferCreate(LoginRequiredMixin, CreateView):
    model = FileTransfer
    form_class = FileTransferForm
    template_name = "dc_management/basic_crispy_form.html"
    success_url = reverse_lazy('dc_management:sendtest')

    def form_valid(self, form):
        # clear email fields in session
        email_details = {   'subject'       :"na",
                            'body'          :"na",
                            'to_email'      :"na",
                            'subject_html'  :"na",
                            'body_html'     :"na",
        }
        self.request.session['email_json'] = json.dumps(email_details)

        # log who made the record
        form.instance.record_author = self.request.user
        
        # send email
        if form.instance.ticket:
            sbj_ticket = "Re: incident {} ".format(form.instance.ticket)
            toemail = 'support@med.cornell.edu'
        else:
            sbj_ticket = ""
            toemail = 'dcore-ticket@med.cornell.edu'
        
        if form.instance.file_num is None: 
            plural = "(s)"
        elif form.instance.file_num > 1:
            plural = "s"
        else:
            plural = ""
        
        if form.instance.source:
            src = f"from {form.instance.source.dc_prj_id} ({form.instance.source.host.node})"
            basepath = f"   \\\\hpr_datacore_{form.instance.source.dc_prj_id}\\"
            src_path = "\n".join(
                [ basepath + fn for fn in str(form.instance.filenames).split('\n') ]
                                ) 
        elif re.search("email|ticket", str(form.instance.transfer_method).lower()):
            src = "attached to this ticket"
            src_path = form.instance.filenames
        else:
            src = f"from {form.instance.transfer_method}"
            src_path = form.instance.filenames
            
        if form.instance.destination:
            dest = f"to {form.instance.destination.dc_prj_id} ({form.instance.destination.host.node})"
            basepath = f"   \\\\hpr_datacore_{form.instance.destination.dc_prj_id}\\"
            dest_path = "\n".join(
                [ basepath + fn for fn in str(form.instance.filepath_dest).split('\n') ]
                                ) 
        else: 
            dest = "to {} via {}".format(form.instance.external_destination, 
                                        form.instance.transfer_method,
                                        )
            dest_path = form.instance.filepath_dest
        
        subj_msg = f'{sbj_ticket}Transfer file{plural} {src} {dest}'
        body_msg = f'''Dear OPs,

Please copy the following {form.instance.file_num} file{plural} {src} {dest}:

_______
SOURCE: 
{src_path}

___________
DESTINATION: 
{dest_path}

{form.instance.comment}

Kind regards,
{self.request.user.get_short_name()}'''

        email_dict = {  'subject'       :subj_msg,
                        'body'          :body_msg,
                        'to_email'      :toemail,
                        'subject_html'  :quote(subj_msg),
                        'body_html'     :quote(body_msg),
        }
        
        self.request.session['email_json'] = json.dumps(email_dict)
        
        
        self.object = form.save(commit=False)
        return super(FileTransferCreate, self).form_valid(form)

class MigrationCreate(LoginRequiredMixin, CreateView):
    model = MigrationLog
    form_class = MigrationForm
    template_name = "dc_management/basic_form.html"

    def get_initial(self):
        initial = super(MigrationCreate, self).get_initial()
        # get the project from the url
        chosen_project = Project.objects.get(pk=self.kwargs['ppk'])
        try: 
            current_node = chosen_project.host
        except:
            current_node = None
        
        # update initial field defaults with custom set default values:
        initial.update({'project': chosen_project,
                        'node_origin':current_node,
        })
        return initial

    
    # default success_url should be to the object page defined in model.
    def form_valid(self, form):
        """
        On successful submission, update the node for the project. 
        """
        self.object = form.save(commit=False)
        
        # update who last edited record
        self.object.record_author = self.request.user
        
        # update the node the project is mounted on
        self.object.project.host = self.object.node_destination
        self.object.project.save()
        
        # save migration log changes
        self.object.save()
        return super(MigrationCreate, self).form_valid(form)

class MigrationUpdate(LoginRequiredMixin, UpdateView):
    model = MigrationLog
    form_class = MigrationForm
    template_name = "dc_management/basic_form.html"
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        # if all dates filled, change onboarding project status to running
        if self.object.access_date and self.object.envt_date and self.object.data_date:
            if self.object.project.status == 'ON':
                self.object.project.status = 'RU'
                self.object.project.save()
                
        return super(MigrationUpdate, self).form_valid(form)

class MigrationDetailView(LoginRequiredMixin, generic.DetailView):
    model = MigrationLog
    template_name = 'dc_management/migration_record.html'

class AddProjectComment(CreateView):
    template_name = 'dc_management/comment_form.html'
    form_class = CommentForm

##############################
######  SEARCH  VIEWS   ######
##############################

class FullSearch(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dc_management/search_results.html'
    def post(self, request, *args, **kwargs):
        st = request.POST['srch_term']
        qs_prj = Project.objects.all()
        qs_prj =  qs_prj.filter(Q(dc_prj_id__icontains=st) | 
                                Q(title__icontains=st) | 
                                Q(nickname__icontains=st) |
                                Q(dynamic_comments__comment__icontains=st)
        ).order_by('dc_prj_id').distinct()
        qs_usr = Person.objects.all()
        qs_usr = qs_usr.filter( Q(first_name__icontains=st) |
                                Q(last_name__icontains=st) |
                                Q(cwid__icontains=st) |
                                Q(comments__icontains=st)
        ).order_by('pk').distinct()
        qs_gov = Governance_Doc.objects.all()
        qs_gov = qs_gov.filter( Q(doc_id__icontains=st) |
                                Q(governance_type=st) |
                                Q(comments__icontains=st)
        ).order_by('pk').distinct()
        context = { "search_str" : st,
                    "qs_prj": qs_prj,
                    "qs_usr": qs_usr,
                    "qs_gov": qs_gov,
        }
        return render(request, self.template_name, context)
        
    
