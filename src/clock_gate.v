// =============================================================================
// clock_gate.v - WITH CORRECT POLARITY active OUTPUT
// =============================================================================
`default_nettype none

module clock_gate (
  input  wire clk,
  input  wire enable,
  output wire gclk,
  output wire active   // 1 = clock is gated (inactive), 0 = clock is active
);

`ifdef FPGA
  // ============================================================
  // FPGA Synthesis Path (ice40 for ChipDiscover)
  // ============================================================
  // Use behavioural model - NO SKY130 cells in FPGA path!
  reg enable_latched;
  
  // Latch enable on falling edge of clock (same as ASIC ICG behaviour)
  always @(negedge clk) begin
    enable_latched <= enable;
  end
  
  // Gate the clock
  assign gclk = clk & enable_latched;
  
  // Active is inverse of enable
  assign active = ~enable;
  
`else
  // ============================================================
  // ASIC or Simulation Path
  // ============================================================
  // For FPGA, we want this path to also work, so use behavioral model
  // This avoids the Sky130 cell dependency
  reg enable_latched;
  
  // Latch on falling edge (matches ASIC behaviour)
  always @(negedge clk) begin
    enable_latched <= enable;
  end
  
  // Gate the clock
  assign gclk = clk & enable_latched;
  
  // Active is inverse of enable
  assign active = ~enable;
`endif

endmodule

`default_nettype wire
