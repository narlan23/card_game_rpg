from enum import Enum

class BattleState(Enum):
    PLAYER_TURN = 1
    ANIMATING = 2
    ENEMY_TURN = 3
    VICTORY = 4
    DEFEAT = 5