// =============================================================================
// elevator.v - Hardened elevator controller from Module 2
// =============================================================================
`default_nettype none

module elevator (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       request_strobe,
    input  wire [3:0] requested_floor,
    input  wire       fault_inject_en,
    output wire [3:0] current_floor,
    output wire [2:0] state,
    output wire       door_open,
    output wire       error_led
);

    // States - binary encoding (IDLE = 0 for test compatibility)
    localparam IDLE      = 3'b000;
    localparam MOVING_UP = 3'b001;
    localparam MOVING_DN = 3'b010;
    localparam DOOR_OPEN = 3'b011;

    reg [2:0] current_state, next_state;
    reg [3:0] floor_reg;
    reg [3:0] target_floor;
    reg [3:0] delay_counter;
    reg       door_open_reg;
    reg       error_led_reg;
    reg       door_opened;          // Track if door has been opened

    // Validate request
    wire request_valid = (requested_floor >= 4'd0 && requested_floor <= 4'd8);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_state <= IDLE;
            floor_reg <= 4'd0;
            target_floor <= 4'd0;
            delay_counter <= 4'd0;
            door_open_reg <= 1'b0;
            error_led_reg <= 1'b0;
            door_opened <= 1'b0;     // ✅ Door not opened yet
        end else begin
            current_state <= next_state;
            
            // Move floor with delay
            if (current_state == MOVING_UP) begin
                if (delay_counter == 4'd1) begin
                    delay_counter <= 4'd0;
                    if (floor_reg < target_floor)
                        floor_reg <= floor_reg + 1'b1;
                end else begin
                    delay_counter <= delay_counter + 1'b1;
                end
            end else if (current_state == MOVING_DN) begin
                if (delay_counter == 4'd1) begin
                    delay_counter <= 4'd0;
                    if (floor_reg > target_floor)
                        floor_reg <= floor_reg - 1'b1;
                end else begin
                    delay_counter <= delay_counter + 1'b1;
                end
            end else begin
                delay_counter <= 4'd0;
            end

            // Latch valid request
            if (request_strobe && request_valid) begin
                target_floor <= requested_floor;
            end

            // Door control - only open when:
            // 1. In IDLE state
            // 2. At target floor
            // 3. A valid request has been received (door_opened flag)
            if (current_state == IDLE && floor_reg == target_floor && request_strobe && request_valid) begin
                door_open_reg <= 1'b1;
                door_opened <= 1'b1;
            end else if (door_opened && current_state == IDLE && floor_reg == target_floor) begin
                // Keep door open after opening
                door_open_reg <= 1'b1;
            end else if (current_state == MOVING_UP || current_state == MOVING_DN) begin
                // Close door when moving
                door_open_reg <= 1'b0;
                door_opened <= 1'b0;
            end else begin
                door_open_reg <= 1'b0;
            end

            // Error injection
            if (fault_inject_en) begin
                error_led_reg <= ~error_led_reg;
            end else begin
                error_led_reg <= 1'b0;
            end
        end
    end

    // Next state logic
    always @(*) begin
        next_state = current_state;
        case (current_state)
            IDLE: begin
                if (request_strobe && request_valid) begin
                    if (floor_reg < requested_floor)
                        next_state = MOVING_UP;
                    else if (floor_reg > requested_floor)
                        next_state = MOVING_DN;
                    else
                        next_state = IDLE;
                end
            end
            MOVING_UP: begin
                if (floor_reg >= target_floor)
                    next_state = IDLE;
            end
            MOVING_DN: begin
                if (floor_reg <= target_floor)
                    next_state = IDLE;
            end
            default: next_state = IDLE;
        endcase
    end

    // Outputs
    assign current_floor = floor_reg;
    assign state = current_state;
    assign door_open = door_open_reg;
    assign error_led = error_led_reg;

endmodule

`default_nettype wire
