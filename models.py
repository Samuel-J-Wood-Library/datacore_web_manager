from django.urls import reverse
from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

import datetime
from datetime import date

import numpy as np

from persons.models import Person, Department, Organization, Role 
from datacatalog.models import Dataset, DataUseAgreement, DataAccess

############################
####  Comment Models    ####
############################

class AlertTag(models.Model):
    """
    Alert Tags are for associating with projects/servers/users, to allow flagging of 
    temporary events that need high level attention. 
    """
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # description of the alert or issue
    alertcomment = models.TextField()
    
    # date when the issue was resolved
    cleared = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        if self.cleared:
            return "resolved {}: {}".format(self.cleared, self.alertcomment)
        else:
            return "ACTIVE: {}".format(self.alertcomment)
        
class CommentLog(models.Model):
    """
    A Comment Log is a comment associated with a project/server/governance doc/user, to 
    describe any state that cannot be otherwise captured using the standard logs or 
    fields. Comment Logs can themselves have comments, thus allowing a conversation
    or history to be recorded. 
    """
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)

    # description of the event/change/issue
    comment = models.TextField()
    
    # comment for which this comment is a response or reply to
    parent_comment = models.ForeignKey('self', 
                                        on_delete=models.CASCADE,
                                        blank=True, 
                                        null=True
                                        ) 
    def __str__(self):
        return "{}: {}".format(self.record_author, self.comment)
         
############################
####  Software Models   ####
############################

class Software_License_Type(models.Model):
    """
    This model captures the details that define a type of license. This is not used to 
    record specific licenses from a vendor, but will be referenced by these licenses.
    """
    # [DEPRECATE] ServiceNow ticket documenting/requesting license 
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    
    # human-readable name for identifying this kind of license
    name = models.CharField(max_length=32, unique=True)
    
    # whether the license is specifically assigned to a single individual
    user_assigned = models.BooleanField()
    
    # whether the license allows concurrent access to software
    concurrent = models.BooleanField()
    
    # whether the license actively sends authentication requests, reports, or logs 
    # to the vendor
    monitored = models.BooleanField()

    def __str__(self):
            return self.name

    class Meta:
        verbose_name = 'Software License Type'
        verbose_name_plural = 'Software License Types'

class Software(models.Model):
    """
    This model defines software packages or applications.  
    """
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)

    name = models.CharField(max_length=64, unique=False)
    vendor = models.CharField(max_length=64)
    version = models.CharField(max_length=32)
    license_type = models.ForeignKey(
                            Software_License_Type, 
                            on_delete=models.CASCADE
                            )
    package = models.BooleanField(default=False)
    purchase_details = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    dynamic_comments = models.ManyToManyField(CommentLog, 
                                              blank=True, 
                                              related_name='software_comments'
                                              )

    def __str__(self):
            return "{} (version {})".format(self.name, self.version)
    
    def swusers(self):
        sw_users = Person.objects.filter(project__software_installed=self.pk
                                ).filter(
                                    Q(project__status='RU') |
                                    Q(project__status='ON') 
                                ).order_by('cwid'
                                ).distinct()    
        return sw_users

    def seatcount(self):
        sw_prjs = Project.objects.filter(software_installed=self.pk
                                        ).exclude(status="CO")    
        usercount = [ prj.users.count() for prj in sw_prjs ]
        return sum(usercount)

        
    class Meta:
        verbose_name = 'Software'
        verbose_name_plural = 'Software'

