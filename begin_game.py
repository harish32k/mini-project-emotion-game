import pygame
import time
import random
import os
import sqlite3
from sqlite3 import Error

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


database = 'gamedb.db'

try:
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    query = ''' CREATE TABLE IF NOT EXISTS emotions (
                                        id integer,
                                        count integer
                                    ); '''

    cursor.execute(query)
    connection.commit()
    connection.close()
except Error as e:
    print(e)

pygame.font.init()

#store colors in tuples
BLACK = (0,0,0); WHITE = (255,255,255); RED = (255,0,0); GREEN = (0,255,0);  BLUE = (0,0,255)

BSHIP = pygame.image.load(os.path.join('assets', 'blue_ship.png'))
GSHIP = pygame.image.load(os.path.join('assets', 'green_ship.png'))
YSHIP = pygame.image.load(os.path.join('assets', 'yellow_ship.png'))
RSHIP = pygame.image.load(os.path.join('assets', 'red_ship.png'))
BOSS = pygame.image.load(os.path.join('assets', 'boss.png'))


BBULLET = pygame.image.load(os.path.join('assets', 'bbullet.png'))
GBULLET = pygame.image.load(os.path.join('assets', 'gbullet.png'))
YBULLET = pygame.image.load(os.path.join('assets', 'ybullet.png'))
RBULLET = pygame.image.load(os.path.join('assets', 'rbullet.png'))

BASTEROID = pygame.image.load(os.path.join('assets', 'big_asteroid.png'))
SASTEROID = pygame.image.load(os.path.join('assets', 'small_asteroid.png'))

SPACEBG = pygame.image.load(os.path.join('assets','space_bg.png'))
INTROBG = pygame.image.load(os.path.join('assets','intro.png'))
ARCADE_FONT = os.path.join('assets', 'ARCADECLASSIC.TTF')
PIXEL_FONT = os.path.join('assets', 'Pixeboy-z8XGD.ttf')

EXP0 = pygame.image.load(os.path.join('assets', 'regularExplosion00.png'))
EXP1 = pygame.image.load(os.path.join('assets', 'regularExplosion01.png'))
EXP2 = pygame.image.load(os.path.join('assets', 'regularExplosion02.png'))
EXP3 = pygame.image.load(os.path.join('assets', 'regularExplosion03.png'))
EXP4 = pygame.image.load(os.path.join('assets', 'regularExplosion04.png'))
EXP5 = pygame.image.load(os.path.join('assets', 'regularExplosion05.png'))
EXP6 = pygame.image.load(os.path.join('assets', 'regularExplosion06.png'))
EXP7 = pygame.image.load(os.path.join('assets', 'regularExplosion07.png'))
EXP8 = pygame.image.load(os.path.join('assets', 'regularExplosion07.png'))

EXPLOSION_IMG = [EXP0, EXP1, EXP2, EXP3, EXP4, EXP5, EXP6, EXP7, EXP8]

