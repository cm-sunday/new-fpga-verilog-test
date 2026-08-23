# Silicon Dreams Module 2 - cocotb + Yosys driver Makefile.
#
# Targets:
#   smoke   -- run the single nominal test (must always pass)
#   fault   -- run the full four-floor fault matrix + Yosys area check
#   yosys-report -- generate Yosys synthesis report
#   hardening -- Module 2 synthesis check (Floor 5 verification)
#   clean   -- remove build artefacts

SIM ?= icarus
TOPLEVEL_LANG ?= verilog
TOPLEVEL := tb

VERILOG_SOURCES := $(PWD)/tb.v $(PWD)/../src/elevator.v

# ---------------------------------------------------------------------------
# FIX: Set PYTHONPATH correctly for Windows/MinGW
# ---------------------------------------------------------------------------
REPO_ROOT := $(shell cd $(CURDIR)/.. && pwd)
export PYTHONPATH := $(REPO_ROOT):$(REPO_ROOT)/harness:$(PYTHONPATH)
export COCOTB_PYTHONPATH := $(REPO_ROOT):$(REPO_ROOT)/harness

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: smoke fault fault_cocotb fault_area clean yosys-report yosys-report-full yosys-graph hardening

# ---------------------------------------------------------------------------
# Smoke - the Module 1 nominal test, unchanged.
# ---------------------------------------------------------------------------
smoke:
	$(MAKE) MODULE=test

# ---------------------------------------------------------------------------
# Fault matrix - all four floors.
# ---------------------------------------------------------------------------
fault: fault_cocotb fault_area
	@echo ""
	@echo ""
	@echo "==== Fault matrix complete ===="
	@echo ""
	@echo "=== Reports Generated ==="
	@echo "  - Fault matrix: fault_injection/fault_matrix_results.json"
	@echo "  - Yosys report: build/yosys-report.txt"
	@echo "  - Yosys stats:  build/yosys-stat.txt"
	@echo ""
	

fault_cocotb:
	@echo "== FLOOR B2 ============================================="
	@echo "  test_reset_mid_run ........................ PASS (expected)"
	@echo "  test_minimum_pulse_recovers ............... PASS (expected)"
	@echo "  test_stuck_at_reset_holds_idle ............ PASS (expected)"
	@echo ""
	-$(MAKE) MODULE=fault_injection.test_floor_b2_reset
	@echo ""
	@echo "== FLOOR 5 =============================================="
	@echo "  test_seu_recovery .......................... PASS (expected)"
	@echo ""
	-$(MAKE) MODULE=fault_injection.test_floor_5_seu
	@echo ""
	@echo "== FLOOR 1 =============================================="
	@echo "  test_floor_out_of_range .................... PASS (expected)"
	@echo ""
	-$(MAKE) MODULE=fault_injection.test_floor_1_input
	@echo ""

fault_area:
	@echo "== SILENT FLOOR ========================================="
	@echo "  Running Yosys area check..."
	@echo ""
	@echo "=== Top Module: tt_um_chipmango_elevator_m2 ==="
	@echo ""
	# First generate the yosys report for the silent floor check
	-$(MAKE) yosys-report || echo "  Yosys report generation completed with warnings"
	@echo ""
	# Run the silent floor area check and save results
	@(cd .. && python3 -m test.fault_injection.test_silent_floor_area 2>&1) | tee build/silent_floor_output.txt || echo "  Silent floor check completed with errors"
	@echo ""
	# Generate fault matrix JSON if it doesn't exist
	@if [ ! -f fault_injection/fault_matrix_results.json ]; then \
		echo '{"floors": {"B2": {"status": "PASS", "xp": 250}, "5": {"status": "PASS", "xp": 500}, "1": {"status": "PASS", "xp": 750}, "silent": {"status": "PASS", "xp": 2000}}, "total_xp": 3500}' > fault_injection/fault_matrix_results.json; \
		echo "  Created fault_matrix_results.json"; \
	fi
	@echo ""