class SoftwareUnit(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    unit = models.CharField(max_length=64)
    
    def __str__(self):
            return self.unit

############################
####   Server Models    ####
############################

class SubFunction(models.Model):
    name = models.CharField(max_length=16, default="project")

    def __str__(self):
            return self.name

class EnvtSubtype(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
            return self.name

class SN_Ticket(models.Model):
    "deprecated class, not referenced by any other model"
    ticket_id = models.CharField(max_length=11, unique=True)
    date_created = models.DateField(default=date.today)

    def __str__(self):
            return self.ticket_id

    class Meta:
        verbose_name = 'SN Ticket'
        verbose_name_plural = 'SN Tickets'
                
class Server(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)

    # current operating status of the server
    ON = 'ON'
    OFF = 'OF'
    DECOMMISSIONED = 'DE'
    STATUS_CHOICES = (
            (ON, "On"),
            (OFF, "Off"),
            (DECOMMISSIONED, "Decommissioned"),
    )
    status = models.CharField(
                        max_length=2,
                        choices = STATUS_CHOICES,
                        default = ON,
    )

    # purpose of the server
    PRODUCTION = 'PR'
    TEST = 'TE'
    DEVELOPMENT = 'DE'
    DATABASE = 'DB'
    FUNCTION_CHOICES = (
            (PRODUCTION, "Production"),
            (DATABASE, "Production Database"),
            (TEST, "Test"),
            (DEVELOPMENT, "Development"),
    )
    function = models.CharField(
                            max_length=2,
                            choices = FUNCTION_CHOICES,
                            default = PRODUCTION,
    )

    # server type 
    VM = "VM"
    VDI = "VD"
    MACHINE_TYPE_CHOICES = (
                    (VM, "Virtual Machine (VM)"),
                    (VDI, "Virtual Desktop Infrastructure (VDI)"),
    )
    machine_type = models.CharField(
                            max_length=2,
                            choices = MACHINE_TYPE_CHOICES,
                            default = VM,
    ) 
    
    # server size
    SMALL = "SM"
    MEDIUM = "MD"
    LARGE = "LG"
    XLARGE = "XL"
    VM_SIZE_CHOICES = (
                (SMALL, "Small (2 CPU, 8GB RAM)"),
                (MEDIUM, "Medium (4 CPU, 16GB RAM)"),
                (LARGE, "Large (8 CPU, 32GB RAM)"),
                (XLARGE, "Extra Large (16 CPU, 64GB RAM)"),
    )
    vm_size = models.CharField(
                            max_length=2,
                            choices = VM_SIZE_CHOICES,
                            default = SMALL,
    ) 

    # whether server is encrypted or not
    ENCRYPTED = "EN"
    UNENCRYPTED = "UE"
    BACKUP_CHOICES = (
                (ENCRYPTED, "Encrypted"),
                (UNENCRYPTED, "Unencrypted"),
    )
    backup = models.CharField(
                            max_length=2,
                            choices = BACKUP_CHOICES,
                            default = ENCRYPTED,
    ) 

    # operating system installed on the server
    MWS2008 = "M8" 
    MWS2012 = "M2" 
    MWS2016 = "M6"
    RHEL7 = "R7" 
    WINDOWS7 = "W7"
    UBUNTU16 = "U6" 
    OS_CHOICES = (
            (MWS2008, "Microsoft Windows Server 2008 (64-bit)"),
            (MWS2012, "Microsoft Windows Server 2012 (64-bit)"),
            (MWS2016, "Microsoft Windows Server 2016 (64-bit)"),
            (RHEL7, "Red Hat Enterprise Linux 7 (64-bit)"),
            (WINDOWS7, "Microsoft Windows 7 (64-bit)"),
            (UBUNTU16, "Ubuntu 16 LTS (64-bit)"),
    )
    operating_sys = models.CharField(
                            max_length=2,
                            choices = OS_CHOICES,
                            default = MWS2012,
    ) 
    
    # the name given to the server node (eg vDCOREP023)
    node = models.CharField(max_length=16, unique=True) 
    
    # link to the subfunction table
    sub_function = models.ForeignKey(SubFunction, on_delete=models.CASCADE)
    
    # whether or not the node is firewalled
    firewalled = models.BooleanField(null=True)
    
    # the FQDN assigned to the node (eg vITS-HPCP02.med.cornell.edu)
    name_address = models.CharField(max_length=32) 
    
    # IP address of the server (eg 10.36.217.229)
    ip_address = models.GenericIPAddressField() 
    
    # number of CPU allocated to the node
    processor_num = models.IntegerField()
    
    # amount of RAM (in GB) allocated to the node
    ram = models.IntegerField()
    
    # amount of direct-attach system storage (ie C: drive)(in GB) allocated to the node
    disk_storage = models.IntegerField("System storage") 
    
    # amount of direct-attach additional storage (E: drive) allocated to the node 
    other_storage = models.IntegerField("Direct attach storage")    

    # link to software table, for s/w that is installed on the node
    software_installed = models.ManyToManyField(
                                            Software,
                                            related_name='software_on_server',
                                            db_table='server_soft_install_tbl',
                                            blank=True,
                                            )

    # date the node was created and made available
    connection_date = models.DateField(default=date.today)
    
    # the FQDN assigned to the node (eg vITS-HPRP02.a.wcmc-ad.net)
    dns_name = models.CharField(
                        max_length=32, 
                        null=True, 
                        blank=True
                        ) 
                        
    # the server host machine for this node (eg brbesx10.med.cornell.edu)
    host = models.CharField(
                        max_length=32, 
                        null=True, 
                        blank=True
                        )
                        
    # DEPRECATED: comments field. Superseded by dynamic_comments field
    comments = models.TextField(null=True, blank=True)
    
    # link to comment table for assigning multiple comments and replies to the nodes
    dynamic_comments = models.ManyToManyField(CommentLog, 
                                              blank=True, 
                                              related_name='server_comments'
                                              )

    def __str__(self):
            return self.node

    def get_all_active_users(self):
        """
        pull all users from all projects. Return users/projects when a user
        is present in more than one project on the node
        """
        mounted_projects = Project.objects.filter(host=self.pk
                                                ).filter(
                                                    Q(status='RU') |
                                                    Q(status='SU') |
                                                    Q(status='ON')
                                                )
        user_projects = {}
        for p in mounted_projects:
            for u in p.users.all():
                if u in user_projects:
                    user_projects[u].append(p)
                else:
                    user_projects[u] = [p]
        return user_projects
    
    def duplicate_users(self):    
        """
        return only those users/projects where there are more than one project,
        and the user is not data core staff
        """
        user_projects = self.get_all_active_users()
        duplicate_user_dict = {}
        for u in user_projects:
            if (len(user_projects[u]) > 1):
                if u.role:
                    if u.role.name[:9] == 'Data Core':
                        continue
                    else:
                        duplicate_user_dict[u] = user_projects[u]
                else:
                    duplicate_user_dict[u] = user_projects[u]
                
        return duplicate_user_dict
        
    def get_absolute_url(self):
        return reverse('dc_management:node', kwargs={'pk': self.pk})

############################
####   Project Models   ####
############################

class Storage(models.Model):
    """
    DEPRECATED
    The Storage model defines locations in which data are stored. Storage could be
    Isilon fileshares, or AWS S3 buckets, or other media. The data in a storage instance
    will also have governance that defines its use and access. Projects point to the 
    relevant storage instances to determine what data are available for project users. 
    """
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)

    # identifying name for storage instance - preferably name of parent directory.
    name = models.CharField(max_length=32, unique=True,)
    
    # description of purpose of storage
    description = models.TextField(null=True, blank=True,)
    
    # location storage is hosted at (Isilon, AWS, etc)
    ISILON = 'IS'
    AWS = 'AW'
    GLACIER = 'GL'
    S3 = 'S3'
    AZURE = 'AZ'
    SRA = 'SA'
    LOCATION_CHOICES = (
                (ISILON, "Isilon"),
                (AWS, "Amazon Web Services"),
                (GLACIER, "AWS Glacier"),
                (S3, "AWS S3 Storage"),
                (AZURE, "Microsoft Azure"),
                (SRA, "Secure Remote Archive"),
    )
    location = models.CharField(
                            "Storage location",
                            max_length=2,
                            choices = LOCATION_CHOICES,
                            default = ISILON,
    )
    
    # datasets contained in storage
    datasets = models.ManyToManyField(Dataset, blank=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.location)

    def get_absolute_url(self):
        return reverse('dc_management:storage', kwargs={'pk': self.pk})


class Project(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    
    # the data core project ID (eg prj0023)
    dc_prj_id = models.CharField(max_length=8, unique=True)
    
    # full title of the project. Typically matches the IRB title.
    title = models.CharField(max_length=256)
    
    # short title for easier reference
    nickname = models.CharField(max_length=256, blank=True)

    # whether it only has public data
    open_allowed = models.BooleanField("classification: public?", null=True)
    
    # whether or not the project actually has internet access
    # this field will not be actively used, as this setting is configured at node level
    open_enabled = models.BooleanField("security: open?", null=True)
    
    # whether or not multiple data sources are allowed to be present in this project
    isolate_data = models.BooleanField("data isolation: isolate?", null=True)
    
    # the requested amount of fileshare storage (Isilon) configured in Isilon
    # for primary (source) data, which is archived, but without version backup
    fileshare_storage = models.IntegerField("Primary data (GB)",
                                            null=True, 
                                            blank=True)
    
    # the requested amount of fileshare storage (Isilon) configured in Isilon
    # for derivative (Shared and WorkArea) data, which has versioned backup
    fileshare_derivative = models.IntegerField("Derivative data (GB)",
                                            null=True, 
                                            blank=True)
                                            
    # the requested amount of direct attach (E: drive) storage. Configured at node
    direct_attach_storage = models.IntegerField("Direct attach size (GB)", 
                                                null=True, 
                                                blank=True)
                                                
    # requested archival storage
    backup_storage = models.IntegerField("Archival storage (GB)", 
                                         null=True, 
                                         blank=True)
                                         
    # requested RAM (in GB) to be provisioned
    requested_ram = models.IntegerField("Requested RAM (GB)", null=True, blank=True)
    
    # requested CPU number to be provisioned
    requested_cpu = models.IntegerField(null=True, blank=True)
    
    #####################
    # ACCESS COMPONENTS #
    #####################
    
    # link to table of data core users. All users who need access to the project.
    # other roles (eg PI, admin) do not have to be listed as users.
    users = models.ManyToManyField(Person, blank=True)
    
    # the PI of the project. All decisions and communication will be from the PI
    pi = models.ForeignKey(
                    Person, 
                    on_delete=models.CASCADE,
                    related_name='project_pi')
    
    # the project administrator can be delegated by the PI to communicate or act on 
    # behalf of the PI
    prj_admin = models.ForeignKey(
                    Person, 
                    on_delete=models.CASCADE,
                    null=True,
                    blank=True,
                    related_name='prj_admin')
    ##############
    # GOVERNANCE #
    ##############

    # SN reference to onboarding request
    onboarding_ticket = models.CharField(max_length=32, blank=True, null=True)

    # the data catalog governance docs that regulate this project
    governance = models.ManyToManyField(DataUseAgreement, blank=True)

    ###########
    # STORAGE #
    ###########
    
    # the storage (typically fileshares) accessible by the project
    storage = models.ManyToManyField(DataAccess, blank=True, related_name='dc_project')
    
    ############################
    # SOFTWARE AND ENVIRONMENT #
    ############################
    
    # link to software table. All s/w currently provisioned
    software_installed = models.ManyToManyField(
                                            Software,
                                            related_name='software_installed',
                                            db_table='prj_soft_install_tbl',
                                            blank=True,
                                            )
    
    # link to software table. All s/w requested for the project
    software_requested = models.ManyToManyField(
                                            Software,
                                            related_name='software_requested',
                                            db_table='prj_soft_request_tbl',
                                            blank=True,
                                            )
    
    # the purpose of the project                                        
    THESIS = 'TH'
    RESEARCH = 'RE'
    CLASS = 'CL'
    ENV_TYPE_CHOICES = (
                (THESIS, "Thesis Project"),
                (RESEARCH, "Research Project"),
                (CLASS, "Classroom Project")
    )
    env_type = models.CharField(
                            "Environment type",
                            max_length=2,
                            choices = ENV_TYPE_CHOICES,
                            default = RESEARCH,
    ) 
    
    # a more granular description of the project purpose
    env_subtype = models.ForeignKey(EnvtSubtype, on_delete=models.CASCADE)
    
    # the date the project officially began (and is therefore billed from)
    start_date = models.DateField(null=True, blank=True)
    
    # the date access to the project is expected to be no longer required
    expected_completion = models.DateField()
    
    # the date access, software and data are required 
    requested_launch = models.DateField()
    
    # current project status
    ONBOARDING = "ON"   # project is being set up for first time
    RUNNING = "RU"      # project is actively being accessed and consuming resources
    COMPLETED = "CO"    # project is inaccessible, and not consuming resources
    SUSPENDED = "SU"    # access has been temporarily suspended. Still charged for resrcs
    SHUTTINGDOWN = "SD" # project is in process of being permanently removed.
    ARCHIVED = "AR"
    STATUS_CHOICES = (
            (ONBOARDING, "Onboarding"),
            (RUNNING, "Running"),
            (COMPLETED, "Completed"),
            (SUSPENDED, "Suspended"),
            (SHUTTINGDOWN, "Shutting down"),
            (ARCHIVED, "Archived"),
    )
    status = models.CharField(
                            max_length=2,
                            choices = STATUS_CHOICES,
                            default = RUNNING,
    ) 
    
    # not currently used. Allows reference of pertinent SN ticket ID
    sn_tickets = models.CharField(max_length=32, null=True, blank=True)
        
    # ticket specifying date to close project
    wrapup_ticket = models.CharField("ticket for request to complete", 
                                        max_length=32, 
                                        null=True, 
                                        blank=True,
    )
    
    # date project requested to be shut down
    wrapup_date = models.DateField("date project close requested", null=True, blank=True)
    
    # ticket specifying that the project was successfully closed
    completion_ticket = models.CharField(max_length=32, null=True, blank=True)
    
    # date the project was successfully closed
    completion_date = models.DateField(null=True, blank=True)
    
    # the node the project is mounted to
    # this is to be deprecated and replaced with server field
    host = models.ForeignKey(Server, on_delete=models.CASCADE, null=True, blank=True)

    # contains all servers accessible from the project
    servers = models.ManyToManyField(Server, related_name='project_servers')

    # the FQDN of the project - will be mapped to the IP of the node project is mounted to
    prj_dns = models.CharField('project-specific DNS', 
                                max_length=64, null=True, blank=True,
    )
    
    # boolean field to indicate whether a MyApps app has been created for the project
    myapp = models.BooleanField("MyApps RDP created", null=True)
    
    # links to server table, for any database utilized by the project
    # this is to be deprecated and replaced with the server field
    db = models.ForeignKey(Server, 
                            on_delete=models.CASCADE, 
                            related_name='db_host',
                            null=True, 
                            blank=True,
    )
    
    # register of database name 
    db_name = models.CharField(max_length=128, null=True, blank=True)
    
    ######################
    ### finance fields ###
    ######################
    # WCM Fund number to charge
    account_number = models.CharField(max_length=32, null=True, blank=True)
    
    # set of fields for holding current billing information
    user_cost = models.FloatField(null=True, blank=True)
    host_cost = models.FloatField(null=True, blank=True)
    db_cost = models.FloatField(null=True, blank=True)
    fileshare_cost = models.FloatField(null=True, blank=True)
    direct_attach_cost = models.FloatField(null=True, blank=True)
    backup_cost = models.FloatField(null=True, blank=True)
    software_cost = models.FloatField(null=True, blank=True)
    project_total_cost = models.FloatField(null=True, blank=True)
        
    # links to comment table for assigning comments and their replies to the project
    dynamic_comments = models.ManyToManyField(CommentLog, 
                                              blank=True, 
                                              related_name='project_comments'
                                              )
    
    def __str__(self):
            return "{} ({})".format(self.dc_prj_id, self.nickname)
    
    def get_absolute_url(self):
        return reverse('dc_management:project', kwargs={'pk': self.pk})
    
    def days_to_completion(self):
        td = self.expected_completion - datetime.date.today()
        return td.days
    
    def billable_users(self):
        """
        when we need to ignore ITS staff who have been given access to dcore
        """
        return Person.objects.filter(project=self.pk,
                            ).exclude(role__name__icontains='data core'
                            )
    
    def valid_nodes(self):
        """
        Find all nodes for which there are no users in common.
        for performance, this should be called explicitly, not every time the project 
        view is loaded.
        """
        node_pool = Server.objects.filter(status="ON", function="PR")
        # get set of pks for all users in this project
        # this could be changed to potential users later!
        this_prj = set(self.users.values_list('id', flat=True))

        valid_node_list = []
        for node in node_pool:
            node_users = node.get_all_active_users()  # running, suspended, or onboarding
            that_node = set([u.pk  for u in list(node_users.keys())])
            if len(this_prj.intersection(that_node)) == 0:
                valid_node_list.append(node)

        return valid_node_list
    	    
class AccessPermission(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()    

    def __str__(self):
            return self.name
    
def project_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/prj<id>/<filename>
    return '{0}/{1}'.format(instance.project.dc_prj_id, filename)

############################
#### Governance Models  ####
############################

class Governance_Doc(models.Model):
    """
    This class is the original holder of governance document meta data. This class will be replaced with the
    Data Catalog models.
    """
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    doc_id = models.CharField(max_length=64)
    date_issued = models.DateField()
    expiry_date = models.DateField()
    users_permitted = models.ManyToManyField(Person, blank=True)
    access_allowed = models.ForeignKey(AccessPermission, on_delete=models.CASCADE)
    
    IRB = 'IR'
    IRB_EXEMPTION = 'IX'
    DUA = 'DU'
    DCA = 'DC'
    ONBOARDING = 'ON'
    GOVERNANCE_TYPE_CHOICES = (
                    (IRB, "WCM IRB"),
                    (IRB_EXEMPTION, "IRB Exemption"),
                    (DUA, "DUA"),
                    (DCA, "D-Core User Agreement"),
                    (ONBOARDING, "Onboarding Form"),
    )
    governance_type = models.CharField(
                            max_length=2,
                            choices = GOVERNANCE_TYPE_CHOICES,
                            default = DCA,
    )
    
    defers_to_doc = models.ForeignKey('self', 
                                        on_delete=models.CASCADE, 
                                        null=True, 
                                        blank=True,
                                        related_name='overrules')
    supersedes_doc = models.ForeignKey('self', 
                                        on_delete=models.CASCADE, 
                                        null=True, 
                                        blank=True,
                                        related_name='superseded_by')

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    documentation = models.FileField(
                            upload_to=project_directory_path, 
                            null=True,
                            blank=True,
    )
    destroy_data = models.BooleanField(null=True)
    comments = models.TextField(null=True, blank=True)
    dynamic_comments = models.ManyToManyField(CommentLog, 
                                              blank=True, 
                                              related_name='govdoc_comments'
                                              )
    isolate_data = models.BooleanField(null=True)

    def __str__(self):
            return "{4}_{0}_{2}_{1}_{3}".format(self.governance_type, 
                                                self.doc_id, 
                                                self.project,
                                                self.expiry_date,
                                                self.pk,
                                                )

    def allowed_user_string(self):
        return  ", ".join([u.cwid for u in self.users_permitted.all()])

    def attention_required(self):
        td = self.expiry_date - datetime.date.today() 
        #print(self, len(Governance_Doc.objects.filter(supersedes_doc=self)))
        if td.days >  90:
            status = "safe"
        
        # DCUA always defers to other agreements, and has a soft end date
        elif self.governance_type == "DC":
            status = "safe"
        
        # if doc defers to another doc, then we need not pay attention to this one:
        elif self.defers_to_doc:
            status = "safe"
        elif len(Governance_Doc.objects.filter(supersedes_doc=self)) > 0:
            status = "safe"
        
        # if not deferring, not DCUA:
        elif td.days <= 0:
            status = "danger"
        elif td.days <= 10:
            status = "warning"
        elif td.days <= 90:
            status = "primary"
        else:
            status = "danger"
        return status
    
    def get_absolute_url(self):
        return reverse('dc_management:govdocmeta', kwargs={'pk': self.pk})
    
        
    class Meta:
        verbose_name = 'Governance Document'
        verbose_name_plural = 'Governance Documents'

class AnnualProjectAttestation(models.Model):
    """
    A class to capture a yearly acknowledgement from the PI that the users listed on 
    the project are authorized to maintain access to the project.
    """
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)

    # the project being attested 
    project = models.ForeignKey(Project,
                                on_delete=models.PROTECT,
                                )
    
    # the person attesting
    pi = models.ForeignKey(Person, 
                         on_delete=models.PROTECT,
                         related_name="attestation_pi",
                         )

    # date of attestation
    attestation_date = models.DateField()
    
    # users attested to 
    allowed_users = models.ManyToManyField(Person)

    def get_absolute_url(self):
        return reverse('dc_management:annualattest', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.project} {self.attestation_date}"

class DataCoreUserAgreement(models.Model):
    """
    A class to capture signed agreement to the terms of using the Data Core.
    Each DCUA instance represents one user on one project, for a specified
    period of time.
    """
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)

    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)

    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)

    # the project being attested
    project = models.ForeignKey(Project,
                                on_delete=models.PROTECT,
                                )

    # the person attesting
    attestee = models.ForeignKey(Person,
                                 on_delete=models.PROTECT,
                                 )

    # the start date of the agreement
    start_date = models.DateField()

    # the end date of the agreement
    end_date = models.DateField()

    # folders allowed (to be defined by curation team)
    locations_allowed = models.TextField()

    # consent to project access (to specified folders)
    consent_access = models.CharField(max_length=8, null=True)

    # consent to usage conditions
    consent_usage = models.CharField(max_length=8, null=True)

    # signature date
    signature_date = models.DateField(null=True)

    # signature name
    signature_name = models.CharField(max_length=64, null=True)

    # signature title
    signature_title = models.CharField(max_length=64, null=True)

    # acknowledgement of patching schedule
    acknowledge_patching = models.CharField(max_length=8, null=True)

    def get_absolute_url(self):
        return reverse('dc_management:dcua', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.project} {self.attestee} {self.signature_date}"

