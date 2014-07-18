from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from dmt.main.models import User as PMTUser
from dmt.main.models import InGroup
from dmt.main.tests.factories import ItemFactory, MilestoneFactory
from dmt.main.tests.support.mixins import LoggedInTestMixin
import unittest


class ActiveProjectTests(LoggedInTestMixin, TestCase):
    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
    def test_active_project_view(self):
        r = self.client.get(reverse('active_projects_report'))
        self.assertEqual(r.status_code, 200)


class UserWeeklyTest(LoggedInTestMixin, TestCase):
    def test_user_weekly(self):
        r = self.client.get("/report/user/testuser/weekly/")
        self.assertEqual(r.status_code, 200)

    def test_user_weekly_date_specified(self):
        r = self.client.get("/report/user/testuser/weekly/?date=2012-12-16")
        self.assertEqual(r.status_code, 200)


class UserYearlyTest(LoggedInTestMixin, TestCase):
    def test_yearly_review_redirect(self):
        r = self.client.get("/report/yearly_review/")
        self.assertEqual(r.status_code, 302)

    def test_user_yearly(self):
        r = self.client.get("/report/user/testuser/yearly/")
        self.assertEqual(r.status_code, 200)


class StaffReportTest(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(StaffReportTest, self).setUp()
        self.pg = PMTUser.objects.create(username='grp_programmers',
                                         fullname='programmers (group)')
        InGroup.objects.create(grp=self.pg, username=self.pu)

    def test_staff_report_date_specified(self):
        r = self.client.get("/report/staff/?date=2012-12-16")
        self.assertEqual(r.status_code, 200)

    def test_staff_report(self):
        r = self.client.get("/report/staff/")
        self.assertEqual(r.status_code, 200)

    def test_staff_report_previous(self):
        r = self.client.get("/report/staff/previous/")
        self.assertEqual(r.status_code, 302)


class ResolvedItemsTest(LoggedInTestMixin, TestCase):
    def test_view(self):
        i = ItemFactory(status='RESOLVED')
        r = self.client.get(reverse('resolved_items_report'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(i.title in r.content)


class WeeklySummaryTests(LoggedInTestMixin, TestCase):
    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
    def test_weekly_summary_view(self):
        r = self.client.get(reverse('weekly_summary_report'))
        self.assertEqual(r.status_code, 200)


class PassedMilestonesViewTests(LoggedInTestMixin, TestCase):
    def test_report(self):
        m = MilestoneFactory(target_date='2000-01-01', status='OPEN')
        r = self.client.get(reverse('passed_milestones_report'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(m.name in r.content)
