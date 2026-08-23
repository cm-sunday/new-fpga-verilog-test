// =============================================================================
// arbiter.v - Round-robin arbiter with priority mode
// =============================================================================
`default_nettype none

module arbiter (
  input  wire       clk,
  input  wire       rst_n,
  input  wire       priority_req,
  input  wire       elev_req_valid,
  output wire       elev_req_ready,
  /* verilator lint_off UNUSEDSIGNAL */
  input  wire [3:0] elev_req_payload,
  /* verilator lint_on UNUSEDSIGNAL */
  output reg        grant_elev,
  output reg        grant_axiom,
  output wire       queue_nonempty
);

  reg last_granted_axiom;
  reg pending_request;

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      grant_elev         <= 1'b0;
      grant_axiom        <= 1'b0;
      last_granted_axiom <= 1'b0;
      pending_request    <= 1'b0;
    end else begin
      grant_elev  <= 1'b0;
      grant_axiom <= 1'b0;
      
      // Track pending requests
      if (elev_req_valid && !grant_elev) begin
        pending_request <= 1'b1;
      end else if (grant_elev) begin
        pending_request <= 1'b0;
      end
      
      // Priority mode: AXIOM gets priority, but alternates to be fair
      if (priority_req) begin
        if (last_granted_axiom) begin
          grant_elev         <= 1'b1;
          grant_axiom        <= 1'b0;
          last_granted_axiom <= 1'b0;
        end else begin
          grant_elev         <= 1'b0;
          grant_axiom        <= 1'b1;
          last_granted_axiom <= 1'b1;
        end
      end
      // Round-robin mode
      else if (elev_req_valid || pending_request) begin
        if (last_granted_axiom) begin
          grant_elev         <= 1'b1;
          grant_axiom        <= 1'b0;
          last_granted_axiom <= 1'b0;
        end else begin
          grant_elev         <= 1'b0;
          grant_axiom        <= 1'b1;
          last_granted_axiom <= 1'b1;
        end
      end
    end
  end

  assign elev_req_ready = grant_elev;
  assign queue_nonempty = elev_req_valid || pending_request;

endmodule

`default_nettype wire
