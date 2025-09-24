class StatusManager:
    def __init__(self, battle_manager):
        self.battle_manager = battle_manager

    def calculate_player_damage(self, base_damage, card=None):
        """Calcula dano considerando status do jogador."""
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
        """Calcula dano recebido considerando status."""
        damage = base_damage
        
        if self.battle_manager.game.player.has_status("vulnerabilidade"):
            multiplier = self.battle_manager.game.player.status_effects["vulnerabilidade"].get("multiplier", 1.5)
            damage = int(damage * multiplier)
        
        return damage

    def apply_status_effects(self):
        """Aplica efeitos de status que acontecem automaticamente."""
        player = self.battle_manager.game.player
        
        if player.has_status("veneno"):
            poison_data = player.status_effects["veneno"]
            damage = poison_data.get("damage", 1)
            player.take_damage(damage)
            self.battle_manager.animation_manager.spawn_damage_animation(player, damage, is_player=True)

        if player.has_status("regeneração"):
            regen_data = player.status_effects["regeneração"]
            heal_amount = regen_data.get("heal", 2)
            player.heal(heal_amount)

    def apply_status_to_target(self, target, status_name, **kwargs):
        """Aplica status a um alvo (jogador ou inimigo)."""
        if hasattr(target, 'add_status'):
            target.add_status(status_name, **kwargs)
            self.battle_manager.animation_manager.spawn_status_animation(target, status_name)