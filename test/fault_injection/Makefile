# Silicon Dreams Module 2 - Simplified Makefile for Windows

SIM ?= icarus
TOPLEVEL_LANG ?= verilog
TOPLEVEL := tb

# Verilog sources
VERILOG_SOURCES := ../tb.v ../../src/elevator.v

# Include cocotb makefile
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: smoke fault fault_cocotb fault_area clean

smoke:
	cd .. && $(MAKE) MODULE=test

fault: fault_cocotb fault_area
	@echo ""
	@echo "==== Fault matrix complete ===="
	@type fault_matrix_results.json 2>nul || echo No results file

fault_cocotb:
	# Set PYTHONPATH and run each test
	set PYTHONPATH=$(shell cd .. && pwd) && $(MAKE) MODULE=fault_injection.floor_b2_reset
	set PYTHONPATH=$(shell cd .. && pwd) && $(MAKE) MODULE=fault_injection.floor_5_seu
	set PYTHONPATH=$(shell cd .. && pwd) && $(MAKE) MODULE=fault_injection.floor_1_input

fault_area:
	cd .. && python3 -m fault_injection.silent_floor_area

clean::
	rm -rf sim_build results.xml fault_matrix_results.json