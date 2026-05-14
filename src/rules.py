#!/usr/bin/env python3
"""
rules.py  --  thin wrappers around C2-symmetric rule generation in evolution.py
"""

import random as _random

from evolution import (
    generate_random_c2_rule as _generate_random_c2_rule,
    _try_build_c2_rule,
    _rotate_c2,
)

_rng = _random.Random()


def random_c2_symmetric_rule(rng: _random.Random | None = None) -> dict:
    """Return a random C2-symmetric rule dict."""
    if rng is None:
        rng = _rng
    return _generate_random_c2_rule(rng)
