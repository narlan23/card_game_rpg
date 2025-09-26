import pygame

class Enemy(pygame.sprite.Sprite):  # Agora é um Sprite
    """Representa um inimigo genérico com buffs e debuffs."""
    def __init__(self, name, health, attack_value, image_path, position):
        super().__init__()  # inicializa o Sprite

        # Atributos lógicos
        self.name = name
        self.max_health = health
        self.health = health
        self.attack_value = attack_value
        self.shield = 0
        self.status_effects = {}  # {"veneno": {"power": 2, "duration": 3}}

        # Atributos gráficos (obrigatórios no Sprite)
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (150, 150))
        self.rect = self.image.get_rect(center=position)

    # -------------------------
    # Métodos de jogo
    # -------------------------
    def take_damage(self, amount: int):
        """Recebe dano, considerando o escudo e vulnerabilidade."""
        if self.shield > 0:
            absorbed = min(amount, self.shield)
            self.shield -= absorbed
            amount -= absorbed
            print(f"{self.name} bloqueou {absorbed} de dano com escudo!")

        if self.has_status("vulneravel"):
            amount *= 1.5
            print(f"O dano foi aumentado para {amount:.0f} devido à vulnerabilidade!")

        if amount > 0:
            self.health = max(0, self.health - int(amount))
            print(f"{self.name} recebeu {amount:.0f} de dano! Vida atual: {self.health}")

        return self.health <= 0

    def heal(self, amount: int):
        """Cura o inimigo, sem passar da vida máxima."""
        if amount > 0:
            self.health = min(self.max_health, self.health + amount)
            print(f"{self.name} recuperou {amount} de vida! Vida atual: {self.health}")

    def add_shield(self, amount=1):
        self.shield += amount
        print(f"{self.name} ganhou {amount} de escudo!")

    def add_status(self, status: str, **kwargs):
        """Adiciona um status com atributos extras (ex: power, duration)."""
        self.status_effects[status] = kwargs
        print(f"{self.name} ganhou status: {status} {kwargs}")

    def has_status(self, status: str):
        return status in self.status_effects

    def remove_status(self, status: str):
        if status in self.status_effects:
            del self.status_effects[status]
            print(f"{self.name} perdeu o status {status}")

    def choose_action(self):
        """IA básica: decide qual ação tomar."""
        # Se o inimigo estiver fortalecido, prioriza ataque
        if self.has_status("fortalecido"):
            return "power_attack"
        return "attack"

    def calculate_attack(self):
        """Calcula o valor real do ataque considerando buffs."""
        base_attack = self.attack_value
        if self.has_status("fortalecido"):
            bonus = self.status_effects["fortalecido"].get("power", 1)
            base_attack += bonus
            print(f"{self.name} ataca com +{bonus} de poder por fortalecimento!")
        return base_attack

    def is_alive(self):
        return self.health > 0

    # -------------------------
    # Integração com pygame.sprite.Group
    # -------------------------
    def update(self):
        """Atualiza o inimigo a cada frame/tick do jogo."""
        expired = []

        # Atualiza duração dos efeitos
        for status, data in list(self.status_effects.items()):
            if "duration" in data:
                data["duration"] -= 1
                if data["duration"] <= 0:
                    expired.append(status)

        # Remove efeitos expirados
        for status in expired:
            self.remove_status(status)

        # Aplicação de efeitos contínuos (ordem fixa: veneno -> regen)
        if self.has_status("veneno"):
            dmg = self.status_effects["veneno"].get("power", 1)
            self.take_damage(dmg)
            print(f"{self.name} sofre {dmg} de dano por veneno!")

        if self.has_status("regen"):
            heal = self.status_effects["regen"].get("power", 1)
            self.heal(heal)
            print(f"{self.name} recupera {heal} de vida pela regeneração!")

    def __str__(self):
        return (f"{self.name} | HP: {self.health}/{self.max_health} | "
                f"Shield: {self.shield} | Status: {list(self.status_effects.keys())}")
