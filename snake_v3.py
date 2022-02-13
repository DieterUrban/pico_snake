
from machine import Pin,SPI,PWM
import framebuf
import time
import os
from random import randint as rnd
from Pico_LCD1_3 import LCD_1inch3


BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

pwm = PWM(Pin(BL))
pwm.freq(1000)
pwm.duty_u16(32768)#max 65535

LCD = LCD_1inch3()
#color BRG
LCD.fill(0x0000)
LCD.show()

keyA = Pin(15,Pin.IN,Pin.PULL_UP)
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
keyX = Pin(19 ,Pin.IN,Pin.PULL_UP)
keyY= Pin(21 ,Pin.IN,Pin.PULL_UP)

up = Pin(2,Pin.IN,Pin.PULL_UP)
dowm = Pin(18,Pin.IN,Pin.PULL_UP)
left = Pin(16,Pin.IN,Pin.PULL_UP)
right = Pin(20,Pin.IN,Pin.PULL_UP)
ctrl = Pin(3,Pin.IN,Pin.PULL_UP)

class SNAKE():
    def __init__(self, x, y, size=10, max_screen=240,
                 tail_color=LCD.green, head_color=LCD.blue, bg_color=0x0000):
        
        self.bg_color = bg_color
        self.tail_color = tail_color
        self.head_color = head_color
        self.head_x = x
        self.head_y = y
        self.s_max_x = max_screen - size
        self.s_max_y = max_screen - size
        self.size = size
        
        self.snake = [
                [x,y],[x-size,y],[x-size*2,y]
            ]
        
        self.direction = ""
        
    def move(self, direction):
        self.direction = direction
        
        if direction == "r":
            self.head_x += self.size        
        elif direction == "l":
            self.head_x -= self.size
        elif direction == "u":
            self.head_y -= self.size
        elif direction == "d":
            self.head_y += self.size
            
        self.last_tail_end = self.snake[-1]
        self.snake.insert(0, [self.head_x, self.head_y])
        self.snake.pop()

        if self.head_x > self.s_max_x or self.head_y > self.s_max_y or self.head_x < 0 or self.head_y < 0:
            return True        
            
        return False

    def undo_move(self):        
        # set head to previous head
        self.head_x = self.snake[1][0]
        self.head_y = self.snake[1][1]
        # remove actual head from snake array (out of screen)
        self.snake.pop(0)
        # add previous tail to snake array
        self.snake.append(self.last_tail_end)
        self.last_tail_end = self.snake[-1] # set actual tail end


    def add_food(self):
        self.snake.append(self.last_tail_end)
    
    def draw(self):
        last_tail_end = self.last_tail_end
        
        LCD.fill_rect(last_tail_end[0], last_tail_end[1], self.size, self.size, self.bg_color)
        
        for position in self.snake[1:]:
            LCD.fill_rect(position[0], position[1], self.size, self.size, self.tail_color)
        
        LCD.fill_rect(self.snake[0][0], self.snake[0][1], self.size, self.size, self.head_color)

        LCD.show()
    
    def collision(self):
        head = self.snake[0]
        
        for pos in self.snake[1:]:
            if pos == head:
                return True
            
        return False
    
    def automove(self, errors):
        errors += 1
        if self.head_x > self.s_max_x:
            d_new = "u"
        if self.head_y > self.s_max_y: #move down
            d_new = "r"
        if self.head_x < 0:
            d_new = "d"
        if self.head_y < 0:
            d_new = "l"
        
        self.undo_move()
        # print(d_new)
        return (d_new, errors)

def get_direction(direction):
    if left.value() == 0:
        if direction != "r":
            direction = "l"
    elif right.value() == 0:
        if direction != "l":
            direction = "r"
    elif up.value() == 0:
        if direction != "d":
            direction = "u"
    elif dowm.value() == 0:
        if direction != "u":
            direction = "d"
            
    return direction



if __name__=='__main__':    
    #width height
    sw = 240   # 0 = left, 240 = right
    sh = 240   # 0 = top, 240 = bottom
    size = 10   # block size
    auto_find_food=2  # in godmode: go to food randomly every nth time, smaller values = more often. 0 to disable

    while(1):
        mode = "normal"
        extra_food = False
        errors = 0        
        direction = "r"        
        speed = 0.1        
        food = [rnd(1, sw//size-1)*size, rnd(1, sh//size-1)*size]
        
        snake = SNAKE(sw//2, sh//2, size=size)
             
        while(1):
            LCD.fill_rect(food[0],food[1],size,size,LCD.red)            
            direction = get_direction(direction)            
            gameover = snake.move(direction)
            if gameover:
                if mode == "godmode":
                    direction, errors = snake.automove(errors)            
                else:
                    LCD.fill(0x0000)
                    LCD.text("Game Over",10,10,LCD.red)
                    print("gameover")
                    break
            
            if mode == 'godmode' and auto_find_food:
                # randomly go to food
                if snake.head_x == food[0] and rnd(1,auto_find_food) == 1:
                    # snake position x as food --> move direction up/down towards food 
                    direction = 'u' if snake.head_y > food[1] else 'd' 
                if snake.head_y == food[1] and rnd(1,auto_find_food) == 1:
                    # snake position y as food --> move direction right/left towards food 
                    direction = 'l' if snake.head_x > food[0] else 'r' 
            
            if snake.collision():
                errors += 1
                if mode == "normal":
                    LCD.fill(0x0000)
                    LCD.text("Game Over",10,10,LCD.red)
                    break
            
            if [snake.head_x, snake.head_y] == food:
                snake.add_food()
                #LCD.fill_rect(food[0],food[1],10,10,LCD.white)
                food = [rnd(1, sw//size-1)*size, rnd(1, sh//size-1)*size]
                LCD.fill_rect(food[0],food[1],size,size,LCD.red)
                print(len(snake.snake), errors)                
            elif extra_food:
                snake.add_food()
                extra_food = False
            else:
                pass

            snake.draw()            
            time.sleep(speed)
            
            if keyB.value() == 0:
                speed = speed * 0.8
            
            if keyX.value() == 0:
                speed = speed / 0.8
                
            if ctrl.value() == 0:
                if mode == "normal":
                    mode = "godmode"
                    LCD.fill(0x0000)
                    LCD.text("God Mode",10,10,LCD.red)
                    print("godmode")
                else:
                    mode = "normal"
                    LCD.fill(0x0000)
                    print("normal")
                
            if keyY.value() == 0:
                extra_food = True
                print("+1")
            
            LCD.show()
        
        LCD.show()
        
        # wait for keyA to restart game
        while(1):
            if keyA.value() == 0:
                LCD.fill(0x0000)
                break
                
    LCD.show()
    time.sleep(1)
    LCD.fill(0xFFFF)
    