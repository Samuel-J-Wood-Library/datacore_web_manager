#    CODE BOOK     
---  
##  Comment Models   

###  AlertTag
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | alertcomment  | TextField | --- |
    | cleared  | DateTimeField | --- |
    
###  CommentLog
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | comment  | TextField | --- |
    | parent_comment  | ForeignKey | --- |
##  Software Models   

###  Software_License_Type
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | sn_ticket  | CharField | --- |
    | name  | CharField | --- |
    | user_assigned  | BooleanField | --- |
    | concurrent  | BooleanField | --- |
    | monitored  | BooleanField | --- |

###  Software
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | name  | CharField | --- |
    | vendor  | CharField | --- |
    | version  | CharField | --- |
    | license_type  | ForeignKey | --- |
    | package  | BooleanField | --- |
    | purchase_details  | TextField | --- |
    | comments  | TextField | --- |
    | dynamic_comments  | ManyToManyField | --- |

###  SoftwareUnit
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | unit  | CharField | --- |
    
##   Server Models  

###  SubFunction
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | name  | CharField | --- |

###  EnvtSubtype
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | name  | CharField | --- |

###  Server
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | ON = 'ON'
    | OFF = 'OF'
    | DECOMMISSIONED = 'DE'
    | STATUS_CHOICES =  | --- |
    | status  | CharField | --- |
    | PRODUCTION = 'PR'
    | TEST = 'TE'
    | DEVELOPMENT = 'DE'
    | FUNCTION_CHOICES =  | --- |
    | function  | CharField | --- |
    | VM = "VM"
    | VDI = "VD"
    | MACHINE_TYPE_CHOICES =  | --- |
    | machine_type  | CharField | --- |
    | SMALL = "SM"
    | MEDIUM = "MD"
    | LARGE = "LG"
    | XLARGE = "XL"
    | VM_SIZE_CHOICES =  | --- |
    | vm_size  | CharField | --- |
    | ENCRYPTED = "EN"
    | UNENCRYPTED = "UE"
    | BACKUP_CHOICES =  | --- |
    | backup  | CharField | --- |
    | MWS2008 = "M8" 
    | MWS2012 = "M2" 
    | MWS2016 = "M6"
    | RHEL7 = "R7" 
    | WINDOWS7 = "W7" 
    | OS_CHOICES =  | --- |
    | operating_sys  | CharField | --- |
    | node  | CharField | --- |
    | sub_function  | ForeignKey | --- |
    | name_address  | CharField | --- |
    | ip_address  | GenericIPAddressField | --- |
    | processor_num  | IntegerField | --- |
    | ram  | IntegerField | --- |
    | disk_storage  | IntegerField | --- |
    | other_storage  | IntegerField | --- |
    | software_installed  | ManyToManyField | --- |
    | connection_date  | DateField | --- |
    | dns_name  | CharField | --- |
    | host  | CharField | --- |
    | comments  | TextField | --- |
    | dynamic_comments  | ManyToManyField | --- |

###  Department
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | name  | CharField | --- |   

###  DC_User
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | sn_ticket  | CharField | --- |
    | cwid  | CharField | --- |
    | first_name  | CharField | --- |
    | last_name  | CharField | --- |
    | email  | CharField | --- |
    | department  | ForeignKey | --- |
    | WCM = "WC"
    | NYP = "NP"
    | ROCKU = "RU"
    | MSKCC = "SK"
    | COLUMBIA = "CO"
    | OTHER = "OT" # note this is also used in ROLE_CHOICES
    | AFFILIATION_CHOICES =  | --- |
    | affiliation  | CharField | --- |
    | FACULTY = 'FC'
    | RESEARCHER = 'RE'
    | AFFILIATE = 'AF'
    | RESEARCH_COORDINATOR = 'RC'
    | STUDENT = 'ST'
    | STATISTICIAN = 'SN'
    | VOLUNTEER = 'VO'
    | STAFF = 'SF'
    | DATACORE = 'DC'
    | EXPIRED = 'EX'
    | OTHER = 'OT' # note this is also used in AFFILIATION_CHOICES
    | ROLE_CHOICES =  | --- |
    | role  | CharField | --- |
    | comments  | TextField | --- |
    | dynamic_comments  | ManyToManyField | --- |
    
## Project Models   
 

