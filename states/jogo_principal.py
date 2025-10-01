import pygame
import sys

# Importações de componentes do jogo
from jogo_principal.camera import Camera
from jogo_principal.tileset import TiledMap
from jogo_principal.dialog import Dialogo
from characters.npc import NPC
from states.batalha import Batalha
from states.base_state import BaseState

# 1. Defina o caminho base (o atalho)
ENEMY_ASSET_PATH = "assets/enemy/"

# 1. Defina os dados dos inimigos para este encontro
dados_inimigos_da_torre = [
    {"name": "Goblin", 
     "health": 3, 
     "attack": 1, 
     "image": [
         #f"{ENEMY_ASSET_PATH}agua_frame_1.png",
         #f"{ENEMY_ASSET_PATH}agua_frame_2.png",
         #f"{ENEMY_ASSET_PATH}agua_frame_3.png",
         f"{ENEMY_ASSET_PATH}agua_frame_4.png",
         f"{ENEMY_ASSET_PATH}agua_frame_5.png",
         f"{ENEMY_ASSET_PATH}agua_frame_6.png",
         f"{ENEMY_ASSET_PATH}agua_frame_7.png",
         f"{ENEMY_ASSET_PATH}agua_frame_8.png",
     ],
     "x_tam": 75,
     "y_tam":150},
    {"name": "Orc",
      "health": 5, 
      "attack": 1, 
      "image": [
          f"{ENEMY_ASSET_PATH}agua2_frame_1.png",
          f"{ENEMY_ASSET_PATH}agua2_frame_2.png",
          f"{ENEMY_ASSET_PATH}agua2_frame_3.png",
          f"{ENEMY_ASSET_PATH}agua2_frame_4.png",
          f"{ENEMY_ASSET_PATH}agua2_frame_5.png",
          f"{ENEMY_ASSET_PATH}agua2_frame_6.png",
          f"{ENEMY_ASSET_PATH}agua2_frame_7.png",
      ],
      "x_tam": 100,
      "y_tam":150},
    #{"name": "Orc", "health": 5, "attack": 1, "image": "fire.png","x_tam": 75,"y_tam":120},
]

