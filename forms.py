import datetime
import numpy as np
import re

from dal import autocomplete

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset, HTML

from django import forms
from django.db.models import Q

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.forms.widgets import CheckboxInput

from .models import Server, Person, Software_Log, Project
from .models import DCUAGenerator, Storage_Log, StorageCost, Governance_Doc
from .models import FileTransfer, MigrationLog, CommentLog, Storage
from .models import DataCoreUserAgreement
from .models import ProjectBillingRecord, UserCost, SoftwareCost, DatabaseCost
from .models import ExtraResourceCost, SFTP

"""
class CommentForm(forms.Form):
    comment = forms.TextField(widget=forms.Textarea)
"""


class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentLog
        fields = ['comment', ]

class AddUserToProjectForm(forms.Form):
    dcusers = forms.ModelMultipleChoiceField(
                                queryset=Person.objects.all(), 
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
    locations_allowed =  forms.CharField(required=False, 
                                         label="Locations user is allowed to access",
                                         initial=mark_safe("prj-SOURCE\nprj-SHARED\nWorkArea"),
                                         widget=forms.Textarea,
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
                                queryset=Person.objects.none(), 
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
                                queryset=Person.objects.all(), 
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
                                Q(storage_type__icontains='derivative') |
                                Q(storage_type__icontains='primary') |
                                Q(storage_type__icontains='archiv') 
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
def layout_simple_two(field1, field2):
    form = Div(
                Div(field1,
                    css_class='col-6',
                ),
                Div(field2,
                    css_class='col-6',
                ),
                css_class="row"
            )    
    return form

def layout_three_equal(ONE,TWO,THREE):
    div_thirds = Div(
                        Div(ONE,
                            css_class='col-4',
                        ),
                        Div(TWO,
                            css_class='col-4',
                        ),
                        Div(THREE,
                            css_class='col-4',
                        ),
                        css_class="row"
    )
    return div_thirds

def layout_four_accounting(ONE,TWO,THREE,FOUR):
    div_quarts = Div(
                        Div(ONE,
                            css_class='col-5',
                        ),
                        Div(TWO,
                            css_class='col-2',
                        ),
                        Div(THREE,
                            css_class='col-2',
                        ),
                        Div(FOUR,
                            css_class='col-3'
                        ),
                        css_class="row"
    )
    return div_quarts

def layout_four_equal(ONE,TWO,THREE,FOUR):
    div_quarts = Div(
                        Div(ONE,
                            css_class='col-3',
                        ),
                        Div(TWO,
                            css_class='col-3',
                        ),
                        Div(THREE,
                            css_class='col-3',
                        ),
                        Div(FOUR,
                            css_class='col-3'
                        ),
                        css_class="row"
    )
    return div_quarts
            
project_leaders = Div(
                        Div('pi',
                            css_class='col-6',
                        ),
                        Div('prj_admin',
                            css_class='col-6',
                        ),
                        css_class="row"
                    )

environment_type = Div(
                        Div('env_type',
                            css_class='col-4',
                        ),
                        Div('env_subtype',
                            css_class='col-4',
                        ),
                        Div('status',
                            css_class='col-4',
                        ),
                        css_class="row"
                    )
project_governance = Layout(
                            Fieldset('<div class="alert alert-info">Governance</div>',
                                    Div(
                                            Div('open_allowed',
                                                css_class='col-4',
                                            ),
                                            Div('open_enabled',
                                                css_class='col-4',
                                            ),
                                            Div('isolate_data',
                                                css_class='col-4',
                                            ),
                                            css_class="row",
                                    ),
                                    style="font-weight: bold;"
                            ),
)
project_compute = Div(
                        Div('requested_ram',
                            css_class='col-6',
                        ),
                        Div('requested_cpu',
                            css_class='col-6',
                        ),
                        css_class="row"
)

project_access = Div(
                    Div('myapp',
                        css_class='col-3',
                        style='font-size:100%;font-weight: bold;'
                    ),
                    Div('prj_dns',
                        css_class='col-9',
                    ),
                    css_class="row"
)     
project_dates = Layout(Fieldset('<div class="alert alert-info">Project dates</div>',
                        Div(
                                Div('start_date',
                                    css_class='col-6',
                                ),
                                css_class="row"
                        ),
                        Div(
                                Div('requested_launch',
                                    css_class='col-6',
                                ),
                                Div('expected_completion',
                                    css_class='col-6',
                                ),
                                css_class="row"
                        ),
                        Div(
                                Div('wrapup_ticket',
                                    css_class='col-6',
                                ),
                                Div('wrapup_date',
                                    css_class='col-6',
                                ),
                                css_class="row"
                        ),
                        Div(
                                Div('completion_ticket',
                                    css_class='col-6',
                                ),
                                Div('completion_date',
                                    css_class='col-6',
                                ),
                                css_class="row"
                        ),

                        style="font-weight: bold; ",
                ),  
)           

def get_storage_costs(storage_type, project):
    st = StorageCost.objects.get(storage_type__icontains=storage_type)
    st_type = st.storage_type               # kind of storage 
    
    if storage_type == 'archiv':
        st_value = project.backup_storage
    elif storage_type == 'direct':
        st_value = project.direct_attach_storage
    elif storage_type == 'primary':
        st_value = project.fileshare_storage
    elif storage_type == 'derivative':
        st_value = project.fileshare_derivative
    else:
        st_value = 0
    
    st_rate = st.st_cost_per_gb                 # rate per 100 GB
    st_rate =  (st_rate if st_rate else 0 )     # remove null values
    st_value =  (st_value if st_value else 0 )  # remove null values
    st_expense = st_rate * st_value             # cost
    return st_type, st_value, st_rate, st_expense

class ProjectBillingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        ppk = kwargs.pop('ppk', None)
        super(ProjectBillingForm, self).__init__(*args, **kwargs)
        
        # get project details from URL:
        #ppk = kwargs.pop('ppk', None)
        #prj = Project.objects.get(pk=ppk)
        
        #ppk = self.kwargs['ppk']
        prj = Project.objects.get(pk=ppk)
        
        self.fields['billing_date'].initial = datetime.date.today()
        
        # get the billable number of users
        user_number = prj.billable_users().count()
        self.fields['base_value'].label = "Number of users"
        self.fields['base_value'].initial = user_number

        user_rate = UserCost.objects.get(user_quantity=user_number).user_cost
        self.fields['base_rate'].initial = user_rate
        self.fields['base_expense'].initial = user_rate
        
        # get the storage charges
        st1_type, st1_value, st1_rate, st1_expense = get_storage_costs("primary", prj)
        self.fields['storage_1_type'].initial    = st1_type
        self.fields['storage_1_value'].initial   = st1_value
        self.fields['storage_1_rate'].initial    = st1_rate
        self.fields['storage_1_expense'].initial = st1_expense
        
        st2_type, st2_value, st2_rate, st2_expense = get_storage_costs("derivative", prj)
        self.fields['storage_2_type'].initial    = st2_type
        self.fields['storage_2_value'].initial   = st2_value
        self.fields['storage_2_rate'].initial    = st2_rate
        self.fields['storage_2_expense'].initial = st2_expense

        st3_type, st3_value, st3_rate, st3_expense = get_storage_costs("direct", prj)
        self.fields['storage_3_type'].initial    = st3_type
        self.fields['storage_3_value'].initial   = st3_value
        self.fields['storage_3_rate'].initial    = st3_rate
        self.fields['storage_3_expense'].initial = st3_expense

        st4_type, st4_value, st4_rate, st4_expense = get_storage_costs("archiv", prj)
        self.fields['storage_4_type'].initial    = st4_type
        self.fields['storage_4_value'].initial   = st4_value
        self.fields['storage_4_rate'].initial    = st4_rate
        self.fields['storage_4_expense'].initial = st4_expense
        
        # get software expenses
        sw_str = "; ".join([sw.name for sw in prj.software_installed.all()])
        
        sw_costs = []
        for sw in prj.software_installed.all():
            sw_rate = SoftwareCost.objects.get(software=sw.pk).software_cost
            sw_cost = sw_rate * user_number
            sw_costs.append(sw_cost)
        x = np.array(sw_costs)
        
        sw_rates = "; ".join(["${:.2f}".format(c) for c in sw_costs])
        sw_total = x[x != np.array(None)].sum()
                              
        self.fields['sw_value'].initial   = sw_str
        self.fields['sw_rates'].initial   = sw_rates
        self.fields['sw_expense'].initial = sw_total

        # get extra computation costs
        if prj.requested_cpu and prj.requested_cpu > 4:
            prj_erc = prj.requested_cpu - 4
            erc = ExtraResourceCost.objects.get(extra_cpu=prj_erc)
            erc_cost = erc.cpu_cost
        else:
            prj_erc = 0
            erc_cost = 0
        
       
        self.fields['hosting_value'].initial   = prj_erc    # extra CPU computation
        self.fields['hosting_value'].label   = "Additional CPU"    # extra CPU computation
        self.fields['hosting_rate'].initial    = erc_cost   
        self.fields['hosting_expense'].initial = erc_cost

        # get db costs
        if prj.db:
            db_value = 1
            db_rate = DatabaseCost.objects.get(pk=1).db_cost
        else:
            db_value = 0
            db_rate = 0
                                   
        self.fields['db_value'].initial     = db_value  # flat rate for db hosting
        self.fields['db_rate'].initial      = db_rate   
        self.fields['db_expense'].initial   = db_rate
        self.fields['db_setup'].initial     = 0         # one time setup fee $500
        
        self.fields['multiplier'].initial   = 1         # for charging multiple months
        self.fields['account'].initial      = prj.account_number
        
        
        self.helper = FormHelper()
        self.helper.form_id = 'ProjectBillingForm'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
                    Fieldset(
                            """ 
                            <div class="alert alert-info">
                                Billing record for {}
                            </div>
                            """.format(prj),
                        'billing_date',
                    ),
                    Fieldset(
                        "Curation, administration and basic hosting charges",
                        layout_three_equal('base_value',
                                            'base_rate',
                                            'base_expense',
                        ),
                        
                    ),
                    Fieldset(
                        "Storage charges",
                        layout_four_accounting('storage_1_type',
                                                'storage_1_value',
                                                'storage_1_rate',
                                                'storage_1_expense',
                        ),
                        layout_four_accounting('storage_2_type',
                                                'storage_2_value',
                                                'storage_2_rate',
                                                'storage_2_expense',
                        ),
                        layout_four_accounting('storage_3_type',
                                                'storage_3_value' ,
                                                'storage_3_rate',
                                                'storage_3_expense',
                        ),
                        layout_four_accounting('storage_4_type',
                                                'storage_4_value',
                                                'storage_4_rate',
                                                'storage_4_expense',
                        ),
                    ),
                    Fieldset(    
                        "Software charges",
                        layout_simple_two('sw_value','sw_rates',),
                        'sw_expense',
                    ),
                    Fieldset(
                        "Additional hosting and database charges",                    
                        layout_three_equal('hosting_value',
                                            'hosting_rate',
                                            'hosting_expense',
                        ),
                        layout_four_equal('db_value',
                                            'db_rate',
                                            'db_expense',
                                            'db_setup',
                        ),
                        'multiplier',
                        'account',
                    ),
        )
        
    class Meta:
        model = ProjectBillingRecord
        fields = [      'billing_date',
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
                        'storage_3_value' ,
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
                        'account',
                ]

class DCUAForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DCUAForm, self).__init__(*args, **kwargs)
        self.fields['consent_access'].label = "I consent to the above conditions (enter initials):"
        self.fields['consent_usage'].label = "I consent to the above conditions (enter initials):"
        self.fields['signature_date'].label = "Date (MM/DD/YYYY):"
        self.fields['signature_date'].initial = datetime.datetime.today()
        self.fields['signature_name'].label = "Full Name:"
        self.fields['signature_title'].label = "Title:"
        self.fields['acknowledge_patching'].label = "Initials:"
        
        self.helper = FormHelper()
        self.helper.form_id = 'DCUAForm'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
                    Fieldset(
            f""" <div class="alert alert-info">
                    Data Core User Agreement for {self.instance.attestee} on 
                    {self.instance.project}
                </div>
            """,
            HTML("""
                <p>This agreement is between {{datacoreuseragreement.attestee}} and the Data Core at WCM. This agreement is effective as of {{ datacoreuseragreement.start_date }} and expires on {{ datacoreuseragreement.end_date }} unless extended by mutual consent of the data distributor and Data Core.</p>
                <p>1. {{ datacoreuseragreement.attestee }} is authorized to access only the data residing in the folders (and subfolders) on the Data Core computing system listed below, in accordance with the data user permissions set by the Data Core computing system administrator. Data are not to be stored in any other folder (including subfolders) than those listed below:</p> 
                <p>{{ datacoreuseragreement.locations_allowed | linebreaks }}</p>             
            """),
                            'consent_access',
                            HTML(
            f"""
            <p>2. When required by the Data Use Agreement, the Data Core Data Custodian will disclosure proof any files uploaded to, or downloaded from, the Data Core computing system. Such files will be delivered by secure WS-FTP to authorized IP addresses, or other methods considered appropriate by Data Core staff to ensure compliance with the current Data Use Agreement.</p>
            <p>3. Confidential data on the Data Core system may only be used for non-proprietary scientific research.</p>
            <p>4. {self.instance.attestee} agrees not to allow anyone else to use their credentials to access the Data Core computing system.</p>
            <p>5. {self.instance.attestee} agrees not to attempt to circumvent or disable any of the security systems in place on the Data Core computing system and to report to the Data Core Data Custodian any attempts to circumvent or disable these systems that are known to them.</p>
            <p>6. {self.instance.attestee} agrees to inform the Data Provider and Data Core staff of any change in their employment or WCM status, within the timeframe specified by the DUA, or 30 days, whichever is shorter. </p>
            <p>7. If {self.instance.attestee} is a primary investigator or co-investigator and the restricted data are subject to review by the WCM Institutional Review Board (IRB) for Human Participants, he/she acknowledges that IRB approval will be maintained for the duration of the project.</p>
            <p>8. {self.instance.attestee} acknowledges that the Data Core may suspend or terminate access privileges at any time in order to protect the integrity of the confidential data.</p>
            """
                            ),
                            'consent_usage',
                            HTML("The foregoing has been agreed to and accepted by the person whose name appears below:"),
                            'signature_name',
                            'signature_title',
                            'signature_date',
                            style="font-weight:normal;",
                    ),
                    Fieldset("""<div class="alert alert-info">Acknowledgement of monthly patching</div>""",
                             HTML("""
            <p>Monthly patching of all ITS servers occurs the <strong>third Saturday</strong> of every month, from <strong>6am - noon</strong>. This includes Data Core on-premise servers and will interrupt any ongoing analyses at that time. Please ensure you have saved any work you have prior to the third Saturday of each month at 6am in order to prevent loss of work.</p>
            <p>I acknowledge and understand the Monthly Patching Schedule and its implications for my work in the Data Core:</p>
            """),
                            'acknowledge_patching',                        
                            style="font-weight: normal;",
                    ),
        )
    
    class Meta:
        model = DataCoreUserAgreement
        fields = [  'consent_access',
                    'consent_usage',
                    'signature_date',
                    'signature_name',
                    'signature_title',
                    'acknowledge_patching',
                ]

