from django.contrib import admin

from .models import Access_Log, AccessPermission, Audit_Log, Data_Log
from .models import DC_Administrator, EnvtSubtype, External_Access_Log
from .models import Governance_Doc, Project, Server, Server_Change_Log, SN_Ticket
from .models import Software, Software_License_Type, Software_Log, Software_Purchase
from .models import Storage_Log, SubFunction, SoftwareCost, UserCost, StorageCost
from .models import DCUAGenerator, FileTransfer, TransferMethod
from .models import ResourceLog, MigrationLog, ExtraResourceCost, DatabaseCost
from .models import ProjectBillingRecord, AnnualProjectAttestation
from .models import DataCoreUserAgreement, SFTP

# customize the look of the admin site:
admin.site.site_header = 'Data Core Management Site'
admin.site.site_title = "DCMS"
admin.site.index_title = "Back end administration"

# customize the individual model views:
@admin.register(Governance_Doc)
class GovDocAdmin(admin.ModelAdmin):
    date_hierarchy = 'expiry_date'
    list_display = ('pk',
                    'doc_id', 
                    'expiry_date',
                    'project', 
                    'defers_to_doc', 
                    "supersedes_doc",
                    'allowed_user_string',
                    'isolate_data',
                    )
    list_filter = ('governance_type','expiry_date')
    search_fields = ('pk', 'doc_id', )
    
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('dc_prj_id',
					'nickname',
					'pi',
					'title',
					'prj_dns',
					'fileshare_storage',
					'requested_ram',
					'requested_cpu',
					'status',
					'expected_completion',
					'env_type',
					'isolate_data', 
					'open_allowed', 
					'open_enabled',
    )
    list_filter = ('env_type','status')
    exlude = (  'user_cost',
				'host_cost',
				'db_cost',
				'fileshare_cost',
				'direct_attach_cost',
				'backup_cost',
				'software_cost',
				'project_total_cost',
    )
    search_fields = ('dc_prj_id', 'nickname', 'title')
@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('node',
					'ip_address',
					'status',
					'function',
					'machine_type',
					'operating_sys',
					
    )
    list_filter = ('function','status', 'operating_sys', 'machine_type')

@admin.register(FileTransfer)
class FileTransferAdmin(admin.ModelAdmin):
    list_display = ('change_date',
                    'ticket',
                    'external_source',
                    'source',
                    'external_destination',
                    'destination',
                    'file_num',
                    'data_type',
                    'reviewed_by',
    )
    list_filter = ('change_date', 'data_type')
    
@admin.register(TransferMethod)
class TransferMethodAdmin(admin.ModelAdmin):
    list_display = ('transfer_method',)
    
@admin.register(SoftwareCost)
class SoftwareCostAdmin(admin.ModelAdmin):
    list_display = ('software',
					'software_cost',
					)

@admin.register(UserCost)
class UserCostAdmin(admin.ModelAdmin):
    list_display = ('user_quantity',
					'user_cost',
					)

@admin.register(StorageCost)
class StorageCostAdmin(admin.ModelAdmin):
    list_display = ('storage_type',
					'st_cost_per_gb',
					)

@admin.register(DCUAGenerator)
class DCUAGeneratorAdmin(admin.ModelAdmin):
    list_display = ('project',
					'ticket',
					'startdate',
					'enddate',
					'url',
					)


@admin.register(MigrationLog)
class MigrationLogAdmin(admin.ModelAdmin):
    list_display = ('project',
					'node_origin',
					'node_destination',
					'comments',
					)

    search_fields = ('project__dc_prj_id', 
                     'node_origin__node', 
                     'node_destination__node',
                     'comments')

@admin.register(AnnualProjectAttestation)
class AnnualProjectAttestationAdmin(admin.ModelAdmin):
    list_display = ('project',
					'pi',
					'attestation_date',
					)

    search_fields = ('project__dc_prj_id', 
                     'pi__first_name', 
                     'pi__last_name',
                    )

@admin.register(DataCoreUserAgreement)
class DataCoreUserAgreementAdmin(admin.ModelAdmin):
    list_display = ('project',
					'attestee',
					'end_date',
					'consent_access',
					)

    search_fields = ('project__dc_prj_id', 
                     'attestee__first_name', 
                     'attestee__last_name',
                    )
    
    list_filter = ('consent_access',)

@admin.register(ProjectBillingRecord)
class ProjectBillingRecordAdmin(admin.ModelAdmin):
    list_display = ('project',
					'billing_date',
					'account',
					'base_expense',
					'storage_1_expense',
					'storage_2_expense',
					'sw_expense',
					'hosting_expense',
					)

    search_fields = ('project__dc_prj_id', 
                     'account', 
                    )
    
    list_filter = ('account',)

@admin.register(SFTP)
class SFTPAdmin(admin.ModelAdmin):
    list_display = ('project',
                    'internal_connection',
                    'pusher',
                    'pusher_email',
                    'whitelisted',
                    )
    search_fields = ('pusher', 'whitelisted',)
    list_filter = ('internal_connection', 'project',)

admin.site.register(Access_Log)
admin.site.register(AccessPermission)
admin.site.register(Audit_Log)
admin.site.register(DatabaseCost)
admin.site.register(Data_Log)
admin.site.register(DC_Administrator)
admin.site.register(EnvtSubtype)
admin.site.register(External_Access_Log)
admin.site.register(ExtraResourceCost)
admin.site.register(ResourceLog)
admin.site.register(SN_Ticket)
admin.site.register(Software)
admin.site.register(Software_License_Type)
admin.site.register(Software_Log)
admin.site.register(Software_Purchase)
admin.site.register(Storage_Log)
admin.site.register(SubFunction)