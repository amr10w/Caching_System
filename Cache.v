`timescale 1ns/1ps

module Cache
#(
  // Cache parameters
  parameter SIZE = 32*1024*8,
  parameter NWAYS = 4,
  parameter NSETS = 1024,
  parameter BLOCK_SIZE = 64,
  parameter WIDTH = 32,
  // Memory related parameter, make sure it matches memory module
  parameter MWIDTH = 64,  // same as block size
  // More cache related parameters
  parameter INDEX_WIDTH = 10,
  parameter TAG_WIDTH = 19,
  parameter OFFSET_WIDTH = 3,
  parameter WORD1 = 3,
  parameter WORD2 = 7
)
(
  input  wire                      clk,          // renamed from clock
  input  wire                      reset_n,      // active low reset
  input  wire [WIDTH-1:0]          address,    // address form CPU
  input  wire [WIDTH-1:0]          din,        // data from CPU (if st inst)
  input  wire                      rden,       // 1 if ld instruction
  input  wire                      wren,       // 1 if st instruction
  output wire                      hit_miss,   // 1 if hit, 0 while handling miss
  output wire [WIDTH-1:0]          q,          // data from cache to CPU
  
  // Memory Interface
  output wire [MWIDTH-1:0]         mdout,      // data from cache to memory
  output wire [WIDTH-1:0]          mrdaddress, // memory read address
  output wire                      mrden,      // read enable, 1 if reading from memory
  output wire [WIDTH-1:0]          mwraddress, // memory write address
  output wire                      mwren,      // write enable, 1 if writing to memory
  input  wire [MWIDTH-1:0]         mq          // data coming from memory
);

  // Address Decoding Parameters
  localparam OFFSET_HIGH = OFFSET_WIDTH - 1;
  localparam OFFSET_LOW = 0;
  localparam INDEX_HIGH = INDEX_WIDTH + OFFSET_WIDTH - 1;
  localparam INDEX_LOW = OFFSET_WIDTH;
  localparam TAG_HIGH = WIDTH - 1;
  localparam TAG_LOW = INDEX_WIDTH + OFFSET_WIDTH;


/*******************************************************************
* Global Parameters and Initializations
*******************************************************************/

// WAY 1 cache data
reg                 valid1 [0:NSETS-1];
reg                 dirty1 [0:NSETS-1];
reg [1:0]           lru1   [0:NSETS-1];
reg [TAG_WIDTH-1:0] tag1   [0:NSETS-1];
reg [MWIDTH-1:0]    mem1   [0:NSETS-1] /* synthesis ramstyle = "M20K" */;

// WAY 2 cache data
reg                 valid2 [0:NSETS-1];
reg                 dirty2 [0:NSETS-1];
reg [1:0]           lru2   [0:NSETS-1];
reg [TAG_WIDTH-1:0] tag2   [0:NSETS-1];
reg [MWIDTH-1:0]    mem2   [0:NSETS-1] /* synthesis ramstyle = "M20K" */;

// WAY 3 cache data
reg                 valid3 [0:NSETS-1];
reg                 dirty3 [0:NSETS-1];
reg [1:0]           lru3   [0:NSETS-1];
reg [TAG_WIDTH-1:0] tag3   [0:NSETS-1];
reg [MWIDTH-1:0]    mem3   [0:NSETS-1] /* synthesis ramstyle = "M20K" */;

// WAY 4 cache data
reg                 valid4 [0:NSETS-1];
reg                 dirty4 [0:NSETS-1];
reg [1:0]           lru4   [0:NSETS-1];
reg [TAG_WIDTH-1:0] tag4   [0:NSETS-1];
reg [MWIDTH-1:0]    mem4   [0:NSETS-1] /* synthesis ramstyle = "M20K" */;

// Write Buffer
reg [MWIDTH-1:0] wbuffer_data;
reg [WIDTH-1:0]  wbuffer_addr; // Full address (Tag+Index)

// initialize the cache to zero
integer k;
initial
begin
    for(k = 0; k < NSETS; k = k +1)
    begin
        valid1[k] = 0;
        valid2[k] = 0;
        valid3[k] = 0;
        valid4[k] = 0;
        dirty1[k] = 0;
        dirty2[k] = 0;
        dirty3[k] = 0;
        dirty4[k] = 0;
        lru1[k] = 2'b00;
        lru2[k] = 2'b00;
        lru3[k] = 2'b00;
        lru4[k] = 2'b00;
    end
    wbuffer_data = 0;
    wbuffer_addr = 0;
end

// internal registers
reg              _hit_miss = 1'b0;
reg [WIDTH-1:0]  _q = {WIDTH{1'b0}};
reg [MWIDTH-1:0] _mdout = {MWIDTH{1'b0}};
reg [WIDTH-1:0]  _mwraddress = {WIDTH{1'b0}};
reg [WIDTH-1:0]  _mrdaddress = {WIDTH{1'b0}};
reg              _mwren = 1'b0;
reg              _mrden = 1'b0;
reg [MWIDTH-1:0] new_block; // FIX: Added declaration for new_block

// output assignments of internal registers
assign hit_miss = _hit_miss;
assign mwren = _mwren;
assign mdout = _mdout;
assign mwraddress = _mwraddress;
assign mrden = _mrden;
assign mrdaddress = _mrdaddress;
assign q = _q;

// state parameters
localparam IDLE       = 3'b000;
localparam MISS       = 3'b001; // Processing miss (checking victim)
localparam WRITE_BACK = 3'b010; // Writing dirty line to memory
localparam FETCH      = 3'b011; // Fetching new line from memory (sending read)
localparam FETCH_WAIT = 3'b100; // Wait for RAM latency
localparam REFILL     = 3'b101; // Capturing memory data and updating cache

// state register
reg [2:0] currentState = IDLE;

// Helper variables for FSM
reg [1:0] victim_way;

/*******************************************************************
* State Machine
*******************************************************************/

always @(posedge clk or negedge reset_n)
begin   
    if (!reset_n) begin
        currentState <= IDLE;
        _mwren <= 0;
        _mrden <= 0;
        _hit_miss <= 0;
    end
    else begin
        case (currentState)
            IDLE: begin
                _mwren <= 0;
                _mrden <= 0;
                
                // Do nothing if no request
                if (!rden && !wren) begin
                   _hit_miss <= 0; 
                end
                
                // Check Hit
                else if (valid1[address[INDEX_HIGH:INDEX_LOW]] && (tag1[address[INDEX_HIGH:INDEX_LOW]] == address[TAG_HIGH:TAG_LOW])) begin
                    // ---- WAY 1 HIT ----
                    _hit_miss <= 1;
                    if (rden) begin
                        _q <= (address[OFFSET_HIGH:OFFSET_LOW] <= WORD1) ? mem1[address[INDEX_HIGH:INDEX_LOW]][WIDTH-1:0] : mem1[address[INDEX_HIGH:INDEX_LOW]][2*WIDTH-1:WIDTH];
                    end else if (wren) begin
                        dirty1[address[INDEX_HIGH:INDEX_LOW]] <= 1;
                        if (address[OFFSET_HIGH:OFFSET_LOW] <= WORD1) mem1[address[INDEX_HIGH:INDEX_LOW]][WIDTH-1:0] <= din;
                        else mem1[address[INDEX_HIGH:INDEX_LOW]][2*WIDTH-1:WIDTH] <= din;
                    end
                    // Update LRU
                    if (lru2[address[INDEX_HIGH:INDEX_LOW]] <= lru1[address[INDEX_HIGH:INDEX_LOW]]) lru2[address[INDEX_HIGH:INDEX_LOW]] <= lru2[address[INDEX_HIGH:INDEX_LOW]] + 1;
                    if (lru3[address[INDEX_HIGH:INDEX_LOW]] <= lru1[address[INDEX_HIGH:INDEX_LOW]]) lru3[address[INDEX_HIGH:INDEX_LOW]] <= lru3[address[INDEX_HIGH:INDEX_LOW]] + 1;
                    if (lru4[address[INDEX_HIGH:INDEX_LOW]] <= lru1[address[INDEX_HIGH:INDEX_LOW]]) lru4[address[INDEX_HIGH:INDEX_LOW]] <= lru4[address[INDEX_HIGH:INDEX_LOW]] + 1;
                    lru1[address[INDEX_HIGH:INDEX_LOW]] <= 0;
                end
                else if (valid2[address[INDEX_HIGH:INDEX_LOW]] && (tag2[address[INDEX_HIGH:INDEX_LOW]] == address[TAG_HIGH:TAG_LOW])) begin
                    // ---- WAY 2 HIT ----
                    _hit_miss <= 1;
                    if (rden) begin
                        _q <= (address[OFFSET_HIGH:OFFSET_LOW] <= WORD1) ? mem2[address[INDEX_HIGH:INDEX_LOW]][WIDTH-1:0] : mem2[address[INDEX_HIGH:INDEX_LOW]][2*WIDTH-1:WIDTH];
                    end else if (wren) begin
                        dirty2[address[INDEX_HIGH:INDEX_LOW]] <= 1;
                        if (address[OFFSET_HIGH:OFFSET_LOW] <= WORD1) mem2[address[INDEX_HIGH:INDEX_LOW]][WIDTH-1:0] <= din;
                        else mem2[address[INDEX_HIGH:INDEX_LOW]][2*WIDTH-1:WIDTH] <= din;
                    end
                    // Update LRU
                    if (lru1[address[INDEX_HIGH:INDEX_LOW]] <= lru2[address[INDEX_HIGH:INDEX_LOW]]) lru1[address[INDEX_HIGH:INDEX_LOW]] <= lru1[address[INDEX_HIGH:INDEX_LOW]] + 1;
                    if (lru3[address[INDEX_HIGH:INDEX_LOW]] <= lru2[address[INDEX_HIGH:INDEX_LOW]]) lru3[address[INDEX_HIGH:INDEX_LOW]] <= lru3[address[INDEX_HIGH:INDEX_LOW]] + 1;
                    if (lru4[address[INDEX_HIGH:INDEX_LOW]] <= lru2[address[INDEX_HIGH:INDEX_LOW]]) lru4[address[INDEX_HIGH:INDEX_LOW]] <= lru4[address[INDEX_HIGH:INDEX_LOW]] + 1;
                    lru2[address[INDEX_HIGH:INDEX_LOW]] <= 0;
                end
                else if (valid3[address[INDEX_HIGH:INDEX_LOW]] && (tag3[address[INDEX_HIGH:INDEX_LOW]] == address[TAG_HIGH:TAG_LOW])) begin
                    // ---- WAY 3 HIT ----
                    _hit_miss <= 1;
                    if (rden) begin
                        _q <= (address[OFFSET_HIGH:OFFSET_LOW] <= WORD1) ? mem3[address[INDEX_HIGH:INDEX_LOW]][WIDTH-1:0] : mem3[address[INDEX_HIGH:INDEX_LOW]][2*WIDTH-1:WIDTH];
                    end else if (wren) begin
                        dirty3[address[INDEX_HIGH:INDEX_LOW]] <= 1;
                        if (address[OFFSET_HIGH:OFFSET_LOW] <= WORD1) mem3[address[INDEX_HIGH:INDEX_LOW]][WIDTH-1:0] <= din;
                        else mem3[address[INDEX_HIGH:INDEX_LOW]][2*WIDTH-1:WIDTH] <= din;
                    end
                    // Update LRU
                    if (lru1[address[INDEX_HIGH:INDEX_LOW]] <= lru3[address[INDEX_HIGH:INDEX_LOW]]) lru1[address[INDEX_HIGH:INDEX_LOW]] <= lru1[address[INDEX_HIGH:INDEX_LOW]] + 1;
                    if (lru2[address[INDEX_HIGH:INDEX_LOW]] <= lru3[address[INDEX_HIGH:INDEX_LOW]]) lru2[address[INDEX_HIGH:INDEX_LOW]] <= lru2[address[INDEX_HIGH:INDEX_LOW]] + 1;
                    if (lru4[address[INDEX_HIGH:INDEX_LOW]] <= lru3[address[INDEX_HIGH:INDEX_LOW]]) lru4[address[INDEX_HIGH:INDEX_LOW]] <= lru4[address[INDEX_HIGH:INDEX_LOW]] + 1;
                    lru3[address[INDEX_HIGH:INDEX_LOW]] <= 0;
                end
                else if (valid4[address[INDEX_HIGH:INDEX_LOW]] && (tag4[address[INDEX_HIGH:INDEX_LOW]] == address[TAG_HIGH:TAG_LOW])) begin
                    // ---- WAY 4 HIT ----
                    _hit_miss <= 1;
                    if (rden) begin
                        _q <= (address[OFFSET_HIGH:OFFSET_LOW] <= WORD1) ? mem4[address[INDEX_HIGH:INDEX_LOW]][WIDTH-1:0] : mem4[address[INDEX_HIGH:INDEX_LOW]][2*WIDTH-1:WIDTH];
                    end else if (wren) begin
                        dirty4[address[INDEX_HIGH:INDEX_LOW]] <= 1;
                        if (address[OFFSET_HIGH:OFFSET_LOW] <= WORD1) mem4[address[INDEX_HIGH:INDEX_LOW]][WIDTH-1:0] <= din;
                        else mem4[address[INDEX_HIGH:INDEX_LOW]][2*WIDTH-1:WIDTH] <= din;
                    end
                    // Update LRU
                    if (lru1[address[INDEX_HIGH:INDEX_LOW]] <= lru4[address[INDEX_HIGH:INDEX_LOW]]) lru1[address[INDEX_HIGH:INDEX_LOW]] <= lru1[address[INDEX_HIGH:INDEX_LOW]] + 1;
                    if (lru2[address[INDEX_HIGH:INDEX_LOW]] <= lru4[address[INDEX_HIGH:INDEX_LOW]]) lru2[address[INDEX_HIGH:INDEX_LOW]] <= lru2[address[INDEX_HIGH:INDEX_LOW]] + 1;
                    if (lru3[address[INDEX_HIGH:INDEX_LOW]] <= lru4[address[INDEX_HIGH:INDEX_LOW]]) lru3[address[INDEX_HIGH:INDEX_LOW]] <= lru3[address[INDEX_HIGH:INDEX_LOW]] + 1;
                    lru4[address[INDEX_HIGH:INDEX_LOW]] <= 0;
                end
                else begin
                    // ---- MISS ----
                    _hit_miss <= 0;
                    currentState <= MISS;
                end
            end
        
            MISS: begin
                // Check if any way is invalid (Empty)
                if (!valid1[address[INDEX_HIGH:INDEX_LOW]]) begin
                    victim_way <= 2'b00; 
                    currentState <= FETCH;
                end
                else if (!valid2[address[INDEX_HIGH:INDEX_LOW]]) begin
                    victim_way <= 2'b01;
                    currentState <= FETCH;
                end
                else if (!valid3[address[INDEX_HIGH:INDEX_LOW]]) begin
                    victim_way <= 2'b10;
                    currentState <= FETCH;
                end
                else if (!valid4[address[INDEX_HIGH:INDEX_LOW]]) begin
                    victim_way <= 2'b11;
                    currentState <= FETCH;
                end
                // If all valid, Check LRU and Dirty Status
                else begin
                    // LRU is Way 1
                    if (lru1[address[INDEX_HIGH:INDEX_LOW]] == 3) begin
                        victim_way <= 2'b00;
                        if (dirty1[address[INDEX_HIGH:INDEX_LOW]]) begin
                            wbuffer_data <= mem1[address[INDEX_HIGH:INDEX_LOW]];
                            wbuffer_addr <= {tag1[address[INDEX_HIGH:INDEX_LOW]], address[INDEX_HIGH:INDEX_LOW], {OFFSET_WIDTH{1'b0}}}; 
                            currentState <= WRITE_BACK;
                        end else currentState <= FETCH;
                    end
                    // LRU is Way 2
                    else if (lru2[address[INDEX_HIGH:INDEX_LOW]] == 3) begin
                        victim_way <= 2'b01;
                        if (dirty2[address[INDEX_HIGH:INDEX_LOW]]) begin
                            wbuffer_data <= mem2[address[INDEX_HIGH:INDEX_LOW]];
                            wbuffer_addr <= {tag2[address[INDEX_HIGH:INDEX_LOW]], address[INDEX_HIGH:INDEX_LOW], {OFFSET_WIDTH{1'b0}}};
                            currentState <= WRITE_BACK;
                        end else currentState <= FETCH;
                    end
                    // LRU is Way 3
                    else if (lru3[address[INDEX_HIGH:INDEX_LOW]] == 3) begin
                        victim_way <= 2'b10;
                        if (dirty3[address[INDEX_HIGH:INDEX_LOW]]) begin
                            wbuffer_data <= mem3[address[INDEX_HIGH:INDEX_LOW]];
                            wbuffer_addr <= {tag3[address[INDEX_HIGH:INDEX_LOW]], address[INDEX_HIGH:INDEX_LOW], {OFFSET_WIDTH{1'b0}}};
                            currentState <= WRITE_BACK;
                        end else currentState <= FETCH;
                    end
                    // LRU is Way 4
                    else begin
                        victim_way <= 2'b11;
                        if (dirty4[address[INDEX_HIGH:INDEX_LOW]]) begin
                            wbuffer_data <= mem4[address[INDEX_HIGH:INDEX_LOW]];
                            wbuffer_addr <= {tag4[address[INDEX_HIGH:INDEX_LOW]], address[INDEX_HIGH:INDEX_LOW], {OFFSET_WIDTH{1'b0}}};
                            currentState <= WRITE_BACK;
                        end else currentState <= FETCH;
                    end
                end
            end

            WRITE_BACK: begin
                _mwren <= 1;
                _mwraddress <= wbuffer_addr;
                _mdout <= wbuffer_data;
                currentState <= FETCH;
            end

            FETCH: begin
                _mwren <= 0; 
                _mrden <= 1;
                _mrdaddress <= {address[TAG_HIGH:TAG_LOW], address[INDEX_HIGH:INDEX_LOW], {OFFSET_WIDTH{1'b0}}};
                currentState <= FETCH_WAIT;
            end
            
            FETCH_WAIT: begin
                _mrden <= 0; // Deassert read enable
                currentState <= REFILL;
            end
            
            REFILL: begin
                _mrden <= 0;
                
                new_block = mq; // From memory
                
                if (wren) begin
                    if (address[OFFSET_HIGH:OFFSET_LOW] <= WORD1) new_block[WIDTH-1:0] = din;
                    else new_block[2*WIDTH-1:WIDTH] = din;
                end
                
                case (victim_way)
                    2'b00: begin // Way 1
                        mem1[address[INDEX_HIGH:INDEX_LOW]] <= new_block;
                        tag1[address[INDEX_HIGH:INDEX_LOW]] <= address[TAG_HIGH:TAG_LOW];
                        valid1[address[INDEX_HIGH:INDEX_LOW]] <= 1;
                        dirty1[address[INDEX_HIGH:INDEX_LOW]] <= wren; 
                    end
                    2'b01: begin // Way 2
                        mem2[address[INDEX_HIGH:INDEX_LOW]] <= new_block;
                        tag2[address[INDEX_HIGH:INDEX_LOW]] <= address[TAG_HIGH:TAG_LOW];
                        valid2[address[INDEX_HIGH:INDEX_LOW]] <= 1;
                        dirty2[address[INDEX_HIGH:INDEX_LOW]] <= wren;
                    end
                    2'b10: begin // Way 3
                        mem3[address[INDEX_HIGH:INDEX_LOW]] <= new_block;
                        tag3[address[INDEX_HIGH:INDEX_LOW]] <= address[TAG_HIGH:TAG_LOW];
                        valid3[address[INDEX_HIGH:INDEX_LOW]] <= 1;
                        dirty3[address[INDEX_HIGH:INDEX_LOW]] <= wren;
                    end
                    2'b11: begin // Way 4
                        mem4[address[INDEX_HIGH:INDEX_LOW]] <= new_block;
                        tag4[address[INDEX_HIGH:INDEX_LOW]] <= address[TAG_HIGH:TAG_LOW];
                        valid4[address[INDEX_HIGH:INDEX_LOW]] <= 1;
                        dirty4[address[INDEX_HIGH:INDEX_LOW]] <= wren;
                    end
                endcase
                
                currentState <= IDLE;
            end
        endcase
    end
end

endmodule