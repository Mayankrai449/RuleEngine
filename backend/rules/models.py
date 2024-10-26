from django.db import models
from django.core.exceptions import ValidationError
import json

class Rule(models.Model):
    name = models.CharField(max_length=255, default="Unnamed Rule")
    rule_string = models.TextField()
    ast_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.id})"

    def clean(self):
        if not self.rule_string:
            raise ValidationError("Rule string cannot be empty")
        if not self.ast_json:
            raise ValidationError("AST JSON cannot be empty")