# Module 2 Escape Log

## Floor B2 - Reset Polarity Fix

**Symptom:** 
The elevator state machine was not resetting properly when rst_n was asserted. The reset logic was using posedge rst_n instead of negedge rst_n, causing the state machine to enter an unknown state during power-up.

**Root Cause:** 
The sensitivity list used `posedge rst_n` which is incorrect for active-low reset. On the TinyTapeout platform, rst_n is active-low, meaning the reset should trigger when rst_n goes from 1 to 0.

**Fix:** 
Changed `always @(posedge clk or posedge rst_n)` to `always @(posedge clk or negedge rst_n)` in the elevator_state_machine module.

**Proof:** 
- `grep -n "negedge rst_n" ../src/elevator.v` shows line 158
- `make fault` shows test_floor_b2.py passing
- `make hardening` check 6 shows "[OK] Floor B2: Active-low reset implemented"

**Time:** [Your estimate - e.g., "30 minutes"]

---

## Floor 5 - One-Hot Re-encoding

**Symptom:** 
The state machine was using binary encoding (3 bits, 8 states) instead of one-hot encoding. This made the design vulnerable to SEU (Single Event Upset) and didn't meet the Floor 5 requirements for fault recovery.

**Root Cause:** 
The original state register was declared as `reg [2:0] state` and used binary values (3'b000, 3'b001, etc.) which is the default Verilog encoding.

**Fix:** 
- Changed state register to `reg [3:0] current_state, next_state` (4 bits)
- Added one-hot parameters:
  ```verilog
  parameter IDLE_STATE = 4'b0001;
  parameter MOVING_UP = 4'b0010;
  parameter MOVING_DOWN = 4'b0100;
  parameter DOOR_OPEN = 4'b1000;