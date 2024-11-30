# Sterowanie:
# - Poruszanie się: WASD lub Strzałki
# - Strzelanie: Lewy przycisk myszy (Polecam trzymać)
# - Wyjście z gry: Backspace
# 
# Duża część rozgrywki zależy od Cezarego C (Twórcy RandomGrade'a), miłej zabawy!
ananas_mode = False

import pygame, os, math, random

os.environ['SDL_AUDIODRIVER'] = 'dsp'

pygame.init()

# Ustawienie wielkości okna
screen = pygame.display.set_mode((1800, 960))
pygame.display.set_caption("Starstrike: Alien Assault")
icon = pygame.image.load('img/icon.png').convert()
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
player = pygame.image.load('img/ship.png').convert_alpha()
bullet = pygame.image.load('img/bullet2.png').convert()
bullet = pygame.transform.scale(bullet, (5, 5))
big_bullet = pygame.transform.scale(bullet, (2*10, 2*10))
alien_bullet = pygame.image.load('img/bullet3.png').convert_alpha()
alien_bullet = pygame.transform.scale(alien_bullet, (5, 5))

if ananas_mode:
    alien = pygame.image.load('img/pineapple.png').convert_alpha()
    alien = pygame.transform.scale(alien, (12*2, 26*2))
    alienship = pygame.image.load('img/pizza.png').convert_alpha()
    alienship = pygame.transform.scale(alienship, (73*2, 72*2))
    alienship2 = pygame.image.load('img/pizza_slice.png').convert_alpha()
    alienship2 = pygame.transform.scale(alienship2, (24*2, 24*2))
else:
    alien = pygame.image.load('img/alien.png').convert_alpha()
    alien = pygame.transform.scale(alien, (100/3, 70/3))
    alienship = pygame.image.load('img/alienship.png').convert_alpha()
    alienship2 = pygame.image.load('img/alienship2.png').convert_alpha()
    alienship2 = pygame.transform.scale(alienship2, (19*3, 16*3))
background = pygame.image.load('img/background.jpg').convert()

def get_angle_between(point1, point2):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    angle = math.atan2(dy, dx)
    return angle

running = True
gameover = False

dt = 0

class Bullet:
    def __init__(self, angle, x, y, speed=15, size=None):
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.size = size if size else bullet

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def render(self, screen):
        screen.blit(self.size, (self.x, self.y))

class AlienBullet(Bullet):
    def render(self, screen):
        screen.blit(alien_bullet, (self.x, self.y))

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def render(self, screen):
        arrow_rect = pygame.draw.rect(screen, (0, 255, 0), self.rect)
        arrow = pygame.image.load('img/powerup_arrow.png').convert_alpha()
        screen.blit(arrow, arrow_rect)

    def update(self):
        pass

bullets = []
alien_bullets = []
enemies = []
powerups = []

player_hp = 20
score = 0
invincibility_timer = 0
invincibility_duration = 1.5
firerate_mod = 10

player_pos = player.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))

alienship_hp = 30
alienship_active = False
alienship_timer = 0
alienship_spawn_delay = random.randint(10, 20)

alienship2_hp = 10
alienship2_active = False
alienship2_timer = 0
alienship2_spawn_delay = random.randint(2, 10)

powerup_active = False
powerup2_active = False
powerup3_active = False
powerup_timer = 0
powerup2_timer = 0
powerup3_timer = 0
powerup_duration = 45
powerup2_duration = 20
powerup3_duration = 20

font = pygame.font.Font(None, 36)

spawnrate = 0.01
max_enemies = 10
iter_num = 0