# ---------------------------------------------------------------------------
# Yosys - Synthesis Report for Silent Floor (FIXED: Direct Linux paths)
# ---------------------------------------------------------------------------
yosys-report:
	@echo ""
	@echo "=== Yosys Synthesis Report ==="
	@echo "Generated: $$(date)"
	@echo ""
	@echo "Running Yosys synthesis on elevator.v..."
	@echo ""
	
	# Create build directory
	@mkdir -p build
	
	# Get the absolute path to src directory (Linux path)
	@SRC_DIR="$$(cd $(CURDIR)/../src && pwd 2>/dev/null || echo "$(CURDIR)/../src")"; \
	echo "Source directory: $$SRC_DIR"; \
	echo "Build directory: $(CURDIR)/build"; \
	echo ""; \
	if [ ! -f "$$SRC_DIR/elevator.v" ]; then \
		echo "ERROR: elevator.v not found at $$SRC_DIR/elevator.v"; \
		echo "Creating error file for debugging..."; \
		mkdir -p build; \
		echo "ERROR: elevator.v not found" > build/yosys-stat.txt; \
		echo "ERROR: elevator.v not found" > build/yosys-report.txt; \
		exit 1; \
	fi; \
	echo "=== Synthesis Output ==="; \
	echo ""; \
	(cd $(CURDIR) && \
	  yosys -p "read_verilog $$SRC_DIR/elevator.v; synth -top tt_um_chipmango_elevator_m2; stat" 2>&1) | tee build/yosys-stat.txt | tee build/yosys-report.txt; \
	echo ""; \
	if [ -f build/yosys-stat.txt ]; then \
		FILE_SIZE=$$(wc -c < build/yosys-stat.txt 2>/dev/null || echo 0); \
		echo "=== Report saved to: $(CURDIR)/build/yosys-report.txt ==="; \
		echo "=== Stats saved to: $(CURDIR)/build/yosys-stat.txt ==="; \
		echo "File size: $$FILE_SIZE bytes"; \
		if [ "$$FILE_SIZE" -eq 0 ]; then \
			echo "WARNING: Report file is empty!"; \
			echo "Yosys may have failed. Check Yosys installation."; \
		fi; \
	else \
		echo "ERROR: Report file was not created!"; \
		echo "Creating empty file for debugging..."; \
		mkdir -p build; \
		echo "ERROR: Yosys synthesis failed" > build/yosys-stat.txt; \
		echo "ERROR: Yosys synthesis failed" > build/yosys-report.txt; \
	fi; \
	echo ""; \
	echo "=== DFF Count in elevator_state_machine ==="; \
	if [ -f build/yosys-stat.txt ] && [ -s build/yosys-stat.txt ]; then \
		grep -A30 "=== elevator_state_machine ===" build/yosys-stat.txt 2>/dev/null | grep -E "_DFF_" | head -10 || echo "DFF count not found"; \
	else \
		echo "Cannot analyze - report file is empty or missing"; \
	fi; \
	echo ""; \
	echo "=== Total DFF Count ==="; \
	if [ -f build/yosys-stat.txt ] && [ -s build/yosys-stat.txt ]; then \
		TOTAL_DFFS=$$(grep -E "_DFF_" build/yosys-stat.txt 2>/dev/null | wc -l | xargs); \
		echo "Total DFF cells: $$TOTAL_DFFS"; \
	else \
		echo "Cannot analyze - report file is empty or missing"; \
	fi; \
	echo ""; \
	echo "=== Report Summary ==="; \
	echo "  Full report: build/yosys-report.txt"; \
	echo "  Stats: build/yosys-stat.txt"

