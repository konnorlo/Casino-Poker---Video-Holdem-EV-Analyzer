import pygame
import sys
import os
import threading
import importlib.util
import math
from pygame.locals import *

# Dynamically import the 1_hand_bonus.py as 'hand_bonus'
spec = importlib.util.spec_from_file_location("hand_bonus", "1_hand_bonus.py")
hand_bonus = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hand_bonus)

pygame.init()

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 750
FPS = 60
CARD_WIDTH = 48
CARD_HEIGHT = 70
PADDING = 100

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (220, 0, 0)
BLUE = (0, 0, 220)
GOLD = (218, 165, 32)
DARK_GREEN = (0, 100, 0)
LIGHT_BLUE = (173, 216, 230)

FONT_TINY = pygame.font.Font(None, 17)
FONT_SMALL = pygame.font.Font(None, 26)
FONT_MEDIUM = pygame.font.Font(None, 34)
FONT_LARGE = pygame.font.Font(None, 46)
FONT_TITLE = pygame.font.Font(None, 70)

suits = {"s": "S", "h": "H", "d": "D", "c": "C"}
ranks = {
    "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7", "8": "8", "9": "9", 
    "T": "10", "J": "J", "Q": "Q", "K": "K", "A": "A"
}
suit_colors = {"s": BLACK, "h": RED, "d": RED, "c": BLACK}

selected_cards = []
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
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
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
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=3)
        pygame.draw.rect(surface, BLACK, self.rect, 1, border_radius=3)
        if self.selected:
            highlight_rect = self.rect.inflate(6, 6)
            pygame.draw.rect(surface, GOLD, highlight_rect, 2, border_radius=4)
        rank_text = ranks[self.rank]
        suit_text = suits[self.suit]
        suit_color = suit_colors[self.suit]
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
        pygame.draw.rect(surface, LIGHT_BLUE if not card_value else WHITE, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)
        if card_value:
            rank = card_value[0].upper()
            suit = card_value[1].lower()
            rank_text = ranks[rank]
            suit_text = suits[suit]
            suit_color = suit_colors[suit]
            rank_surf = FONT_SMALL.render(rank_text, True, suit_color)
            suit_surf = FONT_SMALL.render(suit_text, True, suit_color)
            surface.blit(rank_surf, (self.rect.left + 3, self.rect.top + 5))
            surface.blit(suit_surf, (self.rect.left + 3, self.rect.top + 50))
            center_suit = pygame.font.Font(None, 16).render(suit_text, True, suit_color)
            center_rect = center_suit.get_rect(center=self.rect.center)
            surface.blit(center_suit, center_rect)
            surface.blit(rank_surf, (self.rect.right - 16, self.rect.bottom - 25))
            surface.blit(suit_surf, (self.rect.right - 16, self.rect.bottom - 65))
        else:
            text_surf = FONT_SMALL.render(self.label, True, WHITE)
            text_rect = text_surf.get_rect(center=self.rect.midbottom)
            text_rect.y += 13
            surface.blit(text_surf, text_rect)

def run_simulation():
    global results, simulation_running, animation_complete
    try:
        hero_cards = f"{selected_cards[0]} {selected_cards[1]}"
        flop_cards = f"{selected_cards[2]} {selected_cards[3]} {selected_cards[4]}"
        results = hand_bonus.casino_holdem_simulation(hero_cards, flop_cards)
    except Exception as e:
        print(f"Error in simulation: {e}")
        results = {"error": str(e)}
    simulation_running = False
    animation_complete = False

def draw_loading_animation(surface, progress):
    center_x = WINDOW_WIDTH // 2
    center_y = WINDOW_HEIGHT // 2
    radius = 50
    pygame.draw.circle(surface, LIGHT_BLUE, (center_x, center_y), radius)
    rect = pygame.Rect(center_x - radius, center_y - radius, radius * 2, radius * 2)
    start_angle = -90
    end_angle = start_angle + (360 * progress)
    pygame.draw.arc(surface, BLUE, rect, math.radians(start_angle), math.radians(end_angle), width=10)
    text = FONT_MEDIUM.render("Simulating...", True, BLACK)
    text_rect = text.get_rect(center=(center_x, center_y + radius + 30))
    surface.blit(text, text_rect)

