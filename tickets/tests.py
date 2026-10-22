from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Profile, Ticket


class TrackerTests(TestCase):
    def setUp(self):
        self.emp = User.objects.create_user('emp', 'e@x.com', 'pass12345!')
        self.emp2 = User.objects.create_user('emp2', 'e2@x.com', 'pass12345!')
        self.agent = User.objects.create_user('agent', 'a@x.com', 'pass12345!')
        Profile.objects.filter(user=self.agent).update(role='agent')
        self.cat = Category.objects.first()
        self.ticket = Ticket.objects.create(title='Laptop wont boot', description='Black screen on startup',
                                            category=self.cat, created_by=self.emp)

    def test_four_categories_seeded(self):
        self.assertEqual(Category.objects.count(), 4)

    def test_login_required(self):
        self.assertEqual(self.client.get(reverse('ticket_list')).status_code, 302)

    def test_employee_sees_only_own_tickets(self):
        self.client.login(username='emp2', password='pass12345!')
        self.assertEqual(self.client.get(reverse('ticket_detail', args=[self.ticket.pk])).status_code, 404)

    def test_agent_sees_all_and_can_assign(self):
        self.client.login(username='agent', password='pass12345!')
        r = self.client.post(reverse('ticket_detail', args=[self.ticket.pk]),
                             {'action': 'assign', 'assigned_to': self.agent.pk, 'status': 'in_progress'})
        self.assertEqual(r.status_code, 302)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.agent)

    def test_employee_cannot_assign(self):
        self.client.login(username='emp', password='pass12345!')
        self.client.post(reverse('ticket_detail', args=[self.ticket.pk]),
                         {'action': 'assign', 'assigned_to': self.agent.pk, 'status': 'closed'})
        self.ticket.refresh_from_db()
        self.assertIsNone(self.ticket.assigned_to)

    def test_close_and_reopen(self):
        self.client.login(username='emp', password='pass12345!')
        url = reverse('ticket_toggle', args=[self.ticket.pk])
        self.client.post(url); self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'closed')
        self.client.post(url); self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'open')

    def test_validation_and_comment_and_search(self):
        self.client.login(username='emp', password='pass12345!')
        r = self.client.post(reverse('ticket_create'), {'title': 'abc', 'description': 'short',
                                                         'category': self.cat.pk, 'priority': 'low'})
        self.assertEqual(r.status_code, 200)  # re-rendered with errors
        self.client.post(reverse('ticket_detail', args=[self.ticket.pk]), {'action': 'comment', 'body': 'Any update?'})
        self.assertEqual(self.ticket.comments.count(), 1)
        r = self.client.get(reverse('ticket_list'), {'q': 'laptop'})
        self.assertContains(r, 'Laptop wont boot')

    def test_register(self):
        r = self.client.post(reverse('register'), {'username': 'new', 'email': 'n@x.com',
                                                    'password1': 'Str0ngPass!234', 'password2': 'Str0ngPass!234'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(User.objects.get(username='new').profile.role, 'employee')
