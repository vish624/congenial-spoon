

import pdb

import pygame
import math
import copy
import sys
import random



from pygame.locals import *














# Configuration of building shape block
# Width of the shape block
BWIDTH     = 20
# Height of the shape block
BHEIGHT    = 20
# Width of the line around the block
MESH_WIDTH = 1

# Configuration of the player board
# Board line height
BOARD_HEIGHT     = 7
# Margin of upper line (for score)
BOARD_UP_MARGIN  = 40
# Margins around all lines
BOARD_MARGIN     = 2

# Color declarations in the RGB notation
WHITE    = (255,255,255)
RED      = (255,0,0)
GREEN    = (0,255,0)
BLUE     = (0,0,255)
ORANGE   = (255,69,0)
GOLD     = (255,125,0)
PURPLE   = (128,0,128)
CYAN     = (0,255,255) 
BLACK    = (0,0,0)

# Additional colors for enhanced visuals
DARK_GRAY    = (40,40,40)
LIGHT_GRAY   = (100,100,100)
DARK_BLUE    = (0,0,100)
LIGHT_BLUE   = (100,150,255)
DARK_GREEN   = (0,100,0)
LIGHT_GREEN  = (100,255,100)
DARK_RED     = (100,0,0)
LIGHT_RED    = (255,100,100)
YELLOW       = (255,255,0)
PINK         = (255,100,255)
TEAL         = (0,128,128)
BROWN        = (139,69,19)

# Timing constraints
# Time for the generation of TIME_MOVE_EVENT (ms)
MOVE_TICK          = 1000
# Allocated number for the move dowon event
TIMER_MOVE_EVENT   = USEREVENT+1
# Speed up ratio of the game (integer values)
GAME_SPEEDUP_RATIO = 1.5
# Score LEVEL - first threshold of the score
SCORE_LEVEL        = 2000
# Score level ratio
SCORE_LEVEL_RATIO  = 2 

# Configuration of score
# Number of points for one building block
POINT_VALUE       = 100
# Margin of the SCORE string
POINT_MARGIN      = 10

# Font size for all strings (score, pause, game over)
FONT_SIZE           = 25

# Environmental effects configuration
# Wind effect settings
WIND_CHANCE         = 0.08 # 8% chance per frame for wind to affect piece (reduced from 10%)
WIND_STRENGTH       = 1    # Number of blocks wind can push
WIND_DIRECTION      = 1    # 1 for right, -1 for left (randomly chosen)

# Earthquake effect settings  
EARTHQUAKE_CHANCE   = 0.05 # 5% chance per frame for earthquake to affect piece
EARTHQUAKE_ROTATION = 90   # Degrees to rotate during earthquake

# Environmental effects timer
ENVIRONMENT_TICK    = 2000  # Check for environmental effects every 2000ms (2 seconds)
TIMER_ENVIRONMENT_EVENT = USEREVENT+2