class JogoPrincipal(BaseState):
    """
    Estado principal do jogo, onde o jogador explora o mapa,
    interage com NPCs e entra em batalhas.
    """
    def __init__(self, game):
        super().__init__(game)
        
        # --- CONFIGURAÇÕES DO JOGADOR E DO MUNDO ---
        self.player = self.game.player
        self.player_pos = [400, 300] # Posição inicial no mundo
        self.TAMANHO_JOGADOR = 20
        self.VELOCIDADE_JOGADOR = 180 # Movimento baseado em pixels por segundo

        # --- FONTES E INTERFACE ---
        self.font_default = self.game.assets.get_font("default")
        self.font_hud = self.game.assets.get_font("small")
        self.dialogo = Dialogo(self.font_default)

        # --- MAPA E CÂMERA ---
        self.mapa = TiledMap("assets/mapa.tmj")
        map_width = self.mapa.width * self.mapa.tilewidth
        map_height = self.mapa.height * self.mapa.tileheight
        self.camera = Camera(self.game.screen_width // 2, self.game.screen_height // 2, map_width, map_height)

        # NOVO: Carregar retângulos de colisão da camada "collision" do mapa
        try:
            # Garanta que o nome da camada esteja correto (ex: "collision" ou "Colisao")
            self.colisoes_mapa = self.mapa.get_collision_rects("collision") 
            print(f"Colisões carregadas: {len(self.colisoes_mapa)} objetos.")
        except AttributeError:
            # Isso é crucial para que o jogo não quebre se TiledMap for incompleto
            print("ERRO: Sua classe TiledMap não possui o método get_collision_rects(layer_name). Colisões desativadas.")
            self.colisoes_mapa = []

        # --- NPCs ---
        self.npcs = self._create_npcs()
        self.npc_interacao = None # Armazena o NPC com o qual a interação é possível

        # --- CONTROLE DE TEMPO ---
        self.clock = pygame.time.Clock()
        self.delta_time = 0

        # --- ESTADO INTERNO ---
        self.is_paused = False

    def _create_npcs(self):
        """Cria e retorna uma lista com todas as instâncias de NPCs do jogo."""
        return [
            NPC(
                "Velho Sábio",
                pygame.Rect(672, 294, 50, 50),
                {
                    "texto": "Bem-vindo, aventureiro! Cuidado com os perigos da torre...",
                    "opcoes": ["Obrigado!", "Vou ter cuidado."],
                    "callbacks": [lambda: print("Disse 'Obrigado!'"), lambda: print("Prometeu ter cuidado.")],
                    "layout": "vertical"
                }
            ),
            NPC(
                "Torre",
                pygame.Rect(672, 500, 50, 50),
                {
                    "texto": "Deseja enfrentar os perigos da torre?",
                    "opcoes": ["Sim", "Não"],
                    "callbacks": [
                        lambda: self.game.push_state(Batalha(self.game, dados_inimigos_da_torre)),
                        lambda: print("O jogador recuou da torre.")
                    ],
                    "layout": "horizontal"
                }
            )
        ]

    # ========================
    # Loop Principal do Estado
    # ========================

    def handle_events(self, events):
        """Gerencia toda a entrada do usuário para este estado."""
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            
            # Se o diálogo estiver ativo, ele tem prioridade
            if self.dialogo.ativo:
                self.dialogo.handle_event(event)
            else:
                # Caso contrário, processa os eventos do jogo
                self._handle_player_input(event)

    def update(self):
        """Atualiza a lógica do jogo a cada frame."""
        # Calcula o delta_time para movimento consistente
        self.delta_time = self.clock.tick(60) / 1000.0

        if not self.dialogo.ativo:
            self._processar_movimento()
            self._verificar_interacao()
        
        self._update_camera()

    def draw(self, surface):
        """Renderiza todos os elementos do jogo na tela."""
        surface.fill((30, 30, 50)) # Cor de fundo

        # Desenha o mapa e os objetos do jogo
        self.mapa.draw(surface, self.camera)
        
        # Desenhar colisões para debug (opcional)
        # for rect in self.colisoes_mapa:
        #     screen_rect = self.camera.apply(rect)
        #     pygame.draw.rect(surface, (255, 0, 0, 100), screen_rect, 1) # Vermelho com linha 1

        self._draw_npcs(surface)
        self._draw_player(surface)
        
        # Desenha a interface por cima do jogo
        self._draw_hud(surface)
        
        # Se o diálogo estiver ativo, desenha-o por último
        if self.dialogo.ativo:
            self.dialogo.draw(surface)

    # ========================
    # Métodos Auxiliares
    # ========================

    def _handle_player_input(self, event):
        """Processa as teclas pressionadas pelo jogador."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Empilha um menu de pausa sobre o jogo
                self.game.push_state("MENU_PAUSA") # Você precisará criar este estado
            
            elif event.key == pygame.K_c:
                # Empilha a tela de características
                self.game.push_state("CARACTERISTICAS")
            
            elif event.key == pygame.K_e and self.npc_interacao:
                # Interage com o NPC próximo
                self.npc_interacao.interagir(self.dialogo)
    
    # NOVO: Método para obter o Rect do jogador
    def player_rect(self):
        """Retorna o pygame.Rect do jogador, centralizado em sua posição."""
        return pygame.Rect(
            self.player_pos[0] - self.TAMANHO_JOGADOR / 2,
            self.player_pos[1] - self.TAMANHO_JOGADOR / 2,
            self.TAMANHO_JOGADOR,
            self.TAMANHO_JOGADOR
        )

    # NOVO: Lógica de Colisão
    def _resolver_colisoes(self, player_rect, delta_x, delta_y):
        """
        Verifica colisão do player_rect com os objetos do mapa e resolve o problema,
        permitindo o deslizamento suave.
        """
        for rect_mapa in self.colisoes_mapa:
            if player_rect.colliderect(rect_mapa):
                # Colisão no eixo X
                if delta_x > 0: # Movendo para a direita
                    player_rect.right = rect_mapa.left
                elif delta_x < 0: # Movendo para a esquerda
                    player_rect.left = rect_mapa.right
                
                # Colisão no eixo Y
                if delta_y > 0: # Movendo para baixo
                    player_rect.bottom = rect_mapa.top
                elif delta_y < 0: # Movendo para cima
                    player_rect.top = rect_mapa.bottom

    # MODIFICADO: Agora trata movimento e colisão separadamente
    def _processar_movimento(self):
        """Calcula e aplica o movimento do jogador, resolvendo colisões com o mapa."""
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])

        # Normaliza o vetor de movimento para evitar velocidade extra na diagonal
        if dx != 0 and dy != 0:
            norm_factor = 0.7071 # Aprox. 1 / sqrt(2)
            dx *= norm_factor
            dy *= norm_factor

        # 1. Cria o retângulo do jogador na posição atual
        player_rect = self.player_rect()

        # 2. Tenta mover no eixo X e verifica colisão
        delta_x = dx * self.VELOCIDADE_JOGADOR * self.delta_time
        player_rect.x += delta_x
        if self.colisoes_mapa: # Só resolve se houver colisões carregadas
            self._resolver_colisoes(player_rect, delta_x, 0)

        # 3. Tenta mover no eixo Y e verifica colisão
        delta_y = dy * self.VELOCIDADE_JOGADOR * self.delta_time
        player_rect.y += delta_y
        if self.colisoes_mapa: # Só resolve se houver colisões carregadas
            self._resolver_colisoes(player_rect, 0, delta_y)

        # 4. Atualiza a posição central do jogador com a posição corrigida
        self.player_pos[0] = player_rect.centerx
        self.player_pos[1] = player_rect.centery
        
        # Garante que o jogador não saia dos limites do mapa (ainda é útil)
        self._limitar_movimento_mapa()

    # O método _limitar_movimento_mapa permanece o mesmo, mas atua na nova posição.
    def _limitar_movimento_mapa(self):
        """Impede que o jogador se mova para fora da área do mapa."""
        half_size = self.TAMANHO_JOGADOR / 2
        self.player_pos[0] = max(half_size, min(self.player_pos[0], self.camera.map_width - half_size))
        self.player_pos[1] = max(half_size, min(self.player_pos[1], self.camera.map_height - half_size))

    def _verificar_interacao(self):
        """Verifica se o jogador está próximo o suficiente de um NPC para interagir."""
        # Usa o método player_rect() para consistência
        player_rect = self.player_rect() 

        self.npc_interacao = None # Reseta a cada frame
        for npc in self.npcs:
            if player_rect.colliderect(npc.rect):
                self.npc_interacao = npc
                break
        
    def _update_camera(self):
        """Atualiza a posição da câmera para seguir o jogador."""
        self.camera.update(self.player_pos)

    # ========================
    # Métodos de Renderização
    # ========================

    def _draw_player(self, surface):
        """Desenha o jogador na tela."""
        player_screen_pos = self.camera.apply(self.player_pos)
        pygame.draw.circle(surface, (255, 255, 255), player_screen_pos, self.TAMANHO_JOGADOR / 2)

    def _draw_npcs(self, surface):
        """Desenha todos os NPCs na tela."""
        for npc in self.npcs:
            # Aplica o deslocamento da câmera ao retângulo do NPC antes de desenhar
            npc_screen_rect = self.camera.apply(npc.rect)
            pygame.draw.rect(surface, (0, 255, 0), npc_screen_rect, 2)

    def _draw_hud(self, surface):
        """Desenha a interface do usuário, como dicas de interação e stats."""
        # Indicador de interação
        if self.npc_interacao:
            text = self.font_hud.render(f"Pressione [E] para falar com {self.npc_interacao.nome}", True, (255, 255, 0))
            rect = text.get_rect(center=(self.game.screen_width / 2, self.game.screen_height - 30))
            surface.blit(text, rect)

        # Posição do jogador (para debug)
        pos_text = self.font_hud.render(f"X: {int(self.player_pos[0])} | Y: {int(self.player_pos[1])}", True, (255, 255, 255))
        surface.blit(pos_text, (10, 10))