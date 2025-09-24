import pygame

class Dialogo:
    def __init__(self, font, callback_confirm=None, callback_cancel=None):
        self.font = font
        self.callback_confirm = callback_confirm
        self.callback_cancel = callback_cancel
        self.ativo = False
        self.texto = ""
        self.opcoes = []
        self.opcao_selecionada = 0
        self.callbacks = []
        self.layout = "horizontal"  # "horizontal", "vertical", "info"

    def abrir(self, texto, opcoes=None, callbacks=None, layout="horizontal"):
        """
        Abre um diálogo.
        - texto: string da pergunta/mensagem
        - opcoes: lista de strings (ex: ["Sim", "Não"]) ou None no modo "info"
        - callbacks: lista de funções (mesma ordem das opções)
        - layout: "horizontal", "vertical" ou "info"
        """
        self.texto = texto
        self.opcoes = opcoes if opcoes else []
        self.callbacks = callbacks if callbacks else []
        self.layout = layout
        self.opcao_selecionada = 0
        self.ativo = True

    def fechar(self):
        self.ativo = False

    def handle_event(self, event):
        if not self.ativo:
            return

        if event.type == pygame.KEYDOWN:
            if self.layout in ("horizontal", "vertical") and self.opcoes:
                if self.layout == "horizontal":
                    if event.key == pygame.K_LEFT:
                        self.opcao_selecionada = (self.opcao_selecionada - 1) % len(self.opcoes)
                    elif event.key == pygame.K_RIGHT:
                        self.opcao_selecionada = (self.opcao_selecionada + 1) % len(self.opcoes)
                elif self.layout == "vertical":
                    if event.key == pygame.K_UP:
                        self.opcao_selecionada = (self.opcao_selecionada - 1) % len(self.opcoes)
                    elif event.key == pygame.K_DOWN:
                        self.opcao_selecionada = (self.opcao_selecionada + 1) % len(self.opcoes)

                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.processar_escolha()
            else:
                # Modo informativo -> qualquer ENTER/ESC fecha
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    self.fechar()

            if event.key == pygame.K_ESCAPE:
                self.fechar()

    def processar_escolha(self):
        if self.callbacks and 0 <= self.opcao_selecionada < len(self.callbacks):
            self.callbacks[self.opcao_selecionada]()
        self.fechar()

    def draw(self, surface):
        if not self.ativo:
            return

        largura, altura = surface.get_size()
        dialog_rect = pygame.Rect(largura//2 - 300, altura - 220, 600, 200)
        pygame.draw.rect(surface, (30, 30, 40), dialog_rect, border_radius=10)
        pygame.draw.rect(surface, (100, 100, 140), dialog_rect, 3, border_radius=10)

        # Texto principal
        pergunta_text = self.font.render(self.texto, True, (255, 255, 255))
        surface.blit(pergunta_text, (dialog_rect.x + 20, dialog_rect.y + 20))

        if self.layout == "horizontal" and self.opcoes:
            self._draw_horizontal(surface, dialog_rect)
        elif self.layout == "vertical" and self.opcoes:
            self._draw_vertical(surface, dialog_rect)
        elif self.layout == "info":
            self._draw_info(surface, dialog_rect)

    def _draw_horizontal(self, surface, dialog_rect):
        num_opcoes = len(self.opcoes)
        espacamento = dialog_rect.width // (num_opcoes + 1)

        for i, opcao in enumerate(self.opcoes):
            x = dialog_rect.x + espacamento * (i + 1)
            y = dialog_rect.y + 90
            opcao_rect = pygame.Rect(x - 60, y, 120, 40)

            cor = (100, 200, 100) if i == self.opcao_selecionada else (70, 70, 90)
            cor_borda = (150, 255, 150) if i == self.opcao_selecionada else (100, 100, 140)

            pygame.draw.rect(surface, cor, opcao_rect, border_radius=6)
            pygame.draw.rect(surface, cor_borda, opcao_rect, 2, border_radius=6)

            opcao_text = self.font.render(opcao, True, (255, 255, 255))
            text_rect = opcao_text.get_rect(center=opcao_rect.center)
            surface.blit(opcao_text, text_rect)

    def _draw_vertical(self, surface, dialog_rect):
        num_opcoes = len(self.opcoes)
        altura_total = num_opcoes * 50
        inicio_y = dialog_rect.centery - altura_total // 2

        for i, opcao in enumerate(self.opcoes):
            x = dialog_rect.centerx
            y = inicio_y + i * 50
            opcao_rect = pygame.Rect(x - 100, y, 200, 40)

            cor = (100, 200, 100) if i == self.opcao_selecionada else (70, 70, 90)
            cor_borda = (150, 255, 150) if i == self.opcao_selecionada else (100, 100, 140)

            pygame.draw.rect(surface, cor, opcao_rect, border_radius=6)
            pygame.draw.rect(surface, cor_borda, opcao_rect, 2, border_radius=6)

            opcao_text = self.font.render(opcao, True, (255, 255, 255))
            text_rect = opcao_text.get_rect(center=opcao_rect.center)
            surface.blit(opcao_text, text_rect)

    def _draw_info(self, surface, dialog_rect):
        instrucoes_text = self.font.render(
            "Pressione ENTER ou ESC para continuar...",
            True, (200, 200, 200)
        )
        surface.blit(instrucoes_text, (dialog_rect.x + 20, dialog_rect.y + 130))
