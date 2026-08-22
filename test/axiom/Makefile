	TOPLEVEL_LANG = verilog
SIM           ?= icarus
TOPLEVEL      = axiom_shim
MODULE        = test_shim

VERILOG_SOURCES = \
$(PWD)/../../src/axiom_blackbox.v \
$(PWD)/../../src/axiom_blackbox_sim.v \
$(PWD)/../../src/axiom_shim.v \
$(PWD)/../../src/clock_gate.v

COMPILE_ARGS += -DSIM_AXIOM

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: shim test-all

shim:
	$(MAKE) sim MODULE=test_shim

test-all: shim
