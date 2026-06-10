import pygame
import os


class Fighter():
    def __init__(self, player, char_data, x, y):
        self.player = player
        self.flip = False
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.vel_x = 0
        self.jump = False
        self.crouching = False
        self.attacking = False
        self.attack_type = 0
        self.attack_dir = "5"
        self.attack_routed = False
        self.attack_hit = False
        self.combo = 0
        self.throwbox_data = char_data.get("throwbox_data", {})
        self.throw_data    = char_data.get("throw_data", {})
        self.throw_pivot_data = char_data.get("throw_pivot_data", {})
        self.tech_timer    = 0
        self.grabbed_by    = None
        self.hitstun_timer = 0
        self.knocked_down = False
        self.wakeup_timer = 0
        self.hitstop_timer = 0
        self.juggle_limit = 0 
        self.last_forward_tap  = 0
        self.last_backward_tap = 0
        self.dashing           = False
        self.DOUBLE_TAP_WINDOW = 200
        self.dash_speed = char_data.get("dash_speed")
        self.backdash_speed = char_data.get("backdash_speed")
        self.pending_input = None
        self.input_buffer = []
        self.loop_count     = 0
        self.total_loops    = 0
        self.animation_list = {}
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.super_meter        = 0
        self.super_flash_timer  = 0  
        self.super_pending      = None
        self.char_folder  = char_data["folder"]
        self.health       = char_data["health"]
        self.max_health   = char_data["health"]
        self.SPEED        = char_data["speed"]
        self.jump_vel     = char_data["jump_vel"]
        self.special_list = char_data.get("specials", [])
        self.attack_data  = char_data.get("attack_data", {})
        self.hitbox_data  = char_data.get("hitbox_data", {})
        self.hurtbox_data   = char_data.get("hurtbox_data", {})
        self.active_hurtbox = [self.rect.copy()]
        self.throw_recovery_timer = 0
        self.projectile_cfg = char_data.get("projectile_data", None)

        self.active_projectiles = []
        self.projectile_fired   = False
        self.is_heavy_hadouken  = False

        self.current_special = None  
        self.special_hit_count = 0   
        self.special_leapt = False
        self.special_hit_cooldown = 0


        self.pending_grab = None   

        self.active_hitboxes = []

        animation_steps = char_data.get("animation_steps", {})
        for action_id, animation_name in animation_steps.items():
            self.animation_list[action_id] = self.load_images(self.char_folder, animation_name)

        self.image = self.animation_list[self.action][self.frame_index]

        vfx_data = char_data.get("vfx_data", {})

        projectile_folder   = char_data.get("projectile_folder", None)
        proj_hit_folder     = char_data.get("projectile_hit_folder", None)

        self.vfx_list = {
            action_id: self.load_images(self.char_folder, folder)
            for action_id, folder in vfx_data.items()
        }
        self.proj_imgs     = self.load_images(self.char_folder, projectile_folder) if projectile_folder else []
        self.proj_hit_imgs = self.load_images(self.char_folder, proj_hit_folder)   if proj_hit_folder   else []

        proj_crop     = char_data.get("projectile_crop", None)
        proj_hit_crop = char_data.get("projectile_hit_crop", None)

        if proj_crop:
            cx, cy, cw, ch = proj_crop
            self.proj_imgs = [
                pygame.transform.scale(
                    img.subsurface(pygame.Rect(cx, cy, cw, ch)),
                    (cw, ch)
                )
                for img in self.proj_imgs
            ]

        if proj_hit_crop:
            cx, cy, cw, ch = proj_hit_crop
            self.proj_hit_imgs = [
                pygame.transform.scale(
                    img.subsurface(pygame.Rect(cx, cy, cw, ch)),
                    (cw, ch)
                )
                for img in self.proj_hit_imgs
            ]

        if player == 1:
            self.controls = {
                "left":  pygame.K_a,
                "right": pygame.K_d,
                "up":    pygame.K_w,
                "down":  pygame.K_s,
                "lp":    pygame.K_u,
                "hp":    pygame.K_i,
                "lk":    pygame.K_j,
                "hk":    pygame.K_k,
            }
        else:
            self.controls = {
                "left":  pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "up":    pygame.K_UP,
                "down":  pygame.K_DOWN,
                "lp":    pygame.K_KP4,
                "hp":    pygame.K_KP5,
                "lk":    pygame.K_KP1,
                "hk":    pygame.K_KP2,
            }
        self.prev_key = pygame.key.get_pressed()
    def load_images(self, char_folder, animation_name):
        folder_path = f"assets/img/characters/{char_folder}/{animation_name}"
        temp_list = []

        try:
            file_list = sorted(os.listdir(folder_path))
        except FileNotFoundError:
            file_list = []

        for file in file_list:
            if file.lower().endswith(".png"):
                img = pygame.image.load(f"{folder_path}/{file}").convert_alpha()
                img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
                temp_list.append(img)

        if len(temp_list) == 0:
            surface = pygame.Surface((160, 360), pygame.SRCALPHA)
            color_map = {
                "hitstun":                  (255, 0,   0,   128),
                "juggle_state":             (0,   0,   255, 128),
                "knockdown_on_the_ground":  (0,   255, 255, 128),
            }
            surface.fill(color_map.get(animation_name, (255, 165, 0, 200))) 
            temp_list = [surface, surface]
        
        return temp_list

    def check_sequence(self, sequences):
        # If it's a single list of strings (like QCF), wrap it in a list so we can loop it
        if isinstance(sequences, list) and isinstance(sequences[0], str):
            sequences = [sequences]
            
        for seq in sequences:
            seq_idx = len(seq) - 1
            
            # Scan backwards: from the newest input to the oldest
            for i in range(len(self.input_buffer) - 1, -1, -1):
                move = self.input_buffer[i]
                
                if move == seq[seq_idx]:
                    seq_idx -= 1
                    if seq_idx < 0:
                        return True
                        
        return False

    def check_360(self):
        window = self.input_buffer[-20:]
        required = {"2", "4", "6", "8"}
        found = set()
        for inp in window:
            if inp in ("8", "9", "7"):
                found.add("8")
            elif inp in required:
                found.add(inp)
        return required.issubset(found)

    def _button_held(self, key, button_name):
        return key[self.controls[button_name]]

    def try_specials(self, key, can_cancel_special, can_fire, can_cancel_super=False, target=None, pressed_override=None):
        button_map = {
            "light_punch":  "lp",
            "heavy_punch":  "hp",
            "light_kick":   "lk",
            "heavy_kick":   "hk",
        }

        for special in self.special_list:
            ctrl_key = button_map.get(special["button"])

            if pressed_override is not None:
                is_pressed = pressed_override.get(ctrl_key, False)
            else:
                is_pressed = key[self.controls[ctrl_key]] and not self.prev_key[self.controls[ctrl_key]]

            if not is_pressed:
                continue

            if special.get("is_super"):
                can_do = (not self.attacking) or can_cancel_super
            else:
                can_do = (not self.attacking) or can_cancel_special
            
            if not special.get("is_super") and special.get("can_cancel", True) is False:
                can_do = not self.attacking
                
            if not can_do:
                continue

            current_attack_data = self.attack_data.get(self.action, {})
            leap_cancel_safe = self.attacking and current_attack_data.get("leap_cancel_safe", False)

            air_ok = special.get("air_ok", False)
            if self.jump and not air_ok and not leap_cancel_safe:
                continue

            if not self.jump and special.get("air_only", False):
                continue

            if special["type"] == "projectile" and not can_fire:
                continue

            motion = special["motion"]
            if motion == "360":
                matched = self.check_360()
            else:
                matched = self.check_sequence(motion)

            if matched:
                if special.get("is_super"):
                    if self.super_meter < 100:
                        continue
                    self.super_meter = 0
                    self.super_flash_timer = 30
                    if target is not None:
                        target.hitstun_timer += 30 * 40
                    self.execute_special(special)
                    return True
                else:
                    self.execute_special(special)
                    return True

        return False

    def execute_special(self, special):
        #self.hitstop_timer  = 0
        self.dashing = False
        self.attacking      = True
        self.attack_hit     = False
        self.attack_routed  = True
        self.update_action(special["action_id"])
        self.frame_index = 0 
        self.update_time = pygame.time.get_ticks() 
        self.vel_x = 0

        move_type = special["type"]

        self.special_hit_count = 0
        self.special_hit_cooldown = 0
        self.special_leapt = False
        self.loop_count = 0

        if move_type == "projectile":
            self.is_heavy_hadouken = not special["light"]
            self.projectile_fired  = False

        elif move_type == "command_grab":
            self.pending_grab = special
            self.vel_y = 0

        elif move_type == "lariat":
            pass

        elif "dash_vel_x" in self.attack_data.get(special["action_id"], {}):
            raw_vx = self.attack_data.get(special["action_id"], {}).get("dash_vel_x", 10)
            self.vel_x = raw_vx if self.flip else -raw_vx
    
    def check_block(self, attack_property):
        if self.jump or self.knocked_down:
            return False
        if self.attacking:
            return False
        if self.dashing:
            return False
        if self.action in [26, 27]:
            return False
            
        key = pygame.key.get_pressed()
        left_held  = key[self.controls["left"]]
        right_held = key[self.controls["right"]]
        down_held  = key[self.controls["down"]]

        back = left_held if self.flip else right_held

        if back:
            if down_held: 
                if attack_property in ["low", "mid"]:
                    return "crouch"
            else:         
                if attack_property in ["high", "mid"]:
                    return "stand"
        return False

    def block_attack(self, attacker_x, blockstun_duration, is_crouch_block, pushback_vel=7):
        self.attacking = False
        self.attack_hit = False
        self.input_buffer.clear()
        self.pending_grab = None
        self.pending_input = None
        self.dashing = False
        self.flip = self.rect.centerx < attacker_x

        if is_crouch_block:
            self.crouching = True
            self.update_action(31) # crouch_block
            self.vel_x = 0
        else:
            self.crouching = False
            self.update_action(30) # block
            self.vel_x = 0
                
        self.vel_x = -pushback_vel if self.flip else pushback_vel
        self.hitstun_timer = pygame.time.get_ticks() + blockstun_duration
    
    def get_hit(self, is_knockdown, attacker_x, hitstun_duration, launch_velocity=(10, -20), pushback_vel=4):
        self.attacking = False
        self.attack_hit = False
        self.input_buffer.clear()
        self.pending_grab = None
        self.pending_input = None
        self.dashing = False

        self.flip = self.rect.centerx < attacker_x

        if is_knockdown:
            self.update_action(28)
            self.vel_y   = launch_velocity[1]
            self.vel_x   = -launch_velocity[0] if self.flip else launch_velocity[0]
            self.jump    = True
            self.knocked_down = False
            self.crouching = False
        else:
            key = pygame.key.get_pressed()
            down_held = key[self.controls["down"]]
            if down_held or self.crouching:
                self.vel_x = 0
                self.update_action(27)
                self.crouching = True
            else:
                self.vel_x = 0
                self.update_action(26)
                self.crouching = False
                
            self.vel_x = -pushback_vel if self.flip else pushback_vel
            self.hitstun_timer = pygame.time.get_ticks() + hitstun_duration


    def move(self, screen_width, screen_height, surface, target):
        can_fire = len(self.active_projectiles) == 0
        current_time = pygame.time.get_ticks()
        key = pygame.key.get_pressed()
        lp_pressed = key[self.controls["lp"]] and not self.prev_key[self.controls["lp"]]
        lk_pressed = key[self.controls["lk"]] and not self.prev_key[self.controls["lk"]]
        throw_pressed = key[self.controls["lp"]] and key[self.controls["lk"]] and (lp_pressed or lk_pressed)
        forward_tap  = False
        backward_tap = False
        in_hitstun          = self.action in [26, 27, 30, 31, 33] 
        in_juggle_state     = self.action == 28               
        in_knockdown_grounded = self.action == 29
        is_knocked_out_of_action = in_juggle_state or in_knockdown_grounded

        if not self.jump and not self.attacking and not in_hitstun and not is_knocked_out_of_action and not self.dashing:
            left_just_pressed  = key[self.controls["left"]]  and not self.prev_key[self.controls["left"]]
            right_just_pressed = key[self.controls["right"]] and not self.prev_key[self.controls["right"]]

            forward_tap  = right_just_pressed if self.flip else left_just_pressed
            backward_tap = left_just_pressed  if self.flip else right_just_pressed

            if forward_tap:
                if current_time - self.last_forward_tap < self.DOUBLE_TAP_WINDOW:
                    clean_buffer = []
                    for x in self.input_buffer:
                        if not clean_buffer or clean_buffer[-1] != x:
                            clean_buffer.append(x)
                            
                    if len(clean_buffer) >= 2 and clean_buffer[-2:] == ["6", "5"]:
                        self.dashing = True
                        self.update_action(6)
                        self.frame_index = 0
                        self.vel_x = self.dash_speed if self.flip else -self.dash_speed
                self.last_forward_tap = current_time

            elif backward_tap:
                if current_time - self.last_backward_tap < self.DOUBLE_TAP_WINDOW:
                    clean_buffer = []
                    for x in self.input_buffer:
                        if not clean_buffer or clean_buffer[-1] != x:
                            clean_buffer.append(x)
                            
                    if len(clean_buffer) >= 2 and clean_buffer[-2:] == ["4", "5"]:
                        self.dashing = True
                        self.update_action(7)
                        self.frame_index = 0
                        self.vel_x = -self.backdash_speed if self.flip else self.backdash_speed
                self.last_backward_tap = current_time
        if self.grabbed_by is not None:
            # Check for a fresh button press, not just holding the key
            lp_pressed = key[self.controls["lp"]] and not self.prev_key[self.controls["lp"]]
            lk_pressed = key[self.controls["lk"]] and not self.prev_key[self.controls["lk"]]
            throw_pressed = key[self.controls["lp"]] and key[self.controls["lk"]] and (lp_pressed or lk_pressed)
            
            tech_input = throw_pressed and current_time <= self.tech_timer
            
            if tech_input:
                attacker = self.grabbed_by
                self.grabbed_by = None
                
                tech_duration = len(self.animation_list[33]) * 40

                self.update_action(33)
                self.attacking = False
                self.vel_x = 5 if self.flip else -5
                self.hitstun_timer = current_time + tech_duration

                attacker.update_action(33)
                attacker.attacking = False
                attacker.attack_hit = False
                attacker.vel_x = -5 if attacker.flip else 5
                attacker.hitstun_timer = current_time + tech_duration

                self.prev_key = key
                return
            else:
                attacker = self.grabbed_by
                if attacker.action in attacker.throw_pivot_data and attacker.frame_index in attacker.throw_pivot_data[attacker.action]:
                    off_x, off_y = attacker.throw_pivot_data[attacker.action][attacker.frame_index]
                    self.rect.centerx = attacker.rect.centerx + (-off_x if attacker.flip else off_x)
                    self.rect.bottom = attacker.rect.bottom + off_y
                else:
                    self.rect.centerx = attacker.rect.centerx + (-60 if attacker.flip else 60)
                attacker.rect.left  = max(0, attacker.rect.left)
                attacker.rect.right = min(screen_width, attacker.rect.right)

                self.flip = not attacker.flip
                self.prev_key = key
                return

        key = pygame.key.get_pressed()
        moving_forward  = False
        moving_backward = False
        can_input       = False
        left_held       = False
        right_held      = False
        in_hitstop      = current_time < self.hitstop_timer

        # --- Directional inputs ---
        if not in_hitstun and not is_knocked_out_of_action:
            left_held  = key[self.controls["left"]]
            right_held = key[self.controls["right"]]
            down_held  = key[self.controls["down"]]

            self.crouching = down_held
            fwd  = right_held if self.flip else left_held
            back = left_held  if self.flip else right_held

            if self.crouching:
                if fwd:    dir_input = "3"
                elif back: dir_input = "1"
                else:      dir_input = "2"
            else:
                if fwd:    dir_input = "6"
                elif back: dir_input = "4"
                else:      dir_input = "5"

            if key[self.controls["up"]] and not self.jump and not self.crouching:
                self.input_buffer.append("8")

            if not self.input_buffer or self.input_buffer[-1] != dir_input:
                self.input_buffer.append(dir_input)
                self.input_buffer_time = pygame.time.get_ticks()
                if len(self.input_buffer) > 30:
                    self.input_buffer.pop(0)
            else:
                if pygame.time.get_ticks() - self.input_buffer_time > 5 * 40: 
                    self.input_buffer.clear()
                
            can_cancel_special = False
            can_cancel_normal  = False
            can_cancel_super = False

            if self.attacking:
                current_attack_data = self.attack_data.get(self.action, {})
                
                # Normal and Special cancels still require the attack to hit
                if self.attack_hit:
                    n_cancel = current_attack_data.get("normal_cancel")
                    if n_cancel and n_cancel[0] <= self.frame_index <= n_cancel[1]:
                        can_cancel_normal = True
                        
                    s_cancel = current_attack_data.get("special_cancel")
                    if s_cancel and s_cancel[0] <= self.frame_index <= s_cancel[1]:
                        can_cancel_special = True

                sc_cancel = current_attack_data.get("super_cancel")
                if sc_cancel and sc_cancel[0] <= self.frame_index <= sc_cancel[1]:
                    if self.attack_hit or current_attack_data.get("whiff_cancel_super"):
                        can_cancel_super = True
                        
            if self.attacking:
                is_special = self.action in [sp.get("action_id") for sp in self.special_list]
                
                if not self.attack_routed and not is_special:
                    if self.jump:
                        if   self.attack_type == 1: self.update_action(18) # j.LP
                        elif self.attack_type == 2: self.update_action(20) # j.LK
                        elif self.attack_type == 3: self.update_action(19) # j.HP
                        elif self.attack_type == 4: self.update_action(21) # j.HK
                    elif self.crouching:
                        if   self.attack_type == 2 and self.attack_dir == "3": self.update_action(41) # df.LK
                        elif self.attack_type == 1: self.update_action(14) # cr.LP
                        elif self.attack_type == 2: self.update_action(16) # cr.LK
                        elif self.attack_type == 3: self.update_action(15) # cr.HP
                        elif self.attack_type == 4: self.update_action(17) # cr.HK
                    else:
                        if   self.attack_type == 4 and self.attack_dir == "4": self.update_action(40) # b.HK
                        elif self.attack_type == 1: self.update_action(10) # LP
                        elif self.attack_type == 2: self.update_action(12) # LK
                        elif self.attack_type == 3: self.update_action(11) # HP
                        elif self.attack_type == 4: self.update_action(13) # HK
                    self.attack_routed = True

            can_input = (
                (not self.attacking)
                or (self.action in list(range(10, 22)) + [40, 41] and self.frame_index == 0)
                or can_cancel_special
                or can_cancel_normal
                or can_cancel_super
            )

            lp_pressed = key[self.controls["lp"]] and not self.prev_key[self.controls["lp"]]
            hp_pressed = key[self.controls["hp"]] and not self.prev_key[self.controls["hp"]]
            lk_pressed = key[self.controls["lk"]] and not self.prev_key[self.controls["lk"]]
            hk_pressed = key[self.controls["hk"]] and not self.prev_key[self.controls["hk"]]
            throw_pressed = key[self.controls["lp"]] and key[self.controls["lk"]] and (lp_pressed or lk_pressed)
            any_attack = lp_pressed or hp_pressed or lk_pressed or hk_pressed

            if in_hitstop:
                if any_attack and can_input and self.pending_input is None:
                    self.pending_input = {
                        "lp":  lp_pressed,
                        "hp":  hp_pressed,
                        "lk":  lk_pressed,
                        "hk":  hk_pressed,
                        "dir": dir_input,
                        "can_cancel_special": can_cancel_special,
                        "can_cancel_normal":  can_cancel_normal,
                        "can_cancel_super":   can_cancel_super, 
                    }
            else:
                if self.pending_input is not None:
                    pi = self.pending_input
                    self.pending_input = None
                    replay_can_cancel_special = pi["can_cancel_special"]
                    replay_can_cancel_normal  = pi["can_cancel_normal"]
                    replay_can_cancel_super   = pi.get("can_cancel_super", False)
                    
                    replay_can_input = (
                        (not self.attacking)
                        or (self.action in list(range(10, 22)) + [40, 41] and self.frame_index == 0)
                        or replay_can_cancel_special
                        or replay_can_cancel_normal
                        or replay_can_cancel_super 
                    )
                    
                    if replay_can_input:
                        special_fired = self.try_specials(
                            key, replay_can_cancel_special, can_fire, replay_can_cancel_super, target,
                            pressed_override={"lp": pi["lp"], "hp": pi["hp"], "lk": pi["lk"], "hk": pi["hk"]}
                        )
                        
                        if not special_fired and (not self.attacking or replay_can_cancel_normal):
                            self.attack()
                            self.attack_dir = pi["dir"]
                            if pi["lp"]: self.attack_type = 1
                            if pi["lk"]: self.attack_type = 2
                            if pi["hp"]: self.attack_type = 3
                            if pi["hk"]: self.attack_type = 4

                elif can_input and (any_attack or throw_pressed):
                    special_fired = self.try_specials(key, can_cancel_special, can_fire, can_cancel_super, target)
                    
                    if not special_fired and (not self.attacking or can_cancel_normal):
                        self.attack()

                        if throw_pressed:
                            self.update_action(32)
                            self.attack_routed = True
                            self.throw_direction = 35 if back else 34 
                            
                        else:
                            self.attack_dir = dir_input
                            if lp_pressed: self.attack_type = 1
                        self.attack_dir = dir_input
                        if lp_pressed: self.attack_type = 1
                        if lk_pressed: self.attack_type = 2
                        if hp_pressed: self.attack_type = 3
                        if hk_pressed: self.attack_type = 4

        self.prev_key = key

        if current_time < self.hitstop_timer:
            
            current_attack = self.attack_data.get(self.action, {})
            
            if self.attacking and current_attack.get("no_pushback"):
                return

            if not self.jump and self.vel_x != 0:
                self.rect.x += self.vel_x
                if self.vel_x > 0:   
                    self.vel_x = max(0, self.vel_x - 1)
                elif self.vel_x < 0: 
                    self.vel_x = min(0, self.vel_x + 1)
                    
                if self.rect.left < 0:
                    self.rect.left = 0
                if self.rect.right > screen_width:
                    self.rect.right = screen_width
            return

        GRAVITY = 2
        dx = 0
        dy = 0

        if in_hitstun:
            if current_time >= self.hitstun_timer and target.super_flash_timer == 0:
                self.update_action(0)
                in_hitstun = False
                target.combo = 0
                self.juggle_limit = 0
            elif not self.dashing:
                if self.vel_x > 0:   self.vel_x = max(0, self.vel_x - 1)
                elif self.vel_x < 0: self.vel_x = min(0, self.vel_x + 1)

        if not in_hitstun and not is_knocked_out_of_action:
            if not self.jump:
                if self.attacking:
                    current_attack = self.attack_data.get(self.action, {})
                    
                    is_frame_moving = False
                    frame_vel_data = current_attack.get("frame_velocity")
                    
                    if frame_vel_data:
                        start_f = frame_vel_data.get("start", 0)
                        end_f = frame_vel_data.get("end", 999)
                        
                        if start_f <= self.frame_index <= end_f:
                            speed = frame_vel_data.get("vel_x", 0)
                            self.vel_x = speed if not self.flip else -speed
                            is_frame_moving = True

                    is_tatsu = current_attack.get("dash_vel_x") is not None
                    
                    if not is_tatsu and not is_frame_moving:
                        if self.vel_x > 0:   self.vel_x = max(0, self.vel_x - 1)
                        elif self.vel_x < 0: self.vel_x = min(0, self.vel_x + 1)
                        
                elif self.dashing:
                    pass
                else:
                    self.vel_x = 0

            if can_input and not self.dashing:
                if left_held and not self.jump and not self.crouching and not self.attacking:
                    self.vel_x = -self.SPEED
                    moving_backward = True if self.flip else False
                    moving_forward  = False if self.flip else True
                    if self.flip:
                        moving_forward  = True
                        moving_backward = False
                    else:
                        moving_forward  = False
                        moving_backward = True

                if right_held and not self.jump and not self.crouching and not self.attacking:
                    self.vel_x = self.SPEED
                    if self.flip:
                        moving_forward  = False
                        moving_backward = True
                    else:
                        moving_forward  = True
                        moving_backward = False

                if key[self.controls["up"]] and not self.jump and not self.crouching and not self.attacking:
                    self.vel_y = self.jump_vel
                    self.jump  = True

        dx = self.vel_x
        self.vel_y += GRAVITY
        dy += self.vel_y
        next_rect = pygame.Rect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height)
        if next_rect.colliderect(target.rect) and not self.jump and not target.jump:
            dx = int(dx * 0.25)
            if self.rect.centerx < target.rect.centerx and dx > 0:
                if target.rect.right < screen_width:
                    target.rect.x += dx
                    if target.rect.right > screen_width:
                        target.rect.right = screen_width
                else:
                    dx = target.rect.left - self.rect.right
            elif self.rect.centerx > target.rect.centerx and dx < 0:
                if target.rect.left > 0:
                    target.rect.x += dx
                    if target.rect.left < 0:
                        target.rect.left = 0
                else:
                    dx = target.rect.right - self.rect.left

        target_in_stun = target.action in [26, 30, 31]

        if (target.action == 26) and not self.jump and not target.jump:
            target_desired = target.vel_x
            target_clamped = 0
        
        is_tatsu = self.attack_data.get(self.action, {}).get("dash_vel_x") is not None
        attacker_caused_knockdown = self.attacking or self.action in [34, 35] or pygame.time.get_ticks() < self.throw_recovery_timer

        if target_in_stun and not self.jump and not target.jump and not attacker_caused_knockdown and not is_tatsu:
            target_desired = target.vel_x
            target_clamped = 0
            
            if target.rect.left <= 0 and target_desired < 0:
                target_clamped = target_desired
            elif target.rect.right >= screen_width and target_desired > 0:
                target_clamped = target_desired
                
            if target_clamped != 0:
                dx -= target_clamped
            
            if target.rect.left <= 0 and target_desired < 0:
                target_clamped = target_desired
            elif target.rect.right >= screen_width and target_desired > 0:
                target_clamped = target_desired
                
            if target_clamped != 0:
                dx -= target_clamped

        if self.rect.left + dx < 0:
            dx = 0 - self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right

        if self.rect.bottom + dy >= screen_height - 70:
            if self.jump and self.special_leapt and self.vel_y < 0:
                pass
            else:
                self.vel_y = 0
                dy = screen_height - 70 - self.rect.bottom
                self.jump = False

                if self.action == 28 and not self.knocked_down:
                    self.knocked_down = True
                    self.vel_x = 0
                    self.update_action(29)
                    self.wakeup_timer = current_time + 800
                elif self.knocked_down:
                    if current_time >= self.wakeup_timer:
                        self.update_action(0)
                        self.knocked_down = False
                        target.combo = 0
                        self.juggle_limit = 0
                else:
                    leap_frame = self.attack_data.get(self.action, {}).get("leap_on_frame")
                    if leap_frame is not None and self.special_leapt:
                        self.attacking = False
                    elif self.action in [18, 19, 20, 21]:
                        self.attacking = False

        if not self.jump and not self.attacking and not in_hitstun and not is_knocked_out_of_action:
            self.flip = target.rect.centerx > self.rect.centerx

        self.rect.x += dx
        self.rect.y += dy

        if self.rect.collidelist(target.active_hurtbox) != -1 and not target.knocked_down:
            if self.rect.centerx < target.rect.centerx:
                self.rect.x -= 2
            else:
                self.rect.x += 2

        if not in_hitstun and not is_knocked_out_of_action:
            if self.attacking:
                if not self.attack_routed and self.action not in [50, 51, 55, 56]:
                    if self.jump:
                        if   self.attack_type == 1: self.update_action(18) # j.LP
                        elif self.attack_type == 2: self.update_action(20) # j.LK
                        elif self.attack_type == 3: self.update_action(19) # j.HP
                        elif self.attack_type == 4: self.update_action(21) # j.HK
                    elif self.crouching:
                        if   self.attack_type == 2 and self.attack_dir == "3": self.update_action(41) # df.LK
                        elif self.attack_type == 1: self.update_action(14) # cr.LP
                        elif self.attack_type == 2: self.update_action(16) # cr.LK
                        elif self.attack_type == 3: self.update_action(15) # cr.HP
                        elif self.attack_type == 4: self.update_action(17) # cr.HK
                    else:
                        if   self.attack_type == 4 and self.attack_dir == "4": self.update_action(40) # b.HK
                        elif self.attack_type == 1: self.update_action(10) # LP
                        elif self.attack_type == 2: self.update_action(12) # LK
                        elif self.attack_type == 3: self.update_action(11) # HP
                        elif self.attack_type == 4: self.update_action(13) # HK
                    self.attack_routed = True
            elif self.dashing:
                pass

            elif self.jump:
                self.update_action(4 if self.vel_x == 0 else 3)
            elif self.crouching:
                if not self.attacking:
                    was_attacking = self.action not in [0, 1, 2, 3, 4, 5]
                    self.update_action(5)
                    if was_attacking:
                        self.frame_index = len(self.animation_list[5]) - 1
            elif moving_forward:
                self.update_action(1)
            elif moving_backward:
                self.update_action(2)
            else:
                self.update_action(0)

    def handle_animation_loop(self, current_attack):
        loop_range = current_attack.get("loop_range")
        if loop_range:
            if self.frame_index > loop_range[1]:
                self.loop_count += 1
                if self.loop_count < current_attack.get("loop_times", 0):
                    self.frame_index = loop_range[0]
                else:
                    self.frame_index = len(self.animation_list[self.action])

    def update(self, surface, target):
        self.image = self.animation_list[self.action][self.frame_index]
        current_attack = self.attack_data.get(self.action, {})
        max_hits = current_attack.get("max_hits", 1)
        is_multi_hit = max_hits > 1

        if self.super_flash_timer > 0:
            self.super_flash_timer -= 1
            return

        if pygame.time.get_ticks() < self.hitstop_timer:
            return

        current_attack = self.attack_data.get(self.action, {})

        if self.action in list(range(10, 22)) + [6, 7, 40, 41, 50, 51, 52, 53, 54, 55, 56, 80, 81, 30, 31, 32, 33]:
            animation_cooldown = 40
        elif self.action == 5:
            animation_cooldown = 60
        elif self.action in [26, 27, 28, 29]:
            animation_cooldown = 80
        else:
            animation_cooldown = 100
        custom_cooldowns = current_attack.get("frame_cooldowns", {})
        if self.frame_index in custom_cooldowns:
            animation_cooldown = custom_cooldowns[self.frame_index]

        self.active_hitboxes = []

        self.active_hurtbox = [self.rect.copy()] 
        
        if self.action in self.hurtbox_data and self.hurtbox_data[self.action]:
            check_frame = self.frame_index
            
            if check_frame in self.hurtbox_data[self.action]:
                box_data = self.hurtbox_data[self.action][check_frame]
                if isinstance(box_data, tuple) and isinstance(box_data[0], int):
                    box_data = [box_data]
                    
                self.active_hurtbox = []
                for (offset_x, offset_y, box_w, box_h) in box_data:
                    hurt_x = (
                        self.rect.centerx - offset_x - box_w
                        if self.flip
                        else self.rect.centerx + offset_x
                    )
                    hurt_y = (self.rect.centery - 150) + offset_y
                    self.active_hurtbox.append(pygame.Rect(hurt_x, hurt_y, box_w, box_h))

        current_attack = self.attack_data.get(self.action, {})
        max_hits = current_attack.get("max_hits", 1)
        is_multi_hit = max_hits > 1

        if is_multi_hit:
            can_check_hitbox = (self.special_hit_count < max_hits) and (pygame.time.get_ticks() >= self.special_hit_cooldown)
        else:
            can_check_hitbox = self.attacking and not self.attack_hit

        if self.pending_grab and self.action == self.pending_grab["action_id"]:
            active_frame = self.pending_grab.get("active_frame", 5)
            if self.frame_index == active_frame:
                grab_range = self.pending_grab.get("grab_range", 120)
                dist = abs(self.rect.centerx - target.rect.centerx)
                if dist <= grab_range and not target.knocked_down:
                    hit_info = self.attack_data.get(
                        self.action, {"damage": 200, "hitstun": 600}
                    )
                    target.health -= hit_info["damage"]

                    target.get_hit(
                        is_knockdown=True,
                        attacker_x=self.rect.centerx,
                        hitstun_duration=hit_info["hitstun"]
                    )
                self.pending_grab = None

        if self.attacking and self.action == 32 and not self.attack_hit:
            if self.action in self.throwbox_data and self.frame_index in self.throwbox_data[self.action]:
                raw = self.throwbox_data[self.action][self.frame_index]
                box_list = [raw] if isinstance(raw[0], int) else list(raw)

                for (offset_x, offset_y, box_w, box_h) in box_list:
                    t_x = self.rect.centerx - offset_x - box_w if self.flip else self.rect.centerx + offset_x
                    t_y = (self.rect.centery - 150) + offset_y
                    t_rect = pygame.Rect(t_x, t_y, box_w, box_h)
                    
                    self.active_hitboxes.append(t_rect)

                    if t_rect.collidelist(target.active_hurtbox) != -1 and not target.jump and not target.knocked_down:
                        if target.action == 32:
                            # --- INSTANT TECH (Both players threw at the same time) ---
                            self.attack_hit = True
                            self.attacking = False
                            self.vel_x = 5 if self.flip else -5
                            self.update_action(33)
                            self.hitstun_timer = pygame.time.get_ticks() + (len(self.animation_list[33]) * 40)
                            
                            target.attacking = False
                            target.vel_x = -5 if target.flip else 5
                            target.update_action(33)
                            target.hitstun_timer = pygame.time.get_ticks() + (len(target.animation_list[33]) * 40)
                            target.grabbed_by = None
                            break
                        else:
                            # --- NORMAL GRAB ---
                            self.attack_hit = True
                            self.vel_x = 0
                            self.vel_y = 0
                            self.update_action(getattr(self, "throw_direction", 34))
                            
                            target.attacking = False
                            target.update_action(26)
                            target.vel_x = 0
                            target.vel_y = 0 
                            target.tech_timer = pygame.time.get_ticks() + 200
                            target.grabbed_by = self
                            break

       
        if self.action in [34, 35]:
            throw_info = self.throw_data.get(self.action, {"damage": 130})
            damage_frame = throw_info.get("damage_on_frame", len(self.animation_list[self.action]) - 1)
            
            if self.frame_index == damage_frame and target.grabbed_by == self:
                target.health -= throw_info.get("damage", 130)
                
                target.get_hit(
                    is_knockdown=True, 
                    attacker_x=self.rect.centerx, 
                    hitstun_duration=500,
                    launch_velocity=throw_info.get("launch_velocity", (8, -20))
                )
                target.grabbed_by = None

        if self.attacking and can_check_hitbox:
            if self.action in self.hitbox_data and self.hitbox_data[self.action]:
                check_frame = self.frame_index

                if self.action in [16, 17, 18, 19, 50, 51, 55, 56]:
                    max_hb_frame = max(self.hitbox_data[self.action].keys())
                    if check_frame > max_hb_frame:
                        check_frame = max_hb_frame

                if check_frame in self.hitbox_data[self.action]:
                    raw = self.hitbox_data[self.action][check_frame]
                    if isinstance(raw[0], int):
                        box_list = [raw]
                    else:
                        box_list = list(raw)

                    for (offset_x, offset_y, box_w, box_h) in box_list:
                        hitbox_scale = current_attack.get("hitbox_scale", 1.0)
                        hitbox_offset_x = current_attack.get("hitbox_offset_x", 0)

                        box_w = int(box_w * hitbox_scale)
                        offset_x += hitbox_offset_x if self.flip else -hitbox_offset_x

                        hitbox_x = (
                            self.rect.centerx - offset_x - box_w
                            if self.flip
                            else self.rect.centerx + offset_x
                        )
                        hitbox_y = (self.rect.centery - 150) + offset_y
                        self.active_hitboxes.append(pygame.Rect(hitbox_x, hitbox_y, box_w, box_h))

                    any_hit = any(
                        hb.collidelist(target.active_hurtbox) != -1
                        for hb in self.active_hitboxes
                    )

                    if any_hit and not target.knocked_down:
                        # Fetch nested hit data for specials, or root data for normals
                        if "hits" in current_attack:
                            hit_idx = min(self.special_hit_count, len(current_attack["hits"]) - 1)
                            hit_info = current_attack["hits"][hit_idx]
                            attack_prop = current_attack.get("property", "mid")
                        else:
                            hit_info = current_attack if current_attack else {"damage": 50, "hitstun": 300, "property": "mid"}
                            attack_prop = hit_info.get("property", "mid")

                        # Read your custom data to see if the hit is allowed to connect
                        target_eligible = True
                        req_state = hit_info.get("eligible_if")
                        if req_state == "airborne" and not target.jump:
                            target_eligible = False
                        elif req_state == "grounded" and target.jump:
                            target_eligible = False

                        if target_eligible:
                            juggle_potential = current_attack.get("juggle_potential", 0)
                            juggle_increase  = hit_info.get("juggle_add", 1)
                            launch_vel       = hit_info.get("launch_velocity", (10, -20))
                            causes_knock     = hit_info.get("causes_knockdown", False)

                            if target.action == 28 and juggle_potential < target.juggle_limit:
                                pass
                            else:
                                block_type = target.check_block(attack_prop)

                                if self.jump:
                                    self.vel_x = 0
                                elif current_attack.get("no_pushback"):
                                    pass
                                else:
                                    self.vel_x = -3 if self.flip else 3

                                hitstop = 180
                                self.hitstop_timer  = pygame.time.get_ticks() + hitstop
                                target.hitstop_timer = pygame.time.get_ticks() + hitstop
                                self.update_time    += hitstop

                                if block_type:
                                    target.combo = 0 
                                    self.attack_hit = True 
                                    
                                    target.block_attack(
                                        attacker_x=self.rect.centerx, 
                                        blockstun_duration=hit_info["hitstun"] + hitstop, 
                                        is_crouch_block=(block_type == "crouch"),
                                    )
                                    self.super_meter  = min(100, self.super_meter  + int(hit_info["damage"] * 0.4))
                                    target.super_meter = min(100, target.super_meter + int(hit_info["damage"] * 0.3))
                                    
                                    if is_multi_hit:
                                        self.special_hit_count += 1
                                        self.special_hit_cooldown = pygame.time.get_ticks() + hitstop + current_attack.get("hit_cooldown", 40)
                                else:
                                    target.health -= hit_info["damage"]
                                    self.combo += 1
                                    self.super_meter  = min(100, self.super_meter  + int(hit_info["damage"] * 0.2))
                                    target.super_meter = min(100, target.super_meter + int(hit_info["damage"] * 0.15))

                                    # juggle math
                                    if target.action == 28 or causes_knock:
                                        target.juggle_limit += juggle_increase
                                        causes_knock = True

                                    if is_multi_hit:
                                        self.special_hit_count += 1
                                        self.special_hit_cooldown = pygame.time.get_ticks() + hitstop + current_attack.get("hit_cooldown", 40)

                                    self.attack_hit = True

                                    target.get_hit(
                                            is_knockdown=causes_knock,
                                            attacker_x=self.rect.centerx,
                                            hitstun_duration=hit_info["hitstun"] + hitstop,
                                            launch_velocity=launch_vel
                                        )
            
        leap_frame = current_attack.get("leap_on_frame")
        if leap_frame is not None and not self.special_leapt and self.frame_index >= leap_frame:
            self.jump = True
            self.special_leapt = True
            self.vel_y = current_attack.get("leap_vel_y", -25)
            raw_vx = current_attack.get("leap_vel_x", 5)
            self.vel_x = raw_vx if self.flip else -raw_vx

        leaps_list = current_attack.get("leaps")
        if leaps_list is not None:
            for leap in leaps_list:
                if self.frame_index == leap.get("on_frame"):
                    self.jump = True
                    self.special_leapt = True
                    self.vel_y = leap.get("vel_y", -25)
                    raw_vx = leap.get("vel_x", 5)
                    self.vel_x = raw_vx if self.flip else -raw_vx

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time  = pygame.time.get_ticks()
            self.handle_animation_loop(current_attack)

            

        if self.frame_index >= len(self.animation_list[self.action]):
            hold_last = current_attack.get("hold_last_frame", False)

            if hold_last:
                if not self.jump:
                    self.attacking = False
                    self.attack_routed = False
                    self.frame_index = 0
                    self.update_action(0)  # idle
                else:
                    self.frame_index = len(self.animation_list[self.action]) - 1
            
            elif self.action in [4, 5, 26, 27, 28, 29, 30, 31, 33]:
                self.frame_index = len(self.animation_list[self.action]) - 1
                
            else:
                self.frame_index = 0
                if self.action in list(range(10, 22)) + [32, 33, 34, 35, 40, 41] + list(range(50, 57)) + [80, 81]:
                    self.attacking = False
                    self.attack_routed = False
                    self.vel_x = 0
                    if self.action in [34, 35]:
                        self.throw_recovery_timer = pygame.time.get_ticks() + 1000 # 1 second grace period
                    if target.grabbed_by == self:
                        target.grabbed_by = None
                    if self.crouching:
                        self.update_action(5)
                        self.frame_index = len(self.animation_list[5]) - 1
                    else:
                        self.update_action(0)
                
                elif self.action in [6, 7]: 
                    self.dashing = False
                    self.vel_x = 0
                    self.update_action(0)

        for p in self.active_projectiles[:]:
            p.update(target)
            if not p.active:
                self.active_projectiles.remove(p)

        if self.action == 54 and self.frame_index == 5 and not self.projectile_fired:
            proj_cfg = self.projectile_cfg or {}
            speed    = proj_cfg.get("heavy_speed", 22) if self.is_heavy_hadouken else proj_cfg.get("light_speed", 14)
            damage   = proj_cfg.get("damage", 60)
            hitstun  = proj_cfg.get("hitstun", 300)
            hitbox   = proj_cfg.get("hitbox", (0, 0, 60, 60))
            
            vis_x_off = proj_cfg.get("visual_x_offset", 0) 

            if not self.flip:
                speed = -speed

            offset_x, offset_y, box_w, box_h = hitbox

            spawn_x = self.rect.centerx - offset_x - box_w if self.flip else self.rect.centerx + offset_x
            spawn_y = (self.rect.centery - 150) + offset_y

            proj = Projectile(
                self, 
                spawn_x, spawn_y,
                speed,
                self.proj_imgs, self.proj_hit_imgs,
                self.flip,
                damage, hitstun,
                box_w, box_h,
                vis_x_off 
            )
            self.active_projectiles.append(proj)
            self.projectile_fired = True

    def attack(self):
        self.hitstop_timer = 0
        self.dashing = False
        self.attacking    = True
        self.attack_routed = False
        self.attack_hit   = False
        self.frame_index  = 0
        if not self.jump:
            self.vel_x = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action      = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        img_rect        = img.get_rect()
        img_rect.center = self.rect.center
        img_rect.y     += -150
        surface.blit(img, img_rect)
        pygame.draw.rect(surface, (0, 255, 0), self.rect, 2)

        if self.action in self.vfx_list:
            frames = self.vfx_list[self.action]
            if self.frame_index < len(frames):
                vfx_img = pygame.transform.flip(frames[self.frame_index], self.flip, False)
                vfx_rect        = vfx_img.get_rect()
                vfx_rect.center = self.rect.center
                vfx_rect.y     += -150
                surface.blit(vfx_img, vfx_rect)

        for hitbox in self.active_hitboxes:
            pygame.draw.rect(surface, (255, 0, 0), hitbox, 2)
            
        for hurtbox in self.active_hurtbox:
            pygame.draw.rect(surface, (0, 0, 255), hurtbox, 2)

        for p in self.active_projectiles:
            p.draw(surface)


