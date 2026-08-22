# test/clock_gate/test_top_smoke.py
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles

@cocotb.test()
async def test_top_smoke(dut):
    """Basic smoke test for top module"""
    
    # Start clock
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    dut.ena.value = 1
    await Timer(20, unit="ns")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    # Set all inputs to known values
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    
    dut._log.info("=== Top Module Smoke Test ===")
    
    # Test 1: Check outputs after reset
    await ClockCycles(dut.clk, 2)
    dut._log.info(f"uo_out: {dut.uo_out.value}")
    dut._log.info(f"uio_out: {dut.uio_out.value}")
    
    # Test 2: Send a request
    dut._log.info("Sending request to floor 1...")
    dut.ui_in.value = 0b00000011  # Bits 0 and 1 set
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 0b00000010  # Clear strobe
    await ClockCycles(dut.clk, 10)
    
    # Test 3: Check outputs after request
    dut._log.info(f"uo_out after request: {dut.uo_out.value}")
    dut._log.info(f"uio_out after request: {dut.uio_out.value}")
    
    # Test 4: Send another request to floor 3
    dut._log.info("Sending request to floor 3...")
    dut.ui_in.value = 0b00001011  # Bits 0,1,3 set (floor 3)
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 0b00001010  # Clear strobe
    await ClockCycles(dut.clk, 10)
    
    # Test 5: Check clock gate
    if hasattr(dut, 'u_axiom_gate'):
        dut._log.info(f"Clock gate enable: {dut.u_axiom_gate.enable.value}")
        dut._log.info(f"Gated clock: {dut.u_axiom_gate.gclk.value}")
        dut._log.info(f"Clock gate active: {dut.clock_gate_active.value}")
    
    dut._log.info(" Smoke test passed!")
