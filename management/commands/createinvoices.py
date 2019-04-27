from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User

from dc_management.models import   (Project, 
                                    ProjectBillingRecord,
                                    SoftwareCost,
                                    UserCost, 
                                    StorageCost,
                                    ExtraResourceCost,
                                    DatabaseCost,
                                    )

class Command(BaseCommand):
    help = 'Creates an invoice for all projects'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)

    def handle(self, *args, **options):
        # Try to get the user 
        try:
            user = User.object.get(username=options['username'])
        except User.DoesNotExist:
            raise CommandError('User {} does not exist'.format(options['username']))
                            
        # get active projects (full billing)
        active_projects = Project.objects.filter(status='RU'
                                        ).exclude(env_type='CL'
                                        )
        
        active_classrooms = Project.objects.filter(status='RU', env_type='CL'
                                        )
        
        # get completed, suspended or onboarding projects (charge storage only)
        inactive_projects = Project.objects.exclude(status='RU')
        
        for p in active_projects:
            # base charge
            try: 
                base_cost = UserCost.object.get(user_quantity=p.users.count()).user_cost
            except UserCost.DoesNotExist:
                base_cost = 0
                self.stdout.write(self.style.ERROR(
                    "Base rate not found for {} users ({})".format( p.users.count(), 
                                                                    p,)
                                                    )
                )            
            
            ### storage costs
            # primary
            primary_rate = StorageCost.objects.get(storage_type__icontains='primary'
                                             ).st_cost_per_gb
            primary_cost = p.fileshare_storage * primary_rate
            
            # versioned backup costs
            backup_rate = StorageCost.objects.get(storage_type__icontains='backup'
                                             ).st_cost_per_gb
            backup_cost = p.direct_attach_storage * backup_rate
            
            # direct-attach server storage costs
            direct_rate = StorageCost.objects.get(storage_type__icontains='direct'
                                             ).st_cost_per_gb
            direct_cost = p.backup_storage * direct_rate
        
            # software costs
            sw_total_cost = 0
            for sw in p.software_installed:
                cost_item = SoftwareCost.objects.get(software=sw.pk)
                sw_total_cost += cost_item.software_cost
            
            # extra resources
            extra_cpu = (p.requested_cpu - 4)
            cpu_cost = ExtraResourceCost.objects.get(extra_cpu==extra_cpu).cpu_cost
        
            # databases
            if p.db:
                db_cost = DatabaseCost.db_cost
        
                # search to find if a db setup cost has been charged yet to project
                try:
                    db_setup_invoices = ProjectBillingRecord.objects.get(project=p.pk,
                                                                db_setup>0
                    )
                except ProjectBillingRecord.DoesNotExist:
                    db_setup = DatabaseCost.db_setup
                    
        for poll_id in options['poll_id']:
            try:
                poll = Poll.objects.get(pk=poll_id)
            except Poll.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)

            poll.opened = False
            poll.save()

            self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))

