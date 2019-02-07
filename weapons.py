class Weapon:
    def __init__(self, damage, w_range, mods={}):
        self.damage = damage
        self.w_range = w_range
        self.mods = mods