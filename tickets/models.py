from django.conf import settings
from django.db import models


class Profile(models.Model):
    ADMIN, AGENT, EMPLOYEE = 'admin', 'agent', 'employee'
    ROLE_CHOICES = [(ADMIN, 'Admin'), (AGENT, 'IT Agent'), (EMPLOYEE, 'Employee')]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=EMPLOYEE)

    @property
    def is_staff_role(self):
        return self.role in (self.ADMIN, self.AGENT)

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ticket(models.Model):
    OPEN, IN_PROGRESS, CLOSED = 'open', 'in_progress', 'closed'
    STATUS_CHOICES = [(OPEN, 'Open'), (IN_PROGRESS, 'In Progress'), (CLOSED, 'Closed')]
    PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]

    title = models.CharField(max_length=120)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='tickets')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=OPEN)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} {self.title}'


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
