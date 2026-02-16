from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reporter', 'reported_user', 'report_type', 'status', 
                    'handler', 'created_at', 'handled_at']
    list_filter = ['status', 'report_type']
    search_fields = ['reporter__username', 'reported_user__username', 'description']
    raw_id_fields = ['reporter', 'reported_user', 'handler']
    ordering = ['-created_at']
