import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_cache_structure():
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Define Dimensions based on Verilog parameters
    n_ways = 4
    n_sets = 8 # Simplified for drawing (actually 1024)
    
    # 1. Address Breakdown (Top)
    ax.add_patch(patches.Rectangle((2, 9), 6, 0.6, edgecolor='black', facecolor='white', lw=2))
    ax.text(5, 9.7, "CPU Address (32 bits)", fontsize=12, ha='center', weight='bold')
    # Labeling address segments
    ax.text(3, 9.2, "Tag (19 bits)", ha='center', fontsize=9)
    ax.text(5, 9.2, "Index (10 bits)", ha='center', fontsize=9)
    ax.text(7, 9.2, "Offset (3 bits)", ha='center', fontsize=9)
    ax.plot([4, 4], [9, 9.6], color='black', lw=1)
    ax.plot([6, 6], [9, 9.6], color='black', lw=1)

    # 2. Drawing the 4 Ways (Rectangles)
    way_labels = ["Way 1", "Way 2", "Way 3", "Way 4"]
    colors = ['#e1f5fe', '#e8f5e9', '#fff3e0', '#fce4ec']
    
    for i in range(n_ways):
        x_offset = i * 2.5 + 0.5
        # Draw Way Container
        ax.add_patch(patches.Rectangle((x_offset, 4), 2, 4, edgecolor='black', facecolor=colors[i], alpha=0.5))
        ax.text(x_offset + 1, 8.2, way_labels[i], ha='center', weight='bold')
        
        # Columns inside each way
        ax.text(x_offset + 0.2, 7.7, "V", fontsize=8) # Valid bit
        ax.text(x_offset + 0.6, 7.7, "Tag", fontsize=8) # TAG_WIDTH
        ax.text(x_offset + 1.4, 7.7, "Data", fontsize=8) # MWIDTH
        
        # Highlight a specific "Set" (Row)
        ax.add_patch(patches.Rectangle((x_offset, 5.5), 2, 0.4, color='gray', alpha=0.3))
        if i == 0:
            ax.text(x_offset - 0.4, 5.6, "Index k", fontsize=8)

    # 3. Logic Components (Bottom)
    # Comparators
    for i in range(n_ways):
        x = i * 2.5 + 1.5
        ax.add_circle = plt.Circle((x, 3.2), 0.3, color='black', fill=False)
        ax.add_artist(ax.add_circle)
        ax.text(x, 3.1, "=", ha='center', fontsize=12, weight='bold')
        
        # Lines from Tag to Comparator
        ax.annotate('', xy=(x, 3.5), xytext=(x, 5.5), arrowprops=dict(arrowstyle='->'))

    # MUX
    mux = patches.FancyBboxPatch((3, 1.5), 4, 0.8, boxstyle="round,pad=0.1", fc="lightgray", ec="black")
    ax.add_patch(mux)
    ax.text(5, 1.8, "4-to-1 Multiplexor", ha='center', weight='bold')

    # 4. Final Data Output
    ax.annotate('', xy=(5, 0.5), xytext=(5, 1.5), arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(5, 0.2, "Output Data (32 bits / WIDTH)", ha='center', weight='bold', color='blue')

    # Formatting
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.title("4-Way Set Associative Cache Architecture (Verilog Mapping)", fontsize=14)
    plt.tight_layout()
    plt.show()

draw_cache_structure()