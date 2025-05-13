import sys
import pygame
import random
import os

def resource_path(relative_path):
    """ Get absolute path to resources for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quantum Cheat Sheet Heist")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game states
STATE_ALICE_BIT = 0
STATE_ALICE_BASIS = 1
STATE_BOB = 2
STATE_EVE = 3
STATE_SIFTING = 4
STATE_RESULT = 5

class QKDGame:
    def __init__(self):
        self.num_photons = 10
        self.reset_game()
        self.header_image = None
        self.image_height = 0
        
        try:
            # Load and scale image to match window width
            original_image = pygame.image.load(resource_path('image.png'))
            target_width = WIDTH  # Use full window width
            print(original_image.get_width, original_image.get_height)
            
            # Calculate proportional height
            # scale_factor = target_width / original_image.get_width()
            # target_height = int(original_image.get_height() * scale_factor)
            target_height = 300
            
            # Scale image and get dimensions
            self.header_image = pygame.transform.smoothscale(original_image, (target_width, target_height))
            self.image_height = self.header_image.get_height()  # Set AFTER scaling
            
        except Exception as e:
            print(f"Image loading error: {e}")
            self.header_image = None
            self.image_height = 0

    def reset_game(self):
        self.state = STATE_ALICE_BIT
        self.photons = [{
            'alice_bit': None,
            'alice_basis': None,
            'bob_basis': None,
            'eve_basis': None,
            'eve_bit': None,
            'bob_result': None,
            'error': False
        } for _ in range(self.num_photons)]
        self.current_photon = 0
        self.sifted_key = []
        self.eve_key = []
        self.revealed_bits = []
        self.errors = 0

    def draw_stick_figure(self, x, y, color):
        pygame.draw.circle(screen, color, (x, y), 20, 2)
        pygame.draw.line(screen, color, (x, y+20), (x, y+60), 2)
        pygame.draw.line(screen, color, (x-30, y+40), (x+30, y+40), 2)
        pygame.draw.line(screen, color, (x, y+60), (x-20, y+90), 2)
        pygame.draw.line(screen, color, (x, y+60), (x+20, y+90), 2)

    def draw_choice_screen(self, phase):
        font = pygame.font.SysFont('Arial', 40)
        
        # Draw stick figure
        color = BLUE if "Hashir" in phase else GREEN if "Imad" in phase else RED
        self.draw_stick_figure(100, 100 + self.image_height, color)
        
        # Display photon number
        title = font.render(f"Photon {self.current_photon + 1}/{self.num_photons} - {phase}", True, BLACK)
        screen.blit(title, (200, 50 + self.image_height))
        
        # Create buttons based on phase
        buttons = []
        if phase == "Hashir: Choose Bit":
            buttons.append(self.create_button("0", 200, 200 + self.image_height, GREEN))
            buttons.append(self.create_button("1", 450, 200 + self.image_height, RED))
        else:
            buttons.append(self.create_button("+ Basis", 200, 200 + self.image_height, GREEN))
            buttons.append(self.create_button("× Basis", 450, 200 + self.image_height, RED))
        
        return buttons

    def create_button(self, text, x, y, color):
        btn = pygame.Rect(x, y, 150, 60)
        pygame.draw.rect(screen, color, btn)
        font = pygame.font.SysFont('Arial', 30)
        screen.blit(font.render(text, True, WHITE), (x+15, y+15))
        return btn

    def handle_choice(self, choice):
        photon = self.photons[self.current_photon]
        
        if self.state == STATE_ALICE_BIT:
            photon['alice_bit'] = int(choice)
            self.state = STATE_ALICE_BASIS
        elif self.state == STATE_ALICE_BASIS:
            photon['alice_basis'] = choice
            self.state = STATE_BOB
        elif self.state == STATE_BOB:
            photon['bob_basis'] = choice
            self.state = STATE_EVE
        elif self.state == STATE_EVE:
            photon['eve_basis'] = choice
        
            # Eve's interception
            if photon['eve_basis'] == photon['alice_basis']:
                photon['eve_bit'] = photon['alice_bit']
            else:
                photon['eve_bit'] = random.choice([0, 1])
            
            # Bob's measurement
            if photon['bob_basis'] == photon['eve_basis']:
                photon['bob_result'] = photon['eve_bit']
            else:
                photon['bob_result'] = random.choice([0, 1])
            
            self.current_photon += 1
            if self.current_photon >= self.num_photons:
                self.process_sifting()
                self.state = STATE_SIFTING
            else:
                self.state = STATE_ALICE_BIT

    def process_sifting(self):
        self.sifted_key = []
        self.bob_key = []
        self.eve_key = []
        self.sifted_indices = []
        
        for idx, photon in enumerate(self.photons):
            if photon['alice_basis'] == photon['bob_basis']:
                self.sifted_key.append(photon['alice_bit'])
                self.bob_key.append(photon['bob_result'])
                self.sifted_indices.append(idx)
                self.eve_key.append(photon['eve_bit'])
        
        sample_size = max(1, int(len(self.sifted_key) * 1))
        check_indices = random.sample(range(len(self.sifted_key)), min(sample_size, len(self.sifted_key)))
        
        self.errors = 0
        for i in check_indices:
            if self.sifted_key[i] != self.bob_key[i]:
                self.errors += 1
        
        self.revealed_bits = [(i, self.sifted_key[i]) for i in check_indices]

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == STATE_RESULT:
                        if pygame.Rect(300, 300 + self.image_height, 200, 50).collidepoint(mouse_pos):
                            self.reset_game()
                    elif self.state == STATE_SIFTING:
                        self.state = STATE_RESULT
                    else:
                        phase_map = {
                            STATE_ALICE_BIT: "Hashir: Choose Bit",
                            STATE_ALICE_BASIS: "Hashir: Choose Basis",
                            STATE_BOB: "Imad: Choose Basis",
                            STATE_EVE: "Deebaj: Choose Basis"
                        }
                        buttons = self.draw_choice_screen(phase_map[self.state])
                        
                        for i, btn in enumerate(buttons):
                            if btn.collidepoint(mouse_pos):
                                choices = {
                                    STATE_ALICE_BIT: ["0", "1"],
                                    STATE_ALICE_BASIS: ["+", "×"],
                                    STATE_BOB: ["+", "×"],
                                    STATE_EVE: ["+", "×"]
                                }[self.state]
                                self.handle_choice(choices[i])

            # Drawing
            screen.fill(WHITE)
            if self.header_image:
                screen.blit(self.header_image, (0, 0))
            
            if self.state == STATE_RESULT:
                self.draw_results()
            elif self.state == STATE_SIFTING:
                self.draw_sifting()
            else:
                phase_map = {
                    STATE_ALICE_BIT: "Hashir: Choose Bit",
                    STATE_ALICE_BASIS: "Hashir: Choose Basis",
                    STATE_BOB: "Imad: Choose Basis",
                    STATE_EVE: "Deebaj: Choose Basis"
                }
                self.draw_choice_screen(phase_map[self.state])

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
        sys.exit()

    def draw_sifting(self):
        font = pygame.font.SysFont('Arial', 40)
        screen.blit(font.render("Comparing bases...", True, BLACK), (50, 50 + self.image_height))
        screen.blit(font.render(f"Sifted key length: {len(self.sifted_key)}", True, BLACK), (50, 100 + self.image_height))
        pygame.draw.rect(screen, BLUE, (300, 300 + self.image_height, 200, 50))
        screen.blit(font.render("Continue", True, WHITE), (325, 315 + self.image_height))

    def draw_results(self):
        font = pygame.font.SysFont('Arial', 30)
        total_checked = len(self.revealed_bits)
        error_rate = self.errors / total_checked if total_checked > 0 else 0
        
        eve_full_key = (
            len(self.eve_key) == len(self.sifted_key) and 
            all(eve_bit is not None and eve_bit == sifted_bit 
                for eve_bit, sifted_bit in zip(self.eve_key, self.sifted_key))
        )

        detected = error_rate > 0.2
        
        y = 50 + self.image_height
        if detected:
            screen.blit(font.render("Deebaj detected! Transmission aborted!", True, RED), (50, y))
        elif eve_full_key:
            screen.blit(font.render("Deebaj caught you! Plagiarism reported! You both FAIL DAA!!!", True, RED), (50, y))
        else:
            screen.blit(font.render("Answer key shared! You both pass DAA!", True, GREEN), (50, y))
        
        y += 60 
        screen.blit(font.render(f"Hashir's Key: {self.sifted_key}", True, BLACK), (50, y))
        y += 40
        screen.blit(font.render(f"Imad's Key:   {self.bob_key}", True, BLUE), (50, y))
        y += 40
        screen.blit(font.render(f"Deebaj's Knowledge: {self.eve_key}", True, RED), (50, y))
        if detected or not eve_full_key:
            y += 40
            error_text = f"Error rate: {error_rate:.0%} ({self.errors}/{total_checked} errors)"
            screen.blit(font.render(error_text, True, BLACK), (50, y))
        
        pygame.draw.rect(screen, BLUE, (300, 300 + self.image_height, 200, 50))
        screen.blit(font.render("Play Again", True, WHITE), (325, 315 + self.image_height))


if __name__ == "__main__":
    game = QKDGame()
    game.run()