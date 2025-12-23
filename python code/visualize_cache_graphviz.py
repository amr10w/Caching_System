try:
    from graphviz import Digraph
except ImportError:
    print("Graphviz not installed. Please install it using 'pip install graphviz' and ensure Graphviz executables are in your PATH.")
    exit(1)

def create_cache_schematic():
    dot = Digraph('CacheSchematic', comment='4-Way Set Associative Cache')
    # Orthogonal edges for schematic look
    dot.attr(rankdir='TB', splines='ortho', nodesep='1.2', ranksep='1.2', bgcolor='white')
    dot.attr('node', fontname='Helvetica', shape='none')
    dot.attr('edge', fontname='Helvetica', fontsize='10')

    # ------------------------------------------------------------------
    # Colors
    # ------------------------------------------------------------------
    # Matches Pygame palette
    c_tag = "#FFCCBC"     # Light Red/Orange
    c_index = "#C8E6C9"   # Light Green
    c_offset = "#B3E5FC"  # Light Blue
    c_header = "#E0E0E0"  # Grey
    c_select = "#FFF9C4"  # Light Yellow (Selection)
    
    c_lru = "#E1BEE7"     # Lavender for LRU
    c_data = "#D1C4E9"    # Data 
    c_valid = "#F5F5F5"   # Light Grey
    c_dirty = "#FFECB3"   # Amber

    c_comp = "#FFE0B2"    # Orange-ish
    c_and = "#FFF59D"     # Yellow-ish
    c_or = "#FFCC80"
    
    c_line_tag = "#E64A19"      # Dark Orange
    c_line_index = "#388E3C"    # Green
    c_line_data = "#303F9F"     # Blue
    c_line_hit = "#D32F2F"      # Red
    c_line_ctrl = "#616161"     # Grey

    # ------------------------------------------------------------------
    # 1. Parameter Legend (Top Left)
    # ------------------------------------------------------------------
    params_label = f'''<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5" BGCOLOR="white">
        <TR><TD COLSPAN="2" BGCOLOR="#37474F"><FONT COLOR="white"><B>Cache Parameters (Cache.v)</B></FONT></TD></TR>
        <TR><TD ALIGN="LEFT">SIZE</TD><TD ALIGN="RIGHT">256 KB (32*1024*8)</TD></TR>
        <TR><TD ALIGN="LEFT">NWAYS</TD><TD ALIGN="RIGHT">4</TD></TR>
        <TR><TD ALIGN="LEFT">NSETS</TD><TD ALIGN="RIGHT">1024</TD></TR>
        <TR><TD ALIGN="LEFT">BLOCK_SIZE</TD><TD ALIGN="RIGHT">64 bits</TD></TR>
        <TR><TD ALIGN="LEFT">INDEX_WIDTH</TD><TD ALIGN="RIGHT">10</TD></TR>
        <TR><TD ALIGN="LEFT">TAG_WIDTH</TD><TD ALIGN="RIGHT">19</TD></TR>
        <TR><TD ALIGN="LEFT">OFFSET_WIDTH</TD><TD ALIGN="RIGHT">3</TD></TR>
    </TABLE>>'''
    dot.node('Legend', label=params_label, pos='0,0!')


    # ------------------------------------------------------------------
    # 2. Address Register (Top Center)
    # ------------------------------------------------------------------
    addr_label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
        <TR>
            <TD BGCOLOR="{c_tag}" PORT="tag" WIDTH="150"><B>Tag [31:13]</B><BR/>(19 bits)</TD>
            <TD BGCOLOR="{c_index}" PORT="index" WIDTH="100"><B>Index [12:3]</B><BR/>(10 bits)</TD>
            <TD BGCOLOR="{c_offset}" PORT="offset" WIDTH="80"><B>Offset [2:0]</B><BR/>(3 bits)</TD>
        </TR>
    </TABLE>>'''
    dot.node('Address', label=addr_label)

    # ------------------------------------------------------------------
    # 3. Ways (Clusters)
    # ------------------------------------------------------------------
    # We use a subgraph to group them horizontally
    with dot.subgraph(name='cluster_main') as c:
        c.attr(style='invis')
        
        for i in range(1, 5):
            way_id = f'Way{i}'
            
            # HTML Table
            # Columns: Idx, V, D, LRU, Tag, Data
            
            table = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                <TR>
                    <TD COLSPAN="6" BGCOLOR="#546E7A"><FONT COLOR="white"><B>WAY {i}</B></FONT></TD>
                </TR>
                <TR>
                    <TD BGCOLOR="{c_header}"><B>Idx</B></TD>
                    <TD BGCOLOR="{c_header}"><B>V</B></TD>
                    <TD BGCOLOR="{c_header}"><B>D</B></TD>
                    <TD BGCOLOR="{c_header}"><B>LRU</B></TD>
                    <TD BGCOLOR="{c_header}"><B>Tag</B></TD>
                    <TD BGCOLOR="{c_header}"><B>Data</B></TD>
                </TR>
                <TR>
                    <TD>0</TD>
                    <TD BGCOLOR="{c_valid}"></TD>
                    <TD BGCOLOR="{c_dirty}"></TD>
                    <TD BGCOLOR="{c_lru}"></TD>
                    <TD BGCOLOR="#FFEBE5"></TD>
                    <TD BGCOLOR="#EDE7F6"></TD>
                </TR>
                <TR>
                    <TD BORDER="0">...</TD><TD BORDER="0">...</TD><TD BORDER="0">...</TD><TD BORDER="0">...</TD><TD BORDER="0">...</TD><TD BORDER="0">...</TD>
                </TR>
                <TR>
                    <TD BGCOLOR="{c_index}"><B>K</B></TD>
                    <TD BGCOLOR="{c_select}" PORT="v_k">valid{i}[K]</TD>
                    <TD BGCOLOR="{c_select}" PORT="d_k">dirty{i}[K]</TD>
                    <TD BGCOLOR="{c_select}" PORT="lru_k">lru{i}[K]</TD>
                    <TD BGCOLOR="{c_select}" PORT="tag_k">tag{i}[K]</TD>
                    <TD BGCOLOR="{c_select}" PORT="data_k">mem{i}[K]</TD>
                </TR>
                 <TR>
                    <TD BORDER="0">...</TD><TD BORDER="0">...</TD><TD BORDER="0">...</TD><TD BORDER="0">...</TD><TD BORDER="0">...</TD><TD BORDER="0">...</TD>
                </TR>
                <TR>
                    <TD>1023</TD>
                    <TD BGCOLOR="{c_valid}"></TD>
                    <TD BGCOLOR="{c_dirty}"></TD>
                    <TD BGCOLOR="{c_lru}"></TD>
                    <TD BGCOLOR="#FFEBE5"></TD>
                    <TD BGCOLOR="#EDE7F6"></TD>
                </TR>
            </TABLE>>'''
            
            c.node(way_id, label=table)


    # ------------------------------------------------------------------
    # 4. Logic (Comparators, Gates)
    # ------------------------------------------------------------------
    
    for i in range(1, 5):
        # Comparator
        comp_id = f'Comp{i}'
        dot.node(comp_id, label='=', shape='circle', style='filled', fillcolor=c_comp, width='0.5', fixedsize='true')
        
        # AND Gate (Hit generation)
        and_id = f'And{i}'
        dot.node(and_id, label='&', shape='rect', style='filled', fillcolor=c_and, width='0.6')

        # Edges to Logic
        
        # Tag Address -> Comparator
        # Using a hidden node or just routing
        # Edges from Address Table to Logic
        dot.edge('Address:tag', comp_id, color=c_line_tag, penwidth='2.0')
        
        # Tag Way -> Comparator
        dot.edge(f'Way{i}:tag_k', comp_id, label='19', color=c_line_tag, penwidth='2.0')
        
        # Enable/Valid -> AND
        dot.edge(f'Way{i}:v_k', and_id, label='1', color=c_line_ctrl)
        
        # Comparator Out -> AND
        dot.edge(comp_id, and_id, color=c_line_ctrl)


    # Global Index routing (dashed)
    for i in range(1, 5):
        dot.edge('Address:index', f'Way{i}:v_k', style='dashed', color=c_line_index, label='10', constraint='false')


    # ------------------------------------------------------------------
    # 5. Output Stage (MUX & OR)
    # ------------------------------------------------------------------
    
    # OR Gate (Hit/Miss)
    dot.node('OrGate', label='OR', shape='invtrapezium', style='filled', fillcolor=c_or)
    dot.node('HitMissOut', label='hit_miss', shape='plaintext', fontcolor=c_line_hit)
    
    # MUX
    mux_label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="{c_data}">
    <TR><TD COLSPAN="4" PORT="top"><B>4-to-1 MUX</B></TD></TR>
    <TR>
        <TD PORT="in1">00</TD>
        <TD PORT="in2">01</TD>
        <TD PORT="in3">10</TD>
        <TD PORT="in4">11</TD>
    </TR>
    <TR><TD COLSPAN="4" PORT="out">Data Width = 64</TD></TR>
    </TABLE>>'''
    dot.node('Mux', label=mux_label)
    
    dot.node('OutputQ', label='q [31:0]', shape='note', style='filled', fillcolor=c_offset)

    # Connections
    for i in range(1, 5):
        and_id = f'And{i}'
        
        # Hit -> OR
        dot.edge(and_id, 'OrGate', color=c_line_hit, label=f'Hit{i}')
        
        # Hit -> Mux Select (Abstract)
        dot.edge(and_id, 'Mux:top', color=c_line_hit, style='dotted')
        
        # Data -> Mux In
        dot.edge(f'Way{i}:data_k', f'Mux:in{i}', color=c_line_data, label='64', penwidth='2.0')

    # Final Output
    dot.edge('OrGate', 'HitMissOut', color=c_line_hit, penwidth='2.0')
    
    # Word Select Logic (Offset)
    # Mux Out (64) -> Word Select -> Q (32)
    dot.node('WordMux', label='Word Select', shape='invtrapezium', style='filled', fillcolor=c_offset)
    
    dot.edge('Mux:out', 'WordMux', color=c_line_data, label='64')
    dot.edge('Address:offset', 'WordMux', color=c_line_data, label='Offset[3]')
    dot.edge('WordMux', 'OutputQ', color=c_line_data, label='32')

    # Render
    output_filename = 'cache_schematic_graphviz_refined'
    dot.render(output_filename, format='png', cleanup=True)
    print(f"Schematic generated: {output_filename}.png")

if __name__ == "__main__":
    create_cache_schematic()
