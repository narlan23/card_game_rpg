import pygame

class Dialogo:
    # Constantes para melhor legibilidade
    BACKGROUND_COLOR = (30, 30, 40)
    BORDER_COLOR = (100, 100, 140)
    TEXT_COLOR = (255, 255, 255)
    SELECTION_COLOR = (100, 200, 100)
    OPTION_COLOR = (70, 70, 90)
    SELECTION_BORDER = (150, 255, 150)

    def __init__(self, font, padding=20):
        self.font = font
        self.padding = padding  # Espaçamento interno
        self.ativo = False
        self.texto = ""
        self.texto_quebrado = []  # Novo: Lista de linhas de texto
        self.opcoes = []
        self.opcao_selecionada = 0
        self.callbacks = []
        self.layout = "horizontal"

    def abrir(self, texto, opcoes=None, callbacks=None, layout="horizontal", max_largura=560):
        """
        Abre um diálogo.
        - texto: string da pergunta/mensagem
        - opcoes: lista de strings (ex: ["Sim", "Não"]) ou None no modo "info"
        - callbacks: lista de funções (mesma ordem das opções)
        - layout: "horizontal", "vertical" ou "info"
        - max_largura: Largura máxima em pixels para o texto principal.
        """
        self.texto = texto
        # Quebra a linha e armazena
        self.texto_quebrado = self._quebrar_texto(texto, max_largura)
        
        self.opcoes = opcoes if opcoes else []
        self.callbacks = callbacks if callbacks else []
        self.layout = layout
        self.opcao_selecionada = 0
        self.ativo = True
    
    def _quebrar_texto(self, texto, max_largura):
        """
        Divide o texto em linhas para que caiba na largura máxima.
        Trata '\n' como quebra de linha manual.
        """
        linhas = []
        # Trata quebras de linha manuais primeiro
        paragrafos = texto.split('\n')
        
        for paragrafo in paragrafos:
            palavras = paragrafo.split(' ')
            linha_atual = ""
            for palavra in palavras:
                # Tenta adicionar a próxima palavra para verificar a largura
                linha_candidata = linha_atual + (" " if linha_atual else "") + palavra
                
                # Verifica a largura do texto renderizado
                largura_linha, _ = self.font.size(linha_candidata)
                
                if largura_linha <= max_largura:
                    # A palavra cabe, adiciona à linha atual
                    linha_atual = linha_candidata
                else:
                    # A palavra não cabe.
                    if linha_atual:
                        # Adiciona a linha atual (completa) e começa uma nova
                        linhas.append(linha_atual)
                    
                    # Se a palavra sozinha for maior que max_largura, 
                    # ela será forçada a ser uma linha (pode cortar o texto)
                    # Caso contrário, começa a nova linha com a palavra
                    linha_atual = palavra
            
            # Adiciona a linha final do parágrafo, se houver algo
            if linha_atual:
                linhas.append(linha_atual)
                
        return linhas

    def fechar(self):
        self.ativo = False

    def handle_event(self, event):
        if not self.ativo:
            return

        if event.type == pygame.KEYDOWN:
            if self.layout in ("horizontal", "vertical") and self.opcoes:
                # Navegação nas opções (Horizontal/Vertical)
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

                # Confirmação da escolha
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.processar_escolha()
            else:
                # Modo informativo ("info")
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    self.fechar() # Fecha em qualquer confirmação/cancelamento

            # Cancelamento geral
            if event.key == pygame.K_ESCAPE and self.layout in ("horizontal", "vertical"):
                # Se houver uma callback de cancelamento, você pode executá-la
                # (Não implementado no original, mas útil)
                self.fechar()


    def processar_escolha(self):
        if self.callbacks and 0 <= self.opcao_selecionada < len(self.callbacks):
            # Executa a função de retorno (callback)
            self.callbacks[self.opcao_selecionada]()
        self.fechar()

    def draw(self, surface):
        if not self.ativo:
            return

        largura_tela, altura_tela = surface.get_size()
        
        # O tamanho do diálogo é ajustado para caber o texto e as opções
        altura_texto = len(self.texto_quebrado) * (self.font.get_height() + 5) + self.padding * 2 # +5 para espaçamento entre linhas
        
        # Altura mínima
        if self.layout == "info":
            altura_minima = 100
        else: # horizontal ou vertical
            altura_minima = 160
            
        altura_dialogo = max(altura_texto, altura_minima)

        # Posição do retângulo de diálogo (fixo no fundo da tela)
        DIALOG_WIDTH = 600
        DIALOG_HEIGHT = altura_dialogo
        dialog_rect = pygame.Rect(
            largura_tela//2 - DIALOG_WIDTH//2, 
            altura_tela - DIALOG_HEIGHT - 20, # 20px de margem inferior
            DIALOG_WIDTH, 
            DIALOG_HEIGHT
        )
        
        # Desenha fundo e borda
        pygame.draw.rect(surface, self.BACKGROUND_COLOR, dialog_rect, border_radius=10)
        pygame.draw.rect(surface, self.BORDER_COLOR, dialog_rect, 3, border_radius=10)

        # Desenho do Texto Principal (Multilinha)
        self._draw_texto_principal(surface, dialog_rect)

        # Desenho das Opções
        if self.layout == "horizontal" and self.opcoes:
            self._draw_horizontal(surface, dialog_rect, altura_texto)
        elif self.layout == "vertical" and self.opcoes:
            self._draw_vertical(surface, dialog_rect, altura_texto)
        elif self.layout == "info":
            self._draw_info(surface, dialog_rect)

    def _draw_texto_principal(self, surface, dialog_rect):
        """Desenha o texto principal linha por linha."""
        x_inicio = dialog_rect.x + self.padding
        y_inicio = dialog_rect.y + self.padding
        
        # Altura de cada linha renderizada, mais um pequeno espaçamento (5px)
        altura_linha = self.font.get_height() + 5 
        
        for i, linha in enumerate(self.texto_quebrado):
            linha_surface = self.font.render(linha, True, self.TEXT_COLOR)
            surface.blit(linha_surface, (x_inicio, y_inicio + i * altura_linha))
            
    def _draw_horizontal(self, surface, dialog_rect, texto_altura):
        # A posição Y das opções deve ser abaixo do texto principal
        y_base = dialog_rect.y + texto_altura + 10 # 10px de margem

        num_opcoes = len(self.opcoes)
        # Calcula espaçamento dinâmico entre as opções
        espacamento_horizontal = dialog_rect.width // (num_opcoes + 1)

        for i, opcao in enumerate(self.opcoes):
            x = dialog_rect.x + espacamento_horizontal * (i + 1)
            y = y_base
            
            # Cria um retângulo fixo para o botão
            opcao_rect = pygame.Rect(x - 60, y, 120, 40)

            # Define as cores de destaque
            cor = self.SELECTION_COLOR if i == self.opcao_selecionada else self.OPTION_COLOR
            cor_borda = self.SELECTION_BORDER if i == self.opcao_selecionada else self.BORDER_COLOR

            # Desenha o botão
            pygame.draw.rect(surface, cor, opcao_rect, border_radius=6)
            pygame.draw.rect(surface, cor_borda, opcao_rect, 2, border_radius=6)

            # Desenha o texto da opção centralizado
            opcao_text = self.font.render(opcao, True, self.TEXT_COLOR)
            text_rect = opcao_text.get_rect(center=opcao_rect.center)
            surface.blit(opcao_text, text_rect)

    def _draw_vertical(self, surface, dialog_rect, texto_altura):
        # Posição Y inicial para as opções (abaixo do texto)
        y_inicio = dialog_rect.y + texto_altura + 10
        
        num_opcoes = len(self.opcoes)
        
        for i, opcao in enumerate(self.opcoes):
            x = dialog_rect.centerx
            # Posição y de cada opção
            y = y_inicio + i * 50
            
            # Cria um retângulo fixo para o botão
            opcao_rect = pygame.Rect(x - 100, y, 200, 40)

            # Define as cores de destaque
            cor = self.SELECTION_COLOR if i == self.opcao_selecionada else self.OPTION_COLOR
            cor_borda = self.SELECTION_BORDER if i == self.opcao_selecionada else self.BORDER_COLOR

            # Desenha o botão
            pygame.draw.rect(surface, cor, opcao_rect, border_radius=6)
            pygame.draw.rect(surface, cor_borda, opcao_rect, 2, border_radius=6)

            # Desenha o texto da opção centralizado
            opcao_text = self.font.render(opcao, True, self.TEXT_COLOR)
            text_rect = opcao_text.get_rect(center=opcao_rect.center)
            surface.blit(opcao_text, text_rect)

    def _draw_info(self, surface, dialog_rect):
        # A posição das instruções deve ser no final do diálogo
        instrucoes_text = self.font.render(
            "Pressione ENTER ou ESC para continuar...",
            True, (200, 200, 200)
        )
        # Centraliza horizontalmente e alinha à parte inferior do diálogo
        text_x = dialog_rect.x + self.padding
        text_y = dialog_rect.bottom - self.font.get_height() - self.padding
        
        surface.blit(instrucoes_text, (text_x, text_y))