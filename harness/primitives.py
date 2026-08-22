"""
Primitives layer - low-level signal operations.
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer

try:
    from cocotb.handle import ModifiableObject
except ImportError:
    from cocotb.handle import SimHandleBase as ModifiableObject


async def force_bit(signal, bit: int, value: int):
    """Force a specific bit of a signal to 0 or 1."""
    try:
        old = int(signal.value)
    except (ValueError, TypeError):
        old = 0
    
    if value:
        new_val = old | (1 << bit)
    else:
        new_val = old & ~(1 << bit)
    
    try:
        signal._force(new_val)
    except AttributeError:
        signal.value = new_val


async def force_signal(signal, value, duration=None):
    """Force a signal to a value, optionally for a duration."""
    try:
        signal._force(value)
    except AttributeError:
        signal.value = value
    
    if duration is not None:
        for _ in range(duration):
            await RisingEdge(signal)
        try:
            signal._release()
        except AttributeError:
            pass


async def deposit_signal(signal, value):
    """Deposit a value (one-shot write)."""
    signal.value = value


async def release_signal(signal):
    """Release a forced signal."""
    try:
        signal._release()
    except AttributeError:
        pass


async def read_signal(signal):
    """Read a signal value safely."""
    try:
        return int(signal.value)
    except (ValueError, TypeError):
        return 0


async def wait_cycles(dut, n: int):
    """Wait for n clock cycles."""
    for _ in range(n):
        await RisingEdge(dut.clk)


async def wait_ns(ns: int):
    """Wait for n nanoseconds."""
    await Timer(ns, units='ns')


def get_signal(dut, path: str):
    """Get a signal by dotted path."""
    parts = path.split('.')
    current = dut
    for part in parts:
        current = getattr(current, part)
    return current
