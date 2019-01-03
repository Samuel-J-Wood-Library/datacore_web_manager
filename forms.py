import datetime

from dal import autocomplete

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset, HTML
from crispy_forms.bootstrap import Field

from django import forms
from django.db.models import Q

from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.forms.widgets import SelectDateWidget, CheckboxInput

from .models import Server, Project, DC_User, Software, Software_Log, Project
from .models import DCUAGenerator, Storage_Log, StorageCost, Governance_Doc
from .models import FileTransfer, MigrationLog, CommentLog



"""
class CommentForm(forms.Form):
    comment = forms.TextField(widget=forms.Textarea)
"""
class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentLog
        fields = [ 'comment', ]
    
        
class AddUserToProjectForm(forms.Form):
    dcusers = forms.ModelMultipleChoiceField(
                                queryset=DC_User.objects.all(), 
                                label="Data Core User",
                                widget = autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-user'
                                        ),
                                )
    project = forms.ModelChoiceField(
                                queryset=Project.objects.exclude(status="CO"), 
                                label="Project",
                                widget = autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-project'
                                        ),
                                )
    email_comment = forms.CharField(required=False, label="Comment for SN ticket",)                            
    comment = forms.CharField(required=False, label="Comment for db log",)
    class Meta:
        widgets =  {'dcusers' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-user'
                                        ),
                    'project' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-project'
                                        ),
                    }
    
class RemoveUserFromProjectForm(forms.Form):
    dcusers = forms.ModelMultipleChoiceField(
                                queryset=DC_User.objects.none(), 
                                label="Data Core User",
                                    )
    project = forms.ModelChoiceField(
                                queryset=Project.objects.all(), 
                                label="Project"
                                    )
    email_comment = forms.CharField(required=False, label="Comment for SN ticket",)                            
    comment = forms.CharField(required=False, label="Comment for db log",)
    
    
    # the project_users list is now available, add it to the instance data
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('project_users')
        super(RemoveUserFromProjectForm, self).__init__(*args, **kwargs)
        self.fields['dcusers'].queryset = qs
    class Meta:
        widgets = {'project' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-project'
                                        ),
                    }
    
class ExportFileForm(forms.Form):
    dcuser = forms.ModelChoiceField(
                                queryset=DC_User.objects.all(), 
                                label="Data Core User"
                                    )
    project = forms.ModelChoiceField(
                                queryset=Project.objects.exclude(status="CO"), 
                                label="Project"
                                    )
    internal_destination = forms.ModelChoiceField(
                                queryset=Project.objects.exclude(status="CO"), 
                                label="Internal transfer",
                                required=False,
                                    )
    files_requested = forms.CharField(required=False, label="Location of requested files")
    comment = forms.CharField(required=False, label="Comment")
    
    # the project_users list is now available, add it to the instance data
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('project_users')
        super(ExportFileForm, self).__init__(*args, **kwargs)
        self.fields['dcuser'].queryset = qs

class CreateDCAgreementURLFormOld(forms.Form):
    ticket = forms.CharField(required=False, 
                              label="SN Ticket",
                            )
    startdate = forms.CharField(required=True, 
                                label="Start Date", 
                                initial=datetime.datetime.now().strftime("%m/%d/%Y"),
                                )
    enddate = forms.CharField(required=True, 
                            label="End Date",
                            initial=(datetime.datetime.now() + 
                                     datetime.timedelta(days=365)
                                        ).strftime("%m/%d/%Y"),
                                )
    folder1 = forms.CharField(required=True, 
                              label="Folder 1",
                              initial="dcore-prj00XX-SOURCE",)
    folder2 = forms.CharField(required=False, 
                              label="Folder 2",
                              initial="dcore-prj00XX-SHARE",)
    folder3 = forms.CharField(required=False, 
                              label="Folder 3",
                              initial="WorkArea-<user CWID>",)
    folder4 = forms.CharField(required=False, label="Folder 4")
    folder5 = forms.CharField(required=False, label="Folder 5")
    folder6 = forms.CharField(required=False, label="Folder 6")
    folder7 = forms.CharField(required=False, label="Folder 7")

class CreateDCAgreementURLForm(forms.ModelForm):
    class Meta:
        model = DCUAGenerator
        fields = [  'project',
                    'ticket',
                    'startdate',
                    'enddate',
                    'folder1',
                    'folder2',
                    'folder3',
                    'folder4',
                    'folder5',
                    'folder6', 
                    'folder7',
        ]
        help_texts = {'ticket' : _('This will send the DCUA results to ServiceNow') }
        widgets =   {'project' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-project'
                                        ),
                    }

