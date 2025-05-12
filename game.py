import pygame
import random
import sys

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
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
        screen.fill(WHITE)
        font = pygame.font.SysFont('Arial', 40)
        
        # Draw stick figure
        color = BLUE if "Alice" in phase else GREEN if "Bob" in phase else RED
        self.draw_stick_figure(100, 100, color)
        
        # Display photon number
        title = font.render(f"Photon {self.current_photon + 1}/{self.num_photons} - {phase}", True, BLACK)
        screen.blit(title, (200, 50))
        
        # Create buttons based on phase
        buttons = []
        if phase == "Alice: Choose Bit":
            buttons.append(self.create_button("0", 200, 200, GREEN))
            buttons.append(self.create_button("1", 450, 200, RED))
        else:
            buttons.append(self.create_button("+ Basis", 200, 200, GREEN))
            buttons.append(self.create_button("× Basis", 450, 200, RED))
        
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
                photon['eve_bit'] = random.choice([0, 1])  # 50% chance of error
            
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
        # Sift the key by matching bases
        self.sifted_key = []  # Alice's key
        self.bob_key = []     # Bob's key
        self.eve_key = []
        self.sifted_indices = []  # Track original photon indices
        
        for idx, photon in enumerate(self.photons):
            if photon['alice_basis'] == photon['bob_basis']:
                self.sifted_key.append(photon['alice_bit'])
                self.bob_key.append(photon['bob_result'])
                self.sifted_indices.append(idx)
                self.eve_key.append(photon['eve_bit'])
        
        # Error checking - compare Alice's and Bob's sifted keys
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
                        if pygame.Rect(300, 500, 200, 50).collidepoint(mouse_pos):
                            self.reset_game()
                    elif self.state == STATE_SIFTING:
                        self.state = STATE_RESULT
                    else:
                        phase_map = {
                            STATE_ALICE_BIT: "Alice: Choose Bit",
                            STATE_ALICE_BASIS: "Alice: Choose Basis",
                            STATE_BOB: "Bob: Choose Basis",
                            STATE_EVE: "Eve: Choose Basis"
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
            
            if self.state == STATE_RESULT:
                self.draw_results()
            elif self.state == STATE_SIFTING:
                self.draw_sifting()
            else:
                phase_map = {
                    STATE_ALICE_BIT: "Alice: Choose Bit",
                    STATE_ALICE_BASIS: "Alice: Choose Basis",
                    STATE_BOB: "Bob: Choose Basis",
                    STATE_EVE: "Eve: Choose Basis"
                }
                self.draw_choice_screen(phase_map[self.state])

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
        sys.exit()

    def draw_sifting(self):
        font = pygame.font.SysFont('Arial', 40)
        screen.blit(font.render("Comparing bases...", True, BLACK), (50, 50))
        screen.blit(font.render(f"Sifted key length: {len(self.sifted_key)}", True, BLACK), (50, 100))
        pygame.draw.rect(screen, BLUE, (300, 500, 200, 50))
        screen.blit(font.render("Continue", True, WHITE), (325, 515))

    def draw_results(self):
        font = pygame.font.SysFont('Arial', 30)
        total_checked = len(self.revealed_bits)
        error_rate = self.errors / total_checked if total_checked > 0 else 0
        
        # Determine outcome
        eve_full_key = (
            len(self.eve_key) == len(self.sifted_key) and 
            all(eve_bit is not None and eve_bit == sifted_bit 
                for eve_bit, sifted_bit in zip(self.eve_key, self.sifted_key)
            )
        )

        detected = error_rate > 0.25  # 30% error threshold
        
        # Results text
        y = 50
        if detected:
            screen.blit(font.render("Eve detected! Transmission aborted!", True, RED), (50, y))
        elif eve_full_key:
            screen.blit(font.render("TA caught you! Plagiarism reported! FAIL!", True, RED), (50, y))
        else:
            screen.blit(font.render("Answer key shared! You pass DAA!", True, GREEN), (50, y))
        
        # Detailed information
        y += 60
        screen.blit(font.render(f"Alice's Key: {self.sifted_key}", True, BLACK), (50, y))
        y += 40
        screen.blit(font.render(f"Bob's Key:   {self.bob_key}", True, BLUE), (50, y))
        y += 40
        screen.blit(font.render(f"Eve's Knowledge: {self.eve_key}", True, RED), (50, y))
        y += 40
        error_text = f"Error rate: {error_rate:.0%} ({self.errors}/{total_checked} errors)"
        screen.blit(font.render(error_text, True, BLACK), (50, y))
        
        # Replay button
        pygame.draw.rect(screen, BLUE, (300, 500, 200, 50))
        screen.blit(font.render("Play Again", True, WHITE), (325, 515))


if __name__ == "__main__":
    game = QKDGame()
    game.run()