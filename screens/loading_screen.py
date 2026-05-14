"""
EcoCity Mayor — screens/loading_screen.py
Loading screen with eco tips and progress bar.
"""

import pygame
import random
from game_data import ECO_TIPS

BG      = (11,  13,  26)
PANEL   = (18,  24,  48)
ACCENT  = (78,  144, 217)
GREEN   = (72,  200, 118)
TEXT    = (228, 228, 242)
TEXT_DIM= (115, 120, 155)
BORDER2 = (55,  60,  96)
WHITE   = (255, 255, 255)

SCREEN_W, SCREEN_H = 900, 600
LOAD_DURATION = 2400   # ms


class LoadingScreen:
    def __init__(self, screen, fonts):
        self.screen    = screen
        self.fonts     = fonts
        self.start     = pygame.time.get_ticks()
        self.tip       = random.choice(ECO_TIPS)
        self.tip2      = random.choice([t for t in ECO_TIPS if t != self.tip])
        self.done      = False

        # City silhouette buildings
        random.seed(123)
        self.buildings = []
        x = 0
        while x < SCREEN_W:
            w = random.randint(35, 80)
            h = random.randint(50, 140)
            self.buildings.append((x, SCREEN_H - h, w, h))
            x += w + random.randint(2, 6)

    def update(self):
        elapsed = pygame.time.get_ticks() - self.start
        if elapsed >= LOAD_DURATION:
            self.done = True
        return self.done

    def draw(self):
        s       = self.screen
        elapsed = pygame.time.get_ticks() - self.start
        prog    = min(elapsed / LOAD_DURATION, 1.0)
        s.fill(BG)

        # City silhouette
        for (bx, by, bw, bh) in self.buildings:
            col = (16, 20, 44)
            pygame.draw.rect(s, col, (bx, by, bw, bh))
            for wy in range(by + 8, by + bh - 8, 14):
                for wx in range(bx + 5, bx + bw - 5, 12):
                    wc = (55, 88, 140) if (wx + wy) % 3 != 0 else (20, 22, 42)
                    pygame.draw.rect(s, wc, (wx, wy, 5, 7))

        # Smog overlay
        smog = pygame.Surface((SCREEN_W, 300), pygame.SRCALPHA)
        smog.fill((15, 15, 35, 180))
        s.blit(smog, (0, 0))

        # Title
        title = self.fonts["title"].render("EcoCity Mayor", True, GREEN)
        s.blit(title, title.get_rect(center=(SCREEN_W // 2, 200)))

        sub = self.fonts["small"].render(
            "Loading your city...", True, TEXT_DIM)
        s.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 245)))

        # Progress bar
        bw, bh = 500, 14
        bx = SCREEN_W // 2 - bw // 2
        by = 275
        pygame.draw.rect(s, (20, 22, 48), (bx, by, bw, bh), border_radius=7)
        fw = int(bw * prog)
        if fw > 0:
            pygame.draw.rect(s, ACCENT, (bx, by, fw, bh), border_radius=7)
            # Shine
            sh = pygame.Surface((fw, bh // 2), pygame.SRCALPHA)
            sh.fill((255, 255, 255, 30))
            s.blit(sh, (bx, by))
        pygame.draw.rect(s, BORDER2, (bx, by, bw, bh), 1, border_radius=7)
        pct = self.fonts["tiny"].render(f"{int(prog * 100)}%", True, ACCENT)
        s.blit(pct, (bx + bw + 10, by))

        # Eco tip box
        tip_box = pygame.Rect(60, 320, SCREEN_W - 120, 120)
        pygame.draw.rect(s, (16, 20, 42), tip_box, border_radius=10)
        pygame.draw.rect(s, (40, 80, 40), tip_box, 1, border_radius=10)

        label = self.fonts["small"].render("Eco Tip:", True, GREEN)
        s.blit(label, (80, 334))

        # Word-wrap tip text
        words    = self.tip.split()
        lines    = []
        cur_line = ""
        for w in words:
            test = (cur_line + " " + w).strip()
            if self.fonts["small"].size(test)[0] < tip_box.w - 40:
                cur_line = test
            else:
                lines.append(cur_line)
                cur_line = w
        lines.append(cur_line)
        for i, line in enumerate(lines[:3]):
            t = self.fonts["small"].render(line, True, TEXT)
            s.blit(t, (80, 358 + i * 22))

        # Second tip fading in at 60% progress
        if prog > 0.6:
            alpha2 = min(255, int((prog - 0.6) / 0.4 * 255))
            t2     = self.fonts["tiny"].render(
                f"Did you know?  {self.tip2[:80]}{'...' if len(self.tip2) > 80 else ''}",
                True, TEXT_DIM)
            t2.set_alpha(alpha2)
            s.blit(t2, t2.get_rect(center=(SCREEN_W // 2, 460)))

        # Version
        ver = self.fonts["tiny"].render("EcoCity Mayor  v1.0", True, TEXT_DIM)
        s.blit(ver, ver.get_rect(center=(SCREEN_W // 2, 540)))