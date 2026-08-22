"""
Harness for fault injection testing.
"""

from .primitives import (
    force_bit, force_signal, deposit_signal, release_signal,
    read_signal, wait_cycles, wait_ns, get_signal
)

from .faults import (
    Fault, SEUFault, StuckAtFault, BurstFault, PatternFault
)

__all__ = [
    'force_bit', 'force_signal', 'deposit_signal', 'release_signal',
    'read_signal', 'wait_cycles', 'wait_ns', 'get_signal',
    'Fault', 'SEUFault', 'StuckAtFault', 'BurstFault', 'PatternFault'
]
