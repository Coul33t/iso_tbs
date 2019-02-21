from constants import ACTIVE_COLOR, ABBR
from stats import Stats
from inventory import Inventory

class Actor:
    def __init__(self, name, charac, team, sprite=None, color='blue', x=0, y=0, movement=3, stats=None, inventory=None):
        self.name = name
        self.charac = charac
        self.team = team

        self.sprite = sprite

        self.color = color
        self.perma_color = color
        self.x = x
        self.y = y

        self.level = 1

        self.has_played = False

        self.movement = movement
        self.movement_left = movement

        self.has_attacked = False

        self.dead = False

        self.blocks = True

        self.stats = stats
        if not stats:
            self.stats = Stats()

        self.xp = 0
        self.next_level = 100

        self.inventory = inventory
        if not inventory:
            self.inventory = Inventory()
        self.inventory.owner = self

    def __str__(self):
        return_string = f'Name : {self.name} -> {self.charac}\n'
        return_string += f'Level: {self.level}\n'
        return_string += f'Current xp: {self.xp}\n'
        return_string += f'XP to next level: {self.next_level - self.xp}\n'
        return_string += f'Movement: up to {self.movement} tiles\n'

        # Broken rn because of Stats changes
        # return_string += '\nStats:\n'
        # for stat, value in vars(self.stats).items():
        #     return_string += f'{stat} : {value}\n'

        return return_string


    def recompute_mods(self):
        mods = {'damage': 0, 'defence': 0}
        for item in self.inventory:
            for stat, mod in item.get_mods():
                if stat in mods:
                    mods[stat] += mod
                else:
                    mods[stat] = mod
            if item.weapon:
                mods['damage'] += item.weapon.damage

            if item.amor:
                mods['defence'] += item.armor.defence

        for stat, mod in mods.items():
            self.stats.mod[stat] = self.stats.base[stat] + mod

        self.stats.mod['damage'] = self.stats.mod['damage'] + mods['damage']
        self.stats.mod['defence'] = self.stats.mod['defence'] + mods['defence']

    def check_level(self):
        if self.xp >= self.next_level:
            # xp growth: u(n) = u(n-1) + 50 * (n-1)
            self.level += 1
            self.xp = self.xp - self.next_level
            self.next_level = self.next_level + 50 * (self.level - 1)

            # If we take multiples level
            while self.xp >= self.next_level:
                self.level += 1
                self.xp = self.xp - self.next_level
                self.next_level = self.next_level + 50 * (self.level - 1)

    def check_end(self):
        if self.movement_left == 0 and self.has_attacked:
            self.has_played = True


    def end_turn(self):
        self.color = self.perma_color
        self.has_played = True

    def new_turn(self):
        self.color = ACTIVE_COLOR
        self.movement_left = self.movement
        self.has_attacked = False
        self.has_played = False

    def attack(self, other_actor):

        if self.has_attacked:
            return f'The {self.name} already attacked during this turn.'

        self.has_attacked = True

        damage = self.stats.mod['damage']

        if damage > 0:
            other_actor.stats.mod['hp'] -= damage

            if other_actor.stats.mod['hp'] <= 0:
                other_actor.die()

            return f'The {self.name} did {damage} damage to the {other_actor.name}!'

        return f'The {self.name} did non damage to the {other_actor.name}.'

    def die(self):
        self.charac = '%'
        self.name = 'Dead ' + self.name
        self.dead = True
        self.blocks = False
