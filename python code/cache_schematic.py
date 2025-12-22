import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath
import numpy as np

# ==========================================
# Draw Logic Gate Helpers
# ==========================================

def draw_and_gate(ax, x, y, size=1.0, color='black', fill='#e0e0e0', label=None):
    """ Draws a D-shaped AND gate at (x,y) facing Right. 
        Input side is at x. Output side is at x+size.
    """
    width = size
    height = size * 0.8
    
    # Path for D-shape
    verts = [
        (x, y - height/2),          # Bottom-left
        (x, y + height/2),          # Top-left
        (x + width*0.5, y + height/2), # Top-flat start curve
        (x + width, y),             # Tip
        (x + width*0.5, y - height/2), # Bottom curve start
        (x, y - height/2),          # Close
    ]
    codes = [
        mpath.Path.MOVETO,
        mpath.Path.LINETO,
        mpath.Path.LINETO,
        mpath.Path.CURVE3,
        mpath.Path.CURVE3,
        mpath.Path.CLOSEPOLY,
    ]
    path = mpath.Path(verts, codes)
    patch = patches.PathPatch(path, facecolor=fill, edgecolor=color, lw=1.5, zorder=10)
    ax.add_patch(patch)
    if label:
        ax.text(x + width*0.4, y, label, ha='center', va='center', fontsize=8, weight='bold')
    
    # Return ports positions
    return {
        'in1': (x, y + height/4),
        'in2': (x, y - height/4),
        'out': (x + width, y)
    }

def draw_comparator(ax, x, y, size=1.0, color='black', fill='white'):
    """ Draws a circle with '=' inside. """
    circle = patches.Circle((x, y), size/2, facecolor=fill, edgecolor=color, lw=1.5, zorder=10)
    ax.add_patch(circle)
    ax.text(x, y, "=", ha='center', va='center', fontsize=12, weight='bold')
    return {
        'top': (x, y + size/2),
        'bottom': (x, y - size/2),
        'in_left': (x - size/2, y),
        'out_bottom': (x, y - size/2)
    }

def draw_mux_trapezoid(ax, x, y, w, h, label="MUX"):
    """ Draws a trapezoid MUX. (Narrow top, wide bottom? No, MUX is usually wide input, narrow output).
        Here: Inputs top, Output bottom.
        Trapezoid: Top width W, Bottom width W/2.
    """
    top_w = w
    bot_w = w * 0.6
    
    x_left_top = x - top_w/2
    x_right_top = x + top_w/2
    x_left_bot = x - bot_w/2
    x_right_bot = x + bot_w/2
    
    y_top = y + h/2
    y_bot = y - h/2
    
    polygon = np.array([
        [x_left_top, y_top],
        [x_right_top, y_top],
        [x_right_bot, y_bot],
        [x_left_bot, y_bot]
    ])
    
    patch = patches.Polygon(polygon, closed=True, facecolor='#fff3e0', edgecolor='black', lw=1.5)
    ax.add_patch(patch)
    ax.text(x, y, label, ha='center', va='center', weight='bold')
    
    return {
        'top_left': (x_left_top, y_top),
        'top_right': (x_right_top, y_top),
        'out': (x, y_bot),
        'sel': (x_right_bot, y) # approximate side
    }

def draw_bus_label(ax, x, y, text, color='black'):
    """ Draws a small strike through line with bit width number. """
    # Strike
    sl = 0.15
    ax.plot([x-sl, x+sl], [y-sl, y+sl], color=color, lw=1)
    ax.text(x+0.1, y+0.1, text, fontsize=7, color=color)

# ==========================================
# Main Drawing
# ==========================================