class Projectile():
    def __init__(self, owner, x, y, speed, image_list, hit_image_list, flip, damage, hitstun, box_w, box_h, visual_x_offset):
        self.owner           = owner
        self.visual_x_offset = visual_x_offset
        self.rect            = pygame.Rect(x, y, box_w, box_h)
        self.speed           = speed
        self.image_list      = image_list
        self.hit_image_list  = hit_image_list
        self.flip            = flip
        self.damage          = damage
        self.hitstun         = hitstun
        self.frame_index     = 0
        self.update_time     = pygame.time.get_ticks()
        self.active          = True
        self.hit             = False
        self.image           = self.image_list[self.frame_index] if self.image_list else None

    def update(self, target):
        SCREEN_WIDTH = 1200

        if self.hit:
            if pygame.time.get_ticks() - self.update_time > 40:
                self.frame_index += 1
                self.update_time  = pygame.time.get_ticks()
            if self.frame_index >= len(self.hit_image_list):
                self.active = False
            else:
                self.image = self.hit_image_list[self.frame_index]
        else:
            self.rect.x += self.speed
            if pygame.time.get_ticks() - self.update_time > 40:
                self.frame_index += 1
                self.update_time  = pygame.time.get_ticks()
            if self.image_list:
                if self.frame_index >= len(self.image_list):
                    self.frame_index = 0
                self.image = self.image_list[self.frame_index]

            target_attack_info = target.attack_data.get(target.action, {})
            is_proj_invul = target_attack_info.get("projectile_invul", False)

            if self.rect.collidelist(target.active_hurtbox) != -1 and not target.knocked_down:
                if not is_proj_invul:
                    self.hit = True
                    self.frame_index = 0
                    self.update_time = pygame.time.get_ticks()
                    
                    block_type = target.check_block("mid")
                    
                    if block_type:
                        target.combo = 0
                        self.juggle_limit = 0
                        target.block_attack(
                            attacker_x=self.rect.centerx, 
                            blockstun_duration=self.hitstun, 
                            is_crouch_block=(block_type == "crouch")
                        )
                    else:
                        self.owner.combo += 1
                        target.health -= self.damage
                        target.get_hit(
                            is_knockdown=False,
                            attacker_x=self.rect.centerx,
                            hitstun_duration=self.hitstun
                        )

            if self.rect.left > SCREEN_WIDTH + self.rect.width or self.rect.right < -self.rect.width:
                self.active = False

    def draw(self, surface):
        if self.image:
            img = pygame.transform.flip(self.image, self.flip, False)
            img_rect = img.get_rect()
            
            img_rect.center = self.rect.center
            
            if self.flip:
                img_rect.x += self.visual_x_offset
            else:
                img_rect.x -= self.visual_x_offset
                
            surface.blit(img, img_rect)
            
        pygame.draw.rect(surface, (0, 255, 0), self.rect, 2)