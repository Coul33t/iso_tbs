class Item:
    def __init__(self, name, weapon=None, armor=None, consumable=None):
        self.name = name
        self.weapon = weapon
        self.armor = armor
        self.consumable = consumable

    def get_mods(self):
        if self.weapon:
            return self.weapon.mods
        elif self.armor:
            return self.armor.mods
        return {}