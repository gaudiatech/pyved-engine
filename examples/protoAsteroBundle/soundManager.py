
from . import vars

katasdk = vars.katasdk
pygame = katasdk.kengi.pygame


# from pygame.locals import *  

sounds = {}

PREF = 'user_assets/astero-'


def init_sound_manager():
    pygame.mixer.init()
    sounds["fire"] = pygame.mixer.Sound(PREF+"FIRE.WAV")
    sounds["explode1"] = pygame.mixer.Sound(PREF+"EXPLODE1.WAV")
    sounds["explode2"] = pygame.mixer.Sound(PREF+"EXPLODE2.WAV")
    sounds["explode3"] = pygame.mixer.Sound(PREF+"EXPLODE3.WAV")
    sounds["lsaucer"] = pygame.mixer.Sound(PREF+"LSAUCER.WAV")
    sounds["ssaucer"] = pygame.mixer.Sound(PREF+"SSAUCER.WAV")
    sounds["thrust"] = pygame.mixer.Sound(PREF+"THRUST.WAV")
    sounds["sfire"] = pygame.mixer.Sound(PREF+"SFIRE.WAV")
    sounds["extralife"] = pygame.mixer.Sound(PREF+"LIFE.WAV")

def play_sound(soundName):
    channel = sounds[soundName].play()

def play_sound_continuous(soundName):
    channel = sounds[soundName].play(-1)

def stop_sound(soundName):
    channel = sounds[soundName].stop()
