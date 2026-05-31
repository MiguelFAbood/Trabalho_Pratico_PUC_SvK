import pygame
import os 

class Fighter():
    def __init__(self, player, char_folder, x, y): 
        self.player = player
        self.flip = False
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.vel_x = 0  
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_hit = False
        self.health = 1000
        
        self.is_heavy_dp = False
        self.dp_leapt = False
        self.input_buffer = [] 
        
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 
        self.update_time = pygame.time.get_ticks()
        
        animation_steps = ["idle", "walk_forward", "walk_back", "forward_jump", "light_punch", "shoryuken", "neutral_jump"]
        
        for animation in animation_steps:
            temp_img_list = self.load_images(char_folder, animation)
            self.animation_list.append(temp_img_list)
            
        self.image = self.animation_list[self.action][self.frame_index]
        self.vfx_list = self.load_images(char_folder, "shoryuken/VFX")

    def load_images(self, char_folder, animation_name):
        folder_path = f"assets/img/characters/{char_folder}/{animation_name}"
        temp_list = []
        
        try:
            file_list = os.listdir(folder_path)
            file_list.sort() 
        except FileNotFoundError:
            return []

        for file in file_list:
            if file.lower().endswith(".png"): 
                img = pygame.image.load(f"{folder_path}/{file}").convert_alpha()
                img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
                temp_list.append(img)
                
        return temp_list

    def check_sequence(self, sequence):
        seq_idx = 0
        for move in self.input_buffer:
            if move == sequence[seq_idx]:
                seq_idx += 1
                if seq_idx == len(sequence):
                    return True
        return False

    def shoryuken(self, light):
        self.attacking = True
        self.attack_hit = False
        self.input_buffer.clear() 
        self.update_action(5)
        self.is_heavy_dp = not light
        self.dp_leapt = False
        
        if light:
            self.jump = True 
            self.dp_leapt = True
            self.vel_y = -25 
            self.vel_x = 5 if self.flip else -5 
        else:
            self.vel_y = 0
            self.vel_x = 0

    def move(self, screen_width, screen_height, surface, target):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0

        key = pygame.key.get_pressed()
        moving_forward = False
        moving_backward = False

        dir_input = "5" 
        
        if self.player == 1:
            crouch = key[pygame.K_s]
            fwd = key[pygame.K_d] if self.flip else key[pygame.K_a]
        else:
            crouch = key[pygame.K_DOWN]
            fwd = key[pygame.K_RIGHT] if self.flip else key[pygame.K_LEFT]

        if fwd and not crouch: dir_input = "6"
        elif fwd and crouch: dir_input = "3"
        elif crouch and not fwd: dir_input = "2"
        
        self.input_buffer.append(dir_input)
        if len(self.input_buffer) > 20: 
            self.input_buffer.pop(0)

        dp_motion = self.check_sequence(["6", "2", "3"]) or self.check_sequence(["6", "2", "6"])

        can_input = (self.attacking == False) or (self.action == 4 and self.frame_index == 0)

        if self.jump == False:
            self.vel_x = 0  

        if can_input:
            if self.player == 1:
                if key[pygame.K_a] and self.jump == False:
                    self.vel_x = -SPEED
                    if self.flip: moving_backward = True
                    else: moving_forward = True
                if key[pygame.K_d] and self.jump == False:
                    self.vel_x = SPEED
                    if self.flip: moving_forward = True
                    else: moving_backward = True
                if key[pygame.K_w] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True

                if key[pygame.K_u] or key[pygame.K_i] or key[pygame.K_j] or key[pygame.K_k]:
                    if dp_motion and key[pygame.K_u]:
                        self.shoryuken(light=True)
                    elif dp_motion and key[pygame.K_i]:
                        self.shoryuken(light=False)
                    elif self.attacking == False: 
                        self.attack()
                        if key[pygame.K_u]: self.attack_type = 1
                        if key[pygame.K_i]: self.attack_type = 3
                        if key[pygame.K_j]: self.attack_type = 2
                        if key[pygame.K_k]: self.attack_type = 4
            
            elif self.player == 2:
                if key[pygame.K_LEFT] and self.jump == False:
                    self.vel_x = -SPEED
                    if self.flip: moving_backward = True
                    else: moving_forward = True
                if key[pygame.K_RIGHT] and self.jump == False:
                    self.vel_x = SPEED
                    if self.flip: moving_forward = True
                    else: moving_backward = True
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True

                if key[pygame.K_KP4] or key[pygame.K_KP5] or key[pygame.K_KP1] or key[pygame.K_KP2]:
                    if dp_motion and key[pygame.K_KP4]:
                        self.shoryuken(light=True)
                    elif dp_motion and key[pygame.K_KP5]:
                        self.shoryuken(light=False)
                    elif self.attacking == False:
                        self.attack()
                        if key[pygame.K_KP4]: self.attack_type = 1
                        if key[pygame.K_KP5]: self.attack_type = 3
                        if key[pygame.K_KP1]: self.attack_type = 2
                        if key[pygame.K_KP2]: self.attack_type = 4
        
        dx = self.vel_x
        self.vel_y += GRAVITY
        dy += self.vel_y
        
        if self.rect.left + dx < 0:
            dx = 0 - self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
            
        if self.rect.bottom + dy >= screen_height - 70:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 70 - self.rect.bottom
            if self.action == 5 and self.dp_leapt == True:
                self.attacking = False

        if self.jump == False and self.attacking == False:
            if target.rect.centerx > self.rect.centerx:
                self.flip = True
            else:
                self.flip = False

        self.rect.x += dx
        self.rect.y += dy
            
        if self.attacking:
            if self.action != 5: 
                self.update_action(4) 
        elif self.jump:
            if self.vel_x == 0:
                self.update_action(6) 
            else:
                self.update_action(3) 
        elif moving_forward:
            self.update_action(1) 
        elif moving_backward:
            self.update_action(2) 
        else:
            self.update_action(0) 

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def update(self, surface, target): 
        if self.action == 4 or self.action == 5: 
            animation_cooldown = 40 
        else:
            animation_cooldown = 100 
        
        self.image = self.animation_list[self.action][self.frame_index]
        
        if self.attacking == True and self.attack_hit == False and self.frame_index == 2:
            if self.flip == True:
                hitbox_x = self.rect.centerx
            else:
                hitbox_x = self.rect.centerx - (2 * self.rect.width)
                
            hitbox = pygame.Rect(hitbox_x, self.rect.y, 2 * self.rect.width, self.rect.height)
            
            if hitbox.colliderect(target.rect):
                target.health -= 100
                self.attack_hit = True 

        if self.action == 5 and self.is_heavy_dp and self.frame_index == 2 and self.dp_leapt == False:
            self.jump = True
            self.dp_leapt = True
            self.vel_y = -35 
            self.vel_x = 8 if self.flip else -8

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
            
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 5:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action == 4:
                    self.attacking = False

    def attack(self):
        self.attacking = True
        self.attack_hit = False

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        
        img_rect = img.get_rect()
        img_rect.center = self.rect.center
        img_rect.y += -150 

        surface.blit(img, img_rect)
        
        if self.action == 5 and self.is_heavy_dp:
            if self.frame_index < len(self.vfx_list):
                vfx_img = self.vfx_list[self.frame_index]
                vfx_img = pygame.transform.flip(vfx_img, self.flip, False)
                vfx_rect = vfx_img.get_rect()
                vfx_rect.center = self.rect.center
                vfx_rect.y += -150
                surface.blit(vfx_img, vfx_rect)