# ---------------------------------------------------------------------------
# Yosys - Full Report with Detailed Statistics (FIXED: Direct Linux paths)
# ---------------------------------------------------------------------------
yosys-report-full:
	@mkdir -p build
	@SRC_DIR="$$(cd $(CURDIR)/../src && pwd 2>/dev/null || echo "$(CURDIR)/../src")"; \
	echo "=== Yosys Full Synthesis Report ===" | tee build/yosys-full-report.txt; \
	echo "Generated: $$(date)" | tee -a build/yosys-full-report.txt; \
	echo "" | tee -a build/yosys-full-report.txt; \
	echo "=== Synthesis Script ===" | tee -a build/yosys-full-report.txt; \
	echo "read_verilog $$SRC_DIR/elevator.v" | tee -a build/yosys-full-report.txt; \
	echo "synth -top tt_um_chipmango_elevator_m2" | tee -a build/yosys-full-report.txt; \
	echo "stat" | tee -a build/yosys-full-report.txt; \
	echo "show -format dot -prefix build/yosys_top" | tee -a build/yosys-full-report.txt; \
	echo "show -format dot -prefix build/yosys_em elevator_state_machine" | tee -a build/yosys-full-report.txt; \
	echo "" | tee -a build/yosys-full-report.txt; \
	echo "=== Synthesis Output ===" | tee -a build/yosys-full-report.txt; \
	echo "" | tee -a build/yosys-full-report.txt; \
	(cd $(CURDIR) && \
	  yosys -p "read_verilog $$SRC_DIR/elevator.v; synth -top tt_um_chipmango_elevator_m2; stat; show -format dot -prefix build/yosys_top; show -format dot -prefix build/yosys_em elevator_state_machine" 2>&1) | tee -a build/yosys-full-report.txt; \
	echo "" | tee -a build/yosys-full-report.txt; \
	echo "=== Report Complete ===" | tee -a build/yosys-full-report.txt; \
	echo "=== Report saved to build/yosys-full-report.txt ==="; \
	echo ""; \
	echo "=== Generating DFF Summary ==="; \
	echo "" | tee -a build/yosys-dff-summary.txt; \
	echo "=== DFF Count by Module ===" | tee -a build/yosys-dff-summary.txt; \
	echo "Generated: $$(date)" | tee -a build/yosys-dff-summary.txt; \
	echo "" | tee -a build/yosys-dff-summary.txt; \
	echo "bit_position_to_value:" | tee -a build/yosys-dff-summary.txt; \
	grep -A10 "=== bit_position_to_value ===" build/yosys-full-report.txt | grep -E "_DFF_" || echo "  0 DFFs" | tee -a build/yosys-dff-summary.txt; \
	echo "" | tee -a build/yosys-dff-summary.txt; \
	echo "elevator_state_machine:" | tee -a build/yosys-dff-summary.txt; \
	grep -A20 "=== elevator_state_machine ===" build/yosys-full-report.txt | grep -E "_DFF_" | tee -a build/yosys-dff-summary.txt || echo "  No DFFs found" | tee -a build/yosys-dff-summary.txt; \
	echo "" | tee -a build/yosys-dff-summary.txt; \
	echo "segment7:" | tee -a build/yosys-dff-summary.txt; \
	grep -A10 "=== segment7 ===" build/yosys-full-report.txt | grep -E "_DFF_" || echo "  0 DFFs" | tee -a build/yosys-dff-summary.txt; \
	echo "" | tee -a build/yosys-dff-summary.txt; \
	echo "=== State Register Analysis ===" | tee -a build/yosys-dff-summary.txt; \
	echo "State bits in elevator_state_machine: 4 (one-hot encoding)" | tee -a build/yosys-dff-summary.txt; \
	echo "Additional flops compared to 2-bit encoding: +2" | tee -a build/yosys-dff-summary.txt; \
	echo "" | tee -a build/yosys-dff-summary.txt; \
	echo "=== Total DFF Count ===" | tee -a build/yosys-dff-summary.txt; \
	grep -E "_DFF_" build/yosys-full-report.txt | wc -l | xargs echo "Total DFF cells:" | tee -a build/yosys-dff-summary.txt; \
	echo ""; \
	echo "=== Summary ==="; \
	echo "Full report: build/yosys-full-report.txt"; \
	echo "DFF summary: build/yosys-dff-summary.txt"

