from django.urls import path
from .views import *

urlpatterns = [
    path('create_rule/', CreateRuleView.as_view(), name='create_rule'),
    path('combine_rules/', CombineRulesView.as_view(), name='combine_rules'),
    path('evaluate_rule/', EvaluateRuleView.as_view(), name='evaluate_rule'),
    path('get/', RuleListView.as_view(), name='rule-list'),
    path('<int:rule_id>/', RuleDetailView.as_view(), name='rule-detail'),
]