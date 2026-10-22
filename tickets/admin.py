from django.contrib import admin

from .models import Category, Comment, Profile, Ticket


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'status', 'priority', 'created_by', 'assigned_to')
    list_filter = ('status', 'category', 'priority')
    search_fields = ('title', 'description')


admin.site.register(Category)
admin.site.register(Comment)