class Block(object):
    """
    Class for handling of tetris block
    """    

    def __init__(self,shape,x,y,screen,color,rotate_en):
        """
        Initialize the tetris block class

        Parameters:
            - shape - list of block data. The list contains [X,Y] coordinates of
                      building blocks.
            - x - X coordinate of first tetris shape block
            - y - Y coordinate of first tetris shape block
            - screen  - screen to draw on
            - color - the color of each shape block in RGB notation
            - rotate_en - enable or disable the rotation
        """
        # The initial shape (convert all to Rect objects)
        self.shape = []
        for sh in shape:
            bx = sh[0]* BWIDTH + x
            by = sh[1]* BHEIGHT + y
            block = pygame.Rect(bx,by, BWIDTH, BHEIGHT)
            self.shape.append(block)     
        # Setup the rotation attribute
        self.rotate_en = rotate_en
        # Setup the rest of variables
        self.x = x
        self.y = y
        # Movement in the X,Y coordinates
        self.diffx = 0
        self.diffy = 0
        # Screen to drawn on
        self.screen = screen
        self.color = color
        # Rotation of the screen
        self.diff_rotation = 0

    def draw(self):
        """
        Draw the block from shape blocks. Each shape block
        is filled with a color and black border.
        """
        for bl in self.shape:
            pygame.draw.rect(self.screen,self.color,bl)
            pygame.draw.rect(self.screen, BLACK,bl, MESH_WIDTH)
        
    def get_rotated(self,x,y):
        """
        Compute the new coordinates based on the rotation angle.
        
        Parameters:
            - x - the X coordinate to transfer
            - y - the Y coordinate to transfer

        Returns the tuple with new (X,Y) coordinates.
        """
        # Use the classic transformation matrix:
        # https://www.siggraph.org/education/materials/HyperGraph/modeling/mod_tran/2drota.htm
        rads = self.diff_rotation * (math.pi / 180.0)
        newx = x*math.cos(rads) - y*math.sin(rads)
        newy = y*math.cos(rads) + x*math.sin(rads)
        return (newx,newy)        

    def move(self,x,y):
        """
        Move all elements of the block using the given offset.
        
        Parameters:
            - x - movement in the X coordinate
            - y - movement in the Y coordinate 
        """
        # Accumulate X,Y coordinates and call the update function       
        self.diffx += x
        self.diffy += y  
        self._update()

    def remove_blocks(self,y):
        """
        Remove blocks on the Y coordinate. All blocks
        above the Y are moved one step down. 

        Parameters:
            - y - Y coordinate to work with.
        """
        new_shape = []
        for shape_i in range(len(self.shape)):
            tmp_shape = self.shape[shape_i]
            if tmp_shape.y < y:
                # Block is above the y, move down and add it to the list of active shape
                # blocks.
                new_shape.append(tmp_shape)  
                tmp_shape.move_ip(0, BHEIGHT)
            elif tmp_shape.y > y:
                # Block is below the y, add it to the list. The block doesn't need to be moved because
                # the removed line is above it.
                new_shape.append(tmp_shape)
        # Setup the new list of block shapes.
        self.shape = new_shape

    def has_blocks(self):
        """
        Returns true if the block has some shape blocks in the shape list.
        """    
        return True if len(self.shape) > 0 else False

    def rotate(self):
        """
        Setup the rotation value to 90 degrees.
        """
        # Setup the rotation and update coordinates of all shape blocks.
        # The block is rotated iff the rotation is enabled
        if self.rotate_en:
            self.diff_rotation = 90
            self._update()

    def _update(self):
        """
        Update the position of all shape boxes.
        """
        for bl in self.shape:
            # Get old coordinates and compute new x,y coordinates. 
            # All rotation calculates are done in the original coordinates.
            origX = (bl.x - self.x)/ BWIDTH
            origY = (bl.y - self.y)/ BHEIGHT
            rx,ry = self.get_rotated(origX,origY)
            newX = rx* BWIDTH  + self.x + self.diffx
            newY = ry* BHEIGHT + self.y + self.diffy
            # Compute the relative move
            newPosX = newX - bl.x
            newPosY = newY - bl.y
            bl.move_ip(newPosX,newPosY)
        # Everyhting was moved. Setup new x,y, coordinates and reset all disable the move
        # variables.
        self.x += self.diffx
        self.y += self.diffy
        self.diffx = 0
        self.diffy = 0
        self.diff_rotation = 0

    def backup(self):
        """
        Backup the current configuration of shape blocks.
        """
        # Make the deep copy of the shape list. Also, remember
        # the current configuration.
        self.shape_copy = copy.deepcopy(self.shape)
        self.x_copy = self.x
        self.y_copy = self.y
        self.rotation_copy = self.diff_rotation     

    def restore(self):
        """
        Restore the previous configuraiton.
        """
        self.shape = self.shape_copy
        self.x = self.x_copy
        self.y = self.y_copy
        self.diff_rotation = self.rotation_copy

    def check_collision(self,rect_list):
        """
        The function checks if the block colides with any other block
        in the shape list. 

        Parameters:
            - rect_list - the function accepts the list of Rect object which
                         are used for the collistion detection. 
        """
        for blk in rect_list:
            collist = blk.collidelistall(self.shape)
            if len(collist):
                return True
        return False
    



