# Makefile - Simple smoke test with clean
# See https://docs.cocotb.org/en/stable/quickstart.html for more info

# defaults
SIM ?= icarus
WAVES ?= 1
TOPLEVEL_LANG ?= verilog
SRC_DIR = $(PWD)/../src
PROJECT_SOURCES = elevator.v
RESULTS_XML ?= results.xml

# IMPORTANT: Set the top-level module name
TOPLEVEL = tb
MODULE = test

ifneq ($(GATES),yes)

# RTL simulation:
SIM_BUILD = sim_build/rtl
VERILOG_SOURCES += $(SRC_DIR)/elevator.v  # Use absolute path
VERILOG_SOURCES += $(PWD)/tb.v            # Add testbench

else

# Gate level simulation:
SIM_BUILD = sim_build/gl
COMPILE_ARGS    += -DGL_TEST
COMPILE_ARGS    += -DFUNCTIONAL
COMPILE_ARGS    += -DUSE_POWER_PINS
COMPILE_ARGS    += -DSIM
COMPILE_ARGS    += -DUNIT_DELAY=\#1
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v
VERILOG_SOURCES += $(PWD)/tb.v

endif

# Allow sharing configuration between design and testbench via `include`:
COMPILE_ARGS += -I$(SRC_DIR)

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

# Clean target
clean-smoke:
	@echo " Cleaning up..."
	@rm -f results.xml
	@rm -f tb.vcd
	@rm -f *.vcd
	@rm -f *.fst
	@rm -f *.log
	@rm -f *.xml
	@rm -rf sim_build/
	@rm -rf __pycache__/
	@rm -f *.pyc
	@echo " Clean complete"

# Smoke test
smoke: clean-smoke
	@echo ""
	@echo " Running smoke test..."
	@$(MAKE) sim
	@echo ""
	@echo " Smoke test passed!"
	@if [ -f "tb.vcd" ]; then \
		echo " Waveform saved to: tb.vcd"; \
	fi
	@echo " Results saved to: $(RESULTS_XML)"
	@echo ""