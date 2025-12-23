import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1600, 1000
BACKGROUND_COLOR = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)
LINE_COLOR = (0, 0, 0)

# -----------------------------------------------
# Color Palette
# -----------------------------------------------
# Address Breakdown
COLOR_ADDR_TAG = (255, 204, 188)   # #FFCCBC (Light Red/Orange)
COLOR_ADDR_INDEX = (200, 230, 201) # #C8E6C9 (Light Green)
COLOR_ADDR_OFFSET = (179, 229, 252) # #B3E5FC (Light Blue)

# Way Table
COLOR_WAY_HEADER = (224, 224, 224) # #E0E0E0 (Grey)
COLOR_WAY_ROW_NORMAL = (255, 255, 255)
COLOR_SELECTED_BG = (255, 255, 224) # Light Yellow highlight for whole row
# We will use specific colors for cells in selected row
COLOR_CELL_INDEX = COLOR_ADDR_INDEX
COLOR_CELL_TAG = COLOR_ADDR_TAG
COLOR_CELL_DATA = (209, 196, 233)   # #D1C4E9 (Lavender)
COLOR_CELL_VALID = (245, 245, 245)  # Light Grey

# Logic Components
COLOR_COMP = (255, 224, 178)        # #FFE0B2 (Orange-ish)
COLOR_AND = (255, 249, 196)         # #FFF9C4 (Yellow-ish)
COLOR_OR = (255, 249, 196)
COLOR_MUX = (209, 196, 233)         # #D1C4E9 (Lavender)

# Signals
COLOR_HIT_LINE = (255, 82, 82)      # #FF5252 (Red)
COLOR_DATA_LINE = (63, 81, 181)     # #3F51B5 (Blue)
COLOR_INDEX_LINE = (56, 142, 60)    # Green
COLOR_TAG_LINE = (230, 74, 25)      # Dark Orange

# Fonts
FONT_MAIN = pygame.font.SysFont('Arial', 14)
FONT_BOLD = pygame.font.SysFont('Arial', 14, bold=True)
FONT_LARGE = pygame.font.SysFont('Arial', 18, bold=True)
FONT_SMALL = pygame.font.SysFont('Arial', 12)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cache Hardware Schematic (Colorful)")

def draw_text(surface, text, x, y, font=FONT_MAIN, color=TEXT_COLOR, align="center"):
    text_obj = font.render(str(text), True, color)
    rect = text_obj.get_rect()
    if align == "center":
        rect.center = (x, y)
    elif align == "left":
        rect.topleft = (x, y)
    elif align == "right":
        rect.topright = (x, y)
    surface.blit(text_obj, rect)

