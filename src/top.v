// =============================================================================
// Silicon Dreams · Module 3 · top.v
// =============================================================================
`default_nettype none

module tt_um_silicon_dreams (
  input  wire [7:0] ui_in,
  output wire [7:0] uo_out,
  input  wire [7:0] uio_in,
  output wire [7:0] uio_out,
  output wire [7:0] uio_oe,
  input  wire       ena,
  input  wire       clk,
  input  wire       rst_n
);

  // ---------------------------------------------------------------------------
  // Reset-domain partitioning
  // ---------------------------------------------------------------------------
  wire elevator_rst_n;
  wire arbiter_rst_n;
  wire axiom_rst_n_sync;
  wire axiom_rst;

  reset_synchroniser #(.HOLD_CYCLES(4)) u_rst_elev (
    .clk        (clk),
    .rst_n      (rst_n),
    .rst_n_sync (elevator_rst_n)
  );
  
  reset_synchroniser #(.HOLD_CYCLES(6)) u_rst_arb (
    .clk        (clk),
    .rst_n      (rst_n),
    .rst_n_sync (arbiter_rst_n)
  );
  
  reset_synchroniser #(.HOLD_CYCLES(4)) u_rst_axm (
    .clk        (clk),
    .rst_n      (rst_n),
    .rst_n_sync (axiom_rst_n_sync)
  );
  
  assign axiom_rst = ~axiom_rst_n_sync;

  // ---------------------------------------------------------------------------
  // Input decoding
  // ---------------------------------------------------------------------------
  wire       request_strobe       = ui_in[0];
  wire [3:0] requested_floor      = ui_in[4:1];
  wire       priority_override    = ui_in[5];
  wire       axiom_enable         = ui_in[6];
  wire       fault_inject_enable  = uio_in[0];
  // FIX: Removed unused global_test_mode
  // wire       global_test_mode     = ui_in[7];  // DELETED

  // ---------------------------------------------------------------------------
  // Elevator
  // ---------------------------------------------------------------------------
  wire [3:0] current_floor;
  wire [2:0] elevator_state;
  wire       door_open;
  wire       elevator_error_led;

  wire [3:0] req_payload;
  wire       req_valid;
  wire       req_ready;

  // ---------------------------------------------------------------------------
  // Clock Gate - ONLY for AXIOM
  // ---------------------------------------------------------------------------
  wire axiom_clk_gated;
  wire clock_gate_active;  // 1 = gated, 0 = active
  
  clock_gate u_axiom_gate (
    .clk    (clk),
    .enable (axiom_enable),
    .gclk   (axiom_clk_gated),
    .active (clock_gate_active)
  );

  // ---------------------------------------------------------------------------
  // Elevator (uses ungated clock - ALWAYS RUNNING)
  // ---------------------------------------------------------------------------
  elevator_req_port u_req_port (
    .clk         (clk),
    .rst_n       (elevator_rst_n),
    .strobe      (request_strobe),
    .floor       (requested_floor),
    .req_payload (req_payload),
    .req_valid   (req_valid),
    .req_ready   (req_ready)
  );

  elevator u_elevator (
    .clk             (clk),
    .rst_n           (elevator_rst_n),
    .request_strobe  (request_strobe),
    .requested_floor (requested_floor),
    .fault_inject_en (fault_inject_enable),
    .current_floor   (current_floor),
    .state           (elevator_state),
    .door_open       (door_open),
    .error_led       (elevator_error_led)
  );

  // ---------------------------------------------------------------------------
  // Arbiter (uses ungated clock - needs to always respond)
  // ---------------------------------------------------------------------------
  wire grant_elev;
  wire grant_axiom;
  // FIX: Removed unused wire
  // wire arbiter_queue_nonempty;  // DELETED

  arbiter u_arbiter (
    .clk             (clk),
    .rst_n           (arbiter_rst_n),
    .priority_req    (priority_override),
    .elev_req_valid  (req_valid),
    .elev_req_ready  (req_ready),
    .elev_req_payload(req_payload),
    .grant_elev      (grant_elev),
    .grant_axiom     (grant_axiom),
    .queue_nonempty  ()  // Unused output
  );

  // ---------------------------------------------------------------------------
  // AXIOM shim (uses GATED clock)
  // ---------------------------------------------------------------------------
  wire [7:0] axiom_resp_out;
  wire       axiom_mstrobe_led;

  axiom_shim u_axiom_shim (
    .clk              (axiom_clk_gated),
    .rst_n            (axiom_rst_n_sync),
    .axiom_rst        (axiom_rst),
    .granted          (grant_axiom),
    .cmd_in           (req_payload[3:0]),
    .data_in          (8'h00),
    .resp_out         (axiom_resp_out),
    .misbehaviour_led (axiom_mstrobe_led)
  );

  // ---------------------------------------------------------------------------
  // Output pad assignments
  // ---------------------------------------------------------------------------
  assign uo_out = { 
    door_open,           // [7]
    elevator_state,      // [6:4]
    current_floor        // [3:0]
  };

  assign uio_out = { 
    elevator_error_led,  // [7]
    2'b00,               // [6:5] reserved
    axiom_mstrobe_led,   // [4]
    clock_gate_active,   // [3] ← 1 = gated, 0 = active
    grant_axiom,         // [2]
    grant_elev,          // [1]
    1'b0                 // [0] input
  };

  assign uio_oe = 8'b1111_1110;

  /* verilator lint_off UNUSED */
  wire _unused = &{1'b0, uio_in[7:1], ena, axiom_resp_out};
  /* verilator lint_on UNUSED */

endmodule

`default_nettype wire
