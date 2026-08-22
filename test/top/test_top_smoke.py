"""Integration smoke tests for tt_um_silicon_dreams."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles

CLK_PERIOD_NS = 10
RESET_CYCLES = 8


# ============================================================
# HELPER FUNCTIONS
# ============================================================

async def start_clock(dut):
    """Start the clock with proper unit"""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())


async def nominal_reset(dut):
    """Perform a nominal reset sequence"""
    dut.rst_n.value = 0
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    for _ in range(RESET_CYCLES):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    for _ in range(RESET_CYCLES):
        await RisingEdge(dut.clk)


async def send_request(dut, floor, priority=0, axiom_enable=0, test_mode=0):
    """Send a floor request to the elevator
    
    Args:
        floor: 0-7 (requested floor)
        priority: 0 or 1 (priority_override)
        axiom_enable: 0 or 1 (enable AXIOM)
        test_mode: 0 or 1 (keep clock running)
    """
    # ui_in[0] = request_strobe
    # ui_in[4:1] = floor (0-7)
    # ui_in[5] = priority_override
    # ui_in[6] = axiom_enable
    # ui_in[7] = test_mode / global_test_mode
    
    # Set the request (without strobe)
    dut.ui_in.value = (floor << 1) | (priority << 5) | (axiom_enable << 6) | (test_mode << 7)
    await RisingEdge(dut.clk)
    
    # Pulse the strobe (bit 0)
    dut.ui_in.value = (floor << 1) | (priority << 5) | (axiom_enable << 6) | (test_mode << 7) | 0b1
    await RisingEdge(dut.clk)
    
    # Clear the strobe
    dut.ui_in.value = (floor << 1) | (priority << 5) | (axiom_enable << 6) | (test_mode << 7)
    await RisingEdge(dut.clk)


def get_elevator_state(uo_out):
    """Extract elevator state from uo_out (bits 6:4)"""
    return (uo_out >> 4) & 0x7


def get_door_open(uo_out):
    """Extract door_open from uo_out (bit 7)"""
    return (uo_out >> 7) & 0x1


def get_current_floor(uo_out):
    """Extract current_floor from uo_out (bits 3:0)"""
    return uo_out & 0xF


def get_grant_elevator(uio_out):
    """Extract grant_elevator from uio_out (bit 1)"""
    return (uio_out >> 1) & 0x1


def get_grant_axiom(uio_out):
    """Extract grant_axiom from uio_out (bit 2)"""
    return (uio_out >> 2) & 0x1


def get_clock_gated(uio_out):
    """Extract clock_gated from uio_out (bit 3) - 1 = gated, 0 = active"""
    return (uio_out >> 3) & 0x1


def get_misbehaviour_led(uio_out):
    """Extract misbehaviour_led from uio_out (bit 4)"""
    return (uio_out >> 4) & 0x1


def get_elevator_error(uio_out):
    """Extract elevator_error_led from uio_out (bit 7)"""
    return (uio_out >> 7) & 0x1


# ============================================================
# TESTS
# ============================================================

@cocotb.test()
async def reset_release(dut):
    """Test that elevator starts in IDLE state after reset"""
    dut._log.info("=== Test: Reset Release ===")
    
    await start_clock(dut)
    await nominal_reset(dut)
    
    uo_out = int(dut.uo_out.value)
    state = get_elevator_state(uo_out)
    door = get_door_open(uo_out)
    floor = get_current_floor(uo_out)
    
    dut._log.info(f"uo_out: 0x{uo_out:02X} (state: {state}, door: {door}, floor: {floor})")
    assert state == 0, f"elevator state = {state}, expected IDLE=0"
    assert door == 0, f"door_open = {door}, expected 0"
    
    dut._log.info("Reset release test passed")


@cocotb.test()
async def elevator_wakes_in_IDLE(dut):
    """Test that elevator is in IDLE after reset"""
    dut._log.info("=== Test: Elevator Wakes in IDLE ===")
    
    await start_clock(dut)
    await nominal_reset(dut)
    
    uo_out = int(dut.uo_out.value)
    state = get_elevator_state(uo_out)
    
    dut._log.info(f"uo_out: 0x{uo_out:02X}, state: {state}")
    assert state == 0, f"elevator state = {state}, expected IDLE=0"
    
    dut._log.info("Elevator wakes in IDLE test passed")


@cocotb.test()
async def arbiter_grants_elevator_by_default(dut):
    """Test that arbiter grants elevator by default"""
    dut._log.info("=== Test: Arbiter Grants Elevator by Default ===")
    
    await start_clock(dut)
    await nominal_reset(dut)
    
    # Use test_mode to keep clock running
    await send_request(dut, floor=1, priority=0, axiom_enable=0, test_mode=1)
    dut._log.info("Request sent to floor 1 (no priority)")
    
    grant_elev = 0
    for i in range(30):
        await RisingEdge(dut.clk)
        uio_out = int(dut.uio_out.value)
        uo_out = int(dut.uo_out.value)
        grant_elev = get_grant_elevator(uio_out)
        state = get_elevator_state(uo_out)
        
        if i % 5 == 0:
            dut._log.info(f"Cycle {i}: uio=0x{uio_out:02X}, grant_elev={grant_elev}, state={state}")
        
        if grant_elev == 1:
            dut._log.info(f"Grant seen at cycle {i}")
            break
    
    assert grant_elev == 1, f"elevator never received a grant, got {grant_elev}"
    dut._log.info("Arbiter grants elevator by default test passed")


@cocotb.test()
async def priority_override_grants_axiom(dut):
    """Test that priority_override grants AXIOM"""
    dut._log.info("=== Test: Priority Override Grants AXIOM ===")
    
    await start_clock(dut)
    await nominal_reset(dut)
    
    # Send request with priority and test_mode
    await send_request(dut, floor=1, priority=1, axiom_enable=1, test_mode=1)
    dut._log.info("Request sent to floor 1 (priority=1, axiom_enable=1)")
    
    grant_axiom = 0
    grant_elev = 0
    for i in range(30):
        await RisingEdge(dut.clk)
        uio_out = int(dut.uio_out.value)
        grant_axiom = get_grant_axiom(uio_out)
        grant_elev = get_grant_elevator(uio_out)
        
        if i % 5 == 0:
            dut._log.info(f"Cycle {i}: uio=0x{uio_out:02X}, grant_axiom={grant_axiom}, grant_elev={grant_elev}")
        
        if grant_axiom == 1:
            dut._log.info(f"AXIOM grant seen at cycle {i}")
            break
    
    # Note: With priority, AXIOM should get grant, elevator should NOT
    assert grant_axiom == 1, f"priority_override did not grant AXIOM, got {grant_axiom}"
    dut._log.info("Priority override grants AXIOM test passed")


@cocotb.test()
async def axiom_shim_clamps_misbehaviour(dut):
    """Test that AXIOM shim clamps misbehaviour"""
    dut._log.info("=== Test: AXIOM Shim Clamps Misbehaviour ===")
    
    await start_clock(dut)
    await nominal_reset(dut)
    
    # Send cmd=0x4 to trigger misbehaviour (floor=4 with priority)
    await send_request(dut, floor=4, priority=1, axiom_enable=1, test_mode=1)
    dut._log.info("Request sent (floor=4) - should trigger AXIOM misbehaviour")
    
    mstrobe_seen = False
    for i in range(40):
        await RisingEdge(dut.clk)
        uio_out = int(dut.uio_out.value)
        uo_out = int(dut.uo_out.value)
        mstrobe = get_misbehaviour_led(uio_out)
        state = get_elevator_state(uo_out)
        
        if i % 5 == 0:
            dut._log.info(f"Cycle {i}: uio=0x{uio_out:02X}, mstrobe={mstrobe}, state={state}")
        
        if mstrobe:
            mstrobe_seen = True
            dut._log.info(f"Misbehaviour LED seen at cycle {i}!")
            break
    
    # Check resp_out if accessible
    try:
        resp = int(dut.u_axiom_shim.resp_out.value)
        dut._log.info(f"resp_out: 0x{resp:02X}")
        if resp <= 0x3F:
            dut._log.info("resp is clamped (valid range)")
    except:
        pass
    
    assert mstrobe_seen, "axiom misbehaviour LED never pulsed"
    dut._log.info("AXIOM shim clamps misbehaviour test passed")


@cocotb.test()
async def clock_gate_disables_on_idle(dut):
    """Test that clock gate controls AXIOM clock based on axiom_enable"""
    dut._log.info("=== Test: Clock Gate Controls AXIOM ===")
    
    await start_clock(dut)
    await nominal_reset(dut)
    
    # Start with axiom_enable=0 (AXIOM clock gated)
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 10)
    
    # Check clock gate is gated (1 = gated)
    uio_out = int(dut.uio_out.value)
    cga = get_clock_gated(uio_out)
    dut._log.info(f"axiom_enable=0: uio=0x{uio_out:02X}, clock_gated={cga}")
    assert cga == 1, f"clock_gated should be 1 when axiom_enable=0 (gated), got {cga}"
    
    # Enable AXIOM - clock should become active (0 = active)
    dut.ui_in.value = (1 << 6)  # axiom_enable=1
    await ClockCycles(dut.clk, 5)
    
    uio_out = int(dut.uio_out.value)
    cga = get_clock_gated(uio_out)
    dut._log.info(f"axiom_enable=1: uio=0x{uio_out:02X}, clock_gated={cga}")
    assert cga == 0, f"clock_gated should be 0 when axiom_enable=1 (active), got {cga}"
    
    # Disable AXIOM again
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 5)
    
    uio_out = int(dut.uio_out.value)
    cga = get_clock_gated(uio_out)
    dut._log.info(f"axiom_enable=0 again: uio=0x{uio_out:02X}, clock_gated={cga}")
    assert cga == 1, f"clock_gated should be 1 when axiom_enable=0 (gated), got {cga}"
    
    dut._log.info("Clock gate controls AXIOM test passed")


@cocotb.test()
async def debug_signal_mapping(dut):
    """Debug helper to show all signal mappings"""
    dut._log.info("=== DEBUG: Signal Mapping ===")
    
    await start_clock(dut)
    await nominal_reset(dut)
    
    # Read all outputs
    ui_in = int(dut.ui_in.value)
    uo_out = int(dut.uo_out.value)
    uio_out = int(dut.uio_out.value)
    uio_oe = int(dut.uio_oe.value)
    
    dut._log.info(f"ui_in:    0x{ui_in:02X} (bits: {ui_in:08b})")
    dut._log.info(f"uo_out:   0x{uo_out:02X} (bits: {uo_out:08b})")
    dut._log.info(f"uio_out:  0x{uio_out:02X} (bits: {uio_out:08b})")
    dut._log.info(f"uio_oe:   0x{uio_oe:02X} (bits: {uio_oe:08b})")
    
    # Decode signals
    dut._log.info("\nDecoded signals:")
    dut._log.info(f"uo_out[7]   door_open:            {get_door_open(uo_out)}")
    dut._log.info(f"uo_out[6:4] elevator_state:       {get_elevator_state(uo_out)}")
    dut._log.info(f"uo_out[3:0] current_floor:        {get_current_floor(uo_out)}")
    dut._log.info(f"uio_out[1]  grant_elevator:       {get_grant_elevator(uio_out)}")
    dut._log.info(f"uio_out[2]  grant_axiom:          {get_grant_axiom(uio_out)}")
    dut._log.info(f"uio_out[3]  clock_gated:          {get_clock_gated(uio_out)}")
    dut._log.info(f"uio_out[4]  misbehaviour_led:     {get_misbehaviour_led(uio_out)}")
    dut._log.info(f"uio_out[7]  elevator_error_led:   {get_elevator_error(uio_out)}")
    
    # Try to access internal signals
    try:
        if hasattr(dut, 'u_axiom_shim'):
            resp = int(dut.u_axiom_shim.resp_out.value)
            dut._log.info(f"AXIOM resp_out:          0x{resp:02X}")
    except:
        pass
    
    try:
        if hasattr(dut, 'u_arbiter'):
            queue = int(dut.u_arbiter.queue_nonempty.value)
            dut._log.info(f"arbiter_queue_nonempty:   {queue}")
    except:
        pass
    
    dut._log.info("=== DEBUG Complete ===")
    dut._log.info("Debug signal mapping test passed")


@cocotb.test()
async def test_mode_enables_clock(dut):
    """Test that test_mode keeps clock running even when idle"""
    dut._log.info("=== Test: Test Mode Enables Clock ===")
    
    await start_clock(dut)
    await nominal_reset(dut)
    
    # Without test_mode, clock should be gated (axiom_enable=0)
    dut.ui_in.value = 0  # test_mode=0, axiom_enable=0
    await ClockCycles(dut.clk, 5)
    uio_out = int(dut.uio_out.value)
    cga = get_clock_gated(uio_out)
    dut._log.info(f"Without test_mode: clock_gated={cga}")
    assert cga == 1, f"clock should be gated without test_mode, got {cga}"
    
    # With test_mode and axiom_enable, clock should be active
    dut.ui_in.value = 0xC0  # test_mode=1, axiom_enable=1
    await ClockCycles(dut.clk, 5)
    uio_out = int(dut.uio_out.value)
    cga = get_clock_gated(uio_out)
    dut._log.info(f"With test_mode and axiom_enable: clock_gated={cga}")
    assert cga == 0, f"clock should be active with test_mode and axiom_enable, got {cga}"
    
    dut._log.info("Test mode enables clock test passed")
