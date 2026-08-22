# Deliberate Bug Log - Module 1.6 Lab

### Bug 1: Reset Polarity Discrepancy
* **Line Number:** 111 (inside elevator_state_machine module sequential block)
* **Description:** The block sensitivity list listens to `posedge rst_n` and evaluates `if (rst_n)`, which creates an active-high reset behavior even though the input pin `rst_n` is active-low.
* **Proposed Fix:** Modify the sensitivity list to `always @(posedge clk or negedge rst_n)` and change the conditional check to `if (!rst_n)`.

### Bug 2: Unsafe State Branch Grouping
* **Line Number:** 87 (inside elevator_state_machine module combinational block)
* **Description:** The `MOVING_UP` and `MOVING_DOWN` states share a unified case statement body, allowing an unsafe instant direction reversal calculation without isolating individual state directions.
* **Proposed Fix:** Separate `MOVING_UP` and `MOVING_DOWN` into independent, dedicated case statements to ensure directional transitions are tightly controlled.

### Bug 3: Inefficient Register Bit Width (Silicon Waste)
* **Line Number:** 73 (inside elevator_state_machine module declarations)
* **Description:** The `delay` counter is allocated a 32-bit register space, which consumes unnecessary flip-flop hardware resources given that `DELAY_COUNT` is only tracking up to 10.
* **Proposed Fix:** Reduce the register width declaration from `reg [31:0]` to a size adequate for simulation limits, such as `reg [3:0]`.

### Bug 4: Reset Sensitivity Mismatch
* **Line Number:** 111 (inside the elevator_state_machine module)
* **Description:** The sequential block's sensitivity list uses posedge rst_n, which is inconsistent with the signal name rst_n and the active-low reset convention. This causes the asynchronous reset to trigger on the rising edge of rst_n instead of the falling edge, resulting in incorrect reset behavior.
* **Proposed Fix:** Update the sensitivity list to use negedge rst_n so the asynchronous reset correctly matches the active-low reset signal.