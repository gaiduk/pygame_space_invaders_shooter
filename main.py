import pygame, random

pygame.init()

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("space invaders")

FPS = 60
clock = pygame.time.Clock()


# Define classes
class Game():
    def __init__(self, player, alien_group, player_bullet_group, alien_bullet_group):
        self.round_number = 1
        self.score = 0

        self.player = player
        self.alien_group = alien_group
        self.player_bullet_group = player_bullet_group
        self.alien_bullet_group = alien_bullet_group

        self.new_round_sound = pygame.mixer.Sound("assets/new_round.wav")
        self.breach_sound = pygame.mixer.Sound("assets/breach.wav")
        self.alien_hit_sound = pygame.mixer.Sound("assets/alien_hit.wav")
        self.player_hit_sound = pygame.mixer.Sound("assets/player_hit.wav")

        self.font = pygame.font.Font("assets/Facon.ttf", 34)


    def update(self):
        self.shift_aliens()
        self.check_collision()
        self.check_round_complition()

    def draw(self):
        WHITE = (255, 255, 255)

        score_text = self.font.render("Score: " + str(self.score), True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.centerx = WINDOW_WIDTH//2
        score_rect.top = 10

        round_text = self.font.render("Round: " + str(self.round_number), True, WHITE)
        round_rect = round_text.get_rect()
        round_rect.topleft = (20, 10)

        lives_text = self.font.render("Lives: " + str(self.player.lives), True, WHITE)
        lives_rect = lives_text.get_rect()
        lives_rect.topright = (WINDOW_WIDTH - 20, 10)

        display_surface.blit(score_text, score_rect)
        display_surface.blit(round_text, round_rect)
        display_surface.blit(lives_text, lives_rect)

        pygame.draw.line(display_surface, WHITE, (0, 50), (WINDOW_WIDTH, 50), 4)
        pygame.draw.line(display_surface, WHITE, (0, WINDOW_HEIGHT - 100), (WINDOW_WIDTH, WINDOW_HEIGHT - 100), 4)


    def shift_aliens(self):
        # if alien group hit edge
        shift = False
        for alien in (self.alien_group.sprites()):
            if alien.rect.left <= 0 or alien.rect.right >= WINDOW_WIDTH:
                shift = True

        # shift every alien down, change direction, check fpr game over
        if shift:
            breach = False
            for alien in (self.alien_group.sprites()):
                alien.rect.y += 10 * self.round_number

                alien.direction = -1 * alien.direction
                alien.rect.x += alien.direction * alien.velocity

                if alien.rect.bottom >= WINDOW_HEIGHT - 100:
                    breach = True

            if breach:
                self.breach_sound.play()
                self.player.lives -= 1
                self.check_game_status("Aliens breached the line!", "Press 'Space' to continue")

    def check_collision(self):
        if pygame.sprite.groupcollide(self.player_bullet_group, self.alien_group, True, True):
            self.alien_hit_sound.play()
            self.score += 1

        if pygame.sprite.spritecollide(self.player, self.alien_bullet_group, True):
            self.player_hit_sound.play()
            self.player.lives -= 1

            self.is_player_hit()

    def start_new_round(self):
        # create a grid of aliens 11 columns and 5 rows
        for i in range(11):
            for j in range(5):
                alien = Alien(64 + i*64, 64 + j * 64, self.round_number, self.alien_bullet_group)
                self.alien_group.add(alien)

        self.new_round_sound.play()
        self.pause_game("* Space Invaders *  Round: " + str(self.round_number), "Press 'Space' to start")

    def check_round_complition(self):
        if not self.alien_group:
            self.score += 10* self.round_number
            self.round_number += 1

            self.start_new_round()

    def is_player_hit(self):
        if self.player.lives <= 0:
            self.reset_game()

    def check_game_status(self, main_text, sub_text):
        self.alien_bullet_group.empty()
        self.player_bullet_group.empty()

        self.player.reset()

        for alien in self.alien_group:
            alien.reset()

        # Check is game over or round reset
        if self.player.lives <= 0:
            self.reset_game()
        # else:
        #     self.pause_game(main_text, sub_text)

    def pause_game(self, main_text, sub_text):
        global running

        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)

        main_text = self.font.render(main_text, True, WHITE)
        main_rect = main_text.get_rect()
        main_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT // 2)

        sub_text = self.font.render(sub_text, True, WHITE)
        sub_rect = sub_text.get_rect()
        sub_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 64)

        display_surface.fill(BLACK)
        display_surface.blit(main_text, main_rect)
        display_surface.blit(sub_text, sub_rect)
        pygame.display.update()

        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        is_paused = False
                if event.type == pygame.QUIT:
                    is_paused = False
                    running = False

    def reset_game(self):
        self.pause_game("Final Score: "+ str(self.score), "Press 'Space' to try again")

        self.score = 0
        self.round_number = 1
        self.player.lives = 5

        self.alien_group.empty()
        self.alien_bullet_group.empty()
        self.player_bullet_group.empty()

        self.start_new_round()