while running:
    if powerup2_active:
        dt *= 2
    if powerup3_active:
        firerate_mod = 4
    else:
        firerate_mod = 10
    spawnrate += 0.000000000000000000000000000000001+(0.0000000000000001*score)
    iter_num += 1
    if iter_num >= 80:
        iter_num = 1
        alienship_side = random.randint(1, 4)
        alienship2_side = random.randint(1, 4)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    max_enemies += score//20
    mx, my = pygame.mouse.get_pos()
    player_rect = player.get_rect(center=(player_pos.x + 1/2 * player.get_width(), player_pos.y + 1/2 * player.get_height()))
    dx, dy = mx - player_rect.centerx, player_rect.centery - my
    angle = math.degrees(math.atan2(dy, dx)) - 90
    rot_image = pygame.transform.rotate(player, angle)
    rot_image_rect = rot_image.get_rect(center=player_rect.center)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_BACKSPACE]:
        running = False
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player_pos.y -= 300 * dt
        if player_pos.y < 0:
            player_pos.y = 0
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player_pos.y += 300 * dt
        if player_pos.y > screen.get_height() - player.get_height():
            player_pos.y = screen.get_height() - player.get_height()
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_pos.x -= 300 * dt
        if player_pos.x < 0:
            player_pos.x = 0
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_pos.x += 300 * dt
        if player_pos.x > screen.get_width() - player.get_width():
            player_pos.x = screen.get_width() - player.get_width()

    if pygame.mouse.get_pressed()[0]:
        if not gameover:
            if iter_num%firerate_mod == 0:
                bullet_angle = get_angle_between((player_pos.x + (player_rect.width / 2), player_pos.y + (player_rect.height / 2)), (mx, my))
                if powerup_active:
                    tempBullet = Bullet(bullet_angle, player_pos.x + (player_rect.width / 2), player_pos.y + (player_rect.height / 2), size=big_bullet)
                else:
                    tempBullet = Bullet(bullet_angle, player_pos.x + (player_rect.width / 2), player_pos.y + (player_rect.height / 2))
                bullets.append(tempBullet)

    screen.fill((20, 20, 20))
    screen.blit(background, (0, 0))
    screen.blit(rot_image, rot_image_rect.topleft)

    if random.random() < spawnrate:
        side = random.randint(1, 4)
        if side == 1:
            enemy_x = 0
            enemy_y = random.randint(0, screen.get_height())
        if side == 2:
            enemy_x = screen.get_width() - alien.get_width()
            enemy_y = random.randint(0, screen.get_height())
        if side == 3:
            enemy_x = random.randint(0, screen.get_width())
            enemy_y = 0
        if side == 4:
            enemy_x = random.randint(0, screen.get_width())
            enemy_y = screen.get_height() - alien.get_height()
        if len(enemies) <= max_enemies:
            enemies.append(pygame.Vector2(enemy_x, enemy_y))

    for enemy in enemies:
        enemy_angle = get_angle_between((player_pos.x + (player_rect.width / 2), player_pos.y + (player_rect.height / 2)), (enemy.x, enemy.y))
        enemy.x -= math.cos(enemy_angle)
        enemy.y -= math.sin(enemy_angle)
        screen.blit(alien, enemy)

    if invincibility_timer > 0:
        player.fill((255, 255, 255, 30))
        invincibility_timer -= dt
    else:
        player = pygame.image.load('img/ship.png').convert_alpha()

    if invincibility_timer <= 0:
        for enemy in enemies:
            alien_rect = alien.get_rect(topleft=enemy)
            if player_rect.colliderect(alien_rect):
                player_hp -= 1
                invincibility_timer = invincibility_duration
                enemies.remove(enemy)

        if alienship_active and player_rect.colliderect(alienship_rect):
            player_hp -= 1
            invincibility_timer = invincibility_duration
        
        if alienship2_active and player_rect.colliderect(alienship2_rect):
            player_hp -= 1
            invincibility_timer = invincibility_duration

    # Update pocisków
    for bl in bullets:
        bl.update()
        bl.render(screen)
        if bl.y < 0 or bl.y > screen.get_height() or bl.x < 0 or bl.x > screen.get_width():
            bullets.remove(bl)
        if alienship_active and alienship_rect.collidepoint(bl.x, bl.y):
            alienship_hp -= 1
            try:
                bullets.remove(bl)
            except:
                pass
            if alienship_hp <= 0:
                alienship_active = False
                score += 30
                alienship_hp = 200
                powerups.append(PowerUp(alienship_rect.x, alienship_rect.y))
        if alienship2_active and alienship2_rect.collidepoint(bl.x, bl.y):
            alienship2_hp -= 1
            try:
                bullets.remove(bl)
            except:
                pass
            if alienship2_hp <= 0:
                alienship2_active = False
                score += 10
                alienship2_hp = 40

        # Spaghetti If (Sprawdzanie trafienia enemy)
        for enemy in enemies:
            alien_rect = alien.get_rect(topleft=enemy)
            if alien_rect.collidepoint(bl.x, bl.y) or alien_rect.collidepoint(bl.x, bl.y + 1) or alien_rect.collidepoint(bl.x, bl.y + 2) or alien_rect.collidepoint(bl.x, bl.y + 3) or alien_rect.collidepoint(bl.x, bl.y + 4) or alien_rect.collidepoint(bl.x, bl.y + 5) or alien_rect.collidepoint(bl.x, bl.y + 6) or alien_rect.collidepoint(bl.x + 1, bl.y + 6) or alien_rect.collidepoint(bl.x + 2, bl.y + 6) or alien_rect.collidepoint(bl.x + 3, bl.y + 6) or alien_rect.collidepoint(bl.x + 4, bl.y + 6) or alien_rect.collidepoint(bl.x + 5, bl.y + 6) or alien_rect.collidepoint(bl.x + 6, bl.y + 6) or alien_rect.collidepoint(bl.x + 7, bl.y + 6) or alien_rect.collidepoint(bl.x + 8, bl.y + 6) or alien_rect.collidepoint(bl.x + 9, bl.y + 6) or alien_rect.collidepoint(bl.x + 1, bl.y) or alien_rect.collidepoint(bl.x + 2, bl.y) or alien_rect.collidepoint(bl.x + 3, bl.y) or alien_rect.collidepoint(bl.x + 4, bl.y) or alien_rect.collidepoint(bl.x + 5, bl.y) or alien_rect.collidepoint(bl.x + 6, bl.y) or alien_rect.collidepoint(bl.x + 7, bl.y) or alien_rect.collidepoint(bl.x + 8, bl.y) or alien_rect.collidepoint(bl.x + 9, bl.y) or alien_rect.collidepoint(bl.x + 9, bl.y + 1) or alien_rect.collidepoint(bl.x + 9, bl.y + 2) or alien_rect.collidepoint(bl.x + 9, bl.y + 3) or alien_rect.collidepoint(bl.x + 9, bl.y + 4) or alien_rect.collidepoint(bl.x + 9, bl.y + 5) or alien_rect.collidepoint(bl.x + 9, bl.y + 6):
                enemies.remove(enemy)
                score += 1
                try:
                    bullets.remove(bl)
                except:
                    pass

    # Update power-up'ów
    for powerup in powerups:
        powerup.update()
        powerup.render(screen)
        if player_rect.colliderect(powerup.rect):
            rand_powerup = random.randint(1, 3)
            if rand_powerup == 1:
                powerup_active = True
            elif rand_powerup == 2:
                powerup2_active = True
            else:
                powerup3_active = True
            powerup_timer = powerup_duration
            powerup2_timer = powerup2_duration
            powerup3_timer = powerup3_duration
            powerups.remove(powerup)

    # Obsługa wyłączania power-up'a po upływie czasu
    if powerup_active:
        powerup_timer -= dt
        if powerup_timer <= 0:
            powerup_active = False

    if powerup2_active:
        powerup2_timer -= dt
        if powerup2_timer <= 0:
            powerup2_active = False
    
    if powerup3_active:
        powerup3_timer -= dt
        if powerup3_timer <= 0:
            powerup3_active = False

    # Pojawienie się statku kosmitów
    if not alienship_active:
        alienship_timer += dt
        if alienship_timer >= alienship_spawn_delay:
            alienship_active = True
            alienship_timer = 0
            alienship_rect = alienship.get_rect(center=(random.randint(0, screen.get_width()), random.randint(0, screen.get_height())))
            alienship_spawn_delay = random.randint(10, 20)

    # Rysowanie i atakowanie przez statek kosmitów
    if alienship_active:
        if random.random() < 0.1:
            # for i in range(100):
                if alienship_side == 1:
                    alienship_rect.y += 200 * dt
                elif alienship_rect.bottom >= screen.get_height():
                    alienship_rect.y -= 200 * dt
                if alienship_side == 2:
                    alienship_rect.y -= 200 * dt
                elif alienship_rect.top <= 0:
                    alienship_rect.y += 200 * dt
                if alienship_side == 3:
                    alienship_rect.x += 200 * dt
                elif alienship_rect.right >= screen.get_width():
                    alienship_rect.x -= 200 * dt
                if alienship_side == 4:
                    alienship_rect.x -= 200 * dt
                elif alienship_rect.left <= 0:
                    alienship_rect.x -= 200 * dt
                if alienship_rect.top < 0:
                    alienship_rect.top = 0
                if alienship_rect.left < 0:
                    alienship_rect.left = 0
                if alienship_rect.right > screen.get_width():
                    alienship_rect.right = screen.get_width()
                if alienship_rect.bottom > screen.get_height():
                    alienship_rect.bottom = screen.get_height()
        screen.blit(alienship, alienship_rect)
        if random.random() < 0.02:
            bullet_angle = get_angle_between((alienship_rect.centerx, alienship_rect.centery), (player_pos.x, player_pos.y))
            alien_bullets.append(AlienBullet(bullet_angle, alienship_rect.centerx, alienship_rect.centery, speed=10))

    if not alienship2_active:
        alienship2_timer += dt
        if alienship2_timer >= alienship2_spawn_delay:
            alienship2_active = True
            alienship2_timer = 0
            alienship2_spawn_delay = random.randint(5, 15)
            alienship2_rect = alienship2.get_rect(center=(random.randint(0, screen.get_width()), random.randint(0, screen.get_height())))
    else:
        if iter_num % 10 == 0:
            alien_bullets.append(AlienBullet(angle, alienship2_rect.centerx, alienship2_rect.centery, speed=4))
        screen.blit(alienship2, alienship2_rect)

    if alienship2_active:
        if random.random() < 0.1:
            if alienship2_side == 1:
                alienship2_rect.y += 200 * dt
            elif alienship2_rect.bottom >= screen.get_height():
                alienship2_rect.y -= 200 * dt
            if alienship2_side == 2:
                alienship2_rect.y -= 200 * dt
            elif alienship2_rect.top <= 0:
                alienship2_rect.y += 200 * dt
            if alienship2_side == 3:
                alienship2_rect.x += 200 * dt
            elif alienship2_rect.right >= screen.get_width():
                alienship2_rect.x -= 200 * dt
            if alienship2_side == 4:
                alienship2_rect.x -= 200 * dt
            elif alienship2_rect.left <= 0:
                alienship2_rect.x -= 200 * dt
            if alienship2_rect.top < 0:
                alienship2_rect.top = 0
            if alienship2_rect.left < 0:
                alienship2_rect.left = 0
            if alienship2_rect.right > screen.get_width():
                alienship2_rect.right = screen.get_width()
            if alienship2_rect.bottom > screen.get_height():
                alienship2_rect.bottom = screen.get_height()

    # Aktualizacja pocisków statku kosmitów
    for ab in alien_bullets:
        ab.update()
        ab.render(screen)
        if ab.y < 0 or ab.y > screen.get_height() or ab.x < 0 or ab.x > screen.get_width():
            alien_bullets.remove(ab)
        if player_rect.collidepoint(ab.x, ab.y):
            player_hp -= 1
            invincibility_timer = invincibility_duration
            alien_bullets.remove(ab)

    hp_text = font.render(f'HP: {player_hp}', True, (255, 0, 0))
    score_text = font.render(f'Score: {score}', True, (255, 0, 0))
    score_rect = score_text.get_rect(topright = (screen.get_width() - 10, 10))
    gameover_text = font.render(f'''GAME OVER
                                
Your Score: {score}

Press Backspace to quit''', True, (255, 0, 0))
    gameover_rect = gameover_text.get_rect(center = (screen.get_width()/2, screen.get_height()/2))
    screen.blit(hp_text, (10, 10))
    screen.blit(score_text, score_rect)

    if player_hp <= 0:
        gameover = True
        screen.blit(background, (0, 0))
        screen.blit(gameover_text, gameover_rect)
        # print("Game Over!")
        # print(f"Your score: {score}")

    dt = clock.tick(60) / 1000
    pygame.display.flip()

pygame.quit()