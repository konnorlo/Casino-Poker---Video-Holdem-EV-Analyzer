import pygame
import sys
import os
from time import sleep
import threading
from pygame.locals import *
import importlib.util
import math

#   to use this bot:
#   instructions are included
#   first type in 2 of your cards
#   then type in flop
#   boom ev  
# 
#   run with
#
#   /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 1_hand_gui.py

# Import the 1_hand.py module dynamically
spec = importlib.util.spec_from_file_location("hand_analyzer", "1_hand.py")
hand_analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hand_analyzer)

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
FPS = 60
CARD_WIDTH = 48  # Reduced to 2/5 of original size (120 * 0.4)
CARD_HEIGHT = 70  # Reduced to 2/5 of original size (174 * 0.4)
PADDING = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (220, 0, 0)
BLUE = (0, 0, 220)
GOLD = (218, 165, 32)
DARK_GREEN = (0, 100, 0)
LIGHT_BLUE = (173, 216, 230)

# Font setup
FONT_SMALL = pygame.font.Font(None, 28)
FONT_MEDIUM = pygame.font.Font(None, 36)
FONT_LARGE = pygame.font.Font(None, 48)
FONT_TITLE = pygame.font.Font(None, 72)

# Card setup
suits = {"s": "S", "h": "H", "d": "D", "c": "C"}  # Using letters instead of symbols
ranks = {
    "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7", "8": "8", "9": "9", 
    "T": "10", "J": "J", "Q": "Q", "K": "K", "A": "A"
}
suit_colors = {"s": BLACK, "h": RED, "d": RED, "c": BLACK}

# Card selection state
selected_cards = []
card_slots = ["hero1", "hero2", "flop1", "flop2", "flop3"]
results = None
simulation_running = False
animation_complete = False

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color, font=FONT_MEDIUM, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.action = action
        self.is_hovered = False
        
    def draw(self, surface):
        # Draw button
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        
        # Draw text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.action:
                return self.action()
        return None
    
class ExitButton(Button):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Exit", RED, (180, 0, 0), WHITE, action=self.exit_game)

    def exit_game(self):
        pygame.quit()
        sys.exit()

