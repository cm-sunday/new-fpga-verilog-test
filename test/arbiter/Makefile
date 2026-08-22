TOPLEVEL_LANG = verilog
SIM           ?= icarus
TOPLEVEL      = arbiter
MODULE        = test_fairness

VERILOG_SOURCES = \
$(PWD)/../../src/arbiter.v

COMPILE_ARGS += -Wall -g2012

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: fairness
fairness:
	$(MAKE) sim MODULE=test_fairness
