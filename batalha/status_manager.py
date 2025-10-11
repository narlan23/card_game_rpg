import random

class StatusManager:
    def __init__(self, battle_manager):
        self.battle_manager = battle_manager

        # Registro centralizado de efeitos contínuos
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

    # ------------------------------------------------------------
    # Cálculo de dano
    # ------------------------------------------------------------
    # ALTERAÇÃO: A assinatura deve ser corrigida para aceitar 'target'
    # ASSUMIMOS QUE A FUNÇÃO QUE CHAMA ESTA JÁ FOI CORRIGIDA (input_manager)
    def calculate_player_damage(self, base_damage, target, card=None):
        """Calcula o dano causado pelo jogador (considerando buffs/debuffs do jogador e debuffs de Vulnerabilidade do alvo)."""
        damage = base_damage
        player = self.battle_manager.game.player
        print(f"[DEBUG] Calculando dano do PLAYER. Base={base_damage}")

        # 1. Checa BUFFs/DEBUFFs do JOGADOR (Força e Fraqueza)
        if player.has_status("força"):
            power = player.status_effects["força"].get("power", 0)
            damage += power
            print(f"[DEBUG] Buff FORÇA aplicado. +{power} → {damage}")

        if player.has_status("fraqueza"):
            multiplier = player.status_effects["fraqueza"].get("multiplier", 0.75)
            damage = int(damage * multiplier)
            print(f"[DEBUG] Debuff FRAQUEZA aplicado. x{multiplier} → {damage}")

        # 2. Checa DEBUFFs no ALVO (Vulnerabilidade)
        if target and (target.has_status("vulnerabilidade") or target.has_status("vulneravel")):
            data = target.status_effects.get("vulnerabilidade", target.status_effects.get("vulneravel", {}))
            multiplier = data.get("multiplier", 1.5)
            
            # Aplica o multiplicador de vulnerabilidade ao dano final
            damage = int(damage * multiplier)
            print(f"[DEBUG] Alvo {getattr(target, 'name', '?')} vulnerável. x{multiplier} → {damage}")

        return max(0, damage)

    def calculate_enemy_damage(self, base_damage, enemy):
        """Calcula o dano que o inimigo causa ao jogador. (O 'player' é o alvo aqui)."""
        damage = base_damage
        player = self.battle_manager.game.player
        print(f"[DEBUG] Calculando dano do INIMIGO {getattr(enemy, 'name', '?')}. Base={base_damage}")

        # Verifica a vulnerabilidade do JOGADOR (o alvo)
        if player.has_status("vulnerabilidade") or player.has_status("vulneravel"):
            data = player.status_effects.get("vulnerabilidade", player.status_effects.get("vulneravel", {}))
            multiplier = data.get("multiplier", 1.5)
            damage = int(damage * multiplier)
            print(f"[DEBUG] Player vulnerável. x{multiplier} → {damage}")

        return max(0, damage)

    # ------------------------------------------------------------
    # Aplicação contínua de efeitos (Nenhuma alteração necessária)
    # ------------------------------------------------------------
    def apply_status_effects(self, targets=None):
        """
        Aplica efeitos contínuos e reduz duração. 
        Usado a cada início de turno inimigo e tick de jogador.
        """
        if targets is None:
            # Aplica tanto no jogador quanto nos inimigos
            targets = [self.battle_manager.game.player] + list(self.battle_manager.enemies)

        for target in targets:
            print(f"[DEBUG] Aplicando efeitos em {getattr(target, 'name', 'Player')}")
            expired_effects = []

            for status_name, data in list(target.status_effects.items()):
                if status_name in self.STATUS_EFFECTS:
                    self.STATUS_EFFECTS[status_name](target, data)

                # Reduz duração (1 por turno)
                if "duration" in data:
                    data["duration"] -= 1
                    print(f"[DEBUG] {status_name} duração restante: {data['duration']}")
                    if data["duration"] <= 0:
                        expired_effects.append(status_name)

            # Remove efeitos expirados
            for status_name in expired_effects:
                print(f"[DEBUG] Removendo status expirado: {status_name}")
                target.remove_status(status_name)

    def apply_status_to_target(self, target, status_name, **kwargs):
        """Aplica um efeito de status a um alvo."""
        print(f"[DEBUG] Aplicando status {status_name} em {getattr(target, 'name', 'Player')} → {kwargs}")
        if hasattr(target, "add_status"):
            target.add_status(status_name, **kwargs)

    # ------------------------------------------------------------
    # Implementação dos efeitos (Nenhuma alteração necessária)
    # ------------------------------------------------------------
    def _apply_poison(self, target, data):
        """Veneno → dano periódico."""
        damage = data.get("damage", data.get("power", 1))
        print(f"[DEBUG] Veneno em {getattr(target, 'name', 'Player')}: {damage} de dano")

        target.take_damage(damage)
        if hasattr(self.battle_manager, "animation_manager"):
            self.battle_manager.animation_manager.spawn_damage_animation(
                target, damage, is_player=getattr(target, "is_player", False)
            )

    def _apply_regeneration(self, target, data):
        """Regeneração → cura periódica."""
        heal = data.get("heal", data.get("power", 2))
        print(f"[DEBUG] Regeneração em {getattr(target, 'name', 'Player')}: +{heal} HP")
        target.heal(heal)

    def _apply_strength(self, target, data):
        """Força → buff de dano."""
        print(f"[DEBUG] Força ativa (+{data.get('power', 0)}) em {getattr(target, 'name', 'Player')}")

    def _apply_weakness(self, target, data):
        """Fraqueza → debuff de dano."""
        print(f"[DEBUG] Fraqueza ativa (x{data.get('multiplier', 0.75)}) em {getattr(target, 'name', 'Player')}")

    def _apply_vulnerability(self, target, data):
        """Vulnerabilidade → recebe mais dano."""
        print(f"[DEBUG] Vulnerabilidade ativa (x{data.get('multiplier', 1.5)}) em {getattr(target, 'name', 'Player')}")

    def _apply_dodge(self, target, data):
        """Esquiva → chance de evitar dano."""
        chance = data.get("chance", 0.2)
        print(f"[DEBUG] Esquiva ativa ({chance*100:.0f}%) em {getattr(target, 'name', 'Player')}")

    def _apply_generic_buff(self, target, data):
        """Buff genérico → trata como força."""
        print(f"[DEBUG] Buff genérico convertido para FORÇA em {getattr(target, 'name', 'Player')}")
        if not target.has_status("força"):
            target.add_status("força", power=data.get("power", 1), duration=data.get("duration", 2))

    def _apply_generic_debuff(self, target, data):
        """Debuff genérico → trata como vulnerabilidade."""
        print(f"[DEBUG] Debuff genérico convertido para VULNERABILIDADE em {getattr(target, 'name', 'Player')}")
        if not target.has_status("vulnerabilidade"):
            target.add_status("vulnerabilidade", multiplier=data.get("multiplier", 1.5), duration=data.get("duration", 2))