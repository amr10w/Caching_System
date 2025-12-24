`timescale 1ns/1ps

module tb_cache_system;

    // Parameters
    parameter WIDTH = 32;
    parameter MWIDTH = 32; // Block size
    parameter ADDR_WIDTH = 16; // As per test requirement (approx)
                               // Cache default is 32-bit address, but test uses 16.
                               // We need to map 16 to Cache.v's expected width if necessary.
                               // Cache.v defaults to WIDTH=32 for address?
                               // Let's override Cache parameters.
    
    // Signals
    reg clk;
    reg reset_n;
    reg [ADDR_WIDTH-1:0] address;
    reg [WIDTH-1:0] din;
    reg wren;
    reg rden;
    
    wire [WIDTH-1:0] q;
    wire hit_miss;
    
    // RAM Interface Signals form Cache
    wire [MWIDTH-1:0] mdout;
    wire [ADDR_WIDTH-1:0]  mrdaddress;
    wire              mrden;
    wire [ADDR_WIDTH-1:0]  mwraddress;
    wire              mwren;
    wire [MWIDTH-1:0] mq; // Input to Cache (from RAM)

    // Signals for RAM Module
    wire [MWIDTH-1:0] ram_data_in;
    wire [ADDR_WIDTH-1:0] ram_address; // RAM depth is parameterized, likely 16 bits
    wire ram_write_enable;
    wire ram_read_enable;
    wire [MWIDTH-1:0] ram_data_out;
    wire ram_valid_out;

    // Cache Instance
    // Note: Cache default ADDR width is WIDTH=32. We can drive it with 32.
    // RAM we will make it 2^16 depth = 16 bit address.
    // We need to connect Cache (32b addr) to Ram (16b addr). Truncate.
    
    Cache #(
        .WIDTH(WIDTH),
        .MWIDTH(MWIDTH),
      .NSETS(64),     
        .NWAYS(4),
      .BLOCK_SIZE(MWIDTH), // Check logic
      .INDEX_WIDTH(6),
      .TAG_WIDTH(8),
      .OFFSET_WIDTH(3)
      
    ) dut_cache (
        .clk(clk),
        .reset_n(reset_n),
        .address(address),
        .din(din),
        .rden(rden),
        .wren(wren),
        .hit_miss(hit_miss),
        .q(q),
        
        .mdout(mdout),
        .mrdaddress(mrdaddress),
        .mrden(mrden),
        .mwraddress(mwraddress),
        .mwren(mwren),
        .mq(mq)
    );

    // RAM Interconnect Logic
    // Cache has separate read/write ports. RAM has one.
    // FSM ensures they are not active same time (Checked: WRITE_BACK then FETCH).
    // So simple mux.
    
    assign ram_write_enable = mwren;
    assign ram_read_enable  = mrden;
    assign ram_address      = mwren ? mwraddress[ADDR_WIDTH-1:0] : 				mrdaddress[ADDR_WIDTH-1:0];
    assign ram_data_in      = mdout;
    assign mq               = ram_data_out; 
  wire [1:0] l1;
  wire [1:0] l2;
  wire [1:0] l3;
    wire [1:0] l4;
  wire [31:0] m1;
  wire [31:0] m2;
  wire [31:0] m3;
  wire [31:0] m4;
  wire d1;
  wire d2;
  wire d3;
  wire d4;
      // RAM Module
    Ram #(
        .WIDTH(MWIDTH),   // RAM stores BLOCKS (64 bits)
        .DEPTH(ADDR_WIDTH) // 16 bits address
    ) dut_ram (
        .clk(clk),
        .reset_n(reset_n),
        .data_in(ram_data_in),
        .adress(ram_address),
        .write_enable(ram_write_enable),
        .read_enable(ram_read_enable),
        .data_out(ram_data_out),
        .valid_out(ram_valid_out)
    );
	assign l1=dut_cache.lru1[0];
  	assign l2=dut_cache.lru2[0];
  	assign l3=dut_cache.lru3[0];
  	assign l4=dut_cache.lru4[0];
  	assign m1=dut_cache.mem1[0];
  	assign m2=dut_cache.mem2[0];
  	assign m3=dut_cache.mem3[0];
  	assign m4=dut_cache.mem4[0];
  	assign d1=dut_cache.dirty1[0];
    assign d2=dut_cache.dirty2[0];
    assign d3=dut_cache.dirty3[0];
    assign d4=dut_cache.dirty4[0];
    // Clock
    always #5 clk = ~clk;
	initial begin
      	clk = 0;
      address=0;
      reset_n=0;
      rden=0;
      wren=0;
      din=0;

        #10 reset_n=1;
     
  
      	#15;
        $readmemh("Test1.mem",dut_ram.mem);
      	#10
        address = 16'h0100;
        rden = 1;
      #15 rden=0;
      #33
      address = 16'h0200;
        rden = 1;
      #15 rden=0;
      #32
      address = 16'h0300;
        rden = 1;
      #15rden=0;
      #33
      address = 16'h0400;
        rden = 1;
      #15 rden=0;
      #33
      address = 16'h0500;
        rden = 1;
      #15 rden=0;
      #50
      // Hits:
      address = 16'h0100;
        rden = 1;
      #10 rden = 0;
      #10
      
      address = 16'h0200;
        rden = 1;
     
       #10 rden = 0;
      #10
      
      address = 16'h0300;
        rden = 1;
   
      #10 rden = 0;
      #10
      
      address = 16'h0400;
        rden = 1;
      #30
      address = 16'h0600;
        rden = 1;
      #15 rden=0;
      #33
      address = 16'h0800;
        rden = 1;
      #15 rden=0;
      #70
      address = 16'h0600;
              rden = 1;
            #10 rden = 0;
            #10
            
            address = 16'h0800;
              rden = 1;
           
             #10 rden = 0;
            #10
 
      address = 16'h0a00;
        rden = 1;
      #15 rden=0;
      #70;
      
      address=16'h0a00;
      din= 32'h 0dda_4444;
      wren = 1;
      #12 wren=0;
      #50;
      address = 16'h0400;
        rden = 1;
     
       #12 rden = 0;
      #12
      
      address = 16'h0600;
        rden = 1;
   
      #12 rden = 0;
      #12
      
      address = 16'h0800;
        rden = 1;
      #12 rden = 0;
      #50;
      address = 16'h0c00;
      rden = 1;
      #12 rden=1;
      #80;
    	$finish;
      
    end
    
    initial begin
        $dumpfile("wave.vcd");
        $dumpvars;
    end
  
  

endmodule