class StorageChangeForm(forms.ModelForm):
    
    class Meta:
        model = Storage_Log
        fields = [ 'sn_ticket',
                    'date_changed',
                    'project',
                    'storage_amount',
                    'storage_type',
                    'comments',
        ]
    # limit the choices in storage_type:
    def __init__(self, *args, **kwargs):
        qs = StorageCost.objects.filter(
                                Q(storage_type__icontains='direct') |
                                Q(storage_type__icontains='backup') |
                                Q(storage_type__icontains='share') 
                        )
        # ppk = kwargs.pop('ppk', None)
        # prj = Project.objects.get(pk=ppk)
        super(StorageChangeForm, self).__init__(*args, **kwargs)
        self.fields['storage_type'].queryset = qs
        #self.fields['project'].queryset = prj

class GovernanceDocForm(forms.ModelForm):
    class Meta:
        model = Governance_Doc
        fields = [  'sn_ticket',
                    'doc_id',
                    'date_issued',
                    'expiry_date',
                    'users_permitted',
                    'access_allowed',
                    'governance_type',
                    'defers_to_doc',
                    'supersedes_doc',
                    'project',  
                    'documentation',
                    'isolate_data',
        ]
        widgets = {
                    'users_permitted' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-user'
                                        ),
                    'defers_to_doc'  :  autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-govdoc'
                                        ),
                    'supersedes_doc' :  autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-govdoc'
                                        ),
                    'project' :         autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-project'
                                        ),
        }

########################
### Layout templates ###
########################
project_leaders = Div(
                        Div('pi',
                            css_class='col-xs-6',
                        ),
                        Div('prj_admin',
                            css_class='col-xs-6',
                        ),
                        css_class="row"
                    )

environment_type = Div(
                        Div('env_type',
                            css_class='col-xs-4',
                        ),
                        Div('env_subtype',
                            css_class='col-xs-4',
                        ),
                        Div('status',
                            css_class='col-xs-4',
                        ),
                        css_class="row"
                    )
project_governance = Layout(
                            Fieldset('<div class="alert alert-info">Governance</div>',
                                    Div(
                                            Div('open_allowed',
                                                css_class='col-xs-4',
                                            ),
                                            Div('open_enabled',
                                                css_class='col-xs-4',
                                            ),
                                            Div('isolate_data',
                                                css_class='col-xs-4',
                                            ),
                                            css_class="row",
                                    ),
                                    style="font-weight: bold;"
                            ),
)
project_compute = Div(
                        Div('requested_ram',
                            css_class='col-xs-6',
                        ),
                        Div('requested_cpu',
                            css_class='col-xs-6',
                        ),
                        css_class="row"
)
project_storage = Div(
                        Div('fileshare_storage',
                            css_class='col-xs-4',
                        ),
                        Div('direct_attach_storage',
                            css_class='col-xs-4',
                        ),
                        Div('backup_storage',
                            css_class='col-xs-4',
                        ),
                        css_class="row"
)  
project_access = Div(
                    Div('myapp',
                        css_class='col-xs-3',
                        style='font-size:100%;font-weight: bold;'
                    ),
                    Div('prj_dns',
                        css_class='col-xs-9',
                    ),
                    css_class="row"
)     
project_dates = Layout(Fieldset('<div class="alert alert-info">Project dates</div>',
                        Div(
                                Div('requested_launch',
                                    css_class='col-xs-6',
                                ),
                                Div('expected_completion',
                                    css_class='col-xs-6',
                                ),
                                css_class="row"
                        ),
                        Div(
                                Div('wrapup_ticket',
                                    css_class='col-xs-6',
                                ),
                                Div('wrapup_date',
                                    css_class='col-xs-6',
                                ),
                                css_class="row"
                        ),
                        Div(
                                Div('completion_ticket',
                                    css_class='col-xs-6',
                                ),
                                Div('completion_date',
                                    css_class='col-xs-6',
                                ),
                                css_class="row"
                        ),

                        style="font-weight: bold; ",
                ),  
)           
                            