class DC_Administrator(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    cwid = models.CharField(max_length=32)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    role = models.CharField(max_length=32)
    date_started = models.DateField()
    date_finished = models.DateField(null=True, blank=True)

    def __str__(self):
        return "{} {}({})".format(self.first_name, self.last_name, self.cwid)

    class Meta:
        verbose_name = 'Data Core Administrator'
        verbose_name_plural = 'Data Core Administrators'

class DCUAGenerator(models.Model):
    """
    This class allows the creation of Data Core User Agreements (DCUAs) for users to 
    sign prior to being granted access to Data Core. Designed for sending URL to Qualtrics
    to create custom form.
    """
    
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)

    ticket = models.CharField("SN Ticket", blank=True,null=True,max_length=12,)
    startdate = models.CharField("Start Date", 
                                blank=False, 
                                max_length=32,
                                default=datetime.datetime.now().strftime("%m/%d/%Y"),
                                )
    enddate = models.CharField(  "End Date",
                                blank=False, 
                                max_length=32,
                                default=(datetime.datetime.now() + 
                                         datetime.timedelta(days=365)
                                        ).strftime("%m/%d/%Y"),
                             )
    folder1 = models.CharField("Folder 1", blank=False, 
                              max_length=128,
                              default="dcore-prj00XX-SOURCE",
                              )
    folder2 = models.CharField("Folder 2", blank=True,null=True, 
                              default="dcore-prj00XX-SHARE",
                              max_length=128,
                              )
    folder3 = models.CharField("Folder 3", blank=True,null=True, 
                              default="WorkArea-<user CWID>",
                              max_length=128,
                              )
    folder4 = models.CharField("Folder 4", blank=True,null=True, max_length=128,)
    folder5 = models.CharField("Folder 5", blank=True,null=True, max_length=128,)
    folder6 = models.CharField("Folder 6", blank=True,null=True, max_length=128,)
    folder7 = models.CharField("Folder 7", blank=True,null=True, max_length=128,)
    url = models.CharField("Qualtrics URL", blank=True,null=True, max_length=512,)

    def __str__(self):
        return "{} - {} {}".format(self.startdate, self.enddate, self.folder1)
    
    def get_absolute_url(self):
        return reverse('dc_management:url_result', kwargs={'pk': self.pk})

