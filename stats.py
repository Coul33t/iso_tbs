from math import ceil

class Stats:
    def __init__(self, strength=1, agility=1, intel=1, main_attribute=None, strength_growth=0.33, agility_growth=0.33, intel_growth=0.33):
        self.base = {}
        self.base['strength'] = strength
        self.base['agility'] = agility
        self.base['intel'] = intel

        self.mod = {}
        self.mod['strength'] = strength
        self.mod['agility'] = agility
        self.mod['intel'] = intel

        self.main_attribute = main_attribute

        self.growth = {}
        self.growth['strength'] = strength_growth
        self.growth['agility'] = agility_growth
        self.growth['intel'] = intel_growth

        self.base['hp'] = round(strength * 2 + agility * 1 + intel * 0.5)
        self.base['max_hp'] = self.base['hp']

        self.base['defence'] = round(strength * 0.15 + agility * 0.2 + intel * 0.05)

        self.mod['hp'] = self.base['hp']
        self.mod['max_hp'] = self.base['max_hp']

        self.mod['defence'] = self.base['defence']

        self.base['damage'] = self.base[self.main_attribute] if self.main_attribute else ceil(self.base['strength'] / 3)
        self.mod['damage'] = self.base['damage']

        self.base['range'] = 1
        self.mod['range'] = self.base['range']