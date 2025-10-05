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
         #f"{ENEMY_ASSET_PATH}agua_frame_4.png",
         #f"{ENEMY_ASSET_PATH}agua_frame_5.png",
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

        # NOVO: Nível de zoom inicial
        self.zoom_level_padrao = 1.5
        self.camera = Camera(
            self.game.screen_width, 
            self.game.screen_height, 
            map_width, 
            map_height, 
            zoom_level=self.zoom_level_padrao
        )
        # NOVO: Configurações de zoom
        self.zoom_speed = 0.25 # Quanto o zoom muda por tecla
        self.min_zoom = 0.5   # Zoom out máximo
        self.max_zoom = 3.0   # Zoom in máximo
        

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
                self._handle_zoom_input(event)

    def _handle_zoom_input(self, event):
        """Gerencia os eventos de zoom (teclas '+' e '-')"""
        if event.type == pygame.KEYDOWN:
            novo_zoom = self.camera.zoom_level
            
            # Tecla '+' ou PgUp (Aumenta o zoom - Aproxima)
            if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                novo_zoom += self.zoom_speed
            # Tecla '-' ou PgDown (Diminui o zoom - Afasta)
            elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                novo_zoom -= self.zoom_speed
            
            # Garante que o zoom esteja dentro dos limites
            novo_zoom = max(self.min_zoom, min(novo_zoom, self.max_zoom))
            
            # Aplica o novo zoom (a propriedade setter faz todo o recálculo)
            self.camera.zoom_level = novo_zoom

    def update(self):
        """Atualiza a lógica do jogo a cada frame."""
        # Calcula o delta_time para movimento consistente
        self.delta_time = self.clock.tick(60) / 1000.0

        if not self.dialogo.ativo:
            self._processar_movimento()
            self._verificar_interacao()
        
        self._update_camera()

# JogoPrincipal.draw(self, surface)

    def draw(self, surface):
        """Renderiza todos os elementos do jogo na tela, aplicando o zoom."""
        
        # === ETAPA 1: Criar e Desenhar na Superfície Temporária (CANVAS) ===
        
        # 1.1 Obtém o tamanho da área de visão (viewport) no mundo.
        # Se o zoom for 2.0, o viewport_w será metade da largura da tela real.
        viewport_w = int(self.camera.width)
        viewport_h = int(self.camera.height)
        
        # 1.2 Cria a Surface temporária (Canvas)
        canvas = pygame.Surface((viewport_w, viewport_h))
        canvas.fill((30, 30, 50)) # Preenche o CANVAS com o fundo
        
        # 1.3 Desenha TODOS os elementos do mundo na CANVAS, usando a camera.apply()
        # Note que passamos 'canvas', não 'surface'
        self.mapa.draw(canvas, self.camera)
        self._draw_npcs(canvas) # Este método deve usar canvas
        self._draw_player(canvas) # Este método deve usar canvas
        
        # === ETAPA 2: Escalonar e Desenhar na Tela Real ===
        
        # 2.1 Escala a imagem da canvas (400x300, por exemplo) para o tamanho real da tela (800x600)
        scaled_canvas = pygame.transform.scale(
            canvas, 
            (self.game.screen_width, self.game.screen_height)
        )
        
        # 2.2 Desenha a imagem ampliada na tela principal (surface)
        surface.blit(scaled_canvas, (0, 0))

        # === ETAPA 3: Desenhar HUD/UI sem Zoom ===
        
        # O HUD e o Diálogo devem ser desenhados por último, diretamente na 'surface',
        # para que não sejam afetados pelo zoom.
        self._draw_hud(surface)
        
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
    
    def _update_camera(self):
        """Atualiza a posição da câmera para seguir o jogador."""
        self.camera.update(self.player_pos)

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
    # Métodos de Renderização (AGORA DESENHAM NA CANVAS)
    # ========================

    def _draw_player(self, canvas):
        """Desenha o jogador na tela (agora na canvas)."""
        # A posição aplicada pela câmera é em relação ao viewport, que é o tamanho da canvas.
        player_screen_pos = self.camera.apply(self.player_pos)
        pygame.draw.circle(canvas, (255, 255, 255), player_screen_pos, self.TAMANHO_JOGADOR / 2)

    def _draw_npcs(self, canvas):
        """Desenha todos os NPCs na tela (agora na canvas)."""
        for npc in self.npcs:
            npc_screen_rect = self.camera.apply(npc.rect)
            pygame.draw.rect(canvas, (0, 255, 0), npc_screen_rect, 2)

    def _draw_hud(self, surface):
        """Desenha a interface do usuário (HUD) na superfície PRINCIPAL (sem zoom)."""
        # Indicador de interação
        if self.npc_interacao:
            text = self.font_hud.render(f"Pressione [E] para falar com {self.npc_interacao.nome}", True, (255, 255, 0))
            rect = text.get_rect(center=(self.game.screen_width / 2, self.game.screen_height - 30))
            surface.blit(text, rect)

        # Posição do jogador (para debug)
        # Também adicionamos o zoom atual para debug
        pos_text = self.font_hud.render(
            f"X: {int(self.player_pos[0])} | Y: {int(self.player_pos[1])} | Zoom: {self.camera.zoom_level:.2f}", 
            True, (255, 255, 255)
        )
        surface.blit(pos_text, (10, 10))