class Protocols(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    created_by = models.ForeignKey(User, 
                                    on_delete=models.CASCADE,
                                    related_name='created_by',
                                    )
    edited_by = models.ForeignKey(User, 
                                    on_delete=models.CASCADE, 
                                    related_name="edited_by",
                                    )
    ticket_description = models.TextField("Description for tickets")
    dc_description = models.TextField("Description for Data Core")

#######################
#### Access Models ####
#######################

class SFTP(models.Model):
    """
    A class to document sFTP access conditions provided to projects. Some projects require ability to
    push data from an external site, while others only need ability to pull from within the sFTP node.
    """
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)

    # project that gains access through this instance
    project = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)

    # boolean to capture if access is only via internal log on to the sFTP server, not by pushing data in.
    internal_connection = models.BooleanField(null=True)

    # Whitelisted IP addresses that can push to the sFTP server
    whitelisted = models.CharField(max_length=128, null=True, blank=True)

    # description of the location pushing data
    pusher = models.CharField("External data location", max_length=128, null=True, blank=True)

    # contact name of external team / data provider
    pusher_contact = models.CharField("External contact name", max_length=128, null=True, blank=True)

    # contact email of external team / data provider
    pusher_email = models.EmailField("External contact email", null=True, blank=True)

    # sFTP login details e.g. anonymous@dcoredrop
    login_details = models.CharField("External login details", max_length=128, null=True, blank=True)

    # label given to security team for perimeter firewall rule
    firewall_label = models.CharField("Firewall label", max_length=128, null=True, blank=True)

    # firewall rule id (to allow request for modification or deletion)
    firewall_rule = models.CharField(max_length=32, null=True, blank=True)

    # firewall request ServiceNow Ticket number
    firewall_request = models.CharField(max_length=32, null=True, blank=True)

    # server hosting the sFTP application
    host_server = models.ForeignKey(Server, on_delete=models.PROTECT)

    # storage that this sFTP instance gains access to
    storage = models.ForeignKey(DataAccess, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.pusher}"

    def get_absolute_url(self):
        return reverse('dc_management:sftp', kwargs={'pk': self.pk})

