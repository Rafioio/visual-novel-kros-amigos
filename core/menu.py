import pygame

class MainMenu:

    def __init__(self, largura, altura):

        self.largura = largura
        self.altura = altura

        self.opcoes = [
            "Iniciar",
            "Créditos",
            "Sair"
        ]

        self.fonte_titulo = pygame.font.SysFont(None, 72)
        self.fonte_opcoes = pygame.font.SysFont(None, 40)

        self.background = pygame.image.load("assets/menu/menu.png")

        self.background = pygame.transform.scale(
            self.background,
            (largura, altura)
        )

    def update(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_1:
                self.opcao_selecionada = 0
                return "Iniciar"

            elif evento.key == pygame.K_2:
                self.opcao_selecionada = 1
                return "Créditos"

            elif evento.key == pygame.K_3:
                self.opcao_selecionada = 2
                return "Sair"

        return None


    def draw(self, tela):

        tela.blit(self.background, (0, 0))

        titulo = self.fonte_titulo.render(
            "Kros & Amigos",
            True,
            (255, 255, 255)
        )

        tela.blit(titulo, (180, 120))

        y = 300

        for i, opcao in enumerate(self.opcoes):

            texto = self.fonte_opcoes.render(
                f"[{i+1}] {opcao}",
                True,
                (255, 255, 255)
            )

            tela.blit(texto, (320, y))

            y += 60