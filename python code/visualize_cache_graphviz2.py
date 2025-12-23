try:
    from graphviz import Digraph
except ImportError:
    print("Graphviz not installed. Please install it using 'pip install graphviz'.")
    exit(1)

def create_master_cache_schematic():
    # 'dot' engine is best for hierarchical hardware schematics
    dot = Digraph('Cache_Master_Fixed', comment='Full Detail Verilog Cache')
    
    # Global attributes
    # Changed splines to 'polyline' to avoid the Orthogonal label warning
    dot.attr(rankdir='TB', splines='polyline', nodesep='1.0', ranksep='1.0', bgcolor='white')
    dot.attr('node', fontname='Helvetica,Arial,sans-serif', shape='none')
    dot.attr('edge', fontname='Helvetica', fontsize='9')

    # Palette
    c_blue   = "#E3F2FD" # Interface
    c_yellow = "#FFFDE7" # Address
    c_red    = "#FFEBEE" # Hit/Miss
    c_purple = "#F3E5F5" # Data
    c_grey   = "#F5F5F5" # Ways
    c_dark   = "#37474F" # Headers

    # 1. MODULE INTERFACE (Ports)
    # ------------------------------------------------------------------
    interface_label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" BGCOLOR="{c_blue}">
        <TR><TD COLSPAN="2" BGCOLOR="#1976D2"><FONT COLOR="white"><B>Cache.v Ports (32-bit Architecture)</B></FONT></TD></TR>
        <TR><TD ALIGN="LEFT">clk / reset_n</TD><TD ALIGN="RIGHT">Clock/Reset</TD></TR>
        <TR><TD ALIGN="LEFT">address [31:0]</TD><TD ALIGN="RIGHT">CPU Addr</TD></TR>
        <TR><TD ALIGN="LEFT">din [31:0]</TD><TD ALIGN="RIGHT">CPU Data In</TD></TR>
        <TR><TD ALIGN="LEFT">rden / wren</TD><TD ALIGN="RIGHT">Control</TD></TR>
        <TR><TD ALIGN="LEFT" BGCOLOR="#BBDEFB"><B>hit_miss</B></TD><TD ALIGN="RIGHT" BGCOLOR="#BBDEFB">Status</TD></TR>
        <TR><TD ALIGN="LEFT" BGCOLOR="#BBDEFB"><B>q [31:0]</B></TD><TD ALIGN="RIGHT" BGCOLOR="#BBDEFB">CPU Data Out</TD></TR>
    </TABLE>>'''
    dot.node('IO', label=interface_label)

    # 2. ADDRESS DECODER (localparams)
    # ------------------------------------------------------------------
    addr_label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" BGCOLOR="{c_yellow}">
        <TR><TD COLSPAN="3" BGCOLOR="#FBC02D"><B>Address Logic (localparam Decoding)</B></TD></TR>
        <TR>
            <TD PORT="tag"><B>TAG [31:13]</B><BR/>(19 bits)</TD>
            <TD PORT="idx"><B>INDEX [12:3]</B><BR/>(10 bits / 1024 sets)</TD>
            <TD PORT="off"><B>OFFSET [2:0]</B><BR/>(3 bits / 8 bytes)</TD>
        </TR>
    </TABLE>>'''
    dot.node('Addr', label=addr_label)

    # 3. 4-WAY SET ASSOCIATIVE STORAGE
    # ------------------------------------------------------------------
    for i in range(1, 5):
        way_label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="{c_grey}">
            <TR><TD COLSPAN="2" BGCOLOR="{c_dark}"><FONT COLOR="white"><B>WAY {i}</B></FONT></TD></TR>
            <TR><TD>Valid</TD><TD PORT="v">1 bit</TD></TR>
            <TR><TD>Dirty</TD><TD PORT="d">1 bit</TD></TR>
            <TR><TD>LRU</TD><TD PORT="l">2 bits</TD></TR>
            <TR><TD BGCOLOR="#FFCCBC">Tag Array</TD><TD PORT="t">19 bits</TD></TR>
            <TR><TD BGCOLOR="#D1C4E9">Data (mem{i})</TD><TD PORT="m">64 bits</TD></TR>
        </TABLE>>'''
        dot.node(f'Way{i}', label=way_label)

    # 4. CONTROL LOGIC (Fixed &amp; escaping)
    # ------------------------------------------------------------------
    logic_label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="10" BGCOLOR="{c_red}">
        <TR><TD BGCOLOR="#D32F2F"><FONT COLOR="white"><B>Comparator &amp; LRU Logic</B></FONT></TD></TR>
        <TR><TD ALIGN="LEFT">
            - Tag Comparators (19-bit x 4)<BR/>
            - Hit Logic: (Tag Match &amp; Valid)<BR/>
            - LRU Replacement: Victim if LRU == 3<BR/>
            - Dirty Check: Trigger Write_Back
        </TD></TR>
    </TABLE>>'''
    dot.node('Logic', label=logic_label)

    # 5. DATA PATH (MUX &amp; Word Selection)
    # ------------------------------------------------------------------
    mux_label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" BGCOLOR="{c_purple}">
        <TR><TD COLSPAN="2" BGCOLOR="#7B1FA2"><FONT COLOR="white"><B>Output Data Path</B></FONT></TD></TR>
        <TR><TD PORT="in">64-bit Block</TD></TR>
        <TR><TD PORT="sel">Word Select (Offset[2])</TD></TR>
        <TR><TD PORT="out">32-bit Word (q)</TD></TR>
    </TABLE>>'''
    dot.node('Mux', label=mux_label)

    # 6. MEMORY INTERFACE (RAM)
    # ------------------------------------------------------------------
    mem_label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" BGCOLOR="#E8F5E9">
        <TR><TD COLSPAN="2" BGCOLOR="#2E7D32"><FONT COLOR="white"><B>Memory Interface (RAM)</B></FONT></TD></TR>
        <TR><TD ALIGN="LEFT">mq [63:0]</TD><TD ALIGN="RIGHT">From RAM</TD></TR>
        <TR><TD ALIGN="LEFT">mdout [63:0]</TD><TD ALIGN="RIGHT">To RAM</TD></TR>
        <TR><TD ALIGN="LEFT">mrdaddress / mwraddress</TD><TD ALIGN="RIGHT">Addr Out</TD></TR>
        <TR><TD ALIGN="LEFT">mrden / mwren</TD><TD ALIGN="RIGHT">Control</TD></TR>
    </TABLE>>'''
    dot.node('RAM', label=mem_label)

    # 7. CONNECTIONS
    # ------------------------------------------------------------------
    dot.edge('IO', 'Addr', label=" CPU Request")
    dot.edge('Addr:idx', 'Way1', style='dashed', label=' Index Select')
    dot.edge('Addr:tag', 'Logic', label=' 19-bit Compare')
    
    for i in range(1, 5):
        dot.edge(f'Way{i}:t', 'Logic')
        dot.edge(f'Way{i}:m', 'Mux', color="#7B1FA2")

    dot.edge('Logic', 'IO', label=' hit_miss status', color="red")
    dot.edge('Addr:off', 'Mux', label=" Offset[2]")
    dot.edge('Mux', 'IO', label=" Data Bus [31:0]")
    
    # RAM Flow
    dot.edge('RAM', 'Way1', label=" REFILL State")
    dot.edge('Way1:d', 'RAM', style='dotted', label=' WRITE_BACK')

    # RENDER
    output_name = 'cache_master_final_fixed'
    dot.render(output_name, format='png', cleanup=True)
    print(f"Schematic generated: {output_name}.png")

if __name__ == "__main__":
    create_master_cache_schematic()