###  Project
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | dc_prj_id  | CharField | --- |
    | title  | CharField | --- |
    | nickname  | CharField | --- |
    | open_allowed  | NullBooleanField | --- |
    | open_enabled  | NullBooleanField | --- |
    | isolate_data  | NullBooleanField | --- |
    | fileshare_storage  | IntegerField | --- |
    | direct_attach_storage  | IntegerField | --- |
    | backup_storage  | IntegerField | --- |
    | requested_ram  | IntegerField | --- |
    | requested_cpu  | IntegerField | --- |
    | users  | ManyToManyField | --- |
    | pi  | ForeignKey | --- |
    | prj_admin  | ForeignKey | --- |
    | software_installed  | ManyToManyField | --- |
    | software_requested  | ManyToManyField | --- |
    | THESIS = 'TH'
    | RESEARCH = 'RE'
    | CLASS = 'CL'
    | ENV_TYPE_CHOICES =  | --- |
    | env_type  | CharField | --- |
    | env_subtype  | ForeignKey | --- |
    | expected_completion  | DateField | --- |
    | requested_launch  | DateField | --- |
    | ONBOARDING = "ON"
    | RUNNING = "RU"
    | COMPLETED = "CO"
    | SUSPENDED = "SU"
    | SHUTTINGDOWN = "SD"
    | STATUS_CHOICES =  | --- |
    | status  | CharField | --- |
    | sn_tickets  | CharField | --- |
    | predata_ticket  | CharField | --- |
    | predata_date  | DateField | --- |
    | postdata_ticket  | CharField | --- |
    | postdata_date  | DateField | --- |
    | wrapup_ticket  | CharField | --- |
    | wrapup_date  | DateField | --- |
    | completion_ticket  | CharField | --- |
    | completion_date  | DateField | --- |
    | host  | ForeignKey | --- |
    | prj_dns  | CharField | --- |
    | myapp  | NullBooleanField | --- |
    | db  | ForeignKey | --- |
    | user_cost  | FloatField | --- |
    | host_cost  | FloatField | --- |
    | db_cost  | FloatField | --- |
    | fileshare_cost  | FloatField | --- |
    | direct_attach_cost  | FloatField | --- |
    | backup_cost  | FloatField | --- |
    | software_cost  | FloatField | --- |
    | project_total_cost  | FloatField | --- |
    | comments  | TextField | --- |
    | dynamic_comments  | ManyToManyField | --- |

###  AccessPermission
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | name  | CharField | --- |
    | description  | TextField | --- |
    
## Governance Models 

###  Governance_Doc
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | sn_ticket  | CharField | --- |
    | doc_id  | CharField | --- |
    | date_issued  | DateField | --- |
    | expiry_date  | DateField | --- |
    | users_permitted  | ManyToManyField | --- |
    | access_allowed  | ForeignKey | --- |
    | IRB = 'IR'
    | IRB_EXEMPTION = 'IX'
    | DUA = 'DU'
    | DCA = 'DC'
    | ONBOARDING = 'ON'
    | GOVERNANCE_TYPE_CHOICES =  | --- |
    | governance_type  | CharField | --- |
    | defers_to_doc  | ForeignKey | --- |
    | supersedes_doc  | ForeignKey | --- |
    | project  | ForeignKey | --- |
    | documentation  | FileField | --- |
    | destroy_data  | NullBooleanField | --- |
    | comments  | TextField | --- |
    | dynamic_comments  | ManyToManyField | --- |
    | isolate_data  | NullBooleanField | --- |

###  DC_Administrator
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | sn_ticket  | CharField | --- |
    | cwid  | CharField | --- |
    | first_name  | CharField | --- |
    | last_name  | CharField | --- |
    | role  | CharField | --- |
    | date_started  | DateField | --- |
    | date_finished  | DateField | --- |
    
###  DCUAGenerator
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | project  | ForeignKey | --- |
    | ticket  | CharField | --- |
    | startdate  | CharField | --- |
    | enddate  | CharField | --- |
    | folder1  | CharField | --- |
    | folder2  | CharField | --- |
    | folder3  | CharField | --- |
    | folder4  | CharField | --- |
    | folder5  | CharField | --- |
    | folder6  | CharField | --- |
    | folder7  | CharField | --- |
    | url  | CharField | --- |

###  Protocols
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | created_by  | ForeignKey | --- |
    | edited_by  | ForeignKey | --- |
    | ticket_description  | TextField | --- |
    | dc_description  | TextField | --- |

##  Finance Models   

###  SoftwareCost
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | software  | ForeignKey | --- |
    | software_cost  | FloatField | --- |
    | cost_classroom  | FloatField | --- |
    | cost_student  | FloatField | --- |
    

###  UserCost
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | user_quantity  | IntegerField | --- |
    | user_cost      | FloatField | --- |
    

###  StorageCost
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | storage_type  | CharField | --- |
    | st_cost_per_gb  | FloatField | --- |


## Log / Audit Models 

###  External_Access_Log
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | sn_ticket  | CharField | --- |
    | date_connected  | DateField | --- |
    | date_disconnected  | DateField | --- |
    | user_requesting  | ForeignKey | --- |
    | project_connected  | ForeignKey | --- |
    | setup_charge  | BooleanField | --- |
    | hosting_charge  | BooleanField | --- |

###  Software_Log
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | sn_ticket  | CharField | --- |
    | change_date  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | applied_to_prj  | ForeignKey | --- |
    | applied_to_node  | ForeignKey | --- |
    | applied_to_user  | ForeignKey | --- |
    | software_changed  | ForeignKey | --- |
    | comments  | TextField | --- |
    | ADD_ACCESS = 'AA'
    | REMOVE_ACCESS = 'RA'
    | CHANGE_TYPE_CHOICES =  | --- |
    | change_type   | CharField | --- |
    