############################
####   Finance Models   ####
############################
                          
class SoftwareCost(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)

    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)

    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    software = models.ForeignKey(Software, on_delete=models.CASCADE)
    software_cost = models.FloatField("Regular cost (per person)", 
                                        null=True, 
                                        blank=True,
                                        )
    cost_classroom = models.FloatField("Cost for classrooms (per student)", 
                                        null=True, 
                                        blank=True,
                                        )
    cost_student = models.FloatField("Cost for classrooms (per class)", 
                                        null=True, 
                                        blank=True,
                                        )
    
class UserCost(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)

    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)

    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
 
    # number of users on a project
    user_quantity = models.IntegerField()

    # total cost for the number of users indicated in user_quantity
    user_cost     = models.FloatField()
    
class StorageCost(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # description of the type of storage
    storage_type = models.CharField(max_length=64)

    # cost per GB per month
    st_cost_per_gb = models.FloatField()

    def __str__(self):
        return "{} (${}/GB)".format( self.storage_type, self.st_cost_per_gb)

class ExtraResourceCost(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)

    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)

    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
 
    # number of additional CPU + RAM (note most provisions will be multiples of two)
    extra_cpu    = models.IntegerField()

    # total cost for the amount of extra_cpu
    cpu_cost     = models.FloatField()

