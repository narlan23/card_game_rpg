import pygame
import sys
from states.base_state import BaseState

class Caracteristicas(BaseState):
    """
    Mostra os status e atributos detalhados do jogador.
    As informações são carregadas dinamicamente do objeto Player.
    """
    def __init__(self, game):
        super().__init__(game)
        
        # Carrega as fontes do gerenciador de assets
        self.font_title = self.game.assets.get_font("large")
        self.font_stats = self.game.assets.get_font("default")
        self.font_status = self.game.assets.get_font("small")
        
        # Cores para a interface
        self.color_title = (255, 215, 0)  # Dourado
        self.color_text = (255, 255, 255) # Branco
        self.color_status = (173, 216, 230) # Azul Claro
        self.background_color = (40, 40, 80) # Azul mais escuro

    def handle_events(self, events):
        """Gerencia os controles da tela de características."""
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            
            elif event.type == pygame.KEYDOWN:
                # Se 'ESC' for pressionado, fecha esta tela e volta para a anterior
                if event.key == pygame.K_ESCAPE:
                    self.game.pop_state()

    def draw(self, surface):
        """Desenha a tela de status do jogador com dados em tempo real."""
        surface.fill(self.background_color)
        player = self.game.player

        # --- Título ---
        title_text = self.font_title.render(f"Atributos de {player.name}", True, self.color_title)
        title_rect = title_text.get_rect(
            center=(self.game.screen_width / 2, 80)
        )
        surface.blit(title_text, title_rect)
        
        # --- Stats Básicos ---
        y_pos = 160
        stats_basicos = [
            f"Vida: {player.health} / {player.max_health}",
            f"Energia: {player.energy} / {player.max_energy}",
            f"Escudo: {player.shield}"
        ]

        for i, stat in enumerate(stats_basicos):
            stat_surface = self.font_stats.render(stat, True, self.color_text)
            stat_rect = stat_surface.get_rect(
                center=(self.game.screen_width / 2, y_pos + i * 45)
            )
            surface.blit(stat_surface, stat_rect)
        
        # --- Efeitos de Status Ativos ---
        y_pos += len(stats_basicos) * 45 + 10
        
        status_title = self.font_stats.render("Efeitos Ativos:", True, self.color_title)
        status_title_rect = status_title.get_rect(
            center=(self.game.screen_width / 2, y_pos)
        )
        surface.blit(status_title, status_title_rect)
        
        y_pos += 40

        # Verifica se o dicionário de status não está vazio
        if player.status_effects:
            for i, (status, data) in enumerate(player.status_effects.items()):
                duration = data.get('duration', '∞')
                status_str = f"- {status.capitalize()}: Duração {duration}"
                
                status_surface = self.font_status.render(status_str, True, self.color_status)
                status_rect = status_surface.get_rect(
                    center=(self.game.screen_width / 2, y_pos + i * 30)
                )
                surface.blit(status_surface, status_rect)
        else:
            none_text = self.font_status.render("- Nenhum", True, self.color_text)
            none_rect = none_text.get_rect(
                center=(self.game.screen_width / 2, y_pos)
            )
            surface.blit(none_text, none_rect)

        # --- Instrução para Voltar ---
        instrucao_text = self.font_stats.render("Pressione ESC para voltar", True, self.color_text)
        instrucao_rect = instrucao_text.get_rect(
            center=(self.game.screen_width / 2, self.game.screen_height - 50)
        )
        surface.blit(instrucao_text, instrucao_rect)