###  Software_Purchase
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | sn_ticket  | CharField | --- |
    | date_purchased  | DateField | --- |
    | software  | ForeignKey | --- |
    | num_units_purchased  | IntegerField | --- |
    | unit_type  | ForeignKey | --- |
    | expiration  | DateField | --- |
    | invoice_number  | CharField | --- |
    | MAINTENANCE = 'MN'
    | ADDITIONAL = 'AD'
    | PURPOSE_CHOICES =  | --- |
    | purpose   | CharField | --- |
    | cost  | FloatField | --- |
    | documentation  | FileField | --- |
    | comments  | TextField | --- |
    
###  Access_Log
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | sn_ticket  | CharField | --- |
    | date_changed  | DateField | --- |
    | dc_user  | ForeignKey | --- |
    | prj_affected  | ForeignKey | --- |
    | ADD_ACCESS = 'AA'
    | REMOVE_ACCESS = 'RA'
    | CHANGE_TYPE_CHOICES =  | --- |
    | change_type   | CharField | --- |

###  Audit_Log
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | performed_by  | ForeignKey | --- |
    | sn_ticket  | CharField | --- |
    | audit_date  | DateField | --- |
    | dc_user  | ForeignKey | --- |
    | project  | ForeignKey | --- |
    | node  | ForeignKey | --- |
    | governance_docs  | ForeignKey | --- |
    | comments  | TextField | --- |

###  Storage_Log
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | sn_ticket  | CharField | --- |
    | date_changed  | DateField | --- |
    | project  | ForeignKey | --- |
    | storage_amount  | IntegerField | --- |
    | storage_type  | ForeignKey | --- |
    | comments  | TextField | --- |
    
###  ResourceLog
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | sn_ticket  | CharField | --- |
    | date_changed  | DateField | --- |
    | project  | ForeignKey | --- |
    | new_RAM  | IntegerField | --- |
    | new_CPU  | IntegerField | --- |
    | comments  | TextField | --- |
    

###  TransferMethod
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | transfer_method   | CharField | --- |

###  FileTransfer
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | change_date  | DateField | --- |
    | ticket  | CharField | --- |
    | external_source  | CharField | --- |
    | source  | ForeignKey | --- |
    | external_destination  | CharField | --- |
    | destination  | ForeignKey | --- |
    | filenames  | TextField | --- |
    | filepath_dest  | TextField | --- |
    | transfer_method  | ForeignKey | --- |
    | requester  | ForeignKey | --- |
    | file_num  | IntegerField | --- |
    | file_num_unknown  | NullBooleanField | --- |
    | DEIDENTIFIED = 'DE'
    | IDENTIFIED = 'ID'
    | LIMITED = 'LM'
    | NOTDETERMINED = 'ND'
    | DATA_TYPE_CHOICES =  | --- |
    | data_type   | CharField | --- |
    | reviewed_by  | ForeignKey | --- |
    | comment  | TextField | --- |

###  Data_Log
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | change_date  | DateField | --- |
    | IMPORT = 'IM'
    | EXPORT = 'EX'
    | DIRECTION_TYPE_CHOICES =  | --- |
    | direction   | CharField | --- |
    | project  | ForeignKey | --- |
    | request_ticket  | CharField | --- |
    | transfer_ticket  | CharField | --- |
    | authorized_by  | ForeignKey | --- |
    | reviewed_by  | ForeignKey | --- |
    | file_description  | TextField | --- |
    | TRANSFERMED = 'TM'
    | PHYSICAL = 'PH'
    | EMAIL = 'EM'
    | SFTP = 'SF'
    | POPMED = 'PM'
    | TRANSFER_METHOD_CHOICES =  | --- |
    | transfer_method   | CharField | --- |

###  Server_Change_Log
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | sn_ticket  | CharField | --- |
    | change_date  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | node_changed  | ForeignKey | --- |
    | CONNECTED = 'CO'
    | DISCONNECTED = 'DC'
    | STATE_CHANGE_CHOICES =  | --- |
    | state_change   | CharField | --- |
    | ADD_STORAGE = 'AS'
    | REM_STORAGE = 'RS'
    | STORAGE_CHANGE_CHOICES =  | --- |
    | state_change   | CharField | --- |
    | change_amount  | IntegerField | --- |
    | comments  | TextField | --- |

###  AlertTagType
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | name  | CharField | --- |
    | description  | TextField | --- |

###  MigrationLog
    | FIELD | FIELD_TYPE | DESCRIPTION |
    | --- | --- | --- |
    | record_creation  | DateField | --- |
    | record_update  | DateField | --- |
    | record_author  | ForeignKey | --- |
    | project  | ForeignKey | --- |
    | node_origin  | ForeignKey | --- |
    | node_destination  | ForeignKey | --- | 
    | access_ticket  | CharField | --- |
    | access_date  | DateField | --- |
    | envt_ticket  | CharField | --- |
    | envt_date  | DateField | --- |
    | data_ticket  | CharField | --- |
    | data_date  | DateField | --- |
    | comments  | TextField | --- |
   