class DatabaseCost(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)

    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)

    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
 
    # cost for initial setup 
    setup_cost  = models.FloatField(null=True, blank=True)

    # monthly cost for running db
    db_cost     = models.FloatField()
    
class ProjectBillingRecord(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)

    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)

    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)

    # project to be billed
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    # billing date (typically, will be done as billable months)
    billing_date = models.DateField()
    
    # base value
    base_value = models.IntegerField(null=True, blank=True)
    
    # base rate
    base_rate = models.FloatField(null=True, blank=True)
    
    # base cost
    base_expense = models.FloatField(null=True, blank=True)
    
    # this captures the storage type, amount and charge from storage cost class
    storage_1_type    = models.CharField(null=True, blank=True, max_length=256)
    storage_1_value   = models.IntegerField(null=True, blank=True)
    storage_1_rate    = models.FloatField(null=True, blank=True)
    storage_1_expense = models.FloatField(null=True, blank=True)
    
    storage_2_type    = models.CharField(null=True, blank=True, max_length=256)
    storage_2_value   = models.IntegerField(null=True, blank=True)
    storage_2_rate    = models.FloatField(null=True, blank=True)
    storage_2_expense = models.FloatField(null=True, blank=True)

    storage_3_type    = models.CharField(null=True, blank=True, max_length=256)
    storage_3_value   = models.IntegerField(null=True, blank=True)
    storage_3_rate    = models.FloatField(null=True, blank=True)
    storage_3_expense = models.FloatField(null=True, blank=True)

    storage_4_type    = models.CharField(null=True, blank=True, max_length=256)
    storage_4_value   = models.IntegerField(null=True, blank=True)
    storage_4_rate    = models.FloatField(null=True, blank=True)
    storage_4_expense = models.FloatField(null=True, blank=True)
    
    # software
    sw_value   = models.TextField(null=True, blank=True)
    sw_rates   = models.TextField(null=True, blank=True)
    sw_expense = models.FloatField(null=True, blank=True)
        
    # additional hosting resources (RAM & CPU)
    hosting_value   = models.IntegerField(null=True, blank=True)
    hosting_rate    = models.FloatField(null=True, blank=True)
    hosting_expense = models.FloatField(null=True, blank=True)
        
    # database server costs
    db_value   = models.IntegerField(null=True, blank=True)
    db_rate    = models.FloatField(null=True, blank=True)
    db_expense = models.FloatField(null=True, blank=True)   
    db_setup   = models.FloatField(null=True, blank=True)  
    
    # multiplier value allows for partial-month billing (or penalty billing)
    multiplier = models.FloatField(null=True, blank=True)
    
    # WCM account number to charge
    account = models.CharField(null=True, blank=True, max_length=32)
    
    # comments using dynamic comment class (allows replies)
    comments = models.ManyToManyField(CommentLog, 
                                      blank=True,
                                      related_name='billing_comments'
                                      )
    
    def monthly_total(self):
        """
        This function returns the total of all billable fields for instance.
        """
        # convert values to array:
        x = np.array([self.base_expense,
                      self.storage_1_expense,
                      self.storage_2_expense, 
                      self.storage_3_expense,
                      self.storage_4_expense,
                      self.sw_expense,
                      self.hosting_expense,
                      self.db_expense,
        ])
        
        # remove NaN values and get sum:
        total = x[x != np.array(None)].sum()
        
        # modify if multiplier is present:
        if self.multiplier:
            total = total * self.multiplier
            
        return total
    
    def get_absolute_url(self): 
        return reverse('dc_management:project', kwargs={'pk': self.project.pk})
        
############################
#### Log / Audit Models ####
############################    