def visualize_hardware():
    fig, ax = plt.subplots(figsize=(18, 12))
    ax.set_aspect('equal')
    
    # -----------------------------
    # 1. Address Register (Top)
    # -----------------------------
    y_addr = 14
    ax.add_patch(patches.Rectangle((4, y_addr), 12, 1, facecolor='white', edgecolor='black', lw=2))
    ax.text(10, y_addr+1.2, "CPU Physical Address [31:0]", ha='center', fontsize=12, weight='bold')
    
    # Fields
    # Tag
    ax.fill_between([4, 10], y_addr, y_addr+1, color='#ffccbc', alpha=0.5)
    ax.text(7, y_addr+0.5, "Tag [31:13]\n(19 bits)", ha='center', va='center', fontsize=9)
    # Index
    ax.fill_between([10, 14], y_addr, y_addr+1, color='#fff9c4', alpha=0.5)
    ax.text(12, y_addr+0.5, "Index [12:3]\n(10 bits)", ha='center', va='center', fontsize=9)
    # Offset
    ax.fill_between([14, 16], y_addr, y_addr+1, color='#e1bee7', alpha=0.5)
    ax.text(15, y_addr+0.5, "Offset\n[2:0]", ha='center', va='center', fontsize=9)

    # Decode Lines
    # Index selects the SET. We represent "One Set" (Set K).
    ax.annotate("Index selects\nSet K", xy=(12, y_addr), xytext=(12, 11), 
                arrowprops=dict(arrowstyle="->", linestyle="dashed"), ha='center')

    # Tag Bus Line
    y_bus = 12.5
    ax.plot([7, 7], [y_addr, y_bus], 'k-', lw=1.5)
    ax.plot([2, 18], [y_bus, y_bus], 'k-', lw=1.5) # Horizontal Bus
    draw_bus_label(ax, 3, y_bus, "19")

    # -----------------------------
    # 2. Cache Ways (Columns)
    # -----------------------------
    ways_x = [3, 8, 13, 18] # Centers
    way_width = 4
    y_array = 8
    
    mux_inputs = []

    for i, xc in enumerate(ways_x):
        way_id = i + 1
        
        # Enclosure
        ax.add_patch(patches.Rectangle((xc - way_width/2, y_array - 2), way_width, 4, 
                                       facecolor='none', edgecolor='#b0bec5', linestyle='--'))
        ax.text(xc, y_array + 2.2, f"WAY {way_id}", ha='center', weight='bold', color='#546e7a')

        # Memory Line (The Row for Set K)
        # Structure: Valid(1) | Dirty(1) | LRU(2) | Tag(19) | Data(64)
        
        # Visual Block
        bw = way_width - 0.2
        bx = xc - bw/2
        by = y_array
        bh = 1.0
        
        # We'll split the block into small rects
        # V
        ax.add_patch(patches.Rectangle((bx, by), 0.4, bh, fc='#b2dfdb', ec='black'))
        ax.text(bx+0.2, by+0.5, f"V{way_id}", ha='center', va='center', fontsize=8)
        
        # Tag
        ax.add_patch(patches.Rectangle((bx+0.4, by), 1.6, bh, fc='#ffccbc', ec='black'))
        ax.text(bx+1.2, by+0.5, f"tag{way_id}\n[19]", ha='center', va='center', fontsize=8)

        # Data (Put below or beside? Beside is tight. Let's put Data BELOW tag/valid row)
        # Verilog: mem1[index] checks tag1[index].
        # Drawing data block separately
        y_data = y_array - 1.5
        ax.add_patch(patches.Rectangle((bx, y_data), bw, 1.0, fc='#c8e6c9', ec='black'))
        ax.text(xc, y_data+0.5, f"mem{way_id} [64 bits]", ha='center', va='center', fontfamily='monospace')
        
        # Logic Connections
        # 1. Comparator (Tag Match)
        comp = draw_comparator(ax, xc + 0.5, y_array + 2.5, size=0.8)
        
        # Route Tag Bus to Comparator (Input A)
        ax.plot([xc + 0.5, xc + 0.5], [y_bus, comp['top'][1]], 'k-', lw=1.5)
        
        # Route Stored Tag to Comparator (Input B)
        ax.plot([bx+1.2, bx+1.2], [by+bh, comp['bottom'][1]], 'k-', lw=1.5)
        ax.fill([bx+1.1, bx+1.3, bx+1.2], [by+bh, by+bh, by+bh+0.2], 'k') # Arrow head start
        
        # 2. AND Gate (Hit Logic)
        # Inputs: Comparator Out & Valid Bit
        and_g = draw_and_gate(ax, xc + 1.5, y_array + 1.5, size=0.8, fill='#ffecb3')
        
        # Conn: Comparator -> AND
        ax.plot([comp['out_bottom'][0], comp['out_bottom'][0]], [and_g['in1'][1], and_g['in1'][1]], 'k-', lw=1.5) # Straight down? No, Shift right
        # Using stepped line
        ax.plot([comp['out_bottom'][0], comp['out_bottom'][0]], [comp['out_bottom'][1], comp['out_bottom'][1]-0.2], 'k-')
        ax.plot([comp['out_bottom'][0], and_g['in1'][0]-0.2], [comp['out_bottom'][1]-0.2, and_g['in1'][1]], 'k-') # diagonal
        ax.plot([and_g['in1'][0]-0.2, and_g['in1'][0]], [and_g['in1'][1], and_g['in1'][1]], 'k-')
        
        # Conn: Valid -> AND
        # Valid is at bx+0.2
        ax.plot([bx+0.2, bx+0.2], [by+bh, and_g['in2'][1]], 'k-', lw=1.5) # Up?
        # Gate is ABOVE Valid array? Yes (y=9.5 vs y=8).
        ax.plot([bx+0.2, and_g['in2'][0]], [and_g['in2'][1], and_g['in2'][1]], 'k-') 
        
        # Hit Signal
        hit_y = 5 # Level for hit bus
        ax.plot([and_g['out'][0], and_g['out'][0]+0.2], [and_g['out'][1], and_g['out'][1]], 'r-', lw=2) # Out stub
        ax.text(and_g['out'][0]+0.3, and_g['out'][1], f"Hit{way_id}", color='red', fontsize=9, weight='bold')
        
        # Route Hit to Mux logic
        # Store for Mux
        mux_inputs.append({'data_x': xc, 'data_y': y_data, 'hit_x': and_g['out'][0]})

    # -----------------------------
    # 3. Output MUX
    # -----------------------------
    mux = draw_mux_trapezoid(ax, 10.5, 3, 14, 2, label="4-Way MUX\nSelected by Hit1..Hit4")
    
    # Route Data to MUX
    for i, minp in enumerate(mux_inputs):
        # Data path
        ax.plot([minp['data_x'], minp['data_x']], [minp['data_y'], mux['top_left'][1]], 'g-', lw=2)
        draw_bus_label(ax, minp['data_x'], 4, "64", 'green')
    
    # Output of Mux
    ax.plot([mux['out'][0], mux['out'][0]], [mux['out'][1], 1], 'b-', lw=3)
    draw_bus_label(ax, mux['out'][0]+0.2, 1.5, "64", 'blue')
    
    # -----------------------------
    # 4. Word Select MUX (Offset)
    # -----------------------------
    word_mux = draw_mux_trapezoid(ax, 10.5, 0, 4, 1.5, "Word Select")
    ax.plot([10.5, 10.5], [1, 0.75], 'b-', lw=3) # input from big mux
    
    # Offset Control
    ax.annotate("Offset [2]", xy=(12.5, 0), xytext=(15, 0), 
                arrowprops=dict(arrowstyle="->"), ha='center')
    
    # Final Output
    ax.arrow(10.5, -0.75, 0, -0.5, head_width=0.3, color='blue', lw=2)
    ax.text(10.5, -1.5, "q [31:0] (Data Out)", ha='center', weight='bold', fontsize=14, color='blue')

    # -----------------------------
    # Layout Limits
    # -----------------------------
    ax.set_xlim(0, 21)
    ax.set_ylim(-2, 16)
    ax.axis('off')
    plt.title("Hardware Schematic: 4-Way Set Associative Cache", fontsize=18, pad=20)
    plt.tight_layout()
    plt.savefig('cache_schematic.png', dpi=150)
    plt.show()

if __name__ == "__main__":
    visualize_hardware()
