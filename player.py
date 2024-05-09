import pygame
from pygame.math import Vector2 as vector
from os import walk

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, path, collision_sprites, create_bullet):
        super().__init__(groups)
        self.import_assets(path)

        self.frame_index = 0
        self.status = 'down_idle'

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)

        self.pos = vector(self.rect.center)
        self.direction = vector()
        self.speed = 200
        self.status = None

        self.hitbox = self.rect.inflate(-self.rect.width * 0.5, -self.rect.height / 2)
        self.collision_sprites = collision_sprites

        self.attacking = False
        self.create_bullet = create_bullet
        self.bullet_shot = False
        self.bullet_direction = ''

    def get_status(self):
        if self.status == None:
            self.status = 'down_idle'
        if self.direction.x == 0 and self.direction.y == 0:
            self.status = self.status.split('_')[0] + '_idle'

        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'



    def import_assets(self, path):
        self.animations = {}
        # print(list(walk(path)))
        for index, folder in enumerate(walk(path)):
            if index == 0:
                for name in folder[1]:
                    self.animations[name] = []
            else:
                for filename in sorted(folder[2], key= lambda string: int(string.split('.')[0])):
                    path = folder[0].replace('\\', '/') + '/' + filename
                    surf = pygame.image.load(path).convert_alpha()
                    key = folder[0].split('\\')[1]
                    self.animations[key].append(surf)
        print(self.animations)


    def input(self):
        keys = pygame.key.get_pressed()

        if not self.attacking:
            if keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            elif keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            else:
                self.direction.y = 0

            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.direction = vector()
                self.frame_index = 0
                self.bullet_shot = False

                match self.status.split('_')[0]:
                    case 'left': self.bullet_direction = vector(-1,0)
                    case 'right': self.bullet_direction = vector(1,0)
                    case 'up': self.bullet_direction = vector(0,-1)
                    case 'down': self.bullet_direction = vector(0,1)

    def move(self, dt):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

            # horizontal movement
            self.pos.x += self.direction.x * self.speed * dt
            self.hitbox.centerx = round(self.pos.x)
            self.rect.centerx = self.hitbox.centerx
            self.collision('horizontal')

            # vertical movement
            self.pos.y += self.direction.y * self.speed * dt
            self.hitbox.centery = round(self.pos.y)
            self.rect.centery = self.hitbox.centery
            self.collision('vertical')

    def animate(self, dt):

        current_animation = self.animations[self.status]

        self.frame_index += 8 * dt

        if int(self.frame_index) == 2 and self.attacking and not self.bullet_shot:
            bullet_start_pos = self.rect.center + self.bullet_direction * 70

            if self.bullet_direction == [0, 1]:
                bullet_start_pos.x -= 14
            if self.bullet_direction == [0, -1]:
                bullet_start_pos.x += 20

            self.create_bullet(bullet_start_pos, self.bullet_direction)
            self.bullet_shot = True

        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False

        self.image = current_animation[int(self.frame_index)]

    def collision(self, direction):

            for sprite in self.collision_sprites.sprites():
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == "horizontal":
                        if self.direction.x > 0:  # we moving right
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    else:
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery


    def update(self, dt):
        self.input()
        self.get_status()
        self.move(dt)
        self.animate(dt)