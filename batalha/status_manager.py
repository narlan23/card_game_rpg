class StatusManager:
    def __init__(self, battle_manager):
        self.battle_manager = battle_manager

        # Registro central de efeitos contínuos
        self.STATUS_EFFECTS = {
            "veneno": self._apply_poison,
            "regeneração": self._apply_regeneration,
        }

    # ------------------ CÁLCULO DE DANO ------------------

    def calculate_player_damage(self, base_damage, card=None):
        """Calcula o dano que o jogador causa (considerando buffs/debuffs)."""
        damage = base_damage
        player = self.battle_manager.game.player

        if player.has_status("força"):
            power = player.status_effects["força"].get("power", 0)
            damage += power

        if player.has_status("fraqueza"):
            multiplier = player.status_effects["fraqueza"].get("multiplier", 0.75)
            damage = int(damage * multiplier)

        return max(0, damage)

    def calculate_enemy_damage(self, base_damage, enemy):
        """Calcula o dano que o inimigo causa ao jogador (considerando vulnerabilidades)."""
        damage = base_damage
        player = self.battle_manager.game.player

        if player.has_status("vulnerabilidade"):
            multiplier = player.status_effects["vulnerabilidade"].get("multiplier", 1.5)
            damage = int(damage * multiplier)

        return max(0, damage)

    # ------------------ APLICAÇÃO DE STATUS ------------------

    def apply_status_effects(self, targets=None):
        """
        Aplica efeitos contínuos em todos os alvos e reduz duração.
        Remove status quando a duração chega a 0.
        """
        if targets is None:
            targets = [self.battle_manager.game.player]

        for target in targets:
            expired_effects = []

            for status_name, data in list(target.status_effects.items()):
                # Aplica efeito se existir no registro
                if status_name in self.STATUS_EFFECTS:
                    self.STATUS_EFFECTS[status_name](target, data)

                # Reduz duração se tiver
                if "duration" in data:
                    data["duration"] -= 1
                    if data["duration"] <= 0:
                        expired_effects.append(status_name)

            # Remove os expirados
            for status_name in expired_effects:
                target.remove_status(status_name)

    def apply_status_to_target(self, target, status_name, **kwargs):
        """
        Aplica um efeito de status a um alvo (jogador ou inimigo).
        kwargs pode conter: power, multiplier, damage, heal, duration, etc.
        """
        if hasattr(target, "add_status"):
            target.add_status(status_name, **kwargs)

            if hasattr(self.battle_manager, "animation_manager"):
                self.battle_manager.animation_manager.spawn_status_animation(
                    target, status_name
                )

    # ------------------ IMPLEMENTAÇÃO DE EFEITOS ------------------

    def _apply_poison(self, target, data):
        """Aplica veneno → causa dano por turno."""
        damage = data.get("damage", 1)
        target.take_damage(damage)

        if hasattr(self.battle_manager, "animation_manager"):
            self.battle_manager.animation_manager.spawn_damage_animation(
                target, damage, is_player=getattr(target, "is_player", False)
            )

    def _apply_regeneration(self, target, data):
        """Aplica regeneração → cura por turno."""
        heal_amount = data.get("heal", 2)
        target.heal(heal_amount)
