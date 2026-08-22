module exercise_force;
    reg clk = 0;
    reg rst_n = 0;
    
    always #10 clk = ~clk;          // 20ns clock period (50MHz)
    
    wire [3:0] dummy_reg;
    assign dummy_reg = 4'd3;        // Always 3 (0b0011)
    
    initial begin
        $dumpfile("exercise_force.vcd");
        $dumpvars(0, exercise_force);
        
        #100 rst_n = 1;             // Release reset at 100ns
        
        #100 force exercise_force.dummy_reg = 4'd7;   // Inject: force to 7 (0b0111)
        #200 release exercise_force.dummy_reg;        // Release: back to 3
        
        #100 $finish;
    end
endmodule