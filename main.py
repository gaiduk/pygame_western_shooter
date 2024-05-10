import pygame, sys
from settings import *
from player import Player
from pygame.math import Vector2 as vector
from pytmx.util_pygame import load_pygame
from sprite import Sprite, Bullet
from monster import Coffin, Cactus


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = vector()
        self.display_surface = pygame.display.get_surface()
        self.bg = pygame.image.load('graphics/other/bg.png').convert()

    def customize_draw(self, player):
        self.offset.x = player.rect.x - WINDOW_WIDTH / 2
        self.offset.y = player.rect.y - WINDOW_HEIGHT / 2

        self.display_surface.blit(self.bg, -self.offset)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_rect = sprite.image.get_rect(center=sprite.rect.center)
            offset_rect.center -= self.offset
            self.display_surface.blit(sprite.image, offset_rect)


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('WildWest shooter')
        self.clock = pygame.time.Clock()
        self.bullet_surf = pygame.image.load('graphics/other/particle.png').convert_alpha()

        # groups
        self.all_sprites = AllSprites()
        self.obstacles = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()

        self.font = pygame.font.SysFont('helvetica', 58)

        self.lose_text_surf = self.font.render("*** GAME OVER ***", True, "red")
        self.lose_text_rect = self.lose_text_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        self.setup()
        self.music = pygame.mixer.Sound('sound/music.mp3')
        self.music.play(loops=-1)

        self.health_text = self.font.render(f'Health: ' + str(self.player.health), True, 'red')
        self.health_text_rect = self.health_text.get_rect(topleft=(50, 50))

        self.enemy_text = self.font.render(f'Enemy: ' + str(len(self.monsters)), True, 'green')
        self.enemy_text_rect = self.enemy_text.get_rect(topright=(WINDOW_WIDTH-50, 50))

        self.win_text_surf = self.font.render("*** YOU WIN ***", True, "blue")
        self.win_text_surf_rect = self.win_text_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

    def create_bullet(self, pos, direction):
        Bullet(pos, direction, self.bullet_surf, [self.all_sprites, self.bullets])

    def bullets_colision(self):
        for obstacle in self.obstacles.sprites():
            pygame.sprite.spritecollide(obstacle, self.bullets, True, pygame.sprite.collide_mask)

        if pygame.sprite.spritecollide(self.player, self.bullets, True, pygame.sprite.collide_mask):
            self.player.damage()

        for bullet in self.bullets.sprites():
            sprites = pygame.sprite.spritecollide(bullet, self.monsters, False, pygame.sprite.collide_mask)
            if sprites:
                bullet.kill()
            for sprite in sprites:
                sprite.damage()

    def setup(self):
        tmx_map = load_pygame('data/map.tmx')
        for x, y, surface in tmx_map.get_layer_by_name('Fence').tiles():
            Sprite((x * 64, y * 64), surface, [self.all_sprites, self.obstacles])

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(pos=(obj.x, obj.y),
                                     groups=self.all_sprites,
                                     path=PATHS['player'],
                                     collision_sprites=self.obstacles,
                                     create_bullet=self.create_bullet)
            if obj.name == 'Coffin':
                Coffin((obj.x, obj.y), [self.all_sprites, self.monsters], PATHS['coffin'], self.obstacles, self.player)

            if obj.name == 'Cactus':
                Cactus((obj.x, obj.y), [self.all_sprites, self.monsters], PATHS['cactus'], self.obstacles, self.player, self.create_bullet)

        for obj in tmx_map.get_layer_by_name('Object'):
            Sprite((obj.x, obj.y), obj.image, [self.all_sprites, self.obstacles])

    def run(self):
        while True:
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            dt = self.clock.tick() / 1000

            self.health_text = self.font.render(f'Health: ' + str(self.player.health), True, 'red')
            self.enemy_text = self.font.render(f'Enemy: ' + str(len(self.monsters)), True, 'green')

            # update groups
            self.all_sprites.update(dt)
            self.bullets_colision()

            # draw groups
            self.display_surface.fill('black')
            self.all_sprites.customize_draw(self.player)
            self.display_surface.blit(self.health_text, self.health_text_rect)
            self.display_surface.blit(self.enemy_text, self.enemy_text_rect)

            if self.player.health <= 0:
                self.display_surface.fill('gray')
                self.display_surface.blit(self.lose_text_surf, self.lose_text_rect)
                self.player.kill()

            if len(self.monsters) <= 0:
                self.display_surface.fill('yellow')
                self.display_surface.blit(self.win_text_surf, self.win_text_surf_rect)
                self.player.kill()

            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
