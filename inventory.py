class Inventory:
    def __init__(self, size=5):
        self.size = size
        self.contents = []

    def add(self, item_to_add):
        if len(self.contents) < self.size:
            self.contents.append(item_to_add)
            self.owner.recompute_mods()
        else:
            return f'Inventory full!'