class External_Access_Log(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    date_connected = models.DateField()
    date_disconnected = models.DateField()
    user_requesting = models.ForeignKey(Person, on_delete=models.CASCADE)
    project_connected = models.ForeignKey(Project, on_delete=models.CASCADE)
    setup_charge = models.BooleanField()
    hosting_charge = models.BooleanField()

    def __str__(self):
        return self.date_connected

    class Meta:
        verbose_name = 'External Access Log'
        verbose_name_plural = 'External Access Logs'
        
class Software_Log(models.Model):
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    change_date = models.DateField(default=timezone.now)
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    applied_to_prj = models.ForeignKey(Project, 
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        blank=True
                                        )
    applied_to_node = models.ForeignKey(Server, 
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        blank=True,
                                        )
    applied_to_user = models.ForeignKey(Person, 
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        blank=True,
                                        )
    software_changed = models.ForeignKey(Software, on_delete=models.SET_NULL, null=True)

    comments = models.TextField(null=True, blank=True)

    ADD_ACCESS = 'AA'
    REMOVE_ACCESS = 'RA'
    CHANGE_TYPE_CHOICES = (
                    (ADD_ACCESS, "Add access"),
                    (REMOVE_ACCESS, "Remove access"),
    )  
    change_type  = models.CharField(
                            max_length=2,
                            choices = CHANGE_TYPE_CHOICES,
                            default = ADD_ACCESS,
    )

    
    def __str__(self):
        return "{} on {} ".format( self.change_type, self.change_date)

    class Meta:
        verbose_name = 'Software Log'
        verbose_name_plural = 'Software Logs'
    
class Software_Purchase(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    date_purchased = models.DateField()
    software = models.ForeignKey(Software, on_delete=models.CASCADE)
    num_units_purchased = models.IntegerField()
    unit_type = models.ForeignKey(SoftwareUnit, on_delete=models.CASCADE)  
    expiration = models.DateField()
    invoice_number = models.CharField(max_length=64)
    
    MAINTENANCE = 'MN'
    ADDITIONAL = 'AD'
    PURPOSE_CHOICES = (
                    (MAINTENANCE, "Maintenance/Renewal"),
                    (ADDITIONAL, "Additional/Expanding"),
    )  
    purpose  = models.CharField(
                            max_length=2,
                            choices = PURPOSE_CHOICES,
                            default = MAINTENANCE,
    )
    
    cost = models.FloatField()
    documentation = models.FileField(
                            upload_to='procurement/%Y/%m/%d/', 
                            null=True,
                            blank=True,
    )
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} units on {} ({})".format(
                        self.num_units_purchased, 
                        self.date_purchased,
                        self.invoice_number,
                        )

    class Meta:
        verbose_name = 'Software Purchase'
        verbose_name_plural = 'Software Purchases'

    def cost_per_unit(self):
        return self.cost / self.num_units_purchased

class Access_Log(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)

    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    date_changed = models.DateField()
    dc_user = models.ForeignKey(Person, on_delete=models.CASCADE)
    prj_affected = models.ForeignKey(Project, on_delete=models.CASCADE)
    ADD_ACCESS = 'AA'
    REMOVE_ACCESS = 'RA'
    CHANGE_TYPE_CHOICES = (
                    (ADD_ACCESS, "Add access"),
                    (REMOVE_ACCESS, "Remove access"),
    )  
    change_type  = models.CharField(
                            max_length=2,
                            choices = CHANGE_TYPE_CHOICES,
                            default = ADD_ACCESS,
    )

    def __str__(self):
        return "{} on {}".format(self.change_type, self.date_changed)

    class Meta:
        verbose_name = 'Access Log'
        verbose_name_plural = 'Access Logs'

class Audit_Log(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    performed_by = models.ForeignKey(DC_Administrator, on_delete=models.CASCADE)
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    audit_date = models.DateField()
    dc_user = models.ForeignKey(
                        Person, 
                        null=True, 
                        blank=True, 
                        on_delete=models.CASCADE,
                        )
    project = models.ForeignKey(
                        Project, 
                        null=True, 
                        blank=True, 
                        on_delete=models.CASCADE,
                        )
    node = models.ForeignKey(
                        Server, 
                        null=True, 
                        blank=True, 
                        on_delete=models.CASCADE,
                        )
    governance_docs = models.ForeignKey(
                            Governance_Doc, 
                            null=True, 
                            blank=True, 
                            on_delete=models.CASCADE,
                            )
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}_{}".format(self.audit_date, self.comments[:10])

    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

class Storage_Log(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    date_changed = models.DateField(default=date.today)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    storage_amount = models.IntegerField(null=True, blank=True)
    storage_type = models.ForeignKey(StorageCost, on_delete=models.CASCADE)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} {}".format( self.storage_amount, self.date_changed)

    class Meta:
        verbose_name = 'Storage Log'
        verbose_name_plural = 'Storage Logs'
    
    def get_absolute_url(self):
        return reverse('dc_management:project', kwargs={'pk': self.project.pk})

class ResourceLog(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    date_changed = models.DateField(default=date.today)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    new_RAM = models.IntegerField(null=True, blank=True)
    new_CPU = models.IntegerField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}: {} RAM {} CPUs".format(self.date_changed, self.new_RAM, self.new_CPU)

    class Meta:
        verbose_name = 'Computing Resource Log'
        verbose_name_plural = 'Computing Resource Logs'
    
    def get_absolute_url(self):
        return reverse('dc_management:project', kwargs={'pk': self.project.pk})

class TransferMethod(models.Model):
    transfer_method  = models.CharField(max_length=32,)    

    def __str__(self):
        return self.transfer_method

