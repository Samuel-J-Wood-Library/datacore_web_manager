import datetime
import unittest

from django.test import TestCase
from django.test import Client

from django.db import IntegrityError
from django.contrib.auth.models import User
from django.urls import reverse

from django.utils import timezone

from .models import Server, Project, DC_User, Access_Log, EnvtSubtype, SubFunction
from .models import StorageCost

from .forms import StorageChangeForm


class ProjectModelTests(TestCase):

    def test_project_id_is_unique(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        
        first_project = Project(dc_prj_id="prj123")
        second_project = Project(dc_prj_id="prj123")
        self.assertEqual(first_project.dc_prj_id, second_project.dc_prj_id)

class TestAccess(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('john', 
                                            'lennon@thebeatles.com', 
                                            'johnpassword'
                                            )
        cls.client = Client()

    
    def test_call_view_denies_anonymous(self):
        response = self.client.get(reverse('dc_management:index'), follow=True)
        self.assertRedirects(response, '/login/?next=/info/')
        response = self.client.post(reverse('dc_management:index'), follow=True)
        self.assertRedirects(response, '/login/?next=/info/')
        pages = ['all_users',
                 'all_projects',
                 'dc_user-add',
                 'url_generator',
                 'govdocmeta-add',
                 'usertoproject-add',
                 'email_results',
                 'finances-active',
                 'file-transfer-add',
        ]
        for p in pages:
            url = reverse('dc_management:'+p)
            
            response = self.client.get(reverse('dc_management:'+p), follow=True)
            self.assertRedirects(response, '/accounts/login/?next='+url)
            response = self.client.post(reverse('dc_management:'+p), follow=True)
            self.assertRedirects(response, '/accounts/login/?next='+url)

        argpages = ['project',
                     'node', 
                     'dcuser',
                     'govdoc',
                     'project-update',
                     'thisusertoproject-add',
                     'storage-change',
                     'govdocmeta-update',
                     'file-transfer-view',
                     'usertothisproject-add',
                     'usertothisproject-remove',
                     'url_result',
                     'dc_user-update',
                     'govdocmeta',
                    ]
        for p in argpages:
            url = reverse('dc_management:'+p, args=[1])
            
            response = self.client.get(reverse('dc_management:'+p, args=[1]), 
                                        follow=True)
            self.assertRedirects(response, '/accounts/login/?next='+url)
            response = self.client.post(reverse('dc_management:'+p, args=[1]),
                                         follow=True)
            self.assertRedirects(response, '/accounts/login/?next='+url)
                    


    def test_call_view_loads(self):
        # defined in fixture or with factory in setUp()
        self.client.login(username='john', password='johnpassword')
          
        response = self.client.get(reverse('dc_management:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'dc_management/index.html')



class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.user = User.objects.create_user('john', 
                                            'lennon@thebeatles.com', 
                                            'johnpassword'
                                            )
        # don't forget to log in!
        self.client.login(username='john', password='johnpassword')
        
    def test_details(self):
        # Issue a GET request.
        response = self.client.get(reverse('dc_management:index'))

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the rendered context contains 0 customers.
        self.assertEqual(len(response.context['user_list']), 0)

class ProjectTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.user = User.objects.create_user(
            username='testuser', email='pro2004@med.cornell.edu', password='top_secret')
        
        cls.js = DC_User.objects.create(first_name='John', 
                                        last_name='Smith', 
                                        cwid='jos1234',
                                        )
        cls.jd = DC_User.objects.create(first_name='Jane', 
                                        last_name='Doe', 
                                        cwid='jed2001',
                                        )
        cls.env = EnvtSubtype.objects.create(name='cool_research')
        cls.subfn = SubFunction.objects.create(name='impo_subfn')
        cls.host = Server.objects.create(   status = "ON",
                            function = "PR",
                            machine_type = "VM",
                            vm_size = "MD",
                            backup = "EN",
                            operating_sys = "M2",
                            node = "HPRP010",
                            sub_function = cls.subfn,
                            name_address = "vITS-HPCP02.med.cornell.edu",
                            ip_address = "10.36.217.229",
                            processor_num = 4,
                            ram = 16,
                            disk_storage = 100,
                            other_storage = 100,   
                            connection_date = datetime.date(2014, 6, 30),
                            comments = "This is an awesome test server for unittest",
        )
        cls.prj1 = Project.objects.create( dc_prj_id = 'prj0006',
                                title = 'test project',
                                nickname = 'testy',
                                fileshare_storage = 100,
                                direct_attach_storage = 100,
                                backup_storage = 0,
                                requested_ram = 16,
                                requested_cpu = 4,
                                pi = cls.js,
                                env_type = 'RE',
                                env_subtype = cls.env,
                                expected_completion = datetime.date(2018, 7, 13),
                                requested_launch = datetime.date(2018, 2, 13),
                                status = 'RU',
                                predata_date = datetime.date(2017, 12, 1),
                                postdata_date = datetime.date(2017, 12, 13),
                                host = cls.host,
                                comments = "This is a test project for unittest",
        )
        cls.prj2 = Project.objects.create( dc_prj_id = 'prj0007',
                                title = 'minimal test project',
                                nickname = 'minitest',
                                pi = cls.jd,
                                env_type = 'RE',
                                env_subtype = cls.env,
                                expected_completion = datetime.date(2018, 7, 13),
                                requested_launch = datetime.date(2018, 2, 13),
                                status = 'RU',
        )
        cls.stor_direct = StorageCost.objects.create(
            record_author = cls.user,
            storage_type = 'direct storage',
            st_cost_per_gb = 0.3,
        )
        cls.stor_fileshare = StorageCost.objects.create(
            record_author = cls.user,
            storage_type = 'fileshare with replication',
            st_cost_per_gb = 0.3,
        )
        cls.stor_vbckup = StorageCost.objects.create(
            record_author = cls.user,
            storage_type = 'versioned backup',
            st_cost_per_gb = 1.2,
        )
        
    def test_unique_cwid(self):
        with self.assertRaises(IntegrityError):
            newbie = DC_User.objects.create(first_name='Tim', 
                                            last_name='Taylor', 
                                            cwid='jos1234')

        
class StorageTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='pro2004@med.cornell.edu', password='top_secret')
        
        js = DC_User.objects.create(first_name='John', last_name='Smith', cwid='jos1234')
        jd = DC_User.objects.create(first_name='Jane', last_name='Doe', cwid='jed2001')
        env = EnvtSubtype.objects.create(name='cool_research')
        subfn = SubFunction.objects.create(name='impo_subfn')
        host = Server.objects.create(   status = "ON",
                            function = "PR",
                            machine_type = "VM",
                            vm_size = "MD",
                            backup = "EN",
                            operating_sys = "M2",
                            node = "HPRP010",
                            sub_function = subfn,
                            name_address = "vITS-HPCP02.med.cornell.edu",
                            ip_address = "10.36.217.229",
                            processor_num = 4,
                            ram = 16,
                            disk_storage = 100,
                            other_storage = 100,   
                            connection_date = datetime.date(2014, 6, 30),
                            comments = "This is an awesome test server for unittest",
        )
        self.prj1 = Project.objects.create( dc_prj_id = 'prj0006',
                                title = 'test project',
                                nickname = 'testy',
                                fileshare_storage = 100,
                                direct_attach_storage = 100,
                                backup_storage = 0,
                                requested_ram = 16,
                                requested_cpu = 4,
                                pi = js,
                                env_type = 'RE',
                                env_subtype = env,
                                expected_completion = datetime.date(2018, 7, 13),
                                requested_launch = datetime.date(2018, 2, 13),
                                status = 'RU',
                                predata_date = datetime.date(2017, 12, 1),
                                postdata_date = datetime.date(2017, 12, 13),
                                host = host,
                                comments = "This is a test project for unittest",
        )
        self.prj2 = Project.objects.create( dc_prj_id = 'prj0007',
                                title = 'minimal test project',
                                nickname = 'minitest',
                                pi = jd,
                                env_type = 'RE',
                                env_subtype = env,
                                expected_completion = datetime.date(2018, 7, 13),
                                requested_launch = datetime.date(2018, 2, 13),
                                status = 'RU',
        )
        self.stor_direct = StorageCost.objects.create(
            record_author = self.user,
            storage_type = 'direct storage',
            st_cost_per_gb = 0.3,
        )
        self.stor_fileshare = StorageCost.objects.create(
            record_author = self.user,
            storage_type = 'fileshare with replication',
            st_cost_per_gb = 0.3,
        )
        self.stor_vbckup = StorageCost.objects.create(
            record_author = self.user,
            storage_type = 'versioned backup',
            st_cost_per_gb = 1.2,
        )
           
    def test_unique_cwid(self):
        with self.assertRaises(IntegrityError):
            newbie = DC_User.objects.create(first_name='Tim', 
                                            last_name='Taylor', 
                                            cwid='jos1234')
    """        
    def test_valid_data(self):
        form = StorageChangeForm({
                    'sn_ticket':"INC1006733",
                    'date_changed':"2017-12-26",
                    'project':self.prj2.pk,
                    'storage_amount':200,
                    'storage_type':self.stor_fileshare.pk,
                    'comments':"random comment",
                    'record_author':self.user.pk
        })
        
        
        #self.assertTrue(form.is_valid())
        form.record_author = self.user
        form.record_author_id = self.user.pk
        self.assertTrue(form.is_valid())
        changelog = form.save()
        self.assertEqual(changelog.sn_ticket, "INC1006733")
        self.assertEqual(changelog.date_changed, datetime.date(2017, 12, 26))
        self.assertEqual(changelog.project, self.prj2.pk)
        self.assertEqual(changelog.storage_amount, 200)
        self.assertEqual(changelog.storage_type, self.stor_fileshare.pk)
        self.assertEqual(changelog.comments, "random comment")

    def test_blank_data(self):
        form = StorageChangeForm({})
        self.assertFalse(form.is_valid())
    """    
   