for img_pos in range(len(EXPLOSION_IMG)):
    imwidth = EXPLOSION_IMG[img_pos].get_width()
    imheight = EXPLOSION_IMG[img_pos].get_height()
    EXPLOSION_IMG[img_pos] = pygame.transform.scale(EXPLOSION_IMG[img_pos], (round(imwidth//2), round(imheight//2)))


#spaceship width
(ship_width,ship_height) = BSHIP.get_rect().size
(enem_width,enem_height) = RSHIP.get_rect().size

# set display width and height
dwidth = 900; dheight = 650
SPACEBG = pygame.transform.scale(SPACEBG, (dwidth, dheight))
INTROBG = pygame.transform.scale(INTROBG, (dwidth, dheight))
pygame.init()
WIN = pygame.display.set_mode((dwidth,dheight))
pygame.display.set_caption('Shooting')
clock = pygame.time.Clock()

BULLET_SOUND = pygame.mixer.Sound(os.path.join('assets', 'bullet.wav'))
HIT_SOUND = pygame.mixer.Sound(os.path.join('assets', 'hit.wav'))
BOOM_SOUND = pygame.mixer.Sound(os.path.join('assets', 'boom.wav'))
FLY_SOUND = pygame.mixer.Sound(os.path.join('assets', 'fly_in_short.wav'))
ROAR_SOUND = pygame.mixer.Sound(os.path.join('assets', 'roar.wav'))


def text_objects(text, font):
    textSurface = font.render(text, True, WHITE)
    return textSurface, textSurface.get_rect()

def message_display(timePlayed):
    
    largeText = pygame.font.Font(ARCADE_FONT,115)
    TextSurf1, TextRect1 = text_objects("GAME OVER !", largeText)
    TextRect1.center = ((dwidth/2),(dheight/4))
    
    smallText = pygame.font.Font(PIXEL_FONT, 50)
    TextSurf2, TextRect2 = text_objects("PLAYED  FOR  "+str(round(timePlayed/60, 2))+" mins.", smallText)
    TextRect2.center = ((dwidth/2),(dheight/2))

    TextSurf3, TextRect3 = text_objects("SCORE  "+str(round(timePlayed, 0))+".", smallText)
    TextRect3.center = ((dwidth/2),(3*dheight/4))

    WIN.blit(TextSurf1, TextRect1)
    WIN.blit(TextSurf2, TextRect2)
    WIN.blit(TextSurf3, TextRect3)
    pygame.display.update()
    time.sleep(5)

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (round(offset_x), round(offset_y))) != None

def move_enemy_bullets(bullets, player):
    for bullet in bullets:
        if bullet.y < -40:
            if bullet in bullets:
                bullets.remove(bullet)
        else:
            if bullet.collision(player):
                #enemies.remove(enemy)
                HIT_SOUND.play()
                player.health -= bullet.power
                #print(player.health)
                if bullet in bullets:
                    bullets.remove(bullet)
        bullet.y += bullet.vel

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
    
    def draw(self):
        index = int(self.frame)
        WIN.blit(EXPLOSION_IMG[index], (self.x, self.y))
        self.frame += 0.25

class Bullet:
    def __init__(self, x, y, image, vel=15, power=20):
        self.x = x
        self.y = y
        self.image = image
        self.vel = vel
        self.power = power
        self.mask = pygame.mask.from_surface(self.image)
    
    def draw(self, window):
        window.blit(self.image, (self.x, self.y))

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.bullet_img = None
        self.bullets = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))

    def collision(self, obj):
        return collide(self, obj)

class Player(Ship):
    def __init__(self, x = (dwidth * 0.45), y = (dheight * 0.87), health=100):
        super().__init__(x, y, health)
        self.ship_img = BSHIP
        self.bullet_img = BBULLET
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.vel = 15
        self.mask = pygame.mask.from_surface(self.ship_img)

    def get_width(self):
        return self.ship_img.get_width()
        
    def get_height(self):
        return self.ship_img.get_height()

    def draw(self, window):
        window.blit(BSHIP, (self.x, self.y))

    def fire(self):
        self.bullets.append(Bullet(self.x, self.y-self.get_height(), BBULLET, vel=-15))
    
    def move_bullets(self, enemies):
        for bullet in self.bullets:
            bullet.y += bullet.vel
            if bullet.y < -40:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
            else:
                for enemy in enemies:
                    if bullet.collision(enemy) and enemy.alive:
                        #enemies.remove(enemy)
                        enemy.health -= 20
                        #print(enemy.health)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)