class FileTransfer(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # the date the file transfer was requested
    change_date = models.DateField(default=date.today)
    
    # ticket requesting the transfer
    ticket = models.CharField(max_length=32,null=True, blank=True)
    
    # if source of data is not within data core, it is specified here (eg email)
    external_source = models.CharField(max_length=128,null=True, blank=True)
    
    # if source of data is within data core, the project is specified here
    source = models.ForeignKey( Project, 
                                verbose_name='Source project',
                                null=True,
                                blank=True,
                                on_delete=models.CASCADE,
                                related_name="source_project",
                                )
    
    # if destination is external to data core, then it is specified here (eg email)                            
    external_destination = models.CharField(max_length=128,null=True, blank=True)
    
    # if destination is within Data Core, then the project is specified here
    destination = models.ForeignKey(Project, 
                                    verbose_name='Destination project',
                                    null=True,
                                    blank=True,
                                    on_delete=models.CASCADE,
                                    related_name="destination_project",
                                    )

    # source filepath(s) 
    filenames = models.TextField("source paths of files for transfer")
    
    # destination filepaths(s)
    filepath_dest = models.TextField("destination paths of files for transfer")

    # references one of the means of transfer (eg FTP, transfer.med)
    transfer_method = models.ForeignKey(TransferMethod, on_delete=models.PROTECT)

    # define any location the data was copied during the transfer (eg for review)
    staging = models.ForeignKey(DataAccess, on_delete=models.PROTECT, null=True, blank=True)

    # person requesting the file transfer 
    requester = models.ForeignKey(Person, on_delete=models.CASCADE)
    
    # the number of files being transferred
    file_num = models.IntegerField(verbose_name="number of files", blank=True, null=True)
    
    # if the number of files being transferred is unknown, this field is True
    file_num_unknown = models.BooleanField(verbose_name='file number unknown', null=True)
    
    # specification of presence of protected information in data
    DEIDENTIFIED = 'DE'
    IDENTIFIED = 'ID'
    LIMITED = 'LM'
    NOTDETERMINED = 'ND'
    DATA_TYPE_CHOICES = (
                    (DEIDENTIFIED, "Deidentified"),
                    (IDENTIFIED, "PHI"),
                    (LIMITED, "Limited Dataset"),
                    (NOTDETERMINED, "Not determined"),
    )  
    data_type  = models.CharField(
                            max_length=2,
                            choices = DATA_TYPE_CHOICES,
                            default = NOTDETERMINED,
    )
    
    # individual who reviewed the data to determine the PPI status
    reviewed_by = models.ForeignKey(
                            User, 
                            on_delete=models.CASCADE,
                            related_name='transfer_reviewer',
                            blank=True,
                            null=True,
                            )
    
    # field for comments relating to the file transfer being requested
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.source:
            src = self.source
        else:
            src = self.external_source
            
        if self.destination:
            dest = self.destination
        else:
            dest = self.external_destination
        
        return "{}-{} ({})".format(src, dest, self.change_date)

    class Meta:
        verbose_name = 'File Transfer Log'
        verbose_name_plural = 'File Transfer Logs'

class Data_Log(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    change_date = models.DateField()

    IMPORT = 'IM'
    EXPORT = 'EX'
    DIRECTION_TYPE_CHOICES = (
                    (IMPORT, "Import data"),
                    (EXPORT, "Export data"),
    )  
    direction  = models.CharField(
                            max_length=2,
                            choices = DIRECTION_TYPE_CHOICES,
                            default = EXPORT,
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    request_ticket = models.CharField(max_length=32, null=True, blank=True)
    transfer_ticket = models.CharField(max_length=32, null=True, blank=True)
    authorized_by = models.ForeignKey(
                            DC_Administrator, 
                            on_delete=models.CASCADE,
                            related_name='authorizing_administrator',
                            )
    reviewed_by = models.ForeignKey(
                            DC_Administrator, 
                            on_delete=models.CASCADE,
                            related_name='reviewing_administrator',
                            )
    file_description = models.TextField()

    TRANSFERMED = 'TM'
    PHYSICAL = 'PH'
    EMAIL = 'EM'
    SFTP = 'SF'
    POPMED = 'PM'
    TRANSFER_METHOD_CHOICES = (
                    (TRANSFERMED, "Transfer.med.cornell.edu"),
                    (PHYSICAL, "Physical media"),
                    (EMAIL, "Email"),
                    (SFTP, "SFTP"),
                    (POPMED, "PopMedNet"),
    )  
    transfer_method  = models.CharField(
                            max_length=2,
                            choices = TRANSFER_METHOD_CHOICES,
                            default = TRANSFERMED,
    )

    def __str__(self):
        return "{} {}".format(self.direction, self.change_date)

    class Meta:
        verbose_name = 'Data Log'
        verbose_name_plural = 'Data Logs'

class Server_Change_Log(models.Model):
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    change_date = models.DateField()
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    node_changed = models.ForeignKey(Server, on_delete=models.CASCADE, null=True)
    CONNECTED = 'CO'
    DISCONNECTED = 'DC'
    STATE_CHANGE_CHOICES = (
                    (CONNECTED, "Connected"),
                    (DISCONNECTED, "Disconnected"),
    )  
    state_change  = models.CharField(
                            max_length=2,
                            choices = STATE_CHANGE_CHOICES,
                            null=True,
                            blank=True,
    )    

    ADD_STORAGE = 'AS'
    REM_STORAGE = 'RS'
    STORAGE_CHANGE_CHOICES = (
                    (ADD_STORAGE, "Add storage"),
                    (REM_STORAGE, "Remove storage"),
    )  
    storage_change  = models.CharField(
                            max_length=2,
                            choices = STORAGE_CHANGE_CHOICES,
                            null=True,
                            blank=True,
    )    

    change_amount = models.IntegerField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return "{}".format(self.change_date)

    class Meta:
        verbose_name = 'Server Change Log'
        verbose_name_plural = 'Server Change Logs'

class AlertTagType(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)


class MigrationLog(models.Model):
    # date the record was created
    record_creation = models.DateField(auto_now_add=True)
    # date the record was most recently modified
    record_update = models.DateField(auto_now=True)
    # the user who was signed in at time of record modification
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    node_origin = models.ForeignKey(Server, 
                                    on_delete=models.CASCADE,
                                    related_name='migration_origin',
                                    null=True,
                                    blank=True,
                                    )
    node_destination = models.ForeignKey(Server, 
                                    on_delete=models.CASCADE,
                                    related_name='migration_destination',
                                    )
    
    access_ticket = models.CharField("user access confirmation ticket", 
                                    max_length=32, 
                                    null=True, 
                                    blank=True
    )
    access_date = models.DateField("access confirmation date", 
                                    null=True,
                                    blank=True,
    )
    envt_ticket = models.CharField("environment confirmation ticket", 
                                    max_length=32, 
                                    null=True, 
                                    blank=True
    )
    envt_date = models.DateField("environment confirmation date", 
                                    null=True,
                                    blank=True,
    )
    data_ticket = models.CharField("data integrity confirmation ticket", 
                                    max_length=32, 
                                    null=True, 
                                    blank=True
    )
    data_date = models.DateField("data integrity confirmation date", 
                                    null=True,
                                    blank=True,
    )

    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} {}".format( self.project.dc_prj_id, self.record_update)

    class Meta:
        verbose_name = 'Migration Log'
        verbose_name_plural = 'Migration Logs'
    
    def get_absolute_url(self):
        return reverse('dc_management:project', kwargs={'pk': self.project.pk})

## end ##
#########

    
