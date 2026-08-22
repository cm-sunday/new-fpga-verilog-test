"""
Fault types layer - fault models for injection.
"""

import random
import cocotb
from .primitives import force_bit, release_signal, wait_cycles, read_signal


class Fault:
    """Base class for all fault types."""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
    
    def log(self, message: str):
        """Log a message with fault context."""
        if hasattr(cocotb, 'log'):
            cocotb.log.info(f"[{self.name}] {message}")
        else:
            print(f"[{self.name}] {message}")


class SEUFault(Fault):
    """Single Event Upset - flips a bit for one cycle."""
    
    def __init__(self, signal, bit: int, at_cycle: int, duration: int = 1):
        super().__init__("SEU")
        self.signal = signal
        self.bit = bit
        self.at_cycle = at_cycle
        self.duration = duration
    
    async def run(self, dut):
        await wait_cycles(dut, self.at_cycle)
        old = await read_signal(self.signal)
        flipped = old ^ (1 << self.bit)
        self.log(f"Flipping bit {self.bit}: 0b{old:04b} -> 0b{flipped:04b}")
        self.signal.value = flipped
        await wait_cycles(dut, self.duration)


class StuckAtFault(Fault):
    """Stuck-at fault - holds a signal at a fixed value."""
    
    def __init__(self, signal, value: int, start: int, duration: int, bit: int = None):
        super().__init__("STUCK")
        self.signal = signal
        self.bit = bit
        self.value = value
        self.start = start
        self.duration = duration
    
    async def run(self, dut):
        await wait_cycles(dut, self.start)
        
        self.log(f"Stuck-at {self.value} for {self.duration} cycles")
        
        for _ in range(self.duration):
            if self.bit is not None:
                await force_bit(self.signal, self.bit, self.value)
            else:
                try:
                    self.signal._force(self.value)
                except AttributeError:
                    self.signal.value = self.value
            await wait_cycles(dut, 1)
        
        try:
            self.signal._release()
        except AttributeError:
            pass
        self.log("Released")


class BurstFault(Fault):
    """Flip random bits over consecutive cycles."""
    
    def __init__(self, signal, n_bits: int = 3, start: int = 0, 
                 duration: int = 10, seed: int = 0xC0FFEE, width: int = None):
        super().__init__("BURST")
        self.signal = signal
        self.n_bits = n_bits
        self.start = start
        self.duration = duration
        self.rng = random.Random(seed)
        
        if width is not None:
            self.width = width
        else:
            try:
                self.width = len(signal)
            except (TypeError, AttributeError):
                self.width = 4
    
    async def run(self, dut):
        await wait_cycles(dut, self.start)
        
        signal_path = self.signal._path if hasattr(self.signal, '_path') else str(self.signal)
        
        for cycle in range(self.duration):
            old = await read_signal(self.signal)
            new = old
            
            bits_flipped = []
            for _ in range(self.n_bits):
                bit = self.rng.randrange(self.width)
                new ^= (1 << bit)
                bits_flipped.append(bit)
            
            if new < (1 << self.width):
                self.signal.value = new
                self.log(f"cycle +{cycle:03d}: flip bits {bits_flipped} on {signal_path}")
                self.log(f"  0b{old:0{self.width}b} -> 0b{new:0{self.width}b}")
            else:
                self.log(f"cycle +{cycle:03d}: skipping (value exceeds width)")
            
            await wait_cycles(dut, 1)
        
        self.log(f"Burst complete after {self.duration} cycles")


class PatternFault(Fault):
    """Drive a specific sequence of values to a signal."""
    
    def __init__(self, signal, pattern: list, start: int = 0):
        super().__init__("PATTERN")
        self.signal = signal
        self.pattern = pattern
        self.start = start
    
    async def run(self, dut):
        await wait_cycles(dut, self.start)
        
        signal_path = self.signal._path if hasattr(self.signal, '_path') else str(self.signal)
        
        for i, (value, duration) in enumerate(self.pattern):
            try:
                self.signal.value = value
            except ValueError as e:
                self.log(f"pattern[{i}]: error setting value {value}: {e}")
            else:
                self.log(f"pattern[{i}]: value 0b{value:08b} for {duration} cycles on {signal_path}")
            await wait_cycles(dut, duration)
        
        self.log("Pattern complete")
