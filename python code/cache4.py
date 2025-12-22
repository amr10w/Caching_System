import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_component(ax, x, y, width, height, label, color='white', fontsize=10):
    rect = patches.Rectangle((x, y), width, height, linewidth=1, edgecolor='black', facecolor=color)
    ax.add_patch(rect)
    ax.text(x + width/2, y + height/2, label, ha='center', va='center', fontsize=fontsize)
    return x + width/2, y + height/2

def draw_cache_hardware():
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # ---------------------------------------------------------
    # 1. CPU Address
    # ---------------------------------------------------------
    ax.text(8, 11.5, "CPU Address (WIDTH=32)", ha='center', fontsize=14, weight='bold')
    
    # Address Register breakdown
    # Tag (19), Index (10), Offset (3)
    # Total width used for drawing = 10 units
    draw_component(ax, 3, 10.5, 5, 0.8, "Tag (19 bits)\naddress[31:13]", '#ffccbc')
    draw_component(ax, 8, 10.5, 3, 0.8, "Index (10 bits)\naddress[12:3]", '#fff9c4')
    draw_component(ax, 11, 10.5, 2, 0.8, "Offset (3 bits)\naddress[2:0]", '#e1bee7')
    
    # Lines dropping down
    # Tag Line
    ax.plot([5.5, 5.5], [10.5, 9.5], 'k-') # Tag out
    ax.plot([1.5, 14.5], [9.5, 9.5], 'k-') # Tag distribution bus
    
    # Index Line
    ax.plot([9.5, 9.5], [10.5, 6.0], 'k--') 
    ax.text(9.6, 6.5, "Index Selects Set", fontsize=9, rotation=0)

    # ---------------------------------------------------------
    # 2. Cache Ways (Hardware Arrays)
    # ---------------------------------------------------------
    way_colors = ['#e3f2fd', '#e0f2f1', '#f3e5f5', '#fbe9e7']
    way_names = ["1", "2", "3", "4"]
    
    # Way X starting positions
    x_starts = [0.5, 4.5, 8.5, 12.5]
    
    for i, x in enumerate(x_starts):
        way_num = way_names[i]
        color = way_colors[i]
        
        # Way Container Outline
        rect = patches.Rectangle((x, 3), 3.5, 6, linewidth=2, edgecolor='gray', facecolor='none', linestyle=':')
        ax.add_patch(rect)
        ax.text(x + 1.75, 9.1, f"WAY {way_num}", ha='center', weight='bold')
        
        # Internal Reg Arrays (Rows representing a Set)
        # We visualize "Selected Set"
        y_set = 5.5
        
        # Valid Bit
        draw_component(ax, x+0.1, y_set, 0.5, 1, f"V{way_num}\n[1]", '#b2dfdb', 8)
        
        # Dirty Bit
        draw_component(ax, x+0.6, y_set, 0.5, 1, f"D{way_num}\n[1]", '#ffcdd2', 8)
        
        # LRU Bits
        draw_component(ax, x+1.1, y_set, 0.6, 1, f"L{way_num}\n[2]", '#e1bee7', 8)
        
        # Tag Array
        draw_component(ax, x+1.7, y_set, 1.7, 1, f"tag{way_num}\n[19]", '#ffccbc', 8)
        
        # Data Block (Visualized slightly below or same line? Same line is better for "Set")
        # But Data is huge (64 bits). Let's put it below to save width, or squeeze.
        # Let's widen the diagram.
        # Actually, let's put Data in the same block but below the tag for compactness.
        draw_component(ax, x+0.1, y_set-1.2, 3.3, 1, f"mem{way_num} [64 bits] (MWIDTH)", '#c8e6c9', 9)
        
        # Comparator
        # Compares Tag Register with CPU Tag
        cx, cy = x + 2.5, 8.0
        circle = patches.Circle((cx, cy), 0.3, edgecolor='black', facecolor='white')
        ax.add_patch(circle)
        ax.text(cx, cy, "=", ha='center', va='center', weight='bold')
        
        # Connection from CPU Tag Bus
        ax.plot([cx, cx], [9.5, 8.3], 'k-')
        # Connection from Way Tag
        ax.plot([x+2.5, x+2.5], [y_set+1.0, 8.3], 'k-') # wait, tag is at y_set
        ax.arrow(x+2.5, y_set+1.0, 0, 1.2, head_width=0.1, color='black') # Arrow up from tag
        
        # AND Gate (Valid Check)
        # (Comparator) AND (Valid)
        ax.text(cx, cy-0.8, "&", fontsize=14, ha='center', weight='bold')
        
        # Hit Signal Line
        ax.plot([cx, cx], [cy-0.3, cy-0.6], 'k-') # from = to &
        # Valid signal to &
        ax.plot([x+0.35, x+0.35], [y_set+1.0, cy-0.8], 'k-') 
        ax.plot([x+0.35, cx-0.1], [cy-0.8, cy-0.8], 'k-') 
        
        # Result = Match Line
        ax.plot([cx, cx], [cy-1.0, 2.5], 'r-', linewidth=2)
        ax.text(cx+0.2, 3.5, f"Hit{way_num}", color='red', fontsize=8)

    # ---------------------------------------------------------
    # 3. Output Logic
    # ---------------------------------------------------------
    
    # MUX
    draw_component(ax, 5, 0.5, 6, 1.5, "4-to-1 MUX", '#ffe0b2')
    
    # Inputs to Mux (Data mem1..mem4)
    # mem1
    ax.arrow(2.2, 4.3, 3.0, -2.5, head_width=0.1, color='green') # Way 1 Data -> Mux
    ax.arrow(6.2, 4.3, 0.5, -2.3, head_width=0.1, color='green') # Way 2 Data
    ax.arrow(10.2, 4.3, -2.5, -2.3, head_width=0.1, color='green') # Way 3 Data
    ax.arrow(14.2, 4.3, -5.0, -2.5, head_width=0.1, color='green') # Way 4 Data
    
    # Hit Signals controlling Mux
    ax.plot([3.0, 8.0], [2.5, 2.5], 'r-', linewidth=2) # Bus for hit signals
    ax.arrow(8.0, 2.5, 0, -0.5, head_width=0.2, color='red') # Mux Select

    # Output Q
    ax.arrow(8, 0.5, 0, -0.4, head_width=0.2, color='blue', linewidth=2)
    ax.text(8, -0.1, "q [32 bits]", ha='center', weight='bold', color='blue')
    
    # ---------------------------------------------------------
    # 4. Word Select (Offset Logic)
    # ---------------------------------------------------------
    # Offset selects lower or upper 32 bits of 64-bit block
    ax.text(12, 1.0, "Word Select Logic", fontsize=10, style='italic')
    ax.plot([12, 11], [10.5, 1.25], 'k:', alpha=0.5) # Line from Offset
    ax.text(12.2, 0.5, "mem[Offset <= 3 ? 31:0 : 63:32]", fontsize=9, bbox=dict(facecolor='white', alpha=0.8))

    # Title and Parameters
    plt.text(0.5, 12, "Verilog Cache Hardware Visualization", fontsize=16, weight='bold')
    param_text = (
        "Parameters matching Cache.v:\n"
        "NWAYS = 4\n"
        "NSETS = 1024\n"
        "BLOCK_SIZE = 64 bits (MWIDTH)\n"
        "TAG_WIDTH = 19\n"
        "INDEX_WIDTH = 10\n"
        "OFFSET_WIDTH = 3"
    )
    plt.text(0.5, 10.5, param_text, fontsize=10, family='monospace', bbox=dict(facecolor='#eceff1'))

    ax.set_xlim(0, 16.5)
    ax.set_ylim(-1, 13)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('cache_hardware_diagram.png', dpi=150)
    plt.show()

if __name__ == "__main__":
    try:
        draw_cache_hardware()
        print("Diagram generated successfully.")
    except Exception as e:
        print(f"Error generating diagram: {e}")