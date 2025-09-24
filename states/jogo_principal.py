import pygame
import sys
from jogo_principal.camera import Camera
from jogo_principal.tileset import TiledMap
from jogo_principal.dialog import Dialogo
from characters.npc import NPC  # import da classe NPC

class JogoPrincipal:
    def __init__(self, game):
        self.game = game
        self.font = game.assets.get_font("default")
        self.player_pos = [400, 300]

        # Configurações do jogador
        self.TAMANHO_JOGADOR = 20
        self.VELOCIDADE_JOGADOR = 3

        # Carregar mapa JSON do Tiled
        self.mapa = TiledMap("assets/mapa.tmj")

        # Configuração da câmera
        map_width = self.mapa.width * self.mapa.tilewidth
        map_height = self.mapa.height * self.mapa.tileheight
        self.camera = Camera(500, 400, map_width, map_height)

        # Sistema de diálogo
        self.dialogo = Dialogo(self.font)

        # NPCs do jogo
        self.npcs = [
            NPC(
                "Velho Sábio",
                pygame.Rect(672, 294, 50, 50),
                {
                    "texto": "Bem-vindo, aventureiro! Cuidado com os perigos da torre...",
                    "opcoes": ["Atacar", "Defender", "Usar Item", "Fugir"],
                    "callbacks": [
                        lambda: print("Atacou!"),
                        lambda: print("Defendeu!"),
                        lambda: print("Usou item!"),
                        lambda: print("Fugiu!")
                    ],
                    "layout": "vertical"
                }
            ),
            NPC(
                "Comerciante",
                pygame.Rect(672, 400, 50, 50),
                {
                    "texto": "Tenho poções e equipamentos para vender!",
                    "layout": "info"
                }
            ),
            NPC(
                "Torre",
                pygame.Rect(672, 500, 50, 50),
                {
                    "texto": "Deseja enfrentar a torre?",
                    "opcoes": ["Sim", "Não", "Talvez"],
                    "callbacks": [
                        lambda: self.game.change_state("BATALHA"),
                        lambda: print("Não enfrentou."),
                        lambda: print("Talvez depois.")
                    ],
                    "layout": "horizontal"
                }
            )
        ]

        # Estado de interação
        self.pode_interagir = False
        self.npc_interacao = None

        # Clock para delta time
        self.clock = pygame.time.Clock()
        self.delta_time = 0

    # ========================
    # Eventos
    # ========================
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._handle_global_event(event)
            if self.dialogo.ativo:
                self.dialogo.handle_event(event)

    def _handle_global_event(self, event):
        if event.key == pygame.K_ESCAPE:
            if self.dialogo.ativo:
                self.dialogo.fechar()
            else:
                self.game.change_state("MENU_PRINCIPAL")
        elif event.key == pygame.K_c:
            self.game.change_state("CARACTERISTICAS")
        elif event.key == pygame.K_b:
            self.game.change_state("BATALHA")
        elif event.key == pygame.K_e and self.pode_interagir and not self.dialogo.ativo:
            self._interagir_com_npc()

    # ========================
    # Atualização
    # ========================
    def update(self):
        self.delta_time = self.clock.tick(60) / 1000.0
        self._processar_movimento()
        self._verificar_colisoes()
        self.camera.update(self.player_pos)

    def _processar_movimento(self):
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.player_pos[0] += dx * self.VELOCIDADE_JOGADOR * 60 * self.delta_time
        self.player_pos[1] += dy * self.VELOCIDADE_JOGADOR * 60 * self.delta_time
        self._limitar_movimento_mapa()

    def _limitar_movimento_mapa(self):
        half_size = self.TAMANHO_JOGADOR // 2
        map_width = self.mapa.width * self.mapa.tilewidth
        map_height = self.mapa.height * self.mapa.tileheight

        self.player_pos[0] = max(half_size, min(self.player_pos[0], map_width - half_size))
        self.player_pos[1] = max(half_size, min(self.player_pos[1], map_height - half_size))

    def _verificar_colisoes(self):
        player_rect = pygame.Rect(
            self.player_pos[0] - self.TAMANHO_JOGADOR // 2,
            self.player_pos[1] - self.TAMANHO_JOGADOR // 2,
            self.TAMANHO_JOGADOR,
            self.TAMANHO_JOGADOR
        )

        self.pode_interagir = False
        self.npc_interacao = None

        for npc in self.npcs:
            if player_rect.colliderect(npc.rect):
                self.pode_interagir = True
                self.npc_interacao = npc
                break

    def _interagir_com_npc(self):
        if self.npc_interacao:
            print(f"Interagindo com {self.npc_interacao.nome}")
            self.npc_interacao.interagir(self.dialogo)

    # ========================
    # Renderização
    # ========================
    def draw(self, surface):
        surface.fill((0, 0, 0))
        temp_surface = pygame.Surface((self.camera.width, self.camera.height))
        temp_surface.fill((30, 30, 50))

        self.mapa.draw(temp_surface, self.camera)

        # Desenha NPCs
        for npc in self.npcs:
            pygame.draw.rect(temp_surface, (0, 255, 0), self.camera.apply_rect(npc.rect), 2)

        # Desenha jogador
        player_screen_pos = self.camera.apply(self.player_pos)
        pygame.draw.circle(temp_surface, (255, 255, 255), player_screen_pos, self.TAMANHO_JOGADOR // 2)

        # Indicador de interação
        if self.pode_interagir:
            interacao_pos = (player_screen_pos[0], player_screen_pos[1] - self.TAMANHO_JOGADOR - 10)
            pygame.draw.circle(temp_surface, (255, 255, 0), interacao_pos, 5)

        surface.blit(pygame.transform.scale(temp_surface, surface.get_size()), (0, 0))

        if self.dialogo.ativo:
            self.dialogo.draw(surface)

        self._draw_debug_info(surface)

    def _draw_debug_info(self, surface):
        debug_text = [
            f"Posição: {int(self.player_pos[0])}, {int(self.player_pos[1])}",
            f"FPS: {int(self.clock.get_fps())}",
            f"Interação: {self.pode_interagir}",
            f"NPC: {self.npc_interacao.nome if self.npc_interacao else 'Nenhum'}"
        ]

        for i, text in enumerate(debug_text):
            text_surface = self.font.render(text, True, (255, 255, 255))
            surface.blit(text_surface, (10, 10 + i * 20))