class Enemy(Ship):
    img_ship = {
        "red" : RSHIP, "green" : GSHIP, "yellow" : YSHIP, "boss" : BOSS
    }
    img_bullet = {
        "red" : RBULLET, "green" : GBULLET, "yellow" : YBULLET, 
        "boss" : RBULLET
    }
    healths = {
        "red" : 160, "green" : 120, "yellow" : 80, "boss" : 1200
    }

    def __init__(self, x, y, color, health=None):
        super().__init__(x, y, health)
        self.ship_img = Enemy.img_ship[color]
        self.bullet_img = Enemy.img_bullet[color]
        if not health:
            self.health = Enemy.healths[color]
        else:
            self.health = health
        self.vel = 1
        self.color = color
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.alive = True
        self.damage = 40

    def get_width(self):
        return self.ship_img.get_width()
        
    def get_height(self):
        return self.ship_img.get_height()

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))

    def fire(self):
        
        if self.color == "green":
            power = 30
        else:
            power = 20
        
        self.bullets.append(Bullet(self.x, self.y+self.get_height(), self.bullet_img, vel=3, power=power))

    def move(self):
        self.y += self.vel

class FastEnemy(Enemy):
    # note to self. reduce health of fast enemy
    def __init__(self, x, y):
        super().__init__(x, y, color='red', health=60)
        self.vel = 5
        self.sounded = False

    def move(self):
        self.y += self.vel
        
        if self.sounded == False:
            if (self.x >= self.vel) and (self.x <= dwidth - self.get_width() - self.vel):
                if (self.y >= self.vel) and (self.y <= dheight):
                    FLY_SOUND.play()
                    self.sounded = True

    def fire(self):
        self.bullets.append(Bullet(self.x, self.y+self.get_height(), self.bullet_img, vel=5))

class QuakingEnemy(Enemy):
    # note to self. reduce health of fast enemy
    def __init__(self, x, y):
        super().__init__(x, y, color='yellow', health=120)
        

    def move(self):
        self.y += self.vel
        self.x += random.randrange(-10, 10)
        if self.x <= self.vel:
            self.x = self.vel
        elif self.x >= dwidth - self.get_width() - self.vel:
            self.x = dwidth - self.get_width() - self.vel

class BouncingEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, color='red', health=40)
        self.sign = 1

    def move(self):
        self.y += 1
        sign = self.sign
        shift =  random.randrange(0, 20)
        self.x += sign*shift
        
        if self.x <= self.vel:
            self.sign = 1
            self.x += sign*shift
            
        elif self.x >= dwidth - self.get_width() - self.vel:
            self.sign = -1
            self.x +=  sign*shift

class BigAsteroid(Enemy):
    # note to self. reduce health of fast enemy
    def __init__(self, x, y):
        super().__init__(x, y, color='baster', health=60)
        self.ship_img = BASTEROID
        self.bullet_img = None
        self.vel = 7

    def move(self):
        self.y += self.vel

    def fire(self):
        pass

class SmallAsteroid(Enemy):
    # note to self. reduce health of fast enemy
    def __init__(self, x, y):
        super().__init__(x, y, color='saster')
        self.ship_img = SASTEROID
        self.bullet_img = None
        self.vel = 8

    def move(self):
        self.y += self.vel

    def fire(self):
        pass

class PointingEnemy(Enemy):
    # note to self. reduce health of fast enemy
    def __init__(self, destx):
        self.ship_img = PointingEnemy.img_ship['green']
        y = 0.1*dheight
        x = random.choice([dwidth, -self.get_width()])
        super().__init__(x, y, color='green', health=60)
        self.destx = destx
        if destx > x:
            sign = 1
        elif destx < x:
            sign = -1
        else:
            sign = 0
        self.sign = sign
        self.entered = False
        self.sounded = False

    def move(self):
        self.y += self.vel
        self.x += self.sign*10
        if abs(self.x - self.destx) <= 10:
            self.sign = 0
            self.vel = 2
        
        if self.sounded == False:
            if (self.x >= self.vel) and (self.x <= dwidth - self.get_width() - self.vel):
                if (self.y >= self.vel) and (self.y <= dheight):
                    FLY_SOUND.play()
                    self.sounded = True

        """if abs(self.x - self.destx) < 10 and self.entered:
            self.sign = 0
        elif self.x <= self.vel and self.entered:
            self.x = self.vel
            self.sign = 0
        elif (self.x >= dwidth - self.get_width() - self.vel) and self.entered:
            self.x = dwidth - self.get_width() - self.vel
            self.sign = 0
        else:
            self.entered = True"""

    def fire(self):
        self.bullets.append(Bullet(self.x, self.y+self.get_height(), self.bullet_img, vel=7))