class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-file-transfer-form'
        self.helper.form_method = 'post'
        #self.helper.form_action = reverse_lazy('dc_management:sendtest')
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
                Fieldset('<div class="alert alert-info">Project details</div>',
                        'dc_prj_id',
                        'title', 
                        'nickname',
                        project_leaders,
                        'users',
                        environment_type,
                        style="font-weight: bold;",
                ),
                project_governance,
                Fieldset('<div class="alert alert-info">Environment</div>',
                        project_compute,
                        project_storage,
                        'software_requested',
                        project_access,
                        'db',
                        style="font-weight: bold;"
                ),
                project_dates,
                'sn_tickets',
                                
                                
                               
                                
        ) 
    class Meta:
        model = Project
        fields = [  'dc_prj_id',
                    'title', 
                    'nickname', 
                    'isolate_data', 
                    'open_allowed', 
                    'open_enabled',
                    'fileshare_storage', 
                    'direct_attach_storage', 
                    'backup_storage',
                    'requested_ram', 
                    'requested_cpu', 
                    'users',
                    'pi',
                    'prj_admin',
                    'software_requested',
                    'env_type',
                    'env_subtype',
                    'requested_launch',
                    'expected_completion',
                    'status',
                    'sn_tickets',
                    'completion_ticket',
                    'completion_date',
                    'prj_dns',
                    'myapp',
                    'db',
                ]

        widgets =  {'users' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-user'
                                        ),
                    'pi' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-user'
                                        ),
                    'host' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-node'
                                        ),
                    'db' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-node'
                                        ),
                    'software_requested' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-software'
                                        ),
                    'myapp' : CheckboxInput(),                
                    }

class ProjectUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-file-transfer-form'
        self.helper.form_method = 'post'
        #self.helper.form_action = reverse_lazy('dc_management:sendtest')
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
                Fieldset('<div class="alert alert-info">Project details</div>',
                        'title', 
                        'nickname',
                        project_leaders,
                        environment_type,

                        style="font-weight: bold;",
                ),
                project_governance,
                Fieldset('<div class="alert alert-info">Environment</div>',
                        project_compute,
                        'software_requested',
                        project_access,
                        'db',
                        style="font-weight: bold;"
                ),
                project_dates,
        )
        
    
    class Meta:
        model = Project
        fields = [  'title', 
                    'nickname', 
                    'isolate_data', 
                    'open_allowed', 
                    'open_enabled',
                    'requested_ram', 
                    'requested_cpu', 
                    'pi',
                    'prj_admin',
                    'software_requested',
                    'env_type',
                    'env_subtype',
                    'requested_launch',
                    'expected_completion',
                    'status',
                    'wrapup_ticket',
                    'wrapup_date',
                    'completion_ticket',
                    'completion_date',
                    'host',
                    'prj_dns',
                    'myapp',
                    'myapp',
                    'db',
                ]

        widgets =  {'users' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-user'
                                        ),
                    'pi' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-user'
                                        ),
                    'prj_admin' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-user'
                                        ),                    
                    'host' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-node'
                                        ),
                    'db' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-node'
                                        ),
                    'software_requested' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-software'
                                        ),
                    'myapp' : CheckboxInput(),  
                    }

class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = [  'status', 
                    'function', 
                    'machine_type', 
                    'vm_size', 
                    'backup',
                    'operating_sys',
                    'node',
                    'sub_function',
                    'name_address',
                    'ip_address',
                    'processor_num',
                    'ram',
                    'disk_storage',
                    'other_storage',  
                    'software_installed',
                    'connection_date',
                    'firewalled',
                    'dns_name',
                    'host',
                    'comments',
                ]

        widgets =  {'software_installed' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-software'
                                        ),
                                    
                    }

class ServerUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Server
        fields = [  'status', 
                    'function', 
                    'machine_type', 
                    'vm_size', 
                    'backup',
                    'operating_sys',
                    'node',
                    'sub_function',
                    'name_address',
                    'ip_address',
                    'processor_num',
                    'ram',
                    'disk_storage',
                    'other_storage',  
                    'software_installed',
                    'firewalled',
                    'connection_date',
                    'dns_name',
                    'host',
                    'comments',
                ]

        widgets =  {'software_installed' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-software'
                                        ),
                                    
                    }
                       