class Player(pygame.sprite.Sprite):

    def __init__(self, bullet_group):
        super().__init__()
        self.image = pygame.image.load("assets/player_ship.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH//2
        self.rect.bottom = WINDOW_HEIGHT - 1

        self.lives = 5
        self.velocity = 8

        self.bullet_group = bullet_group
        self.shoot_sound = pygame.mixer.Sound("assets/player_fire.wav")

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocity
        if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH:
            self.rect.x += self.velocity


    def fire(self):
        # Restrict the numbers of bullets
        if len(self.bullet_group) < 3:
            self.shoot_sound.play()
            PlayerBullet(self.rect.centerx, self.rect.top, self.bullet_group)

    def reset(self):
        self.rect.centerx = WINDOW_WIDTH // 2


class Alien(pygame.sprite.Sprite):

    def __init__(self, x, y, velocity, bullet_group):
        super().__init__()
        self.image = pygame.image.load("assets/alien.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.starting_x = x
        self.starting_y = y

        self.direction = 1
        self.velocity = velocity
        self.bullet_group = bullet_group

        self.shoot_sound = pygame.mixer.Sound("assets/alien_fire.wav")

    def update(self):
        self.rect.x += self.direction * self.velocity

        # Random fire (проверка будет проиходит 60 раз в секунду и для каждого врага а их много,  по этому такая вероятность)
        if random.randint(0, 1000) > 999 and len(self.bullet_group) < 3:
            self.shoot_sound.play()
            self.fire()

    def fire(self):
        AlienBullet(self.rect.centerx, self.rect.bottom, self.bullet_group)

    def reset(self):
        self.rect.topleft = (self.starting_x, self.starting_y)
        self.direction = 1


class PlayerBullet(pygame.sprite.Sprite):

    def __init__(self, x, y, bullet_group):
        super().__init__()
        self.image = pygame.image.load("assets/green_laser.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.velocity = 10
        bullet_group.add(self)

    def update(self):
        self.rect.y -= self.velocity

        # Destroy bullet of the screen
        if self.rect.bottom < 0:
            self.kill()


class AlienBullet(pygame.sprite.Sprite):

    def __init__(self, x, y, bullet_group):
        super().__init__()
        self.image = pygame.image.load("assets/red_laser.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.velocity = 10
        bullet_group.add(self)

    def update(self):
        self.rect.y += self.velocity

        # Destroy bullet of the screen
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()


# Create bullets group
my_player_bullet_group = pygame.sprite.Group()
my_alien_bullet_group = pygame.sprite.Group()

# Create player group and player obj
my_player_group = pygame.sprite.Group()
my_player = Player(my_player_bullet_group)

my_player_group.add(my_player)

# Create alien group
my_alien_group = pygame.sprite.Group()

# Test enemies
# for i in range(10):
#     alien = Alien(64 + i * 64, 100, 1, my_alien_bullet_group)
#     my_alien_group.add(alien)

# Create Game obj
my_game = Game(my_player, my_alien_group, my_player_bullet_group, my_alien_bullet_group)
my_game.start_new_round()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Player want to fire
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                my_player.fire()

    # Fill display
    display_surface.fill((0, 0, 0))

    # Update and display sprite groups
    my_player_group.update()
    my_player_group.draw(display_surface)

    my_alien_group.update()
    my_alien_group.draw(display_surface)

    my_alien_bullet_group.update()
    my_alien_bullet_group.draw(display_surface)

    my_player_bullet_group.update()
    my_player_bullet_group.draw(display_surface)

    # Update and draw game obj
    my_game.update()
    my_game.draw()

    #update display and clock
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()