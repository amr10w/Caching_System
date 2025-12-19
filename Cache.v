module Cache #(
    parameter data_width = 32,
    parameter address_width = 16,
    parameter block_offset = 2,
    parameter index_bits = address_width - block_offset-2,
    parameter tag_bits = address_width - block_offset - index_bits-2
)(
    input wire [address_width-1:0] address,
    input wire [data_width-1:0] data_in,
    input wire write_enable,
    input wire read_enable,
    input wire clk,
    input wire reset_n,
    output reg [data_width-1:0] data_out,    
    output reg hit_out

);

    localparam index_width = 1<<index_bits;
    
    // WAY 1
    reg                     valid_1 [0:index_width-1];
    reg                     dirty_1 [0:index_width-1];
    reg [1:0]               LRU_1   [0:index_width-1];
    reg [tag_bits-1:0]      tag_1   [0:index_width-1];
    reg [data_width-1:0]    data_1  [0:index_width-1];
    
    // WAY 2
    reg                     valid_2 [0:index_width-1];
    reg                     dirty_2 [0:index_width-1];
    reg [1:0]               LRU_2   [0:index_width-1];
    reg [tag_bits-1:0]      tag_2   [0:index_width-1];
    reg [data_width-1:0]    data_2  [0:index_width-1];
    
    // WAY 3
    reg                     valid_3 [0:index_width-1];
    reg                     dirty_3 [0:index_width-1];
    reg [1:0]               LRU_3   [0:index_width-1];
    reg [tag_bits-1:0]      tag_3   [0:index_width-1];
    reg [data_width-1:0]    data_3  [0:index_width-1];
    
    // WAY 4
    reg                     valid_4 [0:index_width-1];
    reg                     dirty_4 [0:index_width-1];
    reg [1:0]               LRU_4   [0:index_width-1];
    reg [tag_bits-1:0]      tag_4   [0:index_width-1];
    reg [data_width-1:0]    data_4  [0:index_width-1];

    integer k;
    initial begin
        data_out <= 0;
        hit_out <= 1'b0;
        for (k = 0; k < index_width; k++) begin
            valid_1[k] <= 1'b0;
            dirty_1[k] <= 1'b0;
            LRU_1[k] <= 2'b00;
            tag_1[k] <= 0;
            data_1[k] <= 0;
            valid_2[k] <= 1'b0;
            dirty_2[k] <= 1'b0;
            LRU_2[k] <= 2'b00;
            tag_2[k] <= 0;
            data_2[k] <= 0;
            valid_3[k] <= 1'b0;
            dirty_3[k] <= 1'b0;
            LRU_3[k] <= 2'b00;
            tag_3[k] <= 0;
            data_3[k] <= 0;
            valid_4[k] <= 1'b0;
            dirty_4[k] <= 1'b0;
            LRU_4[k] <= 2'b00;
            tag_4[k] <= 0;
            data_4[k] <= 0;
        end
    end

    

endmodule