class AddSoftwareToProjectForm(forms.ModelForm):
    
    class Meta:
        model = Software_Log
        fields = [  'software_changed',
                    'applied_to_prj',
                    'applied_to_node',
                    'applied_to_user',
                    'change_type',
                ]
        labels = {
            'software_changed': _('Software'),
            'applied_to_prj': _('Project applied to'),
            'applied_to_node': _('Node applied to'),
            'applied_to_user': _('User applied to'),
            'change_type': _('Add or remove?'),            
        }
        help_texts = {
            'applied_to_node': _('Only select this if you are not applying directly to a project.'),
        }
        widgets =  {'software_changed' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-software'
                                        ),
                    'applied_to_prj' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-project'
                                        ),
                    'applied_to_node' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-node'
                                        ),
                    'applied_to_user' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-user'
                                        ),
                                    
                    }

class BulkUserUploadForm(forms.Form):
    # To be updated for bulk upload of users:
    users_csv = forms.FileField(
                                label="CSV file of users for upload"
                                    )
    comment = forms.CharField(required=False, 
                    label="Comment (will be appended to all users' comment fields)")
 
class FileTransferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FileTransferForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-file-transfer-form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse_lazy('dc_management:sendtest')
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
                Fieldset('File transfer request',
                        Div(
                                Div('change_date',
                                    css_class='col-xs-4',
                                ),
                                Div('requester',
                                    css_class='col-xs-4',
                                ),
                                Div('ticket',
                                    css_class='col-xs-4',
                                ),
                                css_class="row"
                        ),
                        style="font-weight: bold;"
                ),
                Fieldset('Data Source ⇨ Destination',
                            Div(
                                Div('source', 
                                    title="Indicate origin of data (eg abc2001@med).",
                                    css_class="row",
                                ),
                                Div('external_source', 
                                    title="Indicate destination (eg abc2001@med).",
                                    css_class="row",
                                ),
                                Div('filenames',
                                    title="List the full directory path to all files.",
                                    css_class="row",
                                ),
                                css_class='col-xs-5 alert alert-info',
                            ),
                            Div('transfer_method',
                                HTML('⇨'),
                                css_class="col-xs-2 text-center align-bottom row"
                            ),
                            Div(
                                Div(  'destination', 
                                    label='Data Core source',
                                    title="Use if source is a dcore project.",
                                    css_class="row",
                                ),
                                Div('external_destination', 
                                    title="Use if destination is a dcore project.",
                                    css_class="row",
                                ),
                                Div('filepath_dest',
                                    title='List the full path to where files are being transferred. Write "transfer.med" or similar if exporting to user.',
                                    css_class='row',
                                ),
                                css_class='col-xs-5 alert alert-info',
                            ),
                            style="color: blue;font-weight: bold;"
                            
                ),
                Fieldset('File information',
                            Div(
                                Div('file_num',
                                    css_class='col-xs-6',
                                ),
                                Div('file_num_unknown',
                                    css_class='col-xs-6',
                                ),
                                css_class="row"
                            ),
                            Div(
                                Div('data_type',
                                    css_class='col-xs-6',
                                ),
                                Div('reviewed_by',
                                    css_class='col-xs-6',
                                ),
                                css_class="row"
                            ),
                            style="font-weight: bold;"
                ),
                
                'comment',
        )
        
        
    class Meta:
        model = FileTransfer
        fields = [  'change_date',
                    'ticket',
                    'external_source',
                    'source',
                    'external_destination',
                    'destination',
                    'transfer_method',
                    'requester',
                    'filenames',
                    'filepath_dest',
                    'file_num',
                    'file_num_unknown',
                    'data_type',
                    'reviewed_by',
                    'comment',
                ]

        widgets =  {'source' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-project'
                                        ),
                    'destination' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-project'
                                        ),
                    'requester' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-user'
                                        ),
                    'file_num_unknown' : CheckboxInput(),                   
                    }

class MigrationForm(forms.ModelForm):
    
    class Meta:
        model = MigrationLog
        fields = [  'project',
                    'node_origin', 
                    'node_destination', 
                    'access_ticket', 
                    'access_date', 
                    'envt_ticket',
                    'envt_date', 
                    'data_ticket', 
                    'data_date',
                    'comments',
                ]

        widgets =  {'project' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-project'
                                        ),
                    'node_origin' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-node'
                                        ),
                    'node_destination' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-node'
                                        ),
                    }

class MigrationNewForm(forms.ModelForm):
    
    class Meta:
        model = MigrationLog
        fields = [  'project',
                    'node_origin', 
                    'node_destination', 
                    'comments',
                ]

        widgets =  {'project' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-project'
                                        ),
                    'node_origin' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-node'
                                        ),
                    'node_destination' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-node'
                                        ),
                    }
