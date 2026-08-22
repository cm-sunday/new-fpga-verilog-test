// =============================================================================
// axiom_blackbox.v  —  AXIOM Black Box for Synthesis
//
// For SYNTHESIS: Provides a simple stub (will be replaced by grader)
// For SIMULATION: Use axiom_blackbox_sim.v (via -DSIM_AXIOM)
// =============================================================================
`default_nettype none

// Only define this module in synthesis mode (SIM_AXIOM not defined)
`ifndef SIM_AXIOM

module axiom_blackbox (
  input  wire       clk,
  input  wire       rst,
  input  wire [3:0] cmd,
  input  wire [7:0] data,
  output wire [7:0] resp,
  output wire       misbehaviour_strobe
);
  // Simple stub for synthesis - will be replaced by grader
  assign resp = 8'h00;
  assign misbehaviour_strobe = 1'b0;
endmodule

`endif

`default_nettype wire
