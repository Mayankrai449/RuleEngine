from rest_framework import serializers
from .models import Rule

class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ['id', 'name', 'rule_string', 'ast_json', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['created_at', 'updated_at']