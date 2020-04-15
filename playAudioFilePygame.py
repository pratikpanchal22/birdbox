import os
import pygame, time

pygame.mixer.init()
pygame.mixer.music.load("mp3s/frogs.mp3")

pygame.mixer.music.play()
#time.sleep(3)
pygame.mixer.music.fadeout(5000)

while pygame.mixer.music.get_busy() == True:
   continue
