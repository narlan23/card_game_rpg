import pygame

class Enemy(pygame.sprite.Sprite):
    """Representa um inimigo genérico com animações, buffs e debuffs."""

    def __init__(self, name, health, attack_value, image_paths, position, x_tam, y_tam):
        super().__init__()

        # -------------------------
        # Atributos de combate
        # -------------------------
        self.name = name
        self.max_health = health
        self.health = health
        self.attack_value = attack_value
        self.shield = 0
        self.status_effects = {}  # Exemplo: {"veneno": {"power": 2, "duration": 3}}

        # -------------------------
        # Atributos visuais / animação
        # -------------------------
        self.x_tam = x_tam
        self.y_tam = y_tam
        self.animation_speed = 100  # ms por frame
        self.current_frame_index = 0
        self.animation_timer = 0

        # Carrega frames
        self.frames = self._load_and_scale_frames(image_paths, (x_tam, y_tam))
        if self.frames:
            self.image = self.frames[self.current_frame_index]
        else:
            self.image = pygame.Surface((x_tam, y_tam))
            self.image.fill((0, 0, 0))
            print(f"[WARN] Nenhum frame carregado para {self.name}!")

        self.rect = self.image.get_rect(center=position)

    # ================================================================
    # 🔹 MÉTODOS INTERNOS
    # ================================================================

    def _load_and_scale_frames(self, image_paths, size):
        """Carrega e redimensiona todos os frames da animação."""
        frames_list = []
        for path in image_paths:
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, size)
                frames_list.append(img)
            except pygame.error as e:
                print(f"[ERRO] Falha ao carregar {path}: {e}")
        return frames_list

    # ================================================================
    # 🔹 COMBATE
    # ================================================================

    def take_damage(self, amount: int):
        """Recebe dano, considerando escudo e vulnerabilidade."""
        if self.shield > 0:
            absorbed = min(amount, self.shield)
            self.shield -= absorbed
            amount -= absorbed
            print(f"{self.name} bloqueou {absorbed} de dano com escudo!")

        if self.has_status("vulneravel"):
            amount *= 1.5
            print(f"O dano foi aumentado para {amount:.0f} (vulnerável)!")

        if amount > 0:
            self.health = max(0, self.health - int(amount))
            print(f"{self.name} recebeu {amount:.0f} de dano! Vida: {self.health}/{self.max_health}")

        return self.health <= 0

    def heal(self, amount: int):
        """Cura o inimigo, sem ultrapassar o máximo."""
        if amount > 0:
            self.health = min(self.max_health, self.health + int(amount))
            print(f"{self.name} recuperou {amount} de vida! ({self.health}/{self.max_health})")

    def add_shield(self, amount=1):
        """Adiciona escudo temporário."""
        self.shield += amount
        print(f"{self.name} ganhou {amount} de escudo (total: {self.shield})")

    # ================================================================
    # 🔹 STATUS
    # ================================================================

    def add_status(self, status: str, **kwargs):
        """Adiciona ou renova um status com parâmetros (ex: power, duration)."""
        self.status_effects[status] = kwargs
        print(f"{self.name} ganhou status: {status} {kwargs}")

    def has_status(self, status: str):
        return status in self.status_effects

    def remove_status(self, status: str):
        if status in self.status_effects:
            del self.status_effects[status]
            print(f"{self.name} perdeu o status {status}")

    # ================================================================
    # 🔹 IA E AÇÕES
    # ================================================================

    def choose_action(self):
        """IA simples para decidir ações."""
        if self.has_status("fortalecido"):
            return "power_attack"
        return "attack"

    def calculate_attack(self):
        """Calcula o ataque considerando buffs."""
        base = self.attack_value
        if self.has_status("fortalecido"):
            bonus = self.status_effects["fortalecido"].get("power", 1)
            base += bonus
            print(f"{self.name} ataca com +{bonus} de bônus (fortalecido).")
        return base

    def is_alive(self):
        return self.health > 0

    # ================================================================
    # 🔹 ATUALIZAÇÃO
    # ================================================================

    def update(self, dt):
        """Atualiza a animação e efeitos com base no tempo (dt em segundos)."""
        # -------------------------
        # 1. Atualiza animação
        # -------------------------
        if self.frames:
            # converte dt (s) para ms
            self.animation_timer += dt * 1000
            if self.animation_timer >= self.animation_speed:
                self.animation_timer -= self.animation_speed
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
                self.image = self.frames[self.current_frame_index]

        # -------------------------
        # 2. Atualiza duração dos status
        # -------------------------
        expired = []
        for status, data in list(self.status_effects.items()):
            if "duration" in data:
                # duração baseada em segundos
                data["duration"] -= dt
                if data["duration"] <= 0:
                    expired.append(status)

        for status in expired:
            self.remove_status(status)

        # -------------------------
        # 3. Aplica efeitos contínuos
        # -------------------------
        if self.has_status("veneno"):
            dmg = self.status_effects["veneno"].get("power", 1)
            self.take_damage(dmg * dt)  # dano contínuo baseado em tempo real
            print(f"{self.name} sofre {dmg} dano/s por veneno.")

        if self.has_status("regen"):
            heal = self.status_effects["regen"].get("power", 1)
            self.heal(heal * dt)
            print(f"{self.name} regenera {heal} HP/s.")

    def __str__(self):
        return (f"{self.name} | HP: {self.health}/{self.max_health} | "
                f"Shield: {self.shield} | Status: {list(self.status_effects.keys())}")
