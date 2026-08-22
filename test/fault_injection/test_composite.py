"""
Composite fault injection test.
"""

import cocotb
from cocotb.clock import Clock

from harness import (
    BurstFault, StuckAtFault, PatternFault,
    wait_cycles, get_signal
)


@cocotb.test()
async def burst_plus_stuck(dut):
    """Test: Burst fault on state register + Stuck-at fault on input."""
    
    # Start clock
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    
    # Bring up to idle
    dut.rst_n.value = 0
    await wait_cycles(dut, 5)
    dut.rst_n.value = 1
    await wait_cycles(dut, 10)
    
    # Get state signal
    state_signal = get_signal(dut, "user_project.em.current_state")
    
    width = len(state_signal)
    cocotb.log.info(f"State signal width: {width} bits")
    cocotb.log.info("Starting composite fault injection...")
    
    # Fault 1: Burst on state register
    burst = BurstFault(
        signal=state_signal,
        n_bits=1,
        start=100,
        duration=3,
        seed=0xDEADBEEF,
        width=width
    )
    
    # Fault 2: Stuck-at-0 on ui_in bit 4
    stuck = StuckAtFault(
        signal=dut.ui_in,
        bit=4,
        value=0,
        start=120,
        duration=30
    )
    
    # Run faults concurrently
    burst_task = cocotb.start_soon(burst.run(dut))
    stuck_task = cocotb.start_soon(stuck.run(dut))
    
    await burst_task
    await stuck_task
    
    # Wait for recovery
    await wait_cycles(dut, 50)
    
    final_state = int(state_signal.value)
    cocotb.log.info(f"Final state: 0b{final_state:02b}")
    
    assert final_state >= 0 and final_state <= 3, \
        f"State out of range: {final_state}"
    
    cocotb.log.info("PASS: burst_plus_stuck")


@cocotb.test()
async def pattern_plus_burst(dut):
    """Test: Pattern fault on input + Burst fault on state."""
    
    # Start clock
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    
    # Bring up to idle
    dut.rst_n.value = 0
    await wait_cycles(dut, 5)
    dut.rst_n.value = 1
    await wait_cycles(dut, 10)
    
    # Get state signal
    state_signal = get_signal(dut, "user_project.em.current_state")
    width = len(state_signal)
    
    cocotb.log.info("Starting pattern + burst test...")
    
    # Fault 1: Pattern fault on input
    pattern = PatternFault(
        signal=dut.ui_in,
        pattern=[
            (0b00000100, 10),   # Floor 2
            (0b00000000, 5),    # No request
            (0b11111111, 10),   # Invalid
            (0b00000000, 5),    # No request
        ],
        start=50
    )
    
    # Fault 2: Burst on state
    burst = BurstFault(
        signal=state_signal,
        n_bits=1,
        start=80,
        duration=1,
        seed=0x12345678,
        width=width
    )
    
    # Run faults
    pattern_task = cocotb.start_soon(pattern.run(dut))
    burst_task = cocotb.start_soon(burst.run(dut))
    
    await pattern_task
    await burst_task
    
    # Wait for recovery
    await wait_cycles(dut, 30)
    
    final_state = int(state_signal.value)
    cocotb.log.info(f"Final state: 0b{final_state:02b}")
    
    assert final_state >= 0 and final_state <= 3, \
        f"State out of range: {final_state}"
    
    cocotb.log.info("PASS: pattern_plus_burst")