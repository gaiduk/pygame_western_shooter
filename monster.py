import pygame
from entity import Entity
from pygame.math import Vector2 as vector


class Monster():
    def get_player_distance_direction(self):
        enemy_pos = vector(self.rect.center)
        player_pos = vector(self.player.rect.center)
        distance = (player_pos - enemy_pos).magnitude()

        if distance != 0:
            direction = (player_pos - enemy_pos).normalize()
        else:
            direction = vector()

        return (distance, direction)

    def face_to_player(self):
        distance, direction = self.get_player_distance_direction()

        if distance < self.notice_radius:
            if -0.5 < direction.y < 0.5:
                if direction.x > 0:
                    self.status = 'right_idle'
                elif direction.x < 0:
                    self.status = 'left_idle'
            else:
                if direction.y < 0:
                    self.status = 'up_idle'
                elif direction.y > 0:
                    self.status = 'down_idle'

    def walk_to_player(self):
        distance, direction = self.get_player_distance_direction()

        if self.attak_radius < distance < self.walk_radius:
            self.direction = direction
            self.status = self.status.split('_')[0]
        else:
            self.direction = vector()


class Coffin(Entity, Monster):
    def __init__(self, pos, groups, path, collision_sprites, player):
        super().__init__(pos, groups, path, collision_sprites)
        # overwrite
        self.speed = 140

        self.player = player

        self.notice_radius = 550
        self.walk_radius = 400
        self.attak_radius = 50

    def attack(self):
        distance = self.get_player_distance_direction()[0]
        if distance < self.attak_radius and not self.attacking:
            self.attacking = True
            self.frame_index = 0

        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'

    def animate(self, dt):
        current_animation = self.animations[self.status]
        self.frame_index += 8 * dt

        if int(self.frame_index) == 4 and self.attacking:
            if self.get_player_distance_direction()[0] < self.attak_radius:
                self.player.damage()

        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False

        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.face_to_player()
        self.walk_to_player()
        self.attack()
        self.move(dt)
        self.animate(dt)
        self.blink()
        self.check_death()
        self.vulnerability_timer()


class Cactus(Entity, Monster):
    def __init__(self, pos, groups, path, collision_sprites, player, create_bullet):
        super().__init__(pos, groups, path, collision_sprites)
        self.player = player

        self.notice_radius = 600
        self.walk_radius = 500
        self.attak_radius = 350
        self.speed = 95
        self.health = 2

        self.create_bullet = create_bullet
        self.bullet_shot = False

    def attack(self):
        distance = self.get_player_distance_direction()[0]
        if distance < self.attak_radius and not self.attacking:
            self.attacking = True
            self.frame_index = 0
            self.bullet_shot = False

        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'

    def animate(self, dt):
        current_animation = self.animations[self.status]

        if int(self.frame_index) == 6 and self.attacking and not self.bullet_shot:
            direction = self.get_player_distance_direction()[1]
            bullet_start_pos = self.rect.center + direction * 100

            self.create_bullet(bullet_start_pos, direction)
            self.bullet_shot = True
            self.shoot_sound.play()

        self.frame_index += 8 * dt

        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False

        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.face_to_player()
        self.walk_to_player()
        self.attack()
        self.move(dt)
        self.animate(dt)
        self.blink()
        self.check_death()
        self.vulnerability_timer()
