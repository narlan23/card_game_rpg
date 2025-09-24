import pygame
import sys
from states.base_state import BaseState # <-- 1. Importe a classe base

class MainMenu(BaseState):
    """
    Representa o estado do menu principal do jogo.
    O jogador pode iniciar um novo jogo, ver características ou sair.
    """
    def __init__(self, game):
        super().__init__(game)
        
        # Carrega as fontes do gerenciador de assets
        self.font_title = self.game.assets.get_font("large")
        self.font_options = self.game.assets.get_font("default")

        # Opções do menu
        self.options = ["Iniciar Jogo", "Características", "Sair"]
        self.selected_index = 0

        # Cores
        self.color_default = (200, 200, 200)
        self.color_selected = (255, 215, 0) # Dourado
        self.background_color = (30, 30, 40)

    def handle_events(self, events):
        """Gerencia os controles do menu."""
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    # Move a seleção para cima
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    # Move a seleção para baixo
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Executa a ação da opção selecionada
                    self.select_option()
        pass

    def select_option(self):
        """Executa a ação correspondente à opção de menu selecionada."""
        selected_option = self.options[self.selected_index]

        if selected_option == "Iniciar Jogo":
            # Empurra o estado de jogo principal para a pilha, iniciando o jogo
            self.game.push_state("JOGO_PRINCIPAL")
        
        elif selected_option == "Características":
            # Empurra o estado de características
            self.game.push_state("CARACTERISTICAS")
            
        elif selected_option == "Sair":
            # Para sair, basta remover o estado atual da pilha.
            # Como este é o primeiro estado, a pilha ficará vazia e o jogo terminará.
            self.game.pop_state()

    def draw(self, surface):
        """Desenha o menu principal na tela."""
        surface.fill(self.background_color)
        
        # --- Título ---
        title_text = self.font_title.render("Card Game RPG", True, self.color_selected)
        title_rect = title_text.get_rect(
            center=(self.game.screen_width / 2, self.game.screen_height / 4)
        )
        surface.blit(title_text, title_rect)

        # --- Opções do Menu ---
        for i, option_text in enumerate(self.options):
            # Define a cor com base na seleção
            color = self.color_selected if i == self.selected_index else self.color_default
            
            # Adiciona um indicador '>' na opção selecionada para maior clareza
            display_text = f"> {option_text}" if i == self.selected_index else option_text
            
            text_surface = self.font_options.render(display_text, True, color)
            
            # Calcula a posição para centralizar as opções
            text_rect = text_surface.get_rect(
                center=(self.game.screen_width / 2, self.game.screen_height / 2 + i * 50)
            )
            
            surface.blit(text_surface, text_rect)