class BossEnemy(Enemy):
    # note to self. reduce health of fast enemy
    def __init__(self, player):
        y = 0.1*dheight
        x = dwidth/2 - (BOSS.get_width()/2)
        super().__init__(x, y, color='boss', health=700)
        
        self.ship_img = BOSS
        self.vel = 10
        self.entered = False
        self.move_cdc = 1
        self.player = player
        self.limiter = 200
        self.sounded = False

    def move(self):
        if self.move_cdc == 0:
            self.y += self.vel
        xpos = self.x + self.get_width()//3
        if xpos > self.player.x and self.x > 5 :
            self.x -= 2
        elif xpos < self.player.x and self.x < dwidth - self.get_width() - 5:
            self.x += 2
        else:
            self.x += 0
        
        self.move_cdc += 1
        self.move_cdc %= self.limiter

        
        if self.sounded == False:
            if (self.x >= self.vel) and (self.x <= dwidth - self.get_width() - self.vel):
                if (self.y >= self.vel) and (self.y <= dheight):
                    ROAR_SOUND.play()
                    self.sounded = True

    def fire(self):
        power = 20
        bulletx = random.randrange(self.x, self.x+self.ship_img.get_width())
        bullet = Bullet(bulletx, self.y+self.get_height(), self.bullet_img, vel=3, power=power)
        
        self.bullets.append(bullet)

class Mode:
    def __init__(self, mode='A', cooldown = 150):
        self.mode = mode
        self.cdc = cooldown
        self.wave = 0
        self.started = False
        self.ended = False


########################################################################################


