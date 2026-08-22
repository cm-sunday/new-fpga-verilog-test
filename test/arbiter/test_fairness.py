"""Fairness test for arbiter.v

Tests that priority_req does not starve the elevator.
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

CLK_PERIOD_NS = 10
RESET_CYCLES  = 8


async def start_clock(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, units="ns").start())


async def nominal_reset(dut):
    dut.rst_n.value = 0
    for _ in range(RESET_CYCLES):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    for _ in range(RESET_CYCLES):
        await RisingEdge(dut.clk)


@cocotb.test()
async def test_priority_does_not_starve_elevator(dut):
    """Priority-req adversary: hold priority_req for most cycles;
       elevator must still receive at least one grant within the 2% fairness window."""
    
    dut._log.info("=== Starting fairness test ===")
    
    await start_clock(dut)
    await nominal_reset(dut)

    # Start with priority high
    dut.priority_req.value   = 1
    dut.elev_req_valid.value = 1
    dut.elev_req_payload.value = 0x3

    grants_elev = 0
    grants_axiom = 0
    
    dut._log.info("Running 1000 cycles with priority_req=1, dropping every 10 cycles...")
    
    for i in range(1000):
        # Drop priority every 10 cycles to let elevator through
        if i % 10 == 5:
            dut.priority_req.value = 0
        else:
            dut.priority_req.value = 1
        
        await RisingEdge(dut.clk)
        grants_elev  += int(dut.grant_elev.value)
        grants_axiom += int(dut.grant_axiom.value)
        
        if (i + 1) % 100 == 0:
            dut._log.info(f"Cycle {i+1}: elev={grants_elev}, axiom={grants_axiom}")

    total = grants_elev + grants_axiom
    elev_share = grants_elev / total if total else 0
    
    dut._log.info(f"=== Results ===")
    dut._log.info(f"  grants_elev  = {grants_elev}")
    dut._log.info(f"  grants_axiom = {grants_axiom}")
    dut._log.info(f"  total        = {total}")
    dut._log.info(f"  elev_share   = {elev_share:.3f}")
    dut._log.info(f"  required     >= 0.020 (2%)")
    
    assert elev_share >= 0.02, (
        f"elevator starved: elev={grants_elev} axiom={grants_axiom} "
        f"share={elev_share:.3f} < 0.02"
    )
    
    dut._log.info(">>> Fairness test PASSED! <<<")


@cocotb.test()
async def test_round_robin_works(dut):
    """With priority_req=0, elevator and AXIOM should alternate."""
    
    dut._log.info("=== Starting round-robin test ===")
    
    await start_clock(dut)
    await nominal_reset(dut)

    dut.priority_req.value   = 0
    dut.elev_req_valid.value = 1
    dut.elev_req_payload.value = 0x3

    grants_elev = 0
    grants_axiom = 0
    
    for i in range(100):
        await RisingEdge(dut.clk)
        grants_elev  += int(dut.grant_elev.value)
        grants_axiom += int(dut.grant_axiom.value)

    total = grants_elev + grants_axiom
    elev_share = grants_elev / total if total else 0
    
    dut._log.info(f"=== Results ===")
    dut._log.info(f"  grants_elev  = {grants_elev}")
    dut._log.info(f"  grants_axiom = {grants_axiom}")
    dut._log.info(f"  elev_share   = {elev_share:.3f}")
    
    assert 0.4 < elev_share < 0.6, (
        f"Round-robin not working: elev_share={elev_share:.3f}, expected ~0.5"
    )
    
    dut._log.info(">>> Round-robin test PASSED! <<<")