def draw_box(surface, x, y, w, h, color, text=None, font=FONT_MAIN, border_width=1):
    pygame.draw.rect(surface, color, (x, y, w, h))
    pygame.draw.rect(surface, LINE_COLOR, (x, y, w, h), border_width)
    if text:
        draw_text(surface, text, x + w//2, y + h//2, font)

def draw_comparator(surface, x, y, r=20):
    pygame.draw.circle(surface, COLOR_COMP, (x, y), r)
    pygame.draw.circle(surface, LINE_COLOR, (x, y), r, 2)
    draw_text(surface, "=", x, y, FONT_LARGE)
    return (x, y, r)

def main():
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)
        
        # ------------------------------------------------------------------
        # 1. Address Register (Top)
        # ------------------------------------------------------------------
        addr_x = WIDTH // 2 - 250
        addr_y = 50
        h = 40
        
        draw_text(screen, "Physical Address [31:0]", WIDTH//2, 20, FONT_LARGE)
        
        # Tag Box (19 bits)
        draw_box(screen, addr_x, addr_y, 200, h, COLOR_ADDR_TAG, "Tag [31:13]", FONT_BOLD)
        # Index Box (10 bits)
        draw_box(screen, addr_x + 200, addr_y, 200, h, COLOR_ADDR_INDEX, "Index [12:3]", FONT_BOLD)
        # Offset Box (3 bits)
        draw_box(screen, addr_x + 400, addr_y, 100, h, COLOR_ADDR_OFFSET, "Offset [2:0]", FONT_BOLD)
        
        # Wires from Address
        tag_wire_start = (addr_x + 100, addr_y + h)
        index_wire_start = (addr_x + 300, addr_y + h)
        
        # Bus Labels
        pygame.draw.line(screen, COLOR_TAG_LINE, tag_wire_start, (tag_wire_start[0], 250), 3)
        draw_text(screen, "/ 19", tag_wire_start[0] - 15, 120, FONT_SMALL, COLOR_TAG_LINE)
        
        pygame.draw.line(screen, COLOR_INDEX_LINE, index_wire_start, (index_wire_start[0], 180), 3)
        draw_text(screen, "/ 10", index_wire_start[0] + 15, 120, FONT_SMALL, COLOR_INDEX_LINE)

        # ------------------------------------------------------------------
        # 2. Cache Ways (Tables)
        # ------------------------------------------------------------------
        way_y_start = 220
        way_width = 300
        way_gap = 50
        total_ways_width = 4 * way_width + 3 * way_gap
        start_x = (WIDTH - total_ways_width) // 2
        
        # Columns widths
        col_idx_w = 60
        col_v_w = 40
        col_tag_w = 100
        col_data_w = 100
        
        row_h = 30
        
        selected_row_y = 0 
        
        ways_info = [] 
        
        for i in range(4):
            wx = start_x + i * (way_width + way_gap)
            wy = way_y_start
            
            # Header
            draw_box(screen, wx, wy, col_idx_w, row_h, COLOR_WAY_HEADER, f"Index", FONT_BOLD)
            draw_box(screen, wx+col_idx_w, wy, col_v_w, row_h, COLOR_WAY_HEADER, "V", FONT_BOLD)
            draw_box(screen, wx+col_idx_w+col_v_w, wy, col_tag_w, row_h, COLOR_WAY_HEADER, f"Tag", FONT_BOLD)
            draw_box(screen, wx+col_idx_w+col_v_w+col_tag_w, wy, col_data_w, row_h, COLOR_WAY_HEADER, "Data", FONT_BOLD)
            
            wy += row_h
            
            # Row 0
            draw_box(screen, wx, wy, col_idx_w, row_h, COLOR_WAY_ROW_NORMAL, "0")
            draw_box(screen, wx+col_idx_w, wy, col_v_w, row_h, COLOR_WAY_ROW_NORMAL, "")
            draw_box(screen, wx+col_idx_w+col_v_w, wy, col_tag_w, row_h, COLOR_WAY_ROW_NORMAL, "")
            draw_box(screen, wx+col_idx_w+col_v_w+col_tag_w, wy, col_data_w, row_h, COLOR_WAY_ROW_NORMAL, "")
            wy += row_h
            
            # Row 1
            draw_box(screen, wx, wy, col_idx_w, row_h, COLOR_WAY_ROW_NORMAL, "1")
            draw_box(screen, wx+col_idx_w, wy, col_v_w, row_h, COLOR_WAY_ROW_NORMAL, "")
            draw_box(screen, wx+col_idx_w+col_v_w, wy, col_tag_w, row_h, COLOR_WAY_ROW_NORMAL, "")
            draw_box(screen, wx+col_idx_w+col_v_w+col_tag_w, wy, col_data_w, row_h, COLOR_WAY_ROW_NORMAL, "")
            wy += row_h
            
            # Dots
            draw_text(screen, "...", wx + way_width//2, wy + 15, FONT_BOLD)
            wy += row_h
            
            # Selected Row (Index K)
            selected_row_y = wy + row_h//2
            draw_box(screen, wx, wy, col_idx_w, row_h, COLOR_CELL_INDEX, "K", FONT_BOLD)
            draw_box(screen, wx+col_idx_w, wy, col_v_w, row_h, COLOR_CELL_VALID, f"v{i+1}")
            draw_box(screen, wx+col_idx_w+col_v_w, wy, col_tag_w, row_h, COLOR_CELL_TAG, f"tag{i+1}")
            draw_box(screen, wx+col_idx_w+col_v_w+col_tag_w, wy, col_data_w, row_h, COLOR_CELL_DATA, f"mem{i+1}")
            
            # Points
            v_pt = (wx + col_idx_w + col_v_w//2, wy + row_h//2)
            tag_pt = (wx + col_idx_w + col_v_w + col_tag_w//2, wy + row_h//2)
            data_pt = (wx + col_idx_w + col_v_w + col_tag_w + col_data_w//2, wy + row_h//2)
            
            ways_info.append({
                'v': v_pt,
                'tag': tag_pt,
                'data': data_pt,
                'way_center_x': wx + way_width//2,
                'tag_center_x': tag_pt[0]
            })
            
            wy += row_h
            
            # Dots
            draw_text(screen, "...", wx + way_width//2, wy + 15, FONT_BOLD)
            wy += row_h
            
            # Row 1023
            draw_box(screen, wx, wy, col_idx_w, row_h, COLOR_WAY_ROW_NORMAL, "1023")
            draw_box(screen, wx+col_idx_w, wy, col_v_w, row_h, COLOR_WAY_ROW_NORMAL, "")
            draw_box(screen, wx+col_idx_w+col_v_w, wy, col_tag_w, row_h, COLOR_WAY_ROW_NORMAL, "")
            draw_box(screen, wx+col_idx_w+col_v_w+col_tag_w, wy, col_data_w, row_h, COLOR_WAY_ROW_NORMAL, "")
            
        # ------------------------------------------------------------------
        # 3. Connections - Index & Tag
        # ------------------------------------------------------------------
        # Route Index Wire
        pygame.draw.line(screen, COLOR_INDEX_LINE, index_wire_start, (index_wire_start[0], selected_row_y), 3)
        pygame.draw.line(screen, COLOR_INDEX_LINE, (start_x - 50, selected_row_y), (start_x + total_ways_width, selected_row_y), 3) 
        for i in range(4):
            wx = start_x + i * (way_width + way_gap)
            pygame.draw.circle(screen, COLOR_INDEX_LINE, (wx, selected_row_y), 5) 
            
        # Main Tag Bus Horizontal
        pygame.draw.line(screen, COLOR_TAG_LINE, (tag_wire_start[0], 200), (WIDTH - 100, 200), 3)
        pygame.draw.line(screen, COLOR_TAG_LINE, (tag_wire_start[0], 200), tag_wire_start, 3) 
        
        # ------------------------------------------------------------------
        # 4. Logic Gates (Below Ways)
        # ------------------------------------------------------------------
        logic_y_start = 550
        
        mux_inputs = []
        hits = []
        
        for i, info in enumerate(ways_info):
            # Comparator
            comp_x = info['tag_center_x']
            comp_y = logic_y_start
            
            # Line from Way Tag to Comparator
            pygame.draw.line(screen, COLOR_TAG_LINE, info['tag'], (comp_x, comp_y - 20), 2)
            pygame.draw.circle(screen, COLOR_TAG_LINE, info['tag'], 3)
            
            # Line from Address Tag Bus to Comparator
            pygame.draw.line(screen, COLOR_TAG_LINE, (comp_x - 15, 200), (comp_x - 15, comp_y - 20), 2)
            pygame.draw.circle(screen, COLOR_TAG_LINE, (comp_x - 15, 200), 3) 
            
            draw_comparator(screen, comp_x, comp_y)
            
            # AND Gate (Below Comparator)
            and_y = comp_y + 80
            
            # Valid Bit Routing
            pygame.draw.line(screen, LINE_COLOR, info['v'], (info['v'][0], and_y), 2)
            pygame.draw.circle(screen, LINE_COLOR, info['v'], 3)
            
            and_x = (info['v'][0] + comp_x) // 2
            
            # Connect Comparator Out -> And
            pygame.draw.line(screen, LINE_COLOR, (comp_x, comp_y + 20), (comp_x, and_y), 2) 
            pygame.draw.line(screen, LINE_COLOR, (comp_x, and_y), (and_x + 10, and_y), 2)
            
            # Connect Valid -> And
            pygame.draw.line(screen, LINE_COLOR, (info['v'][0], and_y), (and_x - 10, and_y), 2) 
            
            # Draw Gate
            draw_box(screen, and_x - 20, and_y, 40, 30, COLOR_AND, "&")
            
            hits.append((and_x, and_y + 30))
            
            # Data Routing for MUX
            data_x = info['data'][0]
            mux_inputs.append(data_x)
            
            pygame.draw.line(screen, COLOR_DATA_LINE, info['data'], (data_x, 700), 2)
            pygame.draw.circle(screen, COLOR_DATA_LINE, info['data'], 3)
            
        # ------------------------------------------------------------------
        # 5. MUX & Final Output
        # ------------------------------------------------------------------
        mux_w = 400
        mux_h = 60
        mux_x = WIDTH // 2 - mux_w // 2
        mux_y = 700
        
        draw_box(screen, mux_x, mux_y, mux_w, mux_h, COLOR_MUX, "4-to-1 Multiplexor", FONT_LARGE)
        
        # Connect Data lines to MUX
        for dx in mux_inputs:
            pygame.draw.line(screen, COLOR_DATA_LINE, (dx, 650), (dx, mux_y), 2)
            
        # OR Gate
        or_x = mux_x - 100
        or_y = mux_y + 20
        draw_box(screen, or_x, or_y, 40, 40, COLOR_OR, "OR") 
        
        # Route Hits
        for hx, hy in hits:
            # Route to OR gate
            pygame.draw.line(screen, COLOR_HIT_LINE, (hx, hy), (hx, or_y - 10), 2) 
            pygame.draw.line(screen, COLOR_HIT_LINE, (hx, or_y - 10), (or_x + 20, or_y - 10), 2) 
            pygame.draw.line(screen, COLOR_HIT_LINE, (or_x + 20, or_y - 10), (or_x + 20, or_y), 2) 
            
            # Route to MUX (Select)
            pygame.draw.line(screen, COLOR_HIT_LINE, (hx, hy + 20), (mux_x, hy + 80), 1)
            
        # Output OR Gate -> hit_miss
        pygame.draw.line(screen, COLOR_HIT_LINE, (or_x + 20, or_y + 40), (or_x + 20, or_y + 80), 3)
        draw_text(screen, "hit_miss", or_x + 20, or_y + 90, FONT_BOLD, COLOR_HIT_LINE)
            
        # Output Mux -> Data
        pygame.draw.line(screen, COLOR_DATA_LINE, (WIDTH//2, mux_y + mux_h), (WIDTH//2, mux_y + mux_h + 50), 4)
        draw_text(screen, "Data (q)", WIDTH//2, mux_y + mux_h + 60, FONT_LARGE, COLOR_DATA_LINE)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
