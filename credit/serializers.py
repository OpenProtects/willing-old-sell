from rest_framework import serializers
from .models import CreditRecord


class CreditRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditRecord
        fields = ['id', 'change_type', 'change_score', 'before_score', 'after_score', 
                  'reason', 'related_order_id', 'related_report_id', 'created_at']
        read_only_fields = ['id', 'created_at']
