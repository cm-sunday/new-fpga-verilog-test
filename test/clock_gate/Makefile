# test/Makefile
TOPLEVEL_LANG = verilog
SIM           ?= icarus
TOPLEVEL      = tt_um_silicon_dreams
MODULE        = test_top_smoke

VERILOG_SOURCES = \
$(PWD)/../../src/reset_synchroniser.v \
$(PWD)/../../src/elevator.v \
$(PWD)/../../src/elevator_req_port.v \
$(PWD)/../../src/arbiter.v \
$(PWD)/../../src/clock_gate.v \
$(PWD)/../../src/axiom_shim.v \
$(PWD)/../../src/top.v \
$(PWD)/../../src/axiom_blackbox_sim.v

# Add SIM_AXIOM for simulation
COMPILE_ARGS += -DSIM_AXIOM

# Add include paths if needed
COMPILE_ARGS += -I$(PWD)/../../src

include $(shell cocotb-config --makefiles)/Makefile.sim

# Default target
.PHONY: all
all: smoke test-clock-gate

.PHONY: smoke
smoke:
	$(MAKE) sim MODULE=test_top_smoke

.PHONY: test-clock-gate
test-clock-gate:
	$(MAKE) sim MODULE=test_clock_gate

.PHONY: test-clock-gate-stuck
test-clock-gate-stuck:
	$(MAKE) sim MODULE=test_clock_gate_stuck

.PHONY: test-all
test-all: smoke test-clock-gate test-clock-gate-stuck

.PHONY: wipe
wipe:
	rm -rf sim_build/
	rm -f results.xml
	rm -f *.vcd
	rm -f *.log
