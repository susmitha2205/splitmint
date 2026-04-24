from django.contrib import admin
from .models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'category', 'get_member_count', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    filter_horizontal = ['members']

    def get_member_count(self, obj):
        return obj.get_member_count()
    get_member_count.short_description = 'Members'
