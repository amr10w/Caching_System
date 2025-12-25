`timescale 1ns/1ps

module Ram #(
    parameter WIDTH = 32,
    parameter DEPTH = 16 
)(
    input wire clk,
    input wire reset_n,
    input wire [WIDTH-1:0] data_in,
    input wire [DEPTH-1:0] adress,
    input wire write_enable,
    input wire read_enable,
    output reg [WIDTH-1:0] data_out,
    output reg valid_out
);

    localparam DEPTH_MEM = 1 << DEPTH;
    reg [WIDTH-1:0] mem [0:DEPTH_MEM-1];

    integer k;
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            data_out <= 0;
            valid_out <= 0;
            for (k = 0; k < DEPTH_MEM; k = k + 1) begin
                mem[k] <= 0;
            end
        end
        else begin
            valid_out <= 0;
            if (write_enable) begin
                mem[adress] <= data_in;
            end
            if (read_enable) begin
                data_out <= mem[adress];
                valid_out <= 1;
            end
        end
    end
endmodule

module Cache_Controller (
    input wire clk,
    input wire reset_n,
    
    input wire rden,
    input wire wren,
    input wire hit,         
    input wire dirty_victim,
    
    output reg hit_miss, 
    output reg update_lru,        
    output reg update_cache,      
    output reg write_back_en,     
    
    // Memory Interface Logic
    output reg mem_mrden,
    output reg mem_mwren
);

    localparam IDLE       = 3'b000;
    localparam MISS       = 3'b001;
    localparam WRITE_BACK = 3'b010;
    localparam FETCH      = 3'b011;
    localparam FETCH_WAIT = 3'b100;
    localparam REFILL     = 3'b101;

    reg [2:0] current_state, next_state;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) current_state <= IDLE;
        else current_state <= next_state;
    end

    always @(*) begin
        hit_miss = 1'b0;
        mem_mrden = 1'b0;
        mem_mwren = 1'b0;
        update_lru = 1'b0;
        update_cache = 1'b0;
        write_back_en = 1'b0;
        next_state = current_state;

        case (current_state)
            IDLE: begin
                if (rden || wren) begin
                    if (hit) begin
                        hit_miss = 1'b1;
                        update_lru = 1'b1; 
                    end else begin
                        hit_miss = 1'b0;
                        next_state = MISS;
                    end
                end 
            end

            MISS: begin
                if (dirty_victim) begin
                    next_state = WRITE_BACK;
                end else begin
                    next_state = FETCH;
                end
            end

            WRITE_BACK: begin
                mem_mwren = 1'b1; 
                write_back_en = 1'b1; 
                next_state = FETCH; 
            end

            FETCH: begin
                mem_mrden = 1'b1; 
                next_state = FETCH_WAIT;
            end

            FETCH_WAIT: begin
                mem_mrden = 1'b0;
                next_state = REFILL;
            end

            REFILL: begin
                update_cache = 1'b1; 
                update_lru = 1'b1;   
                next_state = IDLE;   
            end
            
            default: next_state = IDLE;
        endcase
    end
endmodule

module Cache #(
    parameter SIZE = 32*1024*8,
    parameter NWAYS = 4,
    parameter NSETS = 64,       
    parameter BLOCK_SIZE = 32,  
    parameter WIDTH = 32,
    parameter MWIDTH = 32,      
    parameter INDEX_WIDTH = 6,
    parameter TAG_WIDTH = 8,
    parameter OFFSET_WIDTH = 3 
)(
    input  wire                      clk,
    input  wire                      reset_n,
    input  wire [WIDTH-1:0]          address,
    input  wire [WIDTH-1:0]          din,
    input  wire                      rden,
    input  wire                      wren,
    output wire                      hit_miss,
    output reg  [WIDTH-1:0]          q,
    
    output reg  [MWIDTH-1:0]         mdout,
    output reg  [WIDTH-1:0]          mrdaddress,
    output wire                      mrden,
    output reg  [WIDTH-1:0]          mwraddress,
    output wire                      mwren,
    input  wire [MWIDTH-1:0]         mq
);

    // Explicit 4-Way Arrays
    reg                 valid1 [0:NSETS-1];
    reg                 valid2 [0:NSETS-1];
    reg                 valid3 [0:NSETS-1];
    reg                 valid4 [0:NSETS-1];

    reg                 dirty1 [0:NSETS-1];
    reg                 dirty2 [0:NSETS-1];
    reg                 dirty3 [0:NSETS-1];
    reg                 dirty4 [0:NSETS-1];

    reg [TAG_WIDTH-1:0] tag1   [0:NSETS-1];
    reg [TAG_WIDTH-1:0] tag2   [0:NSETS-1];
    reg [TAG_WIDTH-1:0] tag3   [0:NSETS-1];
    reg [TAG_WIDTH-1:0] tag4   [0:NSETS-1];

    reg [MWIDTH-1:0]    mem1   [0:NSETS-1];
    reg [MWIDTH-1:0]    mem2   [0:NSETS-1];
    reg [MWIDTH-1:0]    mem3   [0:NSETS-1];
    reg [MWIDTH-1:0]    mem4   [0:NSETS-1];

    reg [1:0]           lru1   [0:NSETS-1];
    reg [1:0]           lru2   [0:NSETS-1];
    reg [1:0]           lru3   [0:NSETS-1];
    reg [1:0]           lru4   [0:NSETS-1];

    wire [INDEX_WIDTH-1:0] set_index = address[INDEX_WIDTH+OFFSET_WIDTH-1 : OFFSET_WIDTH];
    wire [TAG_WIDTH-1:0]   tag_in    = address[TAG_WIDTH+INDEX_WIDTH+OFFSET_WIDTH-1 : INDEX_WIDTH+OFFSET_WIDTH];
    
    // Logic
    wire hit1 = valid1[set_index] && (tag1[set_index] == tag_in);
    wire hit2 = valid2[set_index] && (tag2[set_index] == tag_in);
    wire hit3 = valid3[set_index] && (tag3[set_index] == tag_in);
    wire hit4 = valid4[set_index] && (tag4[set_index] == tag_in);
    
    wire any_hit = hit1 || hit2 || hit3 || hit4;
    
    reg [1:0] hit_way_idx;
    always @(*) begin
        if (hit1) hit_way_idx = 0;
        else if (hit2) hit_way_idx = 1;
        else if (hit3) hit_way_idx = 2;
        else hit_way_idx = 3; 
    end

    // Victim Selection: Way with lru value 3 (LRU)
    // 0=MRU, 3=LRU
    reg [1:0] victim_way_idx;
    always @(*) begin
        if (lru1[set_index] == 3) victim_way_idx = 0;
        else if (lru2[set_index] == 3) victim_way_idx = 1;
        else if (lru3[set_index] == 3) victim_way_idx = 2;
        else victim_way_idx = 3;
    end

    // Muxing
    always @(*) begin
        case(hit_way_idx)
            0: q = mem1[set_index];
            1: q = mem2[set_index];
            2: q = mem3[set_index];
            3: q = mem4[set_index];
        endcase
    end
    
    wire update_lru, update_cache, write_back_en;
    wire dirty_victim_bit;
    assign dirty_victim_bit = (victim_way_idx==0) ? dirty1[set_index] : 
                              (victim_way_idx==1) ? dirty2[set_index] :
                              (victim_way_idx==2) ? dirty3[set_index] : dirty4[set_index];

    Cache_Controller controller (
        .clk(clk),
        .reset_n(reset_n),
        .rden(rden),
        .wren(wren),
        .hit(any_hit),
        .dirty_victim(dirty_victim_bit),
        .hit_miss(hit_miss),
        .update_lru(update_lru),
        .update_cache(update_cache),
        .write_back_en(write_back_en),
        .mem_mrden(mrden),
        .mem_mwren(mwren)
    );

    always @(*) begin
        if (write_back_en) begin
            case(victim_way_idx) 
                0: begin mwraddress = {tag1[set_index], set_index, {OFFSET_WIDTH{1'b0}}}; mdout = mem1[set_index]; end
                1: begin mwraddress = {tag2[set_index], set_index, {OFFSET_WIDTH{1'b0}}}; mdout = mem2[set_index]; end
                2: begin mwraddress = {tag3[set_index], set_index, {OFFSET_WIDTH{1'b0}}}; mdout = mem3[set_index]; end
                3: begin mwraddress = {tag4[set_index], set_index, {OFFSET_WIDTH{1'b0}}}; mdout = mem4[set_index]; end
            endcase
        end else begin
            mwraddress = 0; 
            mdout = 0;
        end
        mrdaddress = {tag_in, set_index, {OFFSET_WIDTH{1'b0}}};
    end

    integer j;
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            for (j=0; j<NSETS; j=j+1) begin
                valid1[j] <= 0; valid2[j] <= 0; valid3[j] <= 0; valid4[j] <= 0;
                dirty1[j] <= 0; dirty2[j] <= 0; dirty3[j] <= 0; dirty4[j] <= 0;
                tag1[j]   <= 0; tag2[j]   <= 0; tag3[j]   <= 0; tag4[j]   <= 0;
                mem1[j]   <= 0; mem2[j]   <= 0; mem3[j]   <= 0; mem4[j]   <= 0;
                // LRU Reset: 0, 1, 2, 3
                lru1[j] <= 2'd0;
                lru2[j] <= 2'd1;
                lru3[j] <= 2'd2;
                lru4[j] <= 2'd3;
            end
        end 
        else begin
            // Write Hit Logic
            if (any_hit && wren) begin
                if (hit1) begin mem1[set_index] <= din; dirty1[set_index] <= 1; end
                if (hit2) begin mem2[set_index] <= din; dirty2[set_index] <= 1; end
                if (hit3) begin mem3[set_index] <= din; dirty3[set_index] <= 1; end
                if (hit4) begin mem4[set_index] <= din; dirty4[set_index] <= 1; end
            end
            
            // Refill Logic
            if (update_cache) begin
               case(victim_way_idx)
                   0: begin mem1[set_index] <= (wren) ? din : mq; tag1[set_index] <= tag_in; valid1[set_index] <= 1; dirty1[set_index] <= wren; end
                   1: begin mem2[set_index] <= (wren) ? din : mq; tag2[set_index] <= tag_in; valid2[set_index] <= 1; dirty2[set_index] <= wren; end
                   2: begin mem3[set_index] <= (wren) ? din : mq; tag3[set_index] <= tag_in; valid3[set_index] <= 1; dirty3[set_index] <= wren; end
                   3: begin mem4[set_index] <= (wren) ? din : mq; tag4[set_index] <= tag_in; valid4[set_index] <= 1; dirty4[set_index] <= wren; end
               endcase
            end

            // LRU Update Logic
             if (update_lru) begin
                 if (any_hit) begin
                     // hit_way becomes 0. Others < hit_lru increment.
                     // We need the current lru values to compare.
                     // Assuming synchronous update of all at once.
                     
                     // Way 1 Update
                     if (hit1) lru1[set_index] <= 0;
                     else if (lru1[set_index] < (hit1?lru1[set_index]:(hit2?lru2[set_index]:(hit3?lru3[set_index]:lru4[set_index]))))
                        lru1[set_index] <= lru1[set_index] + 1;
                        
                     // Way 2 Update
                     if (hit2) lru2[set_index] <= 0;
                     else if (lru2[set_index] < (hit1?lru1[set_index]:(hit2?lru2[set_index]:(hit3?lru3[set_index]:lru4[set_index]))))
                        lru2[set_index] <= lru2[set_index] + 1;

                     // Way 3 Update
                     if (hit3) lru3[set_index] <= 0;
                     else if (lru3[set_index] < (hit1?lru1[set_index]:(hit2?lru2[set_index]:(hit3?lru3[set_index]:lru4[set_index]))))
                        lru3[set_index] <= lru3[set_index] + 1;

                     // Way 4 Update
                     if (hit4) lru4[set_index] <= 0;
                     else if (lru4[set_index] < (hit1?lru1[set_index]:(hit2?lru2[set_index]:(hit3?lru3[set_index]:lru4[set_index]))))
                        lru4[set_index] <= lru4[set_index] + 1;
                 end
                 else if (update_cache) begin
                     // Victim (LRU=3) becomes 0. Others increment.
                     // Way 1
                     if (victim_way_idx == 0) lru1[set_index] <= 0;
                     else lru1[set_index] <= lru1[set_index] + 1;
                     
                     // Way 2
                     if (victim_way_idx == 1) lru2[set_index] <= 0;
                     else lru2[set_index] <= lru2[set_index] + 1;

                     // Way 3
                     if (victim_way_idx == 2) lru3[set_index] <= 0;
                     else lru3[set_index] <= lru3[set_index] + 1;

                     // Way 4
                     if (victim_way_idx == 3) lru4[set_index] <= 0;
                     else lru4[set_index] <= lru4[set_index] + 1;
                 end
             end
        end
    end

endmodule