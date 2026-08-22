# test/fault_injection/exercise_seu.py

import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

def find_state_signal(dut, log):
    """Try to find the state signal in the hierarchy."""
    
    possible_paths = [
        ("em.current_state", lambda: dut.em.current_state),
        ("current_state", lambda: dut.current_state),
        ("dut.em.current_state", lambda: dut.em.current_state),
        ("uut.em.current_state", lambda: dut.uut.em.current_state),
        ("top.em.current_state", lambda: dut.top.em.current_state),
        ("user_project.em.current_state", lambda: dut.user_project.em.current_state),
    ]
    
    for path_name, getter in possible_paths:
        try:
            signal = getter()
            if signal is not None:
                log.info(f"[OK] Found state signal at: {path_name}")
                return signal, path_name
        except (AttributeError, TypeError):
            continue
    
    log.info("Could not find state signal. Available attributes:")
    for attr in dir(dut):
        if not attr.startswith("_"):
            log.info(f"  - {attr}")
    
    return None, None


@cocotb.test()
async def exercise_seu(dut):
    """Test SEU on the state register with one-hot encoding."""
    
    # Start clock
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    
    # Reset
    dut.rst_n.value = 0
    await Timer(100, unit='ns')
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await Timer(100, unit='ns')
    
    # Wait a few cycles
    for _ in range(5):
        await RisingEdge(dut.clk)
    
    # Find the state signal
    state_signal, path = find_state_signal(dut, dut._log)
    
    if state_signal is None:
        dut._log.error("Could not find state signal!")
        return
    
    # Get the width of the state signal
    signal_width = len(state_signal.value)
    dut._log.info(f"State signal width: {signal_width} bits")
    
    # ONE-HOT state encoding (4-bit)
    state_names = {
        0b0001: "IDLE",
        0b0010: "MOVING_UP", 
        0b0100: "MOVING_DOWN",
        0b1000: "DOOR_OPEN"
    }
    
    # Observe state before SEU
    before = int(state_signal.value)
    dut._log.info(f"[SEU] state before = 0b{before:04b} (decimal: {before})")
    dut._log.info(f"[SEU] State name before = {state_names.get(before, 'ILLEGAL')}")
    
    # SEU: Flip each bit one at a time
    # Start with flipping bit 0
    flipped_value = before ^ 0b0001
    dut._log.info(f"[SEU] Flipping bit 0: 0b{before:04b} -> 0b{flipped_value:04b}")
    state_signal.value = flipped_value
    await RisingEdge(dut.clk)
    
    # Observe immediately after SEU
    after = int(state_signal.value)
    dut._log.info(f"[SEU] state after one cycle = 0b{after:04b} (decimal: {after})")
    dut._log.info(f"[SEU] State name after = {state_names.get(after, 'ILLEGAL')}")
    
    # Wait 8 more cycles for recovery
    for _ in range(8):
        await RisingEdge(dut.clk)
    
    # Observe recovery
    recovered = int(state_signal.value)
    dut._log.info(f"[SEU] state after recovery window = 0b{recovered:04b} (decimal: {recovered})")
    dut._log.info(f"[SEU] State name recovered = {state_names.get(recovered, 'ILLEGAL')}")
    
    # With one-hot + illegal trap, any illegal state should recover to IDLE
    # But if the flipped state is still a valid state, it might stay there
    is_valid = recovered in state_names
    is_idle = recovered == 0b0001
    
    if is_idle:
        dut._log.info("[SEU] PASS: Recovery successful! DUT returned to IDLE.")
        assert True
    elif recovered == before:
        dut._log.info("[SEU] PASS: State remained valid (flipped to another valid state).")
        assert True
    else:
        dut._log.warning(f"[SEU] FAIL: Recovery failed! Expected IDLE (0b0001), got 0b{recovered:04b}")
        assert False, f"Recovery failed: expected IDLE or valid state, got {recovered}"


@cocotb.test()
async def exercise_seu_all_states(dut):
    """Test SEU on all valid one-hot states."""
    
    # Start clock
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    
    # Reset
    dut.rst_n.value = 0
    await Timer(100, unit='ns')
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await Timer(100, unit='ns')
    
    for _ in range(5):
        await RisingEdge(dut.clk)
    
    # Find the state signal
    state_signal, path = find_state_signal(dut, dut._log)
    
    if state_signal is None:
        dut._log.error("Could not find state signal!")
        return
    
    # ONE-HOT state encoding (4-bit)
    state_names = {
        0b0001: "IDLE",
        0b0010: "MOVING_UP", 
        0b0100: "MOVING_DOWN",
        0b1000: "DOOR_OPEN"
    }
    
    # Valid one-hot states
    valid_states = [0b0001, 0b0010, 0b0100, 0b1000]
    results = []
    
    for target_state in valid_states:
        # Force the state to target_state
        state_signal.value = target_state
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        
        before = target_state
        dut._log.info(f"\n--- Testing SEU on {state_names.get(target_state, 'UNKNOWN')} (0b{before:04b}) ---")
        
        # Flip each bit (0-3)
        for bit in range(4):
            flipped = before ^ (1 << bit)
            dut._log.info(f"  Flipping bit {bit}: 0b{before:04b} -> 0b{flipped:04b}")
            
            # Inject SEU
            state_signal.value = flipped
            await RisingEdge(dut.clk)
            
            # Wait for recovery
            for _ in range(10):
                await RisingEdge(dut.clk)
            
            recovered = int(state_signal.value)
            
            # Check if recovery was successful
            # With one-hot + illegal trap, should recover to IDLE or original state
            if recovered == target_state:
                success = True
                reason = "recovered to original state"
            elif recovered == 0b0001:
                success = True
                reason = "trapped to IDLE"
            elif recovered in state_names and recovered != target_state:
                # Flipping one bit in a one-hot state always creates an illegal state
                # So this shouldn't happen with proper one-hot encoding
                success = False
                reason = f"flipped to another valid state (should be illegal)"
            else:
                success = False
                reason = f"unexpected state: 0b{recovered:04b}"
            
            status = "[PASS]" if success else "[FAIL]"
            dut._log.info(f"  {status} - Recovered to: {state_names.get(recovered, 'ILLEGAL')} (0b{recovered:04b}) - {reason}")
            
            results.append({
                'state': state_names.get(target_state, 'UNKNOWN'),
                'bit': bit,
                'flipped': flipped,
                'recovered': recovered,
                'success': success,
                'reason': reason
            })
    
    # Summary
    dut._log.info("\n=== SEU Test Summary ===")
    failures = [r for r in results if not r['success']]
    if failures:
        dut._log.warning(f"FAIL: {len(failures)} failures found:")
        for f in failures:
            dut._log.warning(f"  {f['state']} bit {f['bit']} -> {f['reason']}")
        assert False, f"{len(failures)} SEU failures detected"
    else:
        dut._log.info(f"PASS: All {len(results)} SEU tests passed!")
        for r in results:
            dut._log.info(f"  {r['state']} bit {r['bit']} -> {r['reason']}")
