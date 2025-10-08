import pygame
import random

class Enemy(pygame.sprite.Sprite):
    """Representa um inimigo com IA adaptativa, animações e status."""

    def __init__(self, name, health, attack_value, image_paths, position,animation_speed, x_tam, y_tam):
        super().__init__()

        # -------------------------
        # Atributos de combate
        # -------------------------
        self.name = name
        self.max_health = health
        self.health = health
        self.attack_value = attack_value
        self.shield = 0
        self.status_effects = {}

        # -------------------------
        # Animação
        # -------------------------
        self.x_tam = x_tam
        self.y_tam = y_tam
        self.animation_speed = animation_speed
        self.current_frame_index = 0
        self.animation_timer = 0
        self.frames = self._load_and_scale_frames(image_paths, (x_tam, y_tam))

        if self.frames:
            self.image = self.frames[self.current_frame_index]
        else:
            self.image = pygame.Surface((x_tam, y_tam))
            self.image.fill((0, 0, 0))
            print(f"[WARN] Nenhum frame carregado para {self.name}!")

        self.rect = self.image.get_rect(center=position)

    # ================================================================
    # 🔹 UTILITÁRIOS DE ANIMAÇÃO
    # ================================================================
    def _load_and_scale_frames(self, image_paths, size):
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
        if amount > 0:
            self.health = min(self.max_health, self.health + int(amount))
            print(f"{self.name} recuperou {amount} de vida! ({self.health}/{self.max_health})")

    def add_shield(self, amount=1):
        self.shield += amount
        print(f"{self.name} ganhou {amount} de escudo (total: {self.shield})")

    # ================================================================
    # 🔹 STATUS
    # ================================================================
    def add_status(self, status: str, **kwargs):
        self.status_effects[status] = kwargs
        print(f"{self.name} ganhou status: {status} {kwargs}")

    def has_status(self, status: str):
        return status in self.status_effects

    def remove_status(self, status: str):
        if status in self.status_effects:
            del self.status_effects[status]
            print(f"{self.name} perdeu o status {status}")

    # ================================================================
    # 🔹 IA MELHORADA
    # ================================================================
    def choose_action(self, player=None):
        """
        IA adaptativa:
        Decide entre atacar, defender, curar ou aplicar status.
        """
        if not self.is_alive():
            return None

        health_ratio = self.health / self.max_health
        has_shield = self.shield > 0
        action = "attack"

        # -------------------------
        # 1. Situação crítica
        # -------------------------
        if health_ratio < 0.3 and not self.has_status("regen"):
            # Chance maior de curar ou defender
            action = random.choices(
                ["heal", "defend", "attack"],
                weights=[0.5, 0.3, 0.2],
                k=1
            )[0]
        # -------------------------
        # 2. Vida moderada
        # -------------------------
        elif 0.3 <= health_ratio < 0.7:
            if not has_shield:
                action = random.choices(
                    ["defend", "attack", "apply_status"],
                    weights=[0.4, 0.4, 0.2],
                    k=1
                )[0]
            else:
                action = random.choice(["attack", "apply_status"])
        # -------------------------
        # 3. Vida alta — ofensivo
        # -------------------------
        else:
            if self.has_status("fortalecido"):
                action = random.choice(["power_attack", "attack"])
            else:
                action = random.choices(
                    ["attack", "apply_status"],
                    weights=[0.7, 0.3],
                    k=1
                )[0]

        print(f"[IA] {self.name} escolheu a ação: {action}")
        return action

    def execute_action(self, action, player):
        """Executa a ação escolhida."""
        if action == "attack":
            dmg = self.calculate_attack()
            player.take_damage(dmg)
            print(f"{self.name} ataca causando {dmg} de dano!")

        elif action == "power_attack":
            dmg = int(self.calculate_attack() * 1.5)
            player.take_damage(dmg)
            print(f"{self.name} usa um ATAQUE PODEROSO de {dmg}!")

        elif action == "defend":
            shield_amt = random.randint(2, 4)
            self.add_shield(shield_amt)

        elif action == "heal":
            heal_amt = random.randint(2, 5)
            self.heal(heal_amt)

        elif action == "apply_status":
            # Aplica debuff no jogador ou buff em si mesmo
            if random.random() < 0.5:
                player.add_status("vulneravel", duration=3, multiplier=1.5)
                print(f"{self.name} aplica vulnerabilidade no jogador!")
            else:
                self.add_status("fortalecido", power=2, duration=3)

    def calculate_attack(self):
        base = self.attack_value
        if self.has_status("fortalecido"):
            bonus = self.status_effects["fortalecido"].get("power", 1)
            base += bonus
            print(f"{self.name} ataca com bônus de +{bonus} (fortalecido).")
        return base

    # ================================================================
    # 🔹 ATUALIZAÇÃO
    # ================================================================
    def update(self, dt):
        if self.frames:
            self.animation_timer += dt * 1000
            if self.animation_timer >= self.animation_speed:
                self.animation_timer -= self.animation_speed
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
                self.image = self.frames[self.current_frame_index]

        expired = []
        for status, data in list(self.status_effects.items()):
            if "duration" in data:
                data["duration"] -= dt
                if data["duration"] <= 0:
                    expired.append(status)
        for s in expired:
            self.remove_status(s)

        # Efeitos contínuos
        if self.has_status("veneno"):
            dmg = self.status_effects["veneno"].get("power", 1)
            self.take_damage(dmg * dt)

        if self.has_status("regen"):
            heal = self.status_effects["regen"].get("power", 1)
            self.heal(heal * dt)

    def is_alive(self):
        return self.health > 0

    def __str__(self):
        return (f"{self.name} | HP: {self.health:.0f}/{self.max_health} | "
                f"Shield: {self.shield} | Status: {list(self.status_effects.keys())}")