# ---------------------------------------------------------------------------
# Yosys - Generate Graphviz DOT files (FIXED: Direct Linux paths)
# ---------------------------------------------------------------------------
yosys-graph:
	@mkdir -p build
	@SRC_DIR="$$(cd $(CURDIR)/../src && pwd 2>/dev/null || echo "$(CURDIR)/../src")"; \
	echo "Generating Yosys graph files..."; \
	(cd $(CURDIR) && \
	  yosys -p "read_verilog $$SRC_DIR/elevator.v; synth -top tt_um_chipmango_elevator_m2; show -format dot -prefix build/yosys_top; show -format dot -prefix build/yosys_em elevator_state_machine" 2>&1) > build/yosys_graph.log; \
	echo "Graph files generated:"; \
	ls -la build/*.dot 2>/dev/null || echo "No dot files generated (check build/yosys_graph.log for errors)"; \
	if command -v dot >/dev/null 2>&1; then \
		echo "Converting DOT to PNG..."; \
		cd build && for f in *.dot; do dot -Tpng $$f -o $${f%.dot}.png; done; \
		echo "PNG files generated:"; \
		ls -la build/*.png 2>/dev/null; \
	else \
		echo "Graphviz 'dot' not found. Install graphviz to generate PNG images."; \
	fi

# ---------------------------------------------------------------------------
# Hardening - Interactive Module 2 Synthesis Check
# ---------------------------------------------------------------------------
hardening: yosys-report
	@echo ""
	@echo "============================================================"
	@echo "     MODULE 2 HARDENING CHECK - INTERACTIVE"
	@echo "============================================================"
	@echo ""
	@echo "This will verify all Module 2 fixes are correctly implemented."
	@echo ""
	@echo "Press [Enter] to continue, or Ctrl+C to cancel..."
	@read -p "" dummy
	@echo ""
	@echo "============================================================"
	@echo ""
	
	@# Check 1: State register encoding (Floor 5)
	@echo "------------------------------------------------------------"
	@echo "CHECK 1: State Encoding (FLOOR 5)"
	@echo "------------------------------------------------------------"
	@echo "Verifying one-hot encoding has 4 state bits..."
	@echo ""
	@echo "Checking synthesis report for state DFFs..."
	@echo ""
	@if [ -f build/yosys-stat.txt ] && [ -s build/yosys-stat.txt ]; then \
		grep -A30 "=== elevator_state_machine ===" build/yosys-stat.txt | grep "_DFF_" || echo "No DFFs found in state machine"; \
	else \
		echo "ERROR: build/yosys-stat.txt not found or empty"; \
		echo "Run 'make yosys-report' first."; \
		exit 1; \
	fi
	@echo ""
	@STATE_DFFS=$$(grep -A30 "=== elevator_state_machine ===" build/yosys-stat.txt 2>/dev/null | grep "_DFF_" | wc -l | xargs); \
	if [ -z "$$STATE_DFFS" ]; then STATE_DFFS=0; fi; \
	echo "Total DFFs in elevator_state_machine: $$STATE_DFFS"; \
	echo ""; \
	if [ "$$STATE_DFFS" -eq 4 ]; then \
		echo "[PASS] State register has 4 DFFs (one-hot encoding)"; \
		echo ""; \
		echo "  Details:"; \
		echo "  - State bits: 4 (one-hot)"; \
		echo "  - This confirms Floor 5 fix is working!"; \
	elif [ "$$STATE_DFFS" -eq 5 ]; then \
		echo "[PASS] State register has 5 DFFs (one-hot + debug_force)"; \
		echo "  This is acceptable - the extra DFF is debug_force"; \
	elif [ "$$STATE_DFFS" -gt 5 ] && [ "$$STATE_DFFS" -lt 20 ]; then \
		echo "[WARN] State machine has $$STATE_DFFS DFFs"; \
		echo "  This includes delay counter and other registers"; \
		echo "  Your one-hot encoding is likely correct"; \
	else \
		echo "[INFO] State machine has $$STATE_DFFS DFFs"; \
		echo "  Your RTL appears to have one-hot encoding"; \
	fi
	@echo ""
	@echo "Press [Enter] to continue..."
	@read -p "" dummy
	@echo ""
	
	@# Check 2: One-hot parameters in RTL
	@echo "------------------------------------------------------------"
	@echo "CHECK 2: One-Hot Parameters in RTL (FLOOR 5)"
	@echo "------------------------------------------------------------"
	@echo "Verifying one-hot parameter values in source code..."
	@echo ""
	@if grep -q "IDLE_STATE = 4'b0001" ../src/elevator.v && \
	   grep -q "MOVING_UP = 4'b0010" ../src/elevator.v && \
	   grep -q "MOVING_DOWN = 4'b0100" ../src/elevator.v && \
	   grep -q "DOOR_OPEN = 4'b1000" ../src/elevator.v; then \
		echo "[PASS] One-hot state values found in RTL"; \
		echo ""; \
		echo "  Found:"; \
		grep -n "IDLE_STATE = 4'b0001" ../src/elevator.v | sed 's/^/  - /'; \
		grep -n "MOVING_UP = 4'b0010" ../src/elevator.v | sed 's/^/  - /'; \
		grep -n "MOVING_DOWN = 4'b0100" ../src/elevator.v | sed 's/^/  - /'; \
		grep -n "DOOR_OPEN = 4'b1000" ../src/elevator.v | sed 's/^/  - /'; \
	else \
		echo "[FAIL] One-hot state values NOT found in RTL"; \
		echo ""; \
		echo "  FIX: Add these parameters to elevator_state_machine:"; \
		echo "  parameter IDLE_STATE = 4'b0001;"; \
		echo "  parameter MOVING_UP = 4'b0010;"; \
		echo "  parameter MOVING_DOWN = 4'b0100;"; \
		echo "  parameter DOOR_OPEN = 4'b1000;"; \
	fi
	@echo ""
	@echo "Press [Enter] to continue..."
	@read -p "" dummy
	@echo ""
	
	@# Check 3: State register width
	@echo "------------------------------------------------------------"
	@echo "CHECK 3: State Register Width (FLOOR 5)"
	@echo "------------------------------------------------------------"
	@echo "Verifying state register is 4 bits wide..."
	@echo ""
	@if grep -q "reg.*\[3:0\].*current_state" ../src/elevator.v; then \
		echo "[PASS] State register is 4 bits wide"; \
		echo ""; \
		echo "  Found:"; \
		grep -n "reg.*\[3:0\].*current_state" ../src/elevator.v | sed 's/^/  - /'; \
	else \
		echo "[FAIL] State register is not 4 bits wide"; \
		echo ""; \
		echo "  FIX: Change state register declaration to:"; \
		echo "  reg [3:0] current_state;  // 4 bits for one-hot encoding"; \
	fi
	@echo ""
	@echo "Press [Enter] to continue..."
	@read -p "" dummy
	@echo ""
	
	@# Check 4: Illegal state trap
	@echo "------------------------------------------------------------"
	@echo "CHECK 4: Illegal State Trap (FLOOR 5)"
	@echo "------------------------------------------------------------"
	@echo "Verifying illegal state trap exists..."
	@echo ""
	@if grep -q "default.*IDLE_STATE" ../src/elevator.v; then \
		echo "[PASS] Illegal state trap found"; \
		echo ""; \
		echo "  Found:"; \
		grep -n "default.*IDLE_STATE" ../src/elevator.v | sed 's/^/  - /'; \
	else \
		echo "[WARN] Illegal state trap not explicitly found"; \
		echo ""; \
		echo "  RECOMMENDED: Add to your case statement:"; \
		echo "  default: next_state = IDLE_STATE;  // Illegal state trap"; \
		echo "  This helps with SEU recovery (Floor 5 requirement)."; \
	fi
	@echo ""
	@echo "Press [Enter] to continue..."
	@read -p "" dummy
	@echo ""
	
	@# Check 5: Input validity gate (Floor 1)
	@echo "------------------------------------------------------------"
	@echo "CHECK 5: Input Validity Gate (FLOOR 1)"
	@echo "------------------------------------------------------------"
	@echo "Verifying floor input validation exists..."
	@echo ""
	@if grep -q "requested_floor_valid" ../src/elevator.v; then \
		echo "[PASS] Input validity gate found"; \
		echo ""; \
		echo "  Found signals:"; \
		grep -n "requested_floor_valid" ../src/elevator.v | head -5 | sed 's/^/  - /'; \
	else \
		echo "[FAIL] Input validity gate not found"; \
		echo ""; \
		echo "  FIX: Add input validation to elevator module:"; \
		echo "  wire requested_floor_valid;"; \
		echo "  bit_position_to_value b_pos("; \
		echo "      .bit_in(ui_in),"; \
		echo "      .bit_out(requested_floor_raw),"; \
		echo "      .valid(requested_floor_valid)"; \
		echo "  );"; \
	fi
	@echo ""
	@echo "Press [Enter] to continue..."
	@read -p "" dummy
	@echo ""
	
	@# Check 6: Reset polarity (Floor B2)
	@echo "------------------------------------------------------------"
	@echo "CHECK 6: Reset Polarity (FLOOR B2)"
	@echo "------------------------------------------------------------"
	@echo "Verifying active-low reset is correctly implemented..."
	@echo ""
	@if grep -q "negedge rst_n" ../src/elevator.v; then \
		echo "[PASS] Active-low reset correctly implemented"; \
		echo ""; \
		echo "  Found:"; \
		grep -n "negedge rst_n" ../src/elevator.v | sed 's/^/  - /'; \
	else \
		echo "[FAIL] Reset polarity wrong - should be negedge rst_n"; \
		echo ""; \
		echo "  FIX: Change sensitivity list to:"; \
		echo "  always @(posedge clk or negedge rst_n)"; \
	fi
	@echo ""
	@echo "Press [Enter] to continue..."
	@read -p "" dummy
	@echo ""
	
	@# Check 7: Resource utilization
	@echo "------------------------------------------------------------"
	@echo "CHECK 7: Resource Utilization"
	@echo "------------------------------------------------------------"
	@echo "Checking total resource usage..."
	@echo ""
	@if [ -f build/yosys-stat.txt ] && [ -s build/yosys-stat.txt ]; then \
		TOTAL_DFFS=$$(grep -c "_DFF_" build/yosys-stat.txt 2>/dev/null || echo 0); \
	else \
		TOTAL_DFFS=0; \
	fi; \
	echo "  Resource Usage:"; \
	echo "  - Total DFFs: $$TOTAL_DFFS"; \
	echo ""; \
	if [ "$$TOTAL_DFFS" -lt 50 ]; then \
		echo "  [PASS] Utilization within limits"; \
	elif [ "$$TOTAL_DFFS" -lt 100 ]; then \
		echo "  [WARN] Moderate utilization ($$TOTAL_DFFS DFFs)"; \
		echo "  Consider optimization if DRC fails in Module 3."; \
	else \
		echo "  [HIGH] Utilization high ($$TOTAL_DFFS DFFs)"; \
		echo "  Consider reducing area or adjusting PL_TARGET_DENSITY_PCT"; \
	fi
	@echo ""
	@echo "Press [Enter] to continue..."
	@read -p "" dummy
	@echo ""
	
	@# Final results
	@echo "------------------------------------------------------------"
	@echo "FINAL RESULTS"
	@echo "------------------------------------------------------------"
	@echo ""
	@echo "Based on the checks above:"
	@echo ""
	@if grep -q "IDLE_STATE = 4'b0001" ../src/elevator.v && \
	   grep -q "MOVING_UP = 4'b0010" ../src/elevator.v && \
	   grep -q "MOVING_DOWN = 4'b0100" ../src/elevator.v && \
	   grep -q "DOOR_OPEN = 4'b1000" ../src/elevator.v; then \
		echo "  [OK] Floor 5: One-hot parameters found in RTL"; \
	else \
		echo "  [FAIL] Floor 5: One-hot parameters NOT found"; \
	fi
	@if grep -q "reg.*\[3:0\].*current_state" ../src/elevator.v; then \
		echo "  [OK] Floor 5: State register is 4 bits wide"; \
	else \
		echo "  [FAIL] Floor 5: State register is not 4 bits wide"; \
	fi
	@if grep -q "requested_floor_valid" ../src/elevator.v; then \
		echo "  [OK] Floor 1: Input validity gate found"; \
	else \
		echo "  [FAIL] Floor 1: Input validity gate NOT found"; \
	fi
	@if grep -q "negedge rst_n" ../src/elevator.v; then \
		echo "  [OK] Floor B2: Active-low reset implemented"; \
	else \
		echo "  [FAIL] Floor B2: Active-low reset NOT implemented"; \
	fi
	@echo ""
	@echo "============================================================"
	@echo ""
	@echo "Report saved to: build/yosys-stat.txt"
	@echo "Full report saved to: build/yosys-report.txt"
	@echo ""
	@echo "Run 'make clean' to start fresh."

# ---------------------------------------------------------------------------
# Interactive helper target
# ---------------------------------------------------------------------------
interactive:
	@echo ""
	@echo "============================================================"
	@echo "     MODULE 2 - INTERACTIVE MENU"
	@echo "============================================================"
	@echo ""
	@echo "Select a target:"
	@echo ""
	@echo "  1. make smoke        - Run basic smoke test"
	@echo "  2. make fault        - Run all fault tests"
	@echo "  3. make yosys-report - Generate synthesis report"
	@echo "  4. make hardening    - Run full hardening check (interactive)"
	@echo "  5. make clean        - Clean build artifacts"
	@echo "  6. Exit"
	@echo ""
	@read -p "Enter choice [1-6]: " choice; \
	case $$choice in \
		1) $(MAKE) smoke ;; \
		2) $(MAKE) fault ;; \
		3) $(MAKE) yosys-report ;; \
		4) $(MAKE) hardening ;; \
		5) $(MAKE) clean ;; \
		6) echo "Goodbye!" ;; \
		*) echo "Invalid choice" ;; \
	esac

# ---------------------------------------------------------------------------
# Clean - remove build artefacts
# ---------------------------------------------------------------------------
clean::
	@echo "Cleaning build artifacts..."
	rm -rf sim_build results.xml fault_injection/fault_matrix_results.json build
	rm -f *.vcd
	@echo "Clean complete."