class Tetris(object):
    """
    The class with implementation of tetris game logic.
    """

    def __init__(self,bx,by):
        """
        Initialize the tetris object.

        Parameters:
            - bx - number of blocks in x
            - by - number of blocks in y
        """
        # Compute the resolution of the play board based on the required number of blocks.
        self.resx = bx* BWIDTH+2* BOARD_HEIGHT+ BOARD_MARGIN
        self.resy = by* BHEIGHT+2* BOARD_HEIGHT+ BOARD_MARGIN
        
        # Add space for next shape preview
        self.preview_width = 200  # Width for preview area
        self.total_resx = self.resx + self.preview_width  # Total screen width including preview
        # Prepare the pygame board objects (white lines)
        self.board_up    = pygame.Rect(0, BOARD_UP_MARGIN,self.resx, BOARD_HEIGHT)
        self.board_down  = pygame.Rect(0,self.resy- BOARD_HEIGHT,self.resx, BOARD_HEIGHT)
        self.board_left  = pygame.Rect(0, BOARD_UP_MARGIN, BOARD_HEIGHT,self.resy)
        self.board_right = pygame.Rect(self.resx- BOARD_HEIGHT, BOARD_UP_MARGIN, BOARD_HEIGHT,self.resy)
        # List of used blocks
        self.blk_list    = []
        # Compute start indexes for tetris blocks
        self.start_x = math.ceil(self.resx/2.0)
        self.start_y =  BOARD_UP_MARGIN +  BOARD_HEIGHT +  BOARD_MARGIN
        # Blocka data (shapes and colors). The shape is encoded in the list of [X,Y] points. Each point
        # represents the relative position. The true/false value is used for the configuration of rotation where
        # False means no rotate and True allows the rotation.
        self.block_data = (
            ([[0,0],[1,0],[2,0],[3,0]], RED,True),     # I block 
            ([[0,0],[1,0],[0,1],[-1,1]], GREEN,True),  # S block 
            ([[0,0],[1,0],[2,0],[2,1]], BLUE,True),    # J block
            ([[0,0],[0,1],[1,0],[1,1]], ORANGE,False), # O block
            ([[-1,0],[0,0],[0,1],[1,1]], GOLD,True),   # Z block
            ([[0,0],[1,0],[2,0],[1,1]], PURPLE,True),  # T block
            ([[0,0],[1,0],[2,0],[0,1]], CYAN,True),    # J block
        )
        # Compute the number of blocks. When the number of blocks is even, we can use it directly but 
        # we have to decrese the number of blocks in line by one when the number is odd (because of the used margin).
        self.blocks_in_line = bx if bx%2 == 0 else bx-1
        self.blocks_in_pile = by
        # Score settings
        self.score = 0
        # Remember the current speed 
        self.speed = 1
        # The score level threshold
        self.score_level =  SCORE_LEVEL
        
        # Environmental effects settings
        self.wind_active = False
        self.wind_direction = 1  # 1 for right, -1 for left
        self.earthquake_active = False
        self.environment_timer = 0
        
        # Debug tracking for stuck blocks
        self.stuck_block_count = 0
        
        # Next shape preview
        self.next_shape_index = random.randint(0, len(self.block_data)-1)
        self.next_shape_block = None

    def apply_action(self):
        """
        Get the event from the event queue and run the appropriate 
        action.
        """
        # Take the event from the event queue.
        for ev in pygame.event.get():
            # Check if the close button was fired.
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.unicode == 'q'):
                self.done = True
            # Detect the key evevents for game control.
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_DOWN:
                    self.active_block.move(0, BHEIGHT)
                if ev.key == pygame.K_LEFT:
                    self.active_block.move(- BWIDTH,0)
                if ev.key == pygame.K_RIGHT:
                    self.active_block.move( BWIDTH,0)
                if ev.key == pygame.K_UP or ev.key == pygame.K_SPACE:
                    self.active_block.rotate()
                if ev.key == pygame.K_p:
                    self.pause()
       
            # Detect if the movement event was fired by the timer.
            if ev.type ==  TIMER_MOVE_EVENT:
                self.active_block.move(0, BHEIGHT)
                
            # Detect if the environment effects event was fired by the timer.
            if ev.type == TIMER_ENVIRONMENT_EVENT:
                self.update_environmental_effects()
       
    def pause(self):
        """
        Pause the game and draw the string. This function
        also calls the flip function which draws the string on the screen.
        """
        # Draw the string to the center of the screen.
        self.print_center(["PAUSE","Press \"p\" to continue"])
        pygame.display.flip()
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_p:
                    return
       
    def set_move_timer(self):
        """         
        Setup the move timer to the 
        """
        # Setup the time to fire the move event. Minimal allowed value is 1
        speed = math.floor( MOVE_TICK / self.speed)
        speed = max(1,speed)
        pygame.time.set_timer( TIMER_MOVE_EVENT,speed)
        
    def set_environment_timer(self):
        """
        Setup the environment effects timer
        """
        pygame.time.set_timer(TIMER_ENVIRONMENT_EVENT, ENVIRONMENT_TICK)
        
    def apply_wind_effect(self):
        """
        Apply wind effect to the active block
        """
        if self.wind_active and self.active_block:
            # Calculate wind movement
            wind_movement = self.wind_direction * WIND_STRENGTH * BWIDTH
            
            # Check if the wind movement would cause the block to go outside boundaries
            # Get the current block boundaries
            min_x = min(block.x for block in self.active_block.shape)
            max_x = max(block.x for block in self.active_block.shape)
            
            # Check if wind would push block outside the playable area
            if self.wind_direction > 0:  # Wind blowing right
                if max_x + wind_movement >= self.resx - BOARD_HEIGHT - BWIDTH:
                    return  # Don't apply wind if it would push block outside right boundary
            else:  # Wind blowing left
                if min_x + wind_movement <= BOARD_HEIGHT:
                    return  # Don't apply wind if it would push block outside left boundary
            
            # Try to move the block with wind
            self.active_block.backup()
            self.active_block.move(wind_movement, 0)
            
            # Check if wind movement causes collision with other blocks
            if self.block_colides():
                # Restore if collision detected
                self.active_block.restore()
            else:
                # Wind effect applied successfully
                self.active_block._update()
                
    def apply_earthquake_effect(self):
        """
        Apply earthquake effect to the active block
        """
        if self.earthquake_active and self.active_block and self.active_block.rotate_en:
            # Apply random rotation
            self.active_block.backup()
            self.active_block.diff_rotation = EARTHQUAKE_ROTATION
            self.active_block._update()
            
            # Check if rotation causes collision
            earthquake_collision = self.active_block.check_collision([self.board_left, self.board_right, self.board_down]) or self.block_colides()
            
            if earthquake_collision:
                # Restore if collision detected
                self.active_block.restore()
                
    def update_environmental_effects(self):
        """
        Update environmental effects - randomly activate wind and earthquake
        """
        # Update wind effect
        if random.random() < WIND_CHANCE:
            self.wind_active = True
            self.wind_direction = random.choice([-1, 1])  # Random direction
        else:
            self.wind_active = False
            
        # Update earthquake effect
        if random.random() < EARTHQUAKE_CHANCE:
            self.earthquake_active = True
        else:
            self.earthquake_active = False
            
    def check_block_boundaries(self):
        """
        Check if the active block is within proper boundaries and fix if needed
        """
        if not self.active_block:
            return
            
        # Get the current block boundaries
        min_x = min(block.x for block in self.active_block.shape)
        max_x = max(block.x for block in self.active_block.shape)
        
        # Check if block is stuck in left wall
        if min_x < BOARD_HEIGHT:
            # Move block to safe position
            correction = BOARD_HEIGHT - min_x
            self.active_block.backup()
            self.active_block.move(correction, 0)
            if not self.block_colides():
                self.active_block._update()
                self.stuck_block_count += 1
            else:
                self.active_block.restore()
                
        # Check if block is stuck in right wall
        elif max_x > self.resx - BOARD_HEIGHT - BWIDTH:
            # Move block to safe position
            correction = (self.resx - BOARD_HEIGHT - BWIDTH) - max_x
            self.active_block.backup()
            self.active_block.move(correction, 0)
            if not self.block_colides():
                self.active_block._update()
                self.stuck_block_count += 1
            else:
                self.active_block.restore()
                
    def generate_next_shape(self):
        """
        Generate the next shape for preview
        """
        data = self.block_data[self.next_shape_index]
        # Create a preview block positioned in the preview area
        preview_x = self.resx + 20  # Position to the right of the game board
        preview_y = BOARD_UP_MARGIN + 100  # Position below the score
        self.next_shape_block = Block(data[0], preview_x, preview_y, self.screen, data[1], data[2])
        
    def get_next_shape_index(self):
        """
        Get the next shape index and generate a new one
        """
        current_index = self.next_shape_index
        # Generate new next shape
        self.next_shape_index = random.randint(0, len(self.block_data)-1)
        self.generate_next_shape()
        return current_index
 
    def run(self):
        # Initialize the game (pygame, fonts)
        pygame.init()
        pygame.font.init()
        self.myfont = pygame.font.SysFont(pygame.font.get_default_font(), FONT_SIZE)
        self.screen = pygame.display.set_mode((self.total_resx,self.resy))
        pygame.display.set_caption("Tetris")
        # Setup the time to fire the move event every given time
        self.set_move_timer()
        # Setup the environment effects timer
        self.set_environment_timer()
        # Control variables for the game. The done signal is used 
        # to control the main loop (it is set by the quit action), the game_over signal
        # is set by the game logic and it is also used for the detection of "game over" drawing.
        # Finally the new_block variable is used for the requesting of new tetris block. 
        self.done = False
        self.game_over = False
        self.new_block = True
        # Print the initial score
        self.print_status_line()
        
        # Initialize the next shape preview
        self.generate_next_shape()
        while not(self.done) and not(self.game_over):
            # Get the block and run the game logic
            self.get_block()
            self.game_logic()
            self.draw_game()
        # Display the game_over and wait for a keypress
        if self.game_over:
            self.print_game_over()
        # Disable the pygame stuff
        pygame.font.quit()
        pygame.display.quit()        
   
    def print_status_line(self):
        """
        Print the current state line
        """
        status_string = "SCORE: {0}   SPEED: {1}x".format(self.score,self.speed)
        
        # Add environmental effects status
        effects = []
        if self.wind_active:
            direction = "→" if self.wind_direction > 0 else "←"
            effects.append("WIND " + direction)
        if self.earthquake_active:
            effects.append("EARTHQUAKE!")
            
        if effects:
            status_string += "   EFFECTS: " + ", ".join(effects)
            

            
        string = [status_string]
        self.print_text(string, POINT_MARGIN, POINT_MARGIN)        

    def print_game_over(self):
        """
        Print the game over string.
        """
        # Print the game over text
        self.print_center(["Game Over","Press \"q\" to exit"])
        # Draw the string
        pygame.display.flip()
        # Wait untill the space is pressed
        while True: 
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.unicode == 'q'):
                    return

    def print_text(self,str_lst,x,y):
        """
        Print the text on the X,Y coordinates. 

        Parameters:
            - str_lst - list of strings to print. Each string is printed on new line.
            - x - X coordinate of the first string
            - y - Y coordinate of the first string
        """
        prev_y = 0
        for string in str_lst:
            size_x,size_y = self.myfont.size(string)
            txt_surf = self.myfont.render(string,False,(255,255,255))
            self.screen.blit(txt_surf,(x,y+prev_y))
            prev_y += size_y 

    def print_center(self,str_list):
        """
        Print the string in the center of the screen.
        
        Parameters:
            - str_lst - list of strings to print. Each string is printed on new line.
        """
        max_xsize = max([tmp[0] for tmp in map(self.myfont.size,str_list)])
        self.print_text(str_list,self.resx/2-max_xsize/2,self.resy/2)

    def block_colides(self):
        """
        Check if the block colides with any other block.

        The function returns True if the collision is detected.
        """
        for blk in self.blk_list:
            # Check if the block is not the same
            if blk == self.active_block:
                continue 
            # Detect situations
            if(blk.check_collision(self.active_block.shape)):
                return True
        return False

    def game_logic(self):
        """
        Implementation of the main game logic. This function detects colisions
        and insertion of new tetris blocks.
        """
        # Remember the current configuration and try to 
        # apply the action
        self.active_block.backup()
        self.apply_action()
        
        # Apply environmental effects
        self.apply_wind_effect()
        self.apply_earthquake_effect()
        
        # Check and fix any stuck blocks
        self.check_block_boundaries()
        # Border logic, check if we colide with down border or any
        # other border. This check also includes the detection with other tetris blocks. 
        down_board  = self.active_block.check_collision([self.board_down])
        any_border  = self.active_block.check_collision([self.board_left,self.board_up,self.board_right])
        block_any   = self.block_colides()
        # Restore the configuration if any collision was detected
        if down_board or any_border or block_any:
            self.active_block.restore()
        # So far so good, sample the previous state and try to move down (to detect the colision with other block). 
        # After that, detect the the insertion of new block. The block new block is inserted if we reached the boarder
        # or we cannot move down.
        self.active_block.backup()
        self.active_block.move(0, BHEIGHT)
        can_move_down = not self.block_colides()  
        self.active_block.restore()
        # We end the game if we are on the respawn and we cannot move --> bang!
        if not can_move_down and (self.start_x == self.active_block.x and self.start_y == self.active_block.y):
            self.game_over = True
        # The new block is inserted if we reached down board or we cannot move down.
        if down_board or not can_move_down:     
            # Request new block
            self.new_block = True
            # Detect the filled line and possibly remove the line from the 
            # screen.
            self.detect_line()   
 
    def detect_line(self):
        """
        Detect if the line is filled. If yes, remove the line and
        move with remaining bulding blocks to new positions.
        """
        # Get each shape block of the non-moving tetris block and try
        # to detect the filled line. The number of bulding blocks is passed to the class
        # in the init function.
        for shape_block in self.active_block.shape:
            tmp_y = shape_block.y
            tmp_cnt = self.get_blocks_in_line(tmp_y)
            # Detect if the line contains the given number of blocks
            if tmp_cnt != self.blocks_in_line:
                continue 
            # Ok, the full line is detected!     
            self.remove_line(tmp_y)
            # Update the score.
            self.score += self.blocks_in_line *  POINT_VALUE 
            # Check if we need to speed up the game. If yes, change control variables
            if self.score > self.score_level:
                self.score_level *= SCORE_LEVEL_RATIO
                self.speed       *= GAME_SPEEDUP_RATIO
                # Change the game speed
                self.set_move_timer()

    def remove_line(self,y):
        """
        Remove the line with given Y coordinates. Blocks below the filled
        line are untouched. The rest of blocks (yi > y) are moved one level done.

        Parameters:
            - y - Y coordinate to remove.
        """ 
        # Iterate over all blocks in the list and remove blocks with the Y coordinate.
        for block in self.blk_list:
            block.remove_blocks(y)
        # Setup new block list (not needed blocks are removed)
        self.blk_list = [blk for blk in self.blk_list if blk.has_blocks()]

    def get_blocks_in_line(self,y):
        """
        Get the number of shape blocks on the Y coordinate.

        Parameters:
            - y - Y coordinate to scan.
        """
        # Iteraveovel all block's shape list and increment the counter
        # if the shape block equals to the Y coordinate.
        tmp_cnt = 0
        for block in self.blk_list:
            for shape_block in block.shape:
                tmp_cnt += (1 if y == shape_block.y else 0)            
        return tmp_cnt

    def draw_board(self):
        """
        Draw the white board.
        """
        pygame.draw.rect(self.screen, WHITE,self.board_up)
        pygame.draw.rect(self.screen, WHITE,self.board_down)
        pygame.draw.rect(self.screen, WHITE,self.board_left)
        pygame.draw.rect(self.screen, WHITE,self.board_right)
        # Update the score         
        self.print_status_line()

    def get_block(self):
        """
        Generate new block into the game if is required.
        """
        if self.new_block:
            # Use the next shape system
            tmp = self.get_next_shape_index()
            data = self.block_data[tmp]
            self.active_block = Block(data[0],self.start_x,self.start_y,self.screen,data[1],data[2])
            self.blk_list.append(self.active_block)
            self.new_block = False

    def draw_game(self):
        """
        Draw the game screen.
        """
        # Clean the screen, draw the board and draw
        # all tetris blocks
        self.screen.fill( DARK_BLUE)  # Dark blue background instead of black
        self.draw_board()
        for blk in self.blk_list:
            blk.draw()
            
        # Draw environmental effects visual feedback
        self.draw_environmental_effects()
        
        # Draw next shape preview
        self.draw_next_shape_preview()
        
        # Draw the screen buffer
        pygame.display.flip()
        
    def draw_environmental_effects(self):
        """
        Draw visual feedback for environmental effects
        """
        if self.wind_active:
            # Draw wind arrows on the sides
            arrow_color = (100, 150, 255)  # Light blue
            if self.wind_direction > 0:  # Wind blowing right
                # Draw arrows on the right side
                for i in range(3):
                    y_pos = BOARD_UP_MARGIN + 50 + i * 30
                    pygame.draw.polygon(self.screen, arrow_color, [
                        (self.resx - 30, y_pos),
                        (self.resx - 40, y_pos - 5),
                        (self.resx - 40, y_pos + 5)
                    ])
            else:  # Wind blowing left
                # Draw arrows on the left side
                for i in range(3):
                    y_pos = BOARD_UP_MARGIN + 50 + i * 30
                    pygame.draw.polygon(self.screen, arrow_color, [
                        (30, y_pos),
                        (40, y_pos - 5),
                        (40, y_pos + 5)
                    ])
                    
        if self.earthquake_active:
            # Draw earthquake effect (shaking screen effect)
            # This is a simple visual indicator - you could make it more elaborate
            shake_offset = random.randint(-2, 2)
            # Draw a subtle border effect
            pygame.draw.rect(self.screen, (255, 100, 100), 
                           (shake_offset, shake_offset, self.resx - 2*shake_offset, self.resy - 2*shake_offset), 3)
            
    def draw_next_shape_preview(self):
        """
        Draw the next shape preview area
        """
        if self.next_shape_block:
            # Draw preview background
            preview_rect = pygame.Rect(self.resx, 0, self.preview_width, self.resy)
            pygame.draw.rect(self.screen, (50, 50, 50), preview_rect)  # Dark gray background
            
            # Draw preview border
            pygame.draw.rect(self.screen, WHITE, preview_rect, 2)
            
            # Draw "NEXT" label
            next_text = self.myfont.render("NEXT", True, WHITE)
            self.screen.blit(next_text, (self.resx + 10, 10))
            
            # Draw the next shape
            self.next_shape_block.draw()

if __name__ == "__main__":
    Tetris(16,30).run()








