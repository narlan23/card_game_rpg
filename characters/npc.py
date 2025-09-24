
class NPC:
    def __init__(self, nome, rect, dialogo_data):
        self.nome = nome
        self.rect = rect
        self.dialogo_data = dialogo_data  # dados do diálogo desse NPC

    def interagir(self, dialogo_manager):
        """Chama o diálogo do NPC"""
        dialogo_manager.abrir(
            self.dialogo_data["texto"],
            self.dialogo_data.get("opcoes"),
            self.dialogo_data.get("callbacks"),
            self.dialogo_data.get("layout", "horizontal")
        )
