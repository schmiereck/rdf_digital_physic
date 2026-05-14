#!/usr/bin/env python3
"""
rule.py — Thin wrapper around a cellular automaton rule dict.
"""


class Rule:
    """Wraps an integer→integer rule mapping for the hexagonal CA."""

    def __init__(self, rule_dict: dict):
        self.rule_dict = {int(k): int(v) for k, v in rule_dict.items()}
