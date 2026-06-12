import pygame

musica_atual = None

def tocar_musica(caminho, volume=0.2):

    global musica_atual

    if musica_atual != caminho:

        pygame.mixer.music.fadeout(500)

        pygame.mixer.music.load(caminho)

        pygame.mixer.music.set_volume(volume)

        pygame.mixer.music.play(-1, fade_ms=500)

        musica_atual = caminho