class DCUAPrepForm(forms.ModelForm):
    """
    The Prep Form is to allow  administrators to define the terms of the DCUA before sending to the user to sign.
    """

    def __init__(self, *args, **kwargs):
        super(DCUAPrepForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].initial = datetime.datetime.now().strftime("%m/%d/%Y")
        self.fields['end_date'].initial = (datetime.datetime.now() + datetime.timedelta(days=365)
                                            ).strftime("%m/%d/%Y")
        self.fields['locations_allowed'].initial = """WorkArea-[CWID]\ndcore-prj-SOURCE\ndcore-prj-SHARE"""
        self.helper = FormHelper()
        self.helper.form_id = 'DCUAPrepForm'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Fieldset("""<div class="alert alert-info">Data Core User Agreement creation</div>""",
                     'attestee',
                     'project',
                     'start_date',
                     'end_date',
                     'locations_allowed',
                     style="font-weight: normal;",
                     )
        )

    class Meta:
        model = DataCoreUserAgreement
        fields = [  'attestee',
                    'project',
                    'start_date',
                    'end_date', 
                    'locations_allowed',
                ]


        widgets = {'attestee': autocomplete.ModelSelect2(
                        url='dc_management:autocomplete-user'
                    ),
                    'project': autocomplete.ModelSelect2(
                        url='dc_management:autocomplete-project'
                    ),
                }

class SFTPForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SFTPForm, self).__init__(*args, **kwargs)
        self.fields['login_details'].label = "sFTP login details"
        self.fields['internal_connection'].label = "Internal connection ONLY"

        self.helper = FormHelper()
        self.helper.form_id = 'SFTPForm'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Fieldset(
                """ <div class="alert alert-info">
                        Create new sFTP connection for a project
                    </div>
                """,
                'project',
                'internal_connection',
                'whitelisted',
                layout_three_equal( 'pusher',
                                    'pusher_contact',
                                    'pusher_email',),
                'login_details',
                layout_three_equal( 'firewall_label',
                                    'firewall_rule',
                                    'firewall_request'),
                'host_server',
                'storage',
                style="font-weight:bold;",
            ),
        )

    class Meta:
        model = SFTP
        fields = [  'project',
                    'internal_connection',
                    'whitelisted',
                    'pusher',
                    'pusher_contact',
                    'pusher_email',
                    'login_details',
                    'firewall_label',
                    'firewall_rule',
                    'firewall_request',
                    'host_server',
                    'storage',
        ]
        help_texts = {'storage' : _('The fileshare where files will be saved to'),
                      'internal_connection': _('Whether access is only via the WCM network'),
                      'login_details': _('will be of the format anonymous@somewhere')
                      }
        widgets =   {'project' : autocomplete.ModelSelect2(
                         url='dc_management:autocomplete-project'
                     ),
                     'host_server' : autocomplete.ModelSelect2(
                         url='dc_management:autocomplete-node'
                     ),
                     'storage': autocomplete.ModelSelect2(
                         url='dc_management:autocomplete-dataaccess'
                     ),
                    }

