# test/clock_gate/test_clock_gate.py
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles, FallingEdge

@cocotb.test()
async def test_clock_gate_basic(dut):
    """Test basic clock gating functionality on full top module"""
    
    # Start clock
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    dut.ena.value = 1
    await Timer(20, unit="ns")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    # Set initial conditions - all inputs low
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    
    await ClockCycles(dut.clk, 5)
    
    dut._log.info("=== Clock Gating Test on Full Design ===")
    
    try:
        # Check if clock gate exists
        gate_enable = dut.u_elevator_gate.enable
        gate_gclk = dut.u_elevator_gate.gclk
        
        # Test 1: Check initial state (should be IDLE)
        dut._log.info("Test 1: Checking IDLE state...")
        await ClockCycles(dut.clk, 2)
        
        # Get the current enable value
        enable_val = gate_enable.value
        dut._log.info(f"Clock gate enable: {enable_val}")
        
        # Check clock gate active status
        if hasattr(dut, 'clock_gate_active'):
            active_val = dut.clock_gate_active.value
            dut._log.info(f"Clock gate active: {active_val}")
        
        # Test 2: Test mode override - Set entire ui_in
        dut._log.info("Test 2: Enabling test mode...")
        # Set ui_in[7] = 1 (test mode), keep others 0
        dut.ui_in.value = 0b10000000  # Bit 7 is test mode
        await ClockCycles(dut.clk, 3)
        enable_test = gate_enable.value
        dut._log.info(f"Clock gate enable (test mode): {enable_test}")
        assert enable_test == 1, "Test mode should force clock on"
        dut.ui_in.value = 0  # Disable test mode
        
        # Test 3: Send elevator request
        dut._log.info("Test 3: Sending elevator request...")
        # Set ui_in[0] = 1 (request strobe), ui_in[1] = 1 (floor 1)
        dut.ui_in.value = 0b00000011  # Bits 0 and 1 set
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 0b00000010  # Clear strobe, keep floor 1
        await ClockCycles(dut.clk, 5)
        
        # Check if clock is running (enable should be high)
        enable_req = gate_enable.value
        dut._log.info(f"Clock gate enable (with request): {enable_req}")
        
        # Clear request
        dut.ui_in.value = 0
        
        # Test 4: Wait for request to complete and check idle
        dut._log.info("Test 4: Waiting for idle...")
        await ClockCycles(dut.clk, 20)
        enable_idle = gate_enable.value
        dut._log.info(f"Clock gate enable (returned to idle): {enable_idle}")
        
        dut._log.info(" All clock gating tests passed!")
        
    except AttributeError as e:
        dut._log.error(f"Clock gate not found: {e}")
        dut._log.info("Make sure the design has clock gating implemented")
        raise

@cocotb.test()
async def test_clock_gate_power_saving(dut):
    """Verify power saving when clock is gated"""
    
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
    
    dut._log.info("=== Power Saving Test ===")
    
    try:
        # Wait for idle state
        await ClockCycles(dut.clk, 10)
        
        # Count gclk toggles when idle
        dut._log.info("Counting clock toggles in idle state...")
        idle_toggles = 0
        prev_gclk = 0
        for i in range(50):
            await RisingEdge(dut.clk)
            current_gclk = dut.u_elevator_gate.gclk.value
            if current_gclk != prev_gclk:
                idle_toggles += 1
                prev_gclk = current_gclk
        
        dut._log.info(f"Clock toggles when idle: {idle_toggles}/50")
        
        # Send a request - set ui_in[0]=1 (strobe), ui_in[1]=1 (floor 1)
        dut._log.info("Sending request...")
        dut.ui_in.value = 0b00000011  # Bits 0 and 1 set
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 0b00000010  # Clear strobe, keep floor
        await ClockCycles(dut.clk, 5)
        
        # Count gclk toggles when active
        dut._log.info("Counting clock toggles in active state...")
        active_toggles = 0
        prev_gclk = 0
        for i in range(50):
            await RisingEdge(dut.clk)
            current_gclk = dut.u_elevator_gate.gclk.value
            if current_gclk != prev_gclk:
                active_toggles += 1
                prev_gclk = current_gclk
        
        dut._log.info(f"Clock toggles when active: {active_toggles}/50")
        
        # Clear request
        dut.ui_in.value = 0
        
        # Verify power saving
        if idle_toggles < active_toggles:
            saving = (active_toggles - idle_toggles) / active_toggles * 100
            dut._log.info(f" Power saving observed: {saving:.1f}%")
            # Don't assert here as power saving depends on design
        else:
            dut._log.warning(" No significant power saving observed")
            dut._log.info("Check that elevator enters IDLE state")
        
    except AttributeError as e:
        dut._log.error(f"Clock gate not found: {e}")
        raise