def draw_results(surface):
    if not results:
        return
    if "error" in results:
        error_text = FONT_MEDIUM.render(f"Error: {results['error']}", True, RED)
        error_rect = error_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150))
        surface.blit(error_text, error_rect)
        return
    result_box = pygame.Rect(100, WINDOW_HEIGHT - 350, WINDOW_WIDTH - 200, 310)
    pygame.draw.rect(surface, WHITE, result_box, border_radius=10)
    pygame.draw.rect(surface, BLACK, result_box, 2, border_radius=10)
    title_text = FONT_LARGE.render("Simulation Results", True, BLUE)
    title_rect = title_text.get_rect(centerx=result_box.centerx, top=result_box.top + 8)
    surface.blit(title_text, title_rect)
    y_pos = title_rect.bottom + 10

    txt = [
        f"EV from Ante bet:    {results['ante_ev']:.4f} units",
        f"EV from Play bet:    {results['play_ev']:.4f} units",
        f"EV from Bonus bet:   {results['bonus_ev']:.4f} units",
        f"EV if Call+Bonus:    {results['call_ev_with_bonus']:.4f} units",
        f"EV if Call only:     {results['call_ev_without_bonus']:.4f} units",
        f"EV if Fold+Bonus:    {results['fold_ev_with_bonus']:.4f} units",
        f"EV if Fold only:     {results['fold_ev_without_bonus']:.4f} units",
        f"Bonus Hit Rate:      {results['bonus_hit_rate']:.2f}%",
        f"Avg Bonus Win:       {results['bonus_average_win']:.2f} units",
        f"Win/Push/Loss:       {results['win_pct']:.2f}% / {results['push_pct']:.2f}% / {results['loss_pct']:.2f}%",
        f"Recommendation:      {results['recommendation']} | Bonus: {results['bonus_recommendation']}"
    ]
    for i, line in enumerate(txt):
        line_surf = FONT_TINY.render(line, True, BLACK)
        surface.blit(line_surf, (result_box.left + 25, y_pos + i * 21))
    # Show hand frequencies (up to 6 most frequent, or those > 0.1%)
    hand_freqs = sorted(results['hand_percentages'].items(), key=lambda x: -x[1])
    freq_lines = [f"{hn}: {pc:.2f}%" for hn, pc in hand_freqs if pc > 0.1][:6]
    y_hand = result_box.bottom - 45
    for freq in freq_lines:
        hsurf = FONT_SMALL.render(freq, True, BLUE)
        surface.blit(hsurf, (result_box.left + 35, y_hand))
        y_hand += 22

def main():
    global selected_cards, results, simulation_running, animation_complete
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Casino Hold'em Bonus Analyzer")
    clock = pygame.time.Clock()
    selector = CardSelector(50, 350)
    hero_placeholders = [CardPlaceholder(250, 85, "Your Card 1"), CardPlaceholder(400, 85, "Your Card 2")]
    flop_placeholders = [CardPlaceholder(250, 205, "Flop Card 1"), CardPlaceholder(400, 205, "Flop Card 2"), CardPlaceholder(550, 205, "Flop Card 3")]
    simulate_button = Button(700, 90, 250, 52, "Run Simulation", GREEN, DARK_GREEN, WHITE, action=lambda: start_simulation(selector) if len(selected_cards) == 5 else None)
    clear_button = Button(700, 160, 250, 52, "Clear Cards", RED, (190, 0, 0), WHITE, action=lambda: clear_selection(selector))
    exit_button = ExitButton(700, 230, 250, 52)
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
        title_text = FONT_TITLE.render("Casino Hold'em Bonus Analyzer", True, WHITE)
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
