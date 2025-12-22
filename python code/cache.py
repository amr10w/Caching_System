import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_cache_structure():
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Parameters from Verilog
    n_ways = 4
    n_sets = "1024 Sets (INDEX)"
    tag_w = "19 bits (TAG)"
    data_w = "64 bits (BLOCK_SIZE)"
    
    colors = ['#e1f5fe', '#fff9c4', '#f1f8e9', '#fce4ec']
    labels = ['Way 1', 'Way 2', 'Way 3', 'Way 4']
    
    # Draw the 4 Ways
    for i in range(n_ways):
        # Main rectangle for each Way
        rect_x = i * 2.5
        ax.add_patch(patches.Rectangle((rect_x, 0), 2, 6, linewidth=2, edgecolor='black', facecolor=colors[i]))
        
        # Sub-sections (Status bits, Tag, Data)
        # Status (V/D/LRU)
        ax.add_patch(patches.Rectangle((rect_x, 5.2), 2, 0.8, linewidth=1, edgecolor='black', fill=False))
        ax.text(rect_x + 1, 5.6, "Status\n(V, D, LRU)", ha='center', va='center', fontsize=9)
        
        # Tag section
        ax.add_patch(patches.Rectangle((rect_x, 4), 2, 1.2, linewidth=1, edgecolor='black', fill=False))
        ax.text(rect_x + 1, 4.6, f"TAG\n{tag_w}", ha='center', va='center', fontsize=9, fontweight='bold')
        
        # Data section
        ax.add_patch(patches.Rectangle((rect_x, 0), 2, 4, linewidth=1, edgecolor='black', fill=False))
        ax.text(rect_x + 1, 2, f"DATA MEM\n{data_w}\n(2 Words)", ha='center', va='center', fontsize=9)
        
        ax.text(rect_x + 1, -0.5, labels[i], ha='center', fontsize=12, fontweight='bold')

    # Add Indicators for NSETS (Rows)
    ax.annotate('', xy=(-0.5, 0), xytext=(-0.5, 5), arrowprops=dict(arrowstyle='<->'))
    ax.text(-1.2, 2.5, n_sets, rotation=90, va='center', fontweight='bold')

    # Title and Legend
    plt.title("4-Way Set Associative Cache Visualization", fontsize=16, pad=20)
    plt.axis('off')
    plt.xlim(-2, 10)
    plt.ylim(-1, 7)
    
    description = (
        "1. INDEX: Selects 1 of 1024 rows.\n"
        "2. TAG: Compared across all 4 ways simultaneously.\n"
        "3. OFFSET: Selects which Word (WORD1/WORD2) to send to CPU.\n"
        "4. LRU: Decides which way to kick out on a MISS."
    )
    plt.text(-1, -1.2, description, fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    draw_cache_structure()