def game_loop():
    player = Player()
    run = True
    level = 1
    lives = 5
    main_font = pygame.font.Font(PIXEL_FONT,25) #pygame.font.SysFont("comicsans", 30)
    enemies = []
    explosions = []

    mode = Mode('A')
    mode.wave = 10

    def show_explosion():
        for explosion in explosions:
            if explosion.frame == 9:
                if explosion in explosions:
                    explosions.remove(explosion)
            else:
                explosion.draw()

    def show_msg():
        timePlayed = 0
        largeText = pygame.font.Font(ARCADE_FONT,100)
        smallText = pygame.font.Font(ARCADE_FONT, 50)
        stop_dur = 3
        disp_line = "CONTINUING IN "
        text_shown = False

        for sec in range(stop_dur, 0, -1):
            TextSurf1, TextRect1 = text_objects("YOU DIED !", largeText)
            TextRect1.center = ((dwidth/2),(dheight/4))
            TextSurf2, TextRect2 = text_objects(disp_line+"  "+str(sec), smallText)
            TextRect2.topleft = ((dwidth/2)-220,(dheight/2))
            

            WIN.blit(TextSurf1, TextRect1)
            WIN.blit(TextSurf2, TextRect2)


            pygame.display.update()
            time.sleep(1)
            disp_line += "  " + str(sec)

    def redraw_window():
        #WIN.fill(WHITE)
        WIN.blit(SPACEBG, (0,0))
        # draw text
        for enemy in enemies:
            if enemy.alive:
                enemy.draw(WIN)
            for bullet in enemy.bullets:
                bullet.draw(WIN)
                
        player.draw(WIN)
        for bullet in player.bullets:
            bullet.draw(WIN)
        
        show_explosion()

        

        lives_label = main_font.render(f"Lives: {lives}", 1, WHITE)
        level_label = main_font.render(f"Mode: {mode.mode}", 1, WHITE)
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (dwidth - level_label.get_width() - 10, 10))
        pygame.draw.rect(WIN, (125, 125, 125), (10, 40, 100, 5))
        pygame.draw.rect(WIN, (0, 200, 0), (10, 40, player.health, 5))
        
        pygame.display.update()

    def top_emotion(record):
        #angry=0, fear=0, happy=0, sad=0, surprise=0, neutral=0
        modes = ['A', 'B', 'C']
        scores = [0, 0, 0]
        scores[0] = record[2] + record[5]
        scores[1] = 10*(record[0] + record[3])
        scores[2] = 30*(record[1] + record[4])
        return modes[scores.index(max(scores))]

    def set_emotions_zero():
        try:
            database = 'gamedb.db'
            connection = sqlite3.connect(database)
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM emotions;")
            record = cursor.fetchone()
            cursor.execute(f'''UPDATE emotions 
                set angry=0, fear=0, happy=0, sad=0, surprise=0, neutral=0;''')
            print("in game: " + str(record))
            connection.commit()
            connection.close()
            return record
        except Error as e:
            print(e)

    def get_mode():
        
        record = set_emotions_zero()
        return Mode(top_emotion(record))
        

        #random.choice['A', 'B', 'C']
        #return Mode(random.choice(['C']))

    def generate_enemies(mode):
        if len(enemies) == 0 and mode.wave == 0:
            mode = get_mode()
            #print("got mode:" +mode.mode)

        if mode.mode == 'A':
            if mode.started == False:
                #len(enemies) == 0 and mode.wave == 0 and 
                mode.cdc = 0 ; mode.wave = 10 #30
                mode.started = True

            if(mode.cdc == 0 and mode.wave != 0):
                ey = random.randrange(-200, -100)
                ex = random.randrange(100, dwidth - 100)
                ecolor = random.choice(["red", "yellow", "green"])
                enemy = random.choice([Enemy(ex, ey, color=ecolor)])
                enemies.append(enemy)
                mode.wave -= 1
            mode.cdc += 1
            mode.cdc %= 144

            """mode.wave =  5
            for i in range(mode.wave):
                ex = random.randrange(100, dwidth - 100)
                ey = random.randrange(-200, -100)
                ecolor = random.choice(["red", "yellow", "green"])
                enemy = random.choice([Enemy(ex, ey, color=ecolor)])
                enemies.append(enemy)
                mode.wave -= 1"""
            
        elif mode.mode == 'B':
            
            if mode.started == False:
                #len(enemies) == 0 and mode.wave == 0 and mode.started == False
                mode.cdc = 0 ; mode.wave = 15 ; mode.started = True

            if(mode.cdc == 0 and mode.wave != 0):
                if random.randrange(0, 3) == 1:
                    ey = random.randrange(-1000, -100)
                    ex = random.randrange(100, dwidth - 100)
                    enemy = FastEnemy(ex, ey)
                    mode.wave -= 1
                    enemies.append(enemy)
                else:
                    ey = random.randrange(-200, -100)
                    ex = random.randrange(100, dwidth - 100)
                    ecolor = random.choice(["red", "yellow", "green"])
                    enemy = random.choice([QuakingEnemy(ex, ey), QuakingEnemy(ex, ey), Enemy(ex, ey, color=ecolor)]) #Enemy(ex, ey, color=ecolor), 
                    mode.wave -= 1
                    enemies.append(enemy)
                
            mode.cdc += 1
            mode.cdc %= 150

        elif mode.mode == 'C':
            #print(mode.wave, len(enemies))
            if mode.started == False: #len(enemies) == 0 and mode.wave == 0:
                mode.started = True; mode.cdc = 0 ; mode.wave = 10
                #mode.ended = False
            
            # if mode.ended == True:
            #     mode.wave = 0
            if mode.cdc == 0 and mode.wave != 0:
                if mode.wave <= 3:
                    if random.randrange(1,10) == 1 or mode.wave == 1:
                        mode.wave = 0
                        enemy = random.choice([BossEnemy(player)])
                        enemies.append(enemy)
                    else:
                        ex = random.randrange(100, dwidth - 100)
                        ey = random.randrange(-200, -100)
                        enemy = random.choice([BouncingEnemy(ex, ey), PointingEnemy(destx = player.x)])
                        enemies.append(enemy)
                        mode.wave -= 1
                
                else:
                    ex = random.randrange(100, dwidth - 100)
                    ey = random.randrange(-200, -100)
                    
                    enemy = random.choice([PointingEnemy(destx = player.x),
                    BouncingEnemy(ex, ey), FastEnemy(ex, ey),  
                    PointingEnemy(destx = player.x),
                    Enemy(ex, ey, 'green'), FastEnemy(ex, ey)])
                    enemies.append(enemy)
                    mode.wave -= 1
                

                
            mode.cdc += 1
            mode.cdc %= 240
            
            """for i in range(mode.wave):
                ex = random.randrange(100, dwidth - 100)
                ey = random.randrange(-200, -100)
                ecolor = random.choice(["red", "yellow", "green"])
                enemy = random.choice([PointingEnemy(dwidth, ey, destx = player.x, color=ecolor)])
                enemies.append(enemy)
                mode.wave -= 1"""

        return mode

    def enemy_action():

        for enemy in enemies[:]:
            enemy.move()
            if enemy.color == "boss" and enemy.y > 0 and enemy.alive: 
                if random.randrange(0, 2*50) == 1:
                    enemy.fire()
            elif random.randrange(0, 3*60) == 1 and enemy.y > 0 and enemy.alive:
                enemy.fire()
            
            
            if player.collision(enemy) and enemy.alive:
                enemy.health = 0
                player.health = 0

            move_enemy_bullets(enemy.bullets, player)

            if enemy.y > dheight:
                if enemy.alive:
                    player.health -= enemy.damage
                if enemy in enemies:
                    enemies.remove(enemy)

            if enemy.health <= 0:
                if enemy in enemies and enemy.alive == True:
                    BOOM_SOUND.play()
                    if enemy.color != "boss" and player.health > 0:
                        explosions.append(Explosion(enemy.x, enemy.y))
                        print(explosions)
                    enemy.alive = False
                    if enemy.color == 'boss':
                        enemy.vel = 3
                        enemy.limiter = 1



    set_emotions_zero() #before start of game
    while run:
        clock.tick(60)

        # enemy generation
        mode = generate_enemies(mode)
        #enemy generation ends
        
        # obtain events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();run = False

        # get key inputs and assign an action
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and player.x > player.vel:
            player.x -= player.vel
        elif keys[pygame.K_RIGHT] and player.x < dwidth - player.get_width() - player.vel:
            player.x += player.vel

        # player fire button and cool down
        if keys[pygame.K_SPACE] and player.cool_down_counter == 0:
            BULLET_SOUND.play()
            player.fire()
            player.cool_down_counter += 1
        if player.cool_down_counter != 0:
            player.cool_down_counter += 1
            player.cool_down_counter %= 15
        # player firing and cool down end

        # move player bullets
        player.move_bullets(enemies)
        # player bullet move ends
        
        ### enemy move begins
        enemy_action()
        ### enemy move end

        if player.health <= 0:
            lives -= 1
            if lives > 0:
                show_msg()
            player.health = 100
            if lives == 0:
                return time.time()

        show_explosion()

        redraw_window()


def show_intro():
    play = False
    WIN.blit(INTROBG, (0,0))
    pygame.display.update()
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();run = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_RETURN]:
            play = True
            break
        elif keys[pygame.K_ESCAPE]:
            break
        
    return play

import time

while True:
    play = show_intro()
    if not play:
        break
    startTime = time.time()
    endTime = game_loop()

    message_display(endTime-startTime)



connection.close()
pygame.quit()