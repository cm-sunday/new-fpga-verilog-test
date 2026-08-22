Clock and Reset Worksheet Predictions

Exercise 1 

# Predict-then-Simulate
| Scenario | Prediction | Actual |
|----------|------------|--------|
| Hold rst_n=0 for 10 cycles, then assert rst_n=1. | The elevator should remain in reset for 10 cycles and then begin normal operation after reset is released. | The design continuously resets after rst_n becomes high because the reset logic is implemented with posedge rst_n and if (rst_n), so the FSM never runs. |
| After reset, drive ui_in=8'b00000100 for 500 cycles. | The elevator should move to floor 3 and stop there. | Although next_state becomes MOVING_UP, current_state, current_floor, and delay are reset every clock cycle, so the elevator never leaves floor 0. |
| After reaching floor 3, press button 7 (ui_in=8'b01000000). | The elevator should continue from floor 3 to floor 7. | Floor 3 is never reached because the FSM never exits reset. Pressing button 7 only changes requested_floor; the elevator remains at floor 0. |
| Hold rst_n=1 the entire simulation; observe startup state. | Without an active reset, the initial register values would normally be unknown until explicitly initialized. | The incorrect reset polarity causes the design to initialize itself on every clock edge while rst_n is high, forcing the FSM to remain permanently in the reset state. |


Exercise 2 — Spot the Polarity Bug
1. The harness uses active-LOW reset (rst_n=0 means reset). Is this code active-low or active-high?
 The code is active-high.

2. What would the correct sensitivity list be for a proper active-low asynchronous reset?
always @(posedge clk or negedge rst_n)

3. What would the correct if-condition be?
if (!rst_n)

4. Why does the testbench currently pass despite this bug?
The testbench drives rst_n in a way that accidentally matches the buggy implementation. Since the reset is asserted using rst_n=1 in the design, the design still initializes correctly during the simulation even though the reset polarity is incorrect.

