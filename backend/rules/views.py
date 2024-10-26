from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Rule
from .serializers import RuleSerializer
from django.shortcuts import get_object_or_404
from .utils import *
from django.core.cache import cache

class CreateRuleView(APIView):
    def post(self, request):
        rule_string = request.data.get("rule_string")
        name = request.data.get("name", "Unnamed Rule")
        
        if not rule_string:
            return Response(
                {"error": "rule_string is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        parser = RuleParser()
        try:
            # Parse rule to AST
            ast_root = parser.parse(rule_string)
            
            # Convert AST to JSON-serializable format
            def node_to_dict(node):
                if node is None:
                    return None
                return {
                    'type': node.type,
                    'value': node.value,
                    'left': node_to_dict(node.left),
                    'right': node_to_dict(node.right)
                }
            
            ast_json = node_to_dict(ast_root)

            rule = Rule.objects.create(
                name=name,
                rule_string=rule_string,
                ast_json=ast_json
            )
            
            return Response(
                RuleSerializer(rule).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {"error": f"Invalid rule syntax: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class CombineRulesView(APIView):
    def post(self, request):
        rule_ids = request.data.get("rule_ids", [])
        operator = request.data.get("operator", "OR").upper()
        name = request.data.get("name", "Combined Rule")
        
        if not rule_ids or not isinstance(rule_ids, list):
            return Response(
                {"error": "A list of rule_ids is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if operator not in RuleParser.OPERATORS:
            return Response(
                {"error": f"Invalid operator. Must be one of: {', '.join(RuleParser.OPERATORS.keys())}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rules = Rule.objects.filter(id__in=rule_ids, is_active=True)
            if len(rules) != len(rule_ids):
                return Response(
                    {"error": "One or more rules not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Combine rule strings
            combined_rule_string = f" {operator} ".join([f"({rule.rule_string})" for rule in rules])
            
            # Create parser instance and parse combined rule
            parser = RuleParser()
            try:
                ast_root = parser.parse(combined_rule_string)
            except ValueError as e:
                return Response(
                    {"error": f"Error parsing combined rule: {str(e)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Convert AST to JSON-serializable format
            def node_to_dict(node: Optional['Node']) -> Optional[Dict[str, Any]]:
                if node is None:
                    return None
                return {
                    'type': node.type,
                    'value': node.value,
                    'left': node_to_dict(node.left),
                    'right': node_to_dict(node.right)
                }
            
            # Create new combined rule
            combined_rule = Rule.objects.create(
                name=name,
                rule_string=combined_rule_string,
                ast_json=node_to_dict(ast_root)
            )
            
            return Response(
                RuleSerializer(combined_rule).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {"error": f"Error combining rules: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class EvaluateRuleView(APIView):
    def post(self, request):
        rule_id = request.data.get("rule_id")
        data = request.data.get("data", {})
        
        if not rule_id:
            return Response(
                {"error": "rule_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(data, dict):
            return Response(
                {"error": "data must be a dictionary"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f"rule_eval_{rule_id}_{hash(frozenset(data.items()))}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return Response({"result": cached_result})

        try:
            rule = Rule.objects.get(id=rule_id, is_active=True)
            
            # Evaluate the rule using the AST
            try:
                result = RuleEvaluator.evaluate_node(rule.ast_json, data)
            except ValueError as e:
                return Response(
                    {"error": f"Error evaluating rule: {str(e)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cache the result
            cache.set(cache_key, result, timeout=300)  # 5 minutes cache
            
            return Response({
                "result": result,
                "rule_string": rule.rule_string
            })
            
        except Rule.DoesNotExist:
            return Response(
                {"error": "Rule not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error evaluating rule: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class RuleListView(APIView):            # get all rules
    def get(self, request):
        active_only = request.query_params.get('active_only', 'true').lower() == 'true'
        
        queryset = Rule.objects.all()
        if active_only:
            queryset = queryset.filter(is_active=True)
            
        rules = queryset.order_by('-created_at')
        serializer = RuleSerializer(rules, many=True)
        return Response(serializer.data)
    
class RuleDetailView(APIView):              # get rule by id
    def get(self, request, rule_id):
        rule = get_object_or_404(Rule, id=rule_id)
        serializer = RuleSerializer(rule)
        return Response(serializer.data, status=status.HTTP_200_OK)