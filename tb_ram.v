module tb_ram;

    parameter WIDTH = 32;
    parameter DEPTH = 4; // 16 locations

    reg [WIDTH-1:0] data_in;
    reg [DEPTH-1:0] adress;
    reg write_enable;
    reg read_enable;
    reg clk;
    reg reset;
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
        .reset(reset),
        .data_out(data_out),
        .valid_out(valid_out)
    );

    always #5 clk = ~clk;

    initial begin
        // Initialize
        clk = 0;
        reset = 1;
        write_enable = 0;
        read_enable = 0;
        data_in = 0;
        adress = 0;

        #10;
        reset = 0;

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
        #10;
        // Check output
        if (data_out === 32'hAAAA && valid_out === 1) 
            $display("PASS: Read Addr 2 = %h, Valid=1", data_out);
        else 
            $display("FAIL: Read Addr 2 = %h (Exp: AAAA), Valid=%b", data_out, valid_out);

        // Read address 3
        adress = 4'd3;
        #10;
        if (data_out === 32'hBBBB && valid_out === 1) 
            $display("PASS: Read Addr 3 = %h, Valid=1", data_out);
        else 
            $display("FAIL: Read Addr 3 = %h (Exp: BBBB), Valid=%b", data_out, valid_out);

        // Stop Read
        read_enable = 0;
        #10;
        if (valid_out === 0)
            $display("PASS: Valid dropped to 0");
        else
            $display("FAIL: Valid did not drop, val=%b", valid_out);

        $finish;
    end

endmodule
