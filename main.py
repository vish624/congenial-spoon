

import pdb

import constants
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
            bx = sh[0]*constants.BWIDTH + x
            by = sh[1]*constants.BHEIGHT + y
            block = pygame.Rect(bx,by,constants.BWIDTH,constants.BHEIGHT)
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
            pygame.draw.rect(self.screen,constants.BLACK,bl,constants.MESH_WIDTH)
        
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
                tmp_shape.move_ip(0,constants.BHEIGHT)
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
            origX = (bl.x - self.x)/constants.BWIDTH
            origY = (bl.y - self.y)/constants.BHEIGHT
            rx,ry = self.get_rotated(origX,origY)
            newX = rx*constants.BWIDTH  + self.x + self.diffx
            newY = ry*constants.BHEIGHT + self.y + self.diffy
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
        self.resx = bx*constants.BWIDTH+2*constants.BOARD_HEIGHT+constants.BOARD_MARGIN
        self.resy = by*constants.BHEIGHT+2*constants.BOARD_HEIGHT+constants.BOARD_MARGIN
        # Prepare the pygame board objects (white lines)
        self.board_up    = pygame.Rect(0,constants.BOARD_UP_MARGIN,self.resx,constants.BOARD_HEIGHT)
        self.board_down  = pygame.Rect(0,self.resy-constants.BOARD_HEIGHT,self.resx,constants.BOARD_HEIGHT)
        self.board_left  = pygame.Rect(0,constants.BOARD_UP_MARGIN,constants.BOARD_HEIGHT,self.resy)
        self.board_right = pygame.Rect(self.resx-constants.BOARD_HEIGHT,constants.BOARD_UP_MARGIN,constants.BOARD_HEIGHT,self.resy)
        # List of used blocks
        self.blk_list    = []
        # Compute start indexes for tetris blocks
        self.start_x = math.ceil(self.resx/2.0)
        self.start_y = constants.BOARD_UP_MARGIN + constants.BOARD_HEIGHT + constants.BOARD_MARGIN
        # Blocka data (shapes and colors). The shape is encoded in the list of [X,Y] points. Each point
        # represents the relative position. The true/false value is used for the configuration of rotation where
        # False means no rotate and True allows the rotation.
        self.block_data = (
            ([[0,0],[1,0],[2,0],[3,0]],constants.RED,True),     # I block 
            ([[0,0],[1,0],[0,1],[-1,1]],constants.GREEN,True),  # S block 
            ([[0,0],[1,0],[2,0],[2,1]],constants.BLUE,True),    # J block
            ([[0,0],[0,1],[1,0],[1,1]],constants.ORANGE,False), # O block
            ([[-1,0],[0,0],[0,1],[1,1]],constants.GOLD,True),   # Z block
            ([[0,0],[1,0],[2,0],[1,1]],constants.PURPLE,True),  # T block
            ([[0,0],[1,0],[2,0],[0,1]],constants.CYAN,True),    # J block
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
        self.score_level = constants.SCORE_LEVEL

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
                    self.active_block.move(0,constants.BHEIGHT)
                if ev.key == pygame.K_LEFT:
                    self.active_block.move(-constants.BWIDTH,0)
                if ev.key == pygame.K_RIGHT:
                    self.active_block.move(constants.BWIDTH,0)
                if ev.key == pygame.K_SPACE:
                    self.active_block.rotate()
                if ev.key == pygame.K_p:
                    self.pause()
       
            # Detect if the movement event was fired by the timer.
            if ev.type == constants.TIMER_MOVE_EVENT:
                self.active_block.move(0,constants.BHEIGHT)
       
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
        speed = math.floor(constants.MOVE_TICK / self.speed)
        speed = max(1,speed)
        pygame.time.set_timer(constants.TIMER_MOVE_EVENT,speed)
 
    def run(self):
        # Initialize the game (pygame, fonts)
        pygame.init()
        pygame.font.init()
        self.myfont = pygame.font.SysFont(pygame.font.get_default_font(),constants.FONT_SIZE)
        self.screen = pygame.display.set_mode((self.resx,self.resy))
        pygame.display.set_caption("Tetris")
        # Setup the time to fire the move event every given time
        self.set_move_timer()
        # Control variables for the game. The done signal is used 
        # to control the main loop (it is set by the quit action), the game_over signal
        # is set by the game logic and it is also used for the detection of "game over" drawing.
        # Finally the new_block variable is used for the requesting of new tetris block. 
        self.done = False
        self.game_over = False
        self.new_block = True
        # Print the initial score
        self.print_status_line()
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
        string = ["SCORE: {0}   SPEED: {1}x".format(self.score,self.speed)]
        self.print_text(string,constants.POINT_MARGIN,constants.POINT_MARGIN)        

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
        self.active_block.move(0,constants.BHEIGHT)
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
            self.score += self.blocks_in_line * constants.POINT_VALUE 
            # Check if we need to speed up the game. If yes, change control variables
            if self.score > self.score_level:
                self.score_level *= constants.SCORE_LEVEL_RATIO
                self.speed       *= constants.GAME_SPEEDUP_RATIO
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
        pygame.draw.rect(self.screen,constants.WHITE,self.board_up)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_down)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_left)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_right)
        # Update the score         
        self.print_status_line()

    def get_block(self):
        """
        Generate new block into the game if is required.
        """
        if self.new_block:
            # Get the block and add it into the block list(static for now)
            tmp = random.randint(0,len(self.block_data)-1)
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
        self.screen.fill(constants.BLACK)
        self.draw_board()
        for blk in self.blk_list:
            blk.draw()
        # Draw the screen buffer
        pygame.display.flip()

if __name__ == "__main__":
    Tetris(16,30).run()

#Special add to try pull requests