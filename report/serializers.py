from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    reported_user_name = serializers.CharField(source='reported_user.username', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    handler_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = ['id', 'reporter', 'reporter_name', 'reported_user', 'reported_user_name',
                  'report_type', 'report_type_display', 'description', 'evidence',
                  'status', 'status_display', 'result', 'handler', 'handler_name',
                  'handled_at', 'created_at']
        read_only_fields = ['id', 'reporter', 'status', 'result', 'handler', 'handled_at', 'created_at']
    
    def get_handler_name(self, obj):
        return obj.handler.username if obj.handler else None


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['reported_user', 'report_type', 'description', 'evidence']
    
    def validate_evidence(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('证据必须是列表格式')
        return value


class ReportHandleSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['resolved', 'rejected'])
    result = serializers.CharField(max_length=500)
    credit_deduction = serializers.IntegerField(min_value=0, max_value=50, required=False, default=0)
