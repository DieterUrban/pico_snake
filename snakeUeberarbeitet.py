
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


if __name__=='__main__':    
    #width height
    sw = 240   # 0 = left, 240 = right
    sh = 240   # 0 = top, 240 = bottom 
    
    def move(direction):
        global cur_x, cur_y, sw, sh
        
        if direction == "r":
            cur_x += 10        
        elif direction == "l":
            cur_x -= 10
        elif direction == "u":
            cur_y -= 10
        elif direction == "d":
            cur_y += 10
            
        if cur_x > sw-10 or cur_y > sh-10 or cur_x < 0 or cur_y < 0:
            gameover = True
            print("gameover")
            return True        
            
        return False
    
    def draw(snake, tail_end):
        LCD.fill_rect(tail_end[0], tail_end[1], 10, 10, 0x0000)
        
        for position in snake[1:]:
            LCD.fill_rect(position[0],position[1],10,10,LCD.green)
        
        LCD.fill_rect(snake[0][0],snake[0][1],10,10,LCD.blue)

        LCD.show()

    def collision(snake):
        head = snake[0]
        
        for pos in snake[1:]:
            if pos == head:
                return True
            
        return False

    while(1):
        mode = "normal"
        errors = 0
        
        cur_x = sw//2
        cur_y = sh//2
        
        snake = [
                    [cur_x, cur_y],
                    [cur_x-10, cur_y],
                    [cur_x-20, cur_y]
            ]

        direction = "r"
        
        speed = 0.1
        
        food = [rnd(1, sw//10-1)*10, rnd(1, sh//10-1)*10]
        
        extra_food = False
     
        while(1):
            
            LCD.fill_rect(food[0],food[1],10,10,LCD.red)
            
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
            
            if move(direction):
                if mode == "godmode":
                    errors += 1
                    # print(cur_x, cur_y)
                    if cur_x > sw:
                        cur_x = sw-10
                        direction = "u"
                        cur_y -= 10
                    if cur_y > sh:
                        cur_y = sh-10
                        direction = "r"
                        cur_x += 10
                    if cur_x < 0:
                        cur_x = 0
                        direction = "d"
                        cur_y += 10
                    if cur_y < 0:
                        cur_y = 0
                        direction = "l"
                        cur_x -= 10
                    # print(direction)
                else:
                    LCD.fill(0x0000)
                    LCD.text("Game Over",10,10,LCD.red)
                    break
            
            if collision(snake):
                errors += 1
                if mode == "normal":
                    LCD.fill(0x0000)
                    LCD.text("Game Over",10,10,LCD.red)
                    break
            
            tail_end = snake[-1]
            
            snake.insert(0, [cur_x, cur_y])

            if [cur_x, cur_y] != food and not extra_food:
                snake.pop()  
            else:
                extra_food = False
                #LCD.fill_rect(food[0],food[1],10,10,LCD.white)
                food = [rnd(1, sw//10-1)*10, rnd(1, sh//10-1)*10]
                LCD.fill_rect(food[0],food[1],10,10,LCD.red)
                
                print(len(snake), errors)

            draw(snake, tail_end)
            
            time.sleep(speed)
            
            #LCD.fill_rect(100,100,10,10,LCD.red)
            
            if keyB.value() == 0:
                #LCD.fill_rect(208,15,30,30,LCD.blue)
                speed = speed * 0.8
            else :
                pass
                #LCD.fill_rect(208,15,30,30,LCD.white)
                #LCD.rect(208,15,30,30,LCD.red)
            
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
            
            #time.sleep(0.1)       
            LCD.show()
        
        LCD.show()
        
        while(1):
            if keyA.value() == 0:
                LCD.fill(0x0000)
                break
                
    LCD.show()
    time.sleep(1)
    LCD.fill(0xFFFF)
    