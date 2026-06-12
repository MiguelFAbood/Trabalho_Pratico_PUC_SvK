import pygame
import os
import sys

pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("SvK Hitbox Visualizer V2")
font = pygame.font.SysFont(None, 24)

animation_folder = "assets/img/characters/kof/kyo/backdash" 
#animation_folder = "assets/img/characters/street fighter/ken/backdash" 

frames = []
try:
    file_list = os.listdir(animation_folder)
    file_list.sort()
    for file in file_list:
        if file.lower().endswith(".png"):
            img = pygame.image.load(os.path.join(animation_folder, file)).convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            frames.append(img)
except FileNotFoundError:
    print(f"Could not find folder: {animation_folder}")
    sys.exit()

if len(frames) == 0:
    print("No PNG images found in that folder.")
    sys.exit()

# State variables
current_frame = 0
# Dictionary to store hitboxes for specific frames: {frame_index: (offset_x, offset_y, w, h)}
frame_hitboxes = {} 

drawing = False
start_pos = (0, 0)

running = True
while running:
    screen.fill((30, 30, 30))
    
    # Get current sprite
    sprite = frames[current_frame]
    sprite_rect = sprite.get_rect(center=(500, 350))
    
    # Draw the sprite
    screen.blit(sprite, sprite_rect)

    # Draw center axis lines (Red) for reference
    pygame.draw.line(screen, (200, 0, 0), (sprite_rect.centerx, sprite_rect.top), (sprite_rect.centerx, sprite_rect.bottom), 1)
    pygame.draw.line(screen, (200, 0, 0), (sprite_rect.left, sprite_rect.centery), (sprite_rect.right, sprite_rect.centery), 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                current_frame = (current_frame + 1) % len(frames)
            elif event.key == pygame.K_LEFT:
                current_frame = (current_frame - 1) % len(frames)
            elif event.key == pygame.K_c: # Press 'C' to clear the hitbox on the current frame
                if current_frame in frame_hitboxes:
                    del frame_hitboxes[current_frame]
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left Click starts drawing
                drawing = True
                start_pos = event.pos
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing: # Release Left Click
                drawing = False
                end_pos = event.pos
                
                # Calculate the raw rectangle
                x = min(start_pos[0], end_pos[0])
                y = min(start_pos[1], end_pos[1])
                w = abs(start_pos[0] - end_pos[0])
                h = abs(start_pos[1] - end_pos[1])
                
                if w > 5 and h > 5: # Only save if it's an actual box, not an accidental click
                    offset_x = x - sprite_rect.centerx
                    offset_y = y - sprite_rect.centery
                    # Save to our dictionary for this specific frame
                    frame_hitboxes[current_frame] = (offset_x, offset_y, w, h)

    # Render the box while dragging
    if drawing:
        mouse_pos = pygame.mouse.get_pos()
        x = min(start_pos[0], mouse_pos[0])
        y = min(start_pos[1], mouse_pos[1])
        w = abs(start_pos[0] - mouse_pos[0])
        h = abs(start_pos[1] - mouse_pos[1])
        pygame.draw.rect(screen, (0, 255, 0), (x, y, w, h), 2)
        
    # Render the saved box for the current frame if it exists
    elif current_frame in frame_hitboxes:
        box_data = frame_hitboxes[current_frame]
        saved_rect = pygame.Rect(
            sprite_rect.centerx + box_data[0], 
            sprite_rect.centery + box_data[1], 
            box_data[2], 
            box_data[3]
        )
        pygame.draw.rect(screen, (0, 255, 0), saved_rect, 2)

    # --- UI Rendering ---
    # Show Frame Info
    frame_text = font.render(f"Frame: {current_frame} / {len(frames) - 1} (Use Left/Right Arrows to scrub)", True, (255, 255, 255))
    screen.blit(frame_text, (10, 10))
    
    # Show Instructions
    inst_text = font.render("Click & Drag to draw. Press 'C' to clear current frame.", True, (200, 200, 200))
    screen.blit(inst_text, (10, 40))

    # Generate Output String
    if frame_hitboxes:
        # Formats it exactly like your fighter.py dictionary: { 2: (x, y, w, h), 3: (x, y, w, h) }
        formatted_boxes = ", ".join([f"{f}: {data}" for f, data in sorted(frame_hitboxes.items())])
        output_data = f"{{ {formatted_boxes} }}"
    else:
        output_data = "{}"

    output_text = font.render(f"Output for fighter.py: {output_data}", True, (0, 255, 255))
    screen.blit(output_text, (10, 650))
    
    # Print to console as well so it's easy to copy
    print(f"Current Data: {output_data}", end='\r')

    pygame.display.flip()

pygame.quit()
sys.exit()