from django.contrib import admin

from .models import Access_Log, AccessPermission, Audit_Log, Data_Log
from .models import DC_Administrator, DC_User, EnvtSubtype, External_Access_Log
from .models import Governance_Doc, Project, Server, Server_Change_Log, SN_Ticket
from .models import Software, Software_License_Type, Software_Log, Software_Purchase
from .models import Storage_Log, SubFunction, SoftwareCost, UserCost, StorageCost
from .models import DCUAGenerator, FileTransfer, TransferMethod, Department
from .models import ResourceLog, MigrationLog

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
                    )
    list_filter = ('governance_type','expiry_date')
    search_fields = ('pk', 'doc_id', 'project')
    
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('dc_prj_id',
					'nickname',
					'pi',
					'title',
					'fileshare_storage',
					'requested_ram',
					'requested_cpu',
					'status',
					'expected_completion',
					'env_type',
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

@admin.register(DC_User)
class DC_UserAdmin(admin.ModelAdmin):
    list_display = ('first_name',
					'last_name',
					'cwid',
					'role',
					)

    search_fields = ('first_name', 'last_name', 'cwid',)

@admin.register(MigrationLog)
class MigrationLogAdmin(admin.ModelAdmin):
    list_display = ('project',
					'node_origin',
					'node_destination',
					'comments',
					)

    search_fields = ('project', 'node_origin', 'node_destination','comments')



admin.site.register(Access_Log)
admin.site.register(AccessPermission)
admin.site.register(Audit_Log)
admin.site.register(Data_Log)
admin.site.register(Department)
admin.site.register(DC_Administrator)
admin.site.register(EnvtSubtype)
admin.site.register(External_Access_Log)
admin.site.register(ResourceLog)
admin.site.register(SN_Ticket)
admin.site.register(Software)
admin.site.register(Software_License_Type)
admin.site.register(Software_Log)
admin.site.register(Software_Purchase)
admin.site.register(Storage_Log)
admin.site.register(SubFunction)