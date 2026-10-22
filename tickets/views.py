from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AssignForm, CommentForm, RegisterForm, TicketForm
from .models import Category, Ticket


def is_staff_role(user):
    return user.is_authenticated and user.profile.is_staff_role


def visible_tickets(user):
    """Role-based access: staff roles see everything, employees only their own."""
    qs = Ticket.objects.select_related('category', 'created_by', 'assigned_to')
    return qs if is_staff_role(user) else qs.filter(created_by=user)


def register(request):
    if request.user.is_authenticated:
        return redirect('ticket_list')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Welcome! Your account has been created.')
        return redirect('ticket_list')
    return render(request, 'registration/register.html', {'form': form})


@login_required
def ticket_list(request):
    qs = visible_tickets(request.user)
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    category = request.GET.get('category', '')
    priority = request.GET.get('priority', '')
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if status:
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category_id=category)
    if priority:
        qs = qs.filter(priority=priority)
    page = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'tickets/ticket_list.html', {
        'page': page, 'categories': Category.objects.all(),
        'statuses': Ticket.STATUS_CHOICES, 'priorities': Ticket.PRIORITY_CHOICES,
        'filters': {'q': q, 'status': status, 'category': category, 'priority': priority},
    })


@login_required
def ticket_create(request):
    form = TicketForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False)
        ticket.created_by = request.user
        ticket.save()
        messages.success(request, f'Ticket #{ticket.pk} created.')
        return redirect('ticket_detail', pk=ticket.pk)
    return render(request, 'tickets/ticket_form.html', {'form': form})


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(visible_tickets(request.user), pk=pk)
    staff = is_staff_role(request.user)
    comment_form = CommentForm()
    assign_form = AssignForm(instance=ticket) if staff else None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'comment':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                c = comment_form.save(commit=False)
                c.ticket, c.author = ticket, request.user
                c.save()
                messages.success(request, 'Comment added.')
                return redirect('ticket_detail', pk=pk)
        elif action == 'assign' and staff:
            assign_form = AssignForm(request.POST, instance=ticket)
            if assign_form.is_valid():
                assign_form.save()
                messages.success(request, 'Ticket updated.')
                return redirect('ticket_detail', pk=pk)

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket, 'comments': ticket.comments.select_related('author'),
        'comment_form': comment_form, 'assign_form': assign_form, 'staff': staff,
    })


@login_required
@require_POST
def ticket_toggle(request, pk):
    """Close an open ticket or reopen a closed one (owner or staff roles only)."""
    ticket = get_object_or_404(visible_tickets(request.user), pk=pk)
    if ticket.status == Ticket.CLOSED:
        ticket.status = Ticket.OPEN
        messages.info(request, f'Ticket #{pk} reopened.')
    else:
        ticket.status = Ticket.CLOSED
        messages.info(request, f'Ticket #{pk} closed.')
    ticket.save(update_fields=['status', 'updated_at'])
    return redirect('ticket_detail', pk=pk)
