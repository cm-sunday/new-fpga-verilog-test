Bug:
Signal rst_n is intended to be active-low but it is implemented as active-high.           

Line number 101

Current code:
always @(posedge clk or posedge rst_n)

if (rst_n) 

Expected:
always @(posedge clk or negedge rst_n)

if (!rst_n)

Impact:
Reset behavior does not match the interface definition and may behave incorrectly on hardware.