class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].label = "Official project start date"
        self.helper = FormHelper()
        self.helper.form_id = 'project-create-form'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
                Fieldset('<div class="alert alert-info">Project details</div>',
                        'dc_prj_id',
                        'title', 
                        'nickname',
                        'account_number',
                        project_leaders,
                        'users',
                        'storage',
                        environment_type,
                        style="font-weight: bold;",
                ),
                project_governance,
                Fieldset('<div class="alert alert-info">Environment</div>',
                        project_compute,
                        layout_four_equal('fileshare_storage',
                                            'fileshare_derivative',
                                            'direct_attach_storage',
                                            'backup_storage',
                        ),
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
                    'fileshare_derivative',
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
                    'start_date',
                    'expected_completion',
                    'status',
                    'sn_tickets',
                    'completion_ticket',
                    'completion_date',
                    'prj_dns',
                    'myapp',
                    'db',
                    'storage',
                    'account_number',
                ]

        widgets =  {'users' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-user'
                                        ),
                    'storage' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-dataaccess'
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
        self.fields['start_date'].label = "Official project start date"
        self.helper = FormHelper()
        self.helper.form_id = 'project-update-form'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
                Fieldset('<div class="alert alert-info">Project details</div>',
                        'title', 
                        'nickname',
                        'account_number',
                        project_leaders,
                        'storage',
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
                    'start_date',
                    'expected_completion',
                    'status',
                    'wrapup_ticket',
                    'wrapup_date',
                    'completion_ticket',
                    'completion_date',
                    'prj_dns',
                    'myapp',
                    'db',
                    'account_number', 
                    'storage',
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
                    'storage' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-dataaccess'
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

class StorageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StorageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'storage-create-form'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create storage'))
        self.helper.layout = Layout(
                Fieldset('<div class="alert alert-info">Create new storage entry</div>',
                        layout_simple_two('name', 'location'),
                        'description',
                        Div(
                            Div('datasets',
                                css_class='col-xs-9',
                                style='font-size:100%;font-weight: bold;'
                            ),
                            Div(HTML(''' 
                                    </br>
                                    <a  type="button" 
                                    class="btn btn-success"  
                                    href="{% url 'datacatalog:dataset-add' %}">
                                    Create new dataset</a>'''
                                    ),
                                css_class='col-xs-3',
                            ),
                            css_class="row"
                        ), 
                        style="font-weight: bold;",
                        ),
        )
    class Meta:
        model = Storage
        fields = [  'name', 
                    'location', 
                    'description', 
                    'datasets', 
                ]

        widgets =  {'datasets' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-dataset'
                                        ),
                                    
                    }

class StorageAttachForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StorageAttachForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'storage-attach-form'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Update storage'))
        self.helper.layout = Layout(
                Fieldset('<div class="alert alert-info">Add or remove storage from project</div>',
                        'storage', 
                        style="font-weight: bold;",
                ),
        )
        
    class Meta:
        model = Project
        fields = [ 'storage', ]

        widgets =  {'storage' : autocomplete.ModelSelect2Multiple(
                                url='dc_management:autocomplete-dataaccess'
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
                        layout_three_equal('change_date', 
                                            'requester', 
                                            'ticket',
                        ),
                        style="font-weight: bold;"
                ),
                Fieldset('Data Source ⇨ Destination',
                        Div(
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
                                css_class='col-5 card px-4 bg-info',
                            ),
                            
                            Div('transfer_method',
                                HTML('⇨'),
                                css_class="col-2 text-center align-bottom"
                            ),
                            
                            Div(
                                Div(  'destination', 
                                    label='Data Core source',
                                    title="Use if destination is a dcore project.",
                                    css_class="row",
                                ),
                                Div('external_destination', 
                                    title="Use if destination is external to Data Core.",
                                    css_class="row",
                                ),
                                Div('filepath_dest',
                                    title='List the full path to where files are being transferred. Write "transfer.med" or similar if exporting to user.',
                                    css_class='row',
                                ),
                                css_class='col-5 card px-4 bg-info',
                            ),
                        css_class='row',
                        ),
                            style="font-weight: bold;",
                            css_class="container",
                ),
                Fieldset('File information',
                            layout_simple_two('file_num', 'file_num_unknown',),
                            layout_simple_two('data_type', 'reviewed_by',),        
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
                    'reviewed_by' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-djuser'
                                        ),               
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



