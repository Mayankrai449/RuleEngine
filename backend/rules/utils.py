from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from collections import defaultdict
import re


@dataclass
class Node:
    type: str
    value: Any
    left: Optional['Node'] = None
    right: Optional['Node'] = None

class RuleParser:
    OPERATORS = {
        'AND': {'precedence': 2, 'evaluate': lambda x, y: x and y},
        'OR': {'precedence': 1, 'evaluate': lambda x, y: x or y}
    }
    
    COMPARISONS = {
        '>': lambda x, y: float(x) > float(y),
        '<': lambda x, y: float(x) < float(y),
        '>=': lambda x, y: float(x) >= float(y),
        '<=': lambda x, y: float(x) <= float(y),
        '=': lambda x, y: str(x).strip("'") == str(y).strip("'"),
        '!=': lambda x, y: str(x).strip("'") != str(y).strip("'")
    }

    def tokenize(self, rule_string: str) -> list:
        # First, preserve string literals
        string_literals = []
        def replace_string(match):
            string_literals.append(match.group(0))
            return f"__STR_{len(string_literals)-1}__"
        
        # Replace string literals with placeholders
        processed_string = re.sub(r"'[^']*'", replace_string, rule_string)
        
        # Add spaces around parentheses and operators
        processed_string = re.sub(r'([()])', r' \1 ', processed_string)
        
        # Add spaces around comparison operators (handling multi-character operators first)
        processed_string = re.sub(r'(>=|<=|!=|=|>|<)', r' \1 ', processed_string)
        
        # Split into tokens
        tokens = []
        for token in processed_string.split():
            if token.startswith('__STR_') and token.endswith('__'):
                # Replace placeholder with original string literal
                index = int(token[6:-2])
                tokens.append(string_literals[index])
            else:
                tokens.append(token)
        
        return tokens

    def parse(self, rule_string: str) -> Node:
        tokens = self.tokenize(rule_string)
        node, remaining = self._parse_expression(tokens)
        if remaining:
            raise ValueError(f"Unexpected tokens remaining: {' '.join(remaining)}")
        return node

    def _parse_expression(self, tokens: list) -> tuple[Node, list]:
        if not tokens:
            raise ValueError("Empty expression")

        stack = []
        operators = []

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token == '(':
                # Find matching closing parenthesis
                count = 1
                j = i + 1
                while j < len(tokens) and count > 0:
                    if tokens[j] == '(':
                        count += 1
                    elif tokens[j] == ')':
                        count -= 1
                    j += 1
                if count > 0:
                    raise ValueError("Unmatched parenthesis")
                
                # Parse subexpression
                sub_node, _ = self._parse_expression(tokens[i+1:j-1])
                stack.append(sub_node)
                i = j
                continue

            elif token in self.OPERATORS:
                while (operators and operators[-1] != '(' and 
                       self.OPERATORS[operators[-1]]['precedence'] >= self.OPERATORS[token]['precedence']):
                    self._process_operator(stack, operators.pop())
                operators.append(token)

            else:
                # Handle comparison expression
                if i + 2 < len(tokens) and tokens[i+1] in self.COMPARISONS:
                    comparison = Node(
                        type='comparison',
                        value=tokens[i+1],
                        left=Node('variable', token),
                        right=Node('literal', tokens[i+2])
                    )
                    stack.append(comparison)
                    i += 2
                else:
                    raise ValueError(f"Invalid comparison expression near {token}")

            i += 1

        # Process remaining operators
        while operators:
            self._process_operator(stack, operators.pop())

        if len(stack) != 1:
            raise ValueError("Invalid expression structure")

        return stack[0], []

    def _process_operator(self, stack: list, operator: str) -> None:
        if len(stack) < 2:
            raise ValueError(f"Not enough operands for operator {operator}")
        right = stack.pop()
        left = stack.pop()
        stack.append(Node('operator', operator, left, right))
        
class RuleEvaluator:
    @staticmethod
    def evaluate_node(node: Dict[str, Any], data: Dict[str, Any]) -> bool:
        if node['type'] == 'operator':
            left_result = RuleEvaluator.evaluate_node(node['left'], data)
            right_result = RuleEvaluator.evaluate_node(node['right'], data)
            return RuleParser.OPERATORS[node['value']]['evaluate'](left_result, right_result)
        
        elif node['type'] == 'comparison':
            left_value = data.get(node['left']['value'])
            if left_value is None:
                raise ValueError(f"Variable '{node['left']['value']}' not found in data")
            
            right_value = node['right']['value']
            comparison_func = RuleParser.COMPARISONS[node['value']]
            
            return comparison_func(left_value, right_value)
        
        else:
            raise ValueError(f"Invalid node type: {node['type']}")
        