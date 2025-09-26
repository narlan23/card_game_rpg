import random

class StatusManager:
    def __init__(self, battle_manager):
        self.battle_manager = battle_manager

        # Registro central de efeitos contínuos
        self.STATUS_EFFECTS = {
            "veneno": self._apply_poison,
            "regeneração": self._apply_regeneration,
            "força": self._apply_strength,
            "fraqueza": self._apply_weakness,
            "vulnerabilidade": self._apply_vulnerability,
            "esquiva": self._apply_dodge,
            "buff": self._apply_generic_buff,
            "vulneravel": self._apply_generic_debuff,
        }

    # ------------------ CÁLCULO DE DANO ------------------

    def calculate_player_damage(self, base_damage, card=None):
        """Calcula o dano que o jogador causa (considerando buffs/debuffs)."""
        damage = base_damage
        player = self.battle_manager.game.player
        print(f"[DEBUG] Calculando dano do PLAYER. Base={base_damage}")

        if player.has_status("força"):
            power = player.status_effects["força"].get("power", 0)
            damage += power
            print(f"[DEBUG] Buff FORÇA aplicado. +{power} de dano → {damage}")

        if player.has_status("fraqueza"):
            multiplier = player.status_effects["fraqueza"].get("multiplier", 0.75)
            damage = int(damage * multiplier)
            print(f"[DEBUG] Debuff FRAQUEZA aplicado. x{multiplier} → {damage}")

        final = max(0, damage)
        print(f"[DEBUG] Dano final do PLAYER: {final}")
        return final

    def calculate_enemy_damage(self, base_damage, enemy):
        """Calcula o dano que o inimigo causa ao jogador (considerando vulnerabilidades)."""
        damage = base_damage
        player = self.battle_manager.game.player
        print(f"[DEBUG] Calculando dano do INIMIGO {getattr(enemy, 'name', '?')}. Base={base_damage}")

        if player.has_status("vulnerabilidade") or player.has_status("vulneravel"):
            multiplier = player.status_effects.get("vulnerabilidade", player.status_effects.get("vulneravel", {})).get("multiplier", 1.5)
            damage = int(damage * multiplier)
            print(f"[DEBUG] Player está VULNERÁVEL. x{multiplier} → {damage}")

        final = max(0, damage)
        print(f"[DEBUG] Dano final do INIMIGO: {final}")
        return final

    # ------------------ APLICAÇÃO DE STATUS ------------------

    def apply_status_effects(self, targets=None):
        """
        Aplica efeitos contínuos em todos os alvos e reduz duração.
        Remove status quando a duração chega a 0.
        """
        if targets is None:
            targets = [self.battle_manager.game.player]

        for target in targets:
            print(f"[DEBUG] Aplicando efeitos contínuos em {getattr(target, 'name', 'Player')}")

            expired_effects = []

            for status_name, data in list(target.status_effects.items()):
                print(f"[DEBUG] Status ativo: {status_name} {data}")

                # Aplica efeito se existir no registro
                if status_name in self.STATUS_EFFECTS:
                    self.STATUS_EFFECTS[status_name](target, data)

                # Reduz duração se tiver
                if "duration" in data:
                    data["duration"] -= 1
                    print(f"[DEBUG] Reduzindo duração de {status_name}: {data['duration']} turnos restantes")
                    if data["duration"] <= 0:
                        expired_effects.append(status_name)

            # Remove os expirados
            for status_name in expired_effects:
                print(f"[DEBUG] Status {status_name} expirou e será removido.")
                target.remove_status(status_name)

    def apply_status_to_target(self, target, status_name, **kwargs):
        """
        Aplica um efeito de status a um alvo (jogador ou inimigo).
        kwargs pode conter: power, multiplier, damage, heal, duration, etc.
        """
        print(f"[DEBUG] Aplicando status {status_name} em {getattr(target, 'name', 'Player')} com {kwargs}")
        if hasattr(target, "add_status"):
            target.add_status(status_name, **kwargs)


    # ------------------ IMPLEMENTAÇÃO DE EFEITOS ------------------

    def _apply_poison(self, target, data):
        """Aplica veneno → causa dano por turno."""
        damage = data.get("damage", 1)
        print(f"[DEBUG] Veneno ativo em {getattr(target, 'name', 'Player')}: causando {damage} de dano")
        if hasattr(target, "take_damage"):
            target.take_damage(damage)
        else:
            target.health = max(0, target.health - damage)

        if hasattr(self.battle_manager, "animation_manager"):
            self.battle_manager.animation_manager.spawn_damage_animation(
                target, damage, is_player=getattr(target, "is_player", False)
            )

    def _apply_regeneration(self, target, data):
        """Aplica regeneração → cura por turno."""
        heal_amount = data.get("heal", 2)
        print(f"[DEBUG] Regeneração ativa em {getattr(target, 'name', 'Player')}: curando {heal_amount}")
        if hasattr(target, "heal"):
            target.heal(heal_amount)
        else:
            target.health = min(getattr(target, "max_health", target.health), target.health + heal_amount)

    def _apply_strength(self, target, data):
        """Buff de força - efeito já aplicado no cálculo de dano."""
        print(f"[DEBUG] Força ativa em {getattr(target, 'name', 'Player')}: +{data.get('power', 0)} de dano")

    def _apply_weakness(self, target, data):
        """Debuff de fraqueza - efeito já aplicado no cálculo de dano."""
        print(f"[DEBUG] Fraqueza ativa em {getattr(target, 'name', 'Player')}: dano reduzido")

    def _apply_vulnerability(self, target, data):
        """Vulnerabilidade - efeito já aplicado no cálculo de dano."""
        print(f"[DEBUG] Vulnerabilidade ativa em {getattr(target, 'name', 'Player')}: recebe mais dano")

    def _apply_dodge(self, target, data):
        """Chance de esquivar ataques."""
        print(f"[DEBUG] Esquiva ativa em {getattr(target, 'name', 'Player')}")

    def _apply_generic_buff(self, target, data):
        """Buff genérico - trata como força para compatibilidade."""
        print(f"[DEBUG] Buff genérico ativo em {getattr(target, 'name', 'Player')}")
        # Converte buff genérico para força se aplicável
        if "power" in data:
            if not target.has_status("força"):
                target.add_status("força", power=data["power"], duration=data.get("duration", 2))

    def _apply_generic_debuff(self, target, data):
        """Debuff genérico - trata como vulnerabilidade para compatibilidade."""
        print(f"[DEBUG] Debuff genérico ativo em {getattr(target, 'name', 'Player')}")
        # Converte vulneravel para vulnerabilidade se aplicável
        if not target.has_status("vulnerabilidade"):
            target.add_status("vulnerabilidade", multiplier=1.5, duration=data.get("duration", 2))