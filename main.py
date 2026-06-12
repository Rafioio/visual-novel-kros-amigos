import pygame
import sys
from core.engine import GameEngine
from core.asset_manager import AssetManager

pygame.init()
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Visual Novel - Kros & Amigos")

fonte_principal = pygame.font.SysFont(None, 30)
fonte_escolhas = pygame.font.SysFont(None, 28)
fonte_status = pygame.font.SysFont(None, 24)
fonte_gigante = pygame.font.SysFont(None, 64)

engine = GameEngine()
engine.load_script_from_json("data/script.json")

assets = AssetManager()

bgs = [
    ("bg_rua", "street.png"), ("bg_corredor", "school_hallway.png"), ("bg_sala", "school_classroom.png"),
    ("bg_parque", "park.png"), ("bg_lanchonete", "diner.png"), ("bg_biblioteca", "library.png"),
    ("bg_academia", "gym.png"), ("bg_quarto", "kros_room.png"), ("bg_lab", "computer_lab.png"),
    ("bg_cinema", "cinema.png"), ("bg_clube", "literature_club.png"), ("bg_pizzaria", "pizzeria.png"),
    ("bg_jumpscare", "purple_jumpscare.png")
]

bgs.extend([
    ("bg_praia", "beach.png"), 
    ("bg_mar", "sea.png"), 
    ("bg_mar_monstro", "sea_monster.png"), 
    ("bg_isekai", "isekai_city.png")
])

for key, path in bgs:
    assets.load_bg(key, path)

fundo_preto = pygame.Surface((LARGURA, ALTURA))
fundo_preto.fill((0, 0, 0))
assets._images["bg_preto"] = fundo_preto

assets.load_2x2_spritesheet("kros", "kros.png")
assets.load_4x2_spritesheet("lola", "lola.png") 
assets.load_2x2_spritesheet("bibi", "bibi.png")
assets.load_2x2_spritesheet("lily", "lily.png")
assets.load_2x2_spritesheet("white", "mr_white.png")
assets.load_2x2_spritesheet("lily_yandere", "lily_yandere.png")
assets.load_2x2_spritesheet("emilia", "emilia.png")

engine.start("casa1")

esperando_timer = False
tempo_inicio_timer = 0
atraso_necessario = 0

rodando = True
while rodando:
    cena_atual = engine.current_scene

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN and not esperando_timer:
            if cena_atual and cena_atual.is_ending:
                if evento.key == pygame.K_r:
                    engine.reset("casa1") 
            elif cena_atual and not cena_atual.choices:
                if evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                    engine.advance_linear_scene()
            elif cena_atual and cena_atual.choices:
                if pygame.K_1 <= evento.key <= pygame.K_9:
                    engine.make_choice(evento.key - 49)

    if cena_atual and cena_atual.scene_id in ["f_white_corta", "fnaf_jumpscare", "isekai_atropelamento_impacto"] and not esperando_timer:
        esperando_timer = True
        tempo_inicio_timer = pygame.time.get_ticks()
        if cena_atual.scene_id == "f_white_corta": atraso_necessario = 1800
        elif cena_atual.scene_id == "fnaf_jumpscare": atraso_necessario = 2000
        else: atraso_necessario = 3000 

    if esperando_timer:
        if pygame.time.get_ticks() - tempo_inicio_timer >= atraso_necessario:
            esperando_timer = False
            engine.advance_linear_scene()

    tela.fill((0, 0, 0))

    if cena_atual:
        bg_img = assets.get_image(cena_atual.background_key)
        if bg_img:
            tela.blit(pygame.transform.scale(bg_img, (LARGURA, ALTURA)), (0, 0))

        if cena_atual.is_ending:
            texto_fim = fonte_gigante.render(cena_atual.text, True, (255, 255, 255))
            rect_texto = texto_fim.get_rect(center=(LARGURA // 2, ALTURA // 2 - 30))
            tela.blit(texto_fim, rect_texto)
            texto_replay = fonte_escolhas.render("[R] Pressione para Rejogar", True, (255, 255, 0))
            rect_replay = texto_replay.get_rect(center=(LARGURA // 2, ALTURA // 2 + 50))
            tela.blit(texto_replay, rect_replay)
        else:
            if cena_atual.character_sprite and cena_atual.background_key != "bg_jumpscare":
                sprite_img = assets.get_image(cena_atual.character_sprite)
                if sprite_img:
                    sprite_rect = sprite_img.get_rect()
                    sprite_rect.bottomright = (LARGURA - 100, ALTURA - 150)
                    tela.blit(sprite_img, sprite_rect)

            caixa_texto = pygame.Surface((LARGURA, 200), pygame.SRCALPHA)
            caixa_texto.fill((0, 0, 0, 220)) 
            tela.blit(caixa_texto, (0, 400))
            
            tela.blit(fonte_principal.render(cena_atual.text, True, (255, 255, 255)), (20, 420))
            
            if not cena_atual.choices and cena_atual.next_scene_id and not esperando_timer:
                tela.blit(fonte_escolhas.render("[ESPAÇO] para continuar...", True, (150, 150, 150)), (40, 470))
            elif cena_atual.choices and not esperando_timer:
                y_offset = 470
                for i, escolha in enumerate(cena_atual.choices):
                    tela.blit(fonte_escolhas.render(f"[{i+1}] {escolha.text}", True, (255, 255, 0)), (40, y_offset))
                    y_offset += 30

            y_status = 10
            for personagem, valor in engine.affinities.items():
                tela.blit(fonte_status.render(f"{personagem}: {valor}", True, (0, 255, 0)), (10, y_status))
                y_status += 25

    pygame.display.flip()

pygame.quit()
sys.exit()
