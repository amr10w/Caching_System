module Ram #(
    parameter WIDTH = 32,
    parameter DEPTH = 4 
)(
    input wire [WIDTH-1:0] data_in,
    input wire [DEPTH-1:0] adress,
    input wire write_enable,
    input wire read_enable,
    input wire clk,
    input wire reset,
    output reg [WIDTH-1:0] data_out,
    output reg valid_out
);

    
    localparam DEPTH_MEM = 1 << DEPTH;

    reg [WIDTH-1:0] mem [0:DEPTH_MEM-1];

    integer i;
    initial begin
        for (i = 0; i < DEPTH_MEM; i=i+1) begin
            mem[i] <= 0;
        end
    end

    integer k;
    always @(posedge clk) begin
        if (reset) begin
            data_out <= 0;
            valid_out <= 1'b0;
            for (k = 0; k < DEPTH_MEM; k=k+1) begin
                mem[k] <= 0;
            end
        end
        else begin
            valid_out <= 1'b0;
            if (write_enable) begin
                mem[adress] <= data_in;
            end
            
            if (read_enable) begin
                data_out <= mem[adress];
                valid_out <= 1'b1;
            end 
        end
    end

endmodule