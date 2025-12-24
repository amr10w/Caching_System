module tb_ram;

    parameter WIDTH = 32;
    parameter DEPTH = 4; // 16 locations

    reg [WIDTH-1:0] data_in;
    reg [DEPTH-1:0] adress;
    reg write_enable;
    reg read_enable;
    reg clk;
    reg reset_n;
    wire [WIDTH-1:0] data_out;
    wire valid_out;

    Ram #(
        .WIDTH(WIDTH),
        .DEPTH(DEPTH)
    ) uut (
        .data_in(data_in),
        .adress(adress),
        .write_enable(write_enable),
        .read_enable(read_enable),
        .clk(clk),
      .reset_n(reset_n),
        .data_out(data_out),
        .valid_out(valid_out)
    );

    always #5 clk = ~clk;

    initial begin
        // Initialize
        clk = 0;
        reset_n = 0;
        write_enable = 0;
        read_enable = 0;
        data_in = 0;
        adress = 0;

		#10 reset_n=1;
     
  
      	#15;
        $readmemh("Test1.mem",uut.mem);
    

        // Write 0xAAAA at address 2
        #10;
        adress = 4'd2;
        data_in = 32'hAAAA;
        write_enable = 1;
        #10;
        write_enable = 0;

        // Write 0xBBBB at address 3
        #10;
        adress = 4'd3;
        data_in = 32'hBBBB;
        write_enable = 1;
        #10;
        write_enable = 0;

        // IDLE
        #10;

        // Read address 2
        adress = 4'd2;
        read_enable = 1;
     
        #15;
        adress = 4'd3;
       
        #20;
      	adress = 4'd0;
      #20;
        $finish;
    end
  
  initial begin
        $dumpfile("wave.vcd");
        $dumpvars;
    end

endmodule
