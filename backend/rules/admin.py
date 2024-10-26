from django.contrib import admin
from .models import Rule

@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'rule_string', 'created_at', 'updated_at')
    search_fields = ('rule_string',)
    list_filter = ('created_at',)
