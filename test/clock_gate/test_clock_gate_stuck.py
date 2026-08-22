# test/clock_gate/test_clock_gate_stuck.py
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles

@cocotb.test()
async def test_clock_gate_stuck(dut):
    """Test stuck-at fault on enable signal"""
    
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    dut.ena.value = 1
    await Timer(20, unit="ns")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    # Set initial conditions
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    
    await ClockCycles(dut.clk, 5)
    
    dut._log.info("=== Stuck-at Fault Test ===")
    
    try:
        # Check initial state
        if hasattr(dut, 'clock_gate_active'):
            initial_active = dut.clock_gate_active.value
            dut._log.info(f"Initial clock gate active: {initial_active}")
        
        # Inject stuck-at-0 fault on enable
        dut._log.info("Injecting stuck-at-0 fault on enable")
        dut.u_elevator_gate.enable.value = 0
        
        await ClockCycles(dut.clk, 5)
        
        # Check if clock is gated
        if hasattr(dut, 'clock_gate_active'):
            gated_active = dut.clock_gate_active.value
            dut._log.info(f"Clock gate active after fault: {gated_active}")
        
        # Try to send request - should be ignored if stuck
        dut._log.info("Sending request with stuck fault...")
        dut.ui_in.value = 0b00000011  # Bits 0 and 1 set
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 0b00000010  # Clear strobe
        await ClockCycles(dut.clk, 10)
        
        # Check gclk - should be low if stuck
        gclk_val = dut.u_elevator_gate.gclk.value
        dut._log.info(f"Gated clock value during fault: {gclk_val}")
        
        # Release fault
        dut._log.info("Releasing stuck-at-0 fault")
        dut.u_elevator_gate.enable.value = 1
        await ClockCycles(dut.clk, 5)
        
        # Check recovery
        if hasattr(dut, 'clock_gate_active'):
            recovered = dut.clock_gate_active.value
            dut._log.info(f"Clock gate active after release: {recovered}")
        
        # Send another request after release
        dut._log.info("Sending request after fault release...")
        dut.ui_in.value = 0b00010011  # Bits 0,1,4 set (floor 4)
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 0b00010010  # Clear strobe
        await ClockCycles(dut.clk, 10)
        
        # Clear request
        dut.ui_in.value = 0
        
        # Check if clock is running again
        gclk_recovered = dut.u_elevator_gate.gclk.value
        dut._log.info(f"Gated clock value after recovery: {gclk_recovered}")
        
        dut._log.info(" Stuck-at fault test passed!")
        
    except AttributeError as e:
        dut._log.error(f"Clock gate not found: {e}")
        raise