class Card:
    def __init__(self, rank, suit, x, y):
        self.rank = rank
        self.suit = suit
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.selected = False
        
    def draw(self, surface):
        # Draw card background
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=3)
        pygame.draw.rect(surface, BLACK, self.rect, 1, border_radius=3)
        
        # Draw highlight if selected
        if self.selected:
            highlight_rect = self.rect.inflate(6, 6)
            pygame.draw.rect(surface, GOLD, highlight_rect, 2, border_radius=4)
        
        # Draw rank and suit
        rank_text = ranks[self.rank]
        suit_text = suits[self.suit]
        suit_color = suit_colors[self.suit]
        
        # Create a combined text (rank + suit)
        combined_text = f"{rank_text}{suit_text}"
        text_surf = pygame.font.Font(None, 22).render(combined_text, True, suit_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.selected = not self.selected
                return f"{self.rank}{self.suit}"
        return None

class CardSelector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cards = []
        self.create_cards()
        
    def create_cards(self):
        # Create all 52 cards in a grid
        x, y = self.x, self.y
        cards_per_row = 13
        
        for suit in ["s", "h", "d", "c"]:
            for i, rank in enumerate(["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]):
                card_x = x + (i % cards_per_row) * (CARD_WIDTH * 1.3)
                card_y = y + (list(["s", "h", "d", "c"]).index(suit)) * (CARD_HEIGHT * 1.3)
                self.cards.append(Card(rank, suit, card_x, card_y))
    
    def draw(self, surface):
        for card in self.cards:
            card.draw(surface)
    
    def handle_event(self, event):
        for card in self.cards:
            card_id = card.handle_event(event)
            if card_id:
                # Check if this card is already selected
                if card.selected:
                    if card_id not in selected_cards and len(selected_cards) < 5:
                        selected_cards.append(card_id)
                else:
                    if card_id in selected_cards:
                        selected_cards.remove(card_id)
                return True
        return False

class CardPlaceholder:
    def __init__(self, x, y, label):
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.label = label
        
    def draw(self, surface, card_value=None):
        # Draw background
        pygame.draw.rect(surface, LIGHT_BLUE if not card_value else WHITE, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)
        
        if card_value:
            # Draw the actual card
            rank = card_value[0].upper()
            suit = card_value[1].lower()
            
            # Draw rank and suit
            rank_text = ranks[rank]
            suit_text = suits[suit]
            suit_color = suit_colors[suit]
            
            rank_surf = FONT_SMALL.render(rank_text, True, suit_color)
            suit_surf = FONT_SMALL.render(suit_text, True, suit_color)
            
            # Top left
            surface.blit(rank_surf, (self.rect.left + 3, self.rect.top + 5))
            surface.blit(suit_surf, (self.rect.left + 3, self.rect.top + 50))
            
            # Center suit (bigger)
            center_suit = pygame.font.Font(None, 16).render(suit_text, True, suit_color)
            center_rect = center_suit.get_rect(center=self.rect.center)
            surface.blit(center_suit, center_rect)
            
            # Bottom right (upside down)
            surface.blit(rank_surf, (self.rect.right - 16, self.rect.bottom - 25))
            surface.blit(suit_surf, (self.rect.right - 16, self.rect.bottom - 65))
        else:
            # Draw placeholder text
            text_surf = FONT_SMALL.render(self.label, True, WHITE)
            text_rect = text_surf.get_rect(center=self.rect.midbottom)
            text_rect.y += 13
            surface.blit(text_surf, text_rect)

def run_simulation():
    global results, simulation_running, animation_complete
    
    try:
        # Extract the cards
        hero_cards = f"{selected_cards[0]} {selected_cards[1]}"
        flop_cards = f"{selected_cards[2]} {selected_cards[3]} {selected_cards[4]}"
        
        # Use the imported module to run the simulation
        results = hand_analyzer.casino_holdem_simulation(hero_cards, flop_cards)
        
    except Exception as e:
        print(f"Error in simulation: {e}")
        results = {"error": str(e)}
    
    simulation_running = False
    animation_complete = False

def draw_loading_animation(surface, progress):
    # Draw a circular loading animation
    center_x = WINDOW_WIDTH // 2
    center_y = WINDOW_HEIGHT // 2
    radius = 50
    
    # Background circle
    pygame.draw.circle(surface, LIGHT_BLUE, (center_x, center_y), radius)
    
    # Progress arc
    rect = pygame.Rect(center_x - radius, center_y - radius, radius * 2, radius * 2)
    start_angle = -90  # Start from the top
    end_angle = start_angle + (360 * progress)
    pygame.draw.arc(surface, BLUE, rect, math.radians(start_angle), math.radians(end_angle), width=10)
    
    # Text
    text = FONT_MEDIUM.render("Simulating...", True, BLACK)
    text_rect = text.get_rect(center=(center_x, center_y + radius + 30))
    surface.blit(text, text_rect)

def draw_results(surface):
    if not results:
        return
    
    if "error" in results:
        # Draw error message
        error_text = FONT_MEDIUM.render(f"Error: {results['error']}", True, RED)
        error_rect = error_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150))
        surface.blit(error_text, error_rect)
        return
    
    # Draw results box
    result_box = pygame.Rect(100, WINDOW_HEIGHT - 280, WINDOW_WIDTH - 200, 220)
    pygame.draw.rect(surface, WHITE, result_box, border_radius=10)
    pygame.draw.rect(surface, BLACK, result_box, 2, border_radius=10)
    
    # Title
    title_text = FONT_LARGE.render("Simulation Results", True, BLUE)
    title_rect = title_text.get_rect(centerx=result_box.centerx, top=result_box.top + 10)
    surface.blit(title_text, title_rect)
    
    # Draw probabilities
    y_pos = title_rect.bottom + 10
    win_text = FONT_MEDIUM.render(f"Win probability: {results['win_probability']:.4f}", True, BLACK)
    tie_text = FONT_MEDIUM.render(f"Tie probability: {results['tie_probability']:.4f}", True, BLACK)
    loss_text = FONT_MEDIUM.render(f"Loss probability: {results['loss_probability']:.4f}", True, BLACK)
    
    surface.blit(win_text, (result_box.left + 20, y_pos))
    surface.blit(tie_text, (result_box.left + 20, y_pos + 40))
    surface.blit(loss_text, (result_box.left + 20, y_pos + 80))
    
    # Draw EV
    call_ev_text = FONT_MEDIUM.render(f"EV of calling (3x): {results['call_ev']:.4f}", True, BLACK)
    fold_ev_text = FONT_MEDIUM.render(f"EV of folding: {results['fold_ev']:.4f}", True, BLACK)
    
    surface.blit(call_ev_text, (result_box.centerx + 20, y_pos))
    surface.blit(fold_ev_text, (result_box.centerx + 20, y_pos + 40))
    
    # Draw recommendation
    rec_color = GREEN if results['recommendation'] == 'CALL' else RED
    rec_text = FONT_LARGE.render(f"Recommendation: {results['recommendation']}", True, rec_color)
    rec_rect = rec_text.get_rect(centerx=result_box.centerx, bottom=result_box.bottom - 20)
    surface.blit(rec_text, rec_rect)

def main():
    global selected_cards, results, simulation_running, animation_complete

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Casino Hold'em Analyzer")
    clock = pygame.time.Clock()

    selector = CardSelector(50, 350)

    hero_placeholders = [
        CardPlaceholder(250, 85, "Your Card 1"),
        CardPlaceholder(400, 85, "Your Card 2")
    ]

    flop_placeholders = [
        CardPlaceholder(250, 205, "Flop Card 1"),
        CardPlaceholder(400, 205, "Flop Card 2"),
        CardPlaceholder(550, 205, "Flop Card 3")
    ]

    simulate_button = Button(
        700, 90, 200, 50, "Run Simulation",
        GREEN, DARK_GREEN, WHITE,
        action=lambda: start_simulation(selector) if len(selected_cards) == 5 else None
    )

    clear_button = Button(
        700, 160, 200, 50, "Clear Cards",
        RED, (190, 0, 0), WHITE,
        action=lambda: clear_selection(selector)
    )

    exit_button = ExitButton(700, 230, 200, 50)

    animation_frame = 0
    animation_speed = 0.1
    last_frame_time = 0

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if not simulation_running and len(selected_cards) < 5:
                selector.handle_event(event)

            simulate_button.handle_event(event)
            clear_button.handle_event(event)
            exit_button.handle_event(event)

        simulate_button.update(mouse_pos)
        clear_button.update(mouse_pos)
        exit_button.update(mouse_pos)

        screen.fill(DARK_GREEN)

        title_text = FONT_TITLE.render("Casino Hold'em Analyzer", True, WHITE)
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 20))

        for i, placeholder in enumerate(hero_placeholders):
            if i < len(selected_cards):
                placeholder.draw(screen, selected_cards[i])
            else:
                placeholder.draw(screen)

        for i, placeholder in enumerate(flop_placeholders):
            if i + 2 < len(selected_cards):
                placeholder.draw(screen, selected_cards[i + 2])
            else:
                placeholder.draw(screen)

        instruction_text = FONT_SMALL.render("Select 5 cards: 2 for your hand, 3 for the flop", True, WHITE)
        screen.blit(instruction_text, (50, 320))

        selector.draw(screen)

        simulate_button.draw(screen)
        clear_button.draw(screen)
        exit_button.draw(screen)

        if simulation_running:
            if current_time - last_frame_time > animation_speed * 1000:
                animation_frame = (animation_frame + 1) % 100
                last_frame_time = current_time
            draw_loading_animation(screen, animation_frame / 100)
        elif results and not animation_complete:
            if current_time - last_frame_time > animation_speed * 1000:
                animation_frame = min(animation_frame + 1, 100)
                last_frame_time = current_time
                if animation_frame == 100:
                    animation_complete = True
            draw_results(screen)
        elif results:
            draw_results(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

# Updated start_simulation and clear_selection
def start_simulation(selector):
    global simulation_running
    if len(selected_cards) == 5 and not simulation_running:
        simulation_running = True
        threading.Thread(target=run_simulation).start()

def clear_selection(selector):
    global selected_cards, results, animation_complete
    selected_cards = []
    results = None
    animation_complete = False
    for card in selector.cards:
        card.selected = False

if __name__ == "__main__":
    main()

### run with
#      /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 1_hand_gui.py