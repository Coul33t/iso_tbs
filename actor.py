from constants import ACTIVE_COLOR

class Stats:
    def __init__(self, strength=1, agility=1, intel=1, strength_growth=0.33, agility_growth=0.33, intel_growth=0.33):
        self.strength = strength
        self.agility = agility
        self.intel = intel

        self.strength_growth = strength_growth
        self.agility_growth = agility_growth
        self.intel_growth = intel_growth

        self.hp = round(strength * 2 + agility * 1.5 + intel * 0.5)
        self.defence = round(strength * 0.15 + agility * 0.2 + intel * 0.05)

class Actor:
    def __init__(self, name, charac, team, facing, color='blue', x=0, y=0, movement=3, stats=None, main_attribute='None'):
        self.name = name
        self.charac = charac
        self.team = team
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

        self.main_attribute = main_attribute

        self.xp = 0
        self.next_level = 100

    def __str__(self):
        return_string = f'Name : {self.name} -> {self.charac}\n'
        return_string += f'Level: {self.level}\n'
        return_string += f'Current xp: {self.xp}\n'
        return_string += f'XP to next level: {self.next_level - self.xp}\n'
        return_string += f'Movement: up to {self.movement} tiles\n'

        return_string += '\nStats:\n'
        for stat, value in vars(self.stats).items():
            return_string += f'{stat} : {value}\n'

        return return_string

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

    def end_turn(self):
        self.color = self.perma_color

    def new_turn(self):
        self.color = ACTIVE_COLOR
        self.movement_left = self.movement
        self.has_attacked = False

    def attack(self, other_actor):

        if self.has_attacked:
            return f'The {self.name} already attacked during this turn.'

        self.has_attacked = True

        damage = round(self.stats.strength - other_actor.stats.defence)

        if self.main_attribute != 'None':
            damage += self.stats[self.main_attribute]

        if damage > 0:
            other_actor.stats.hp -= damage

            if other_actor.stats.hp <= 0:
                other_actor.die()

            return f'The {self.name} did {damage} damage to the {other_actor.name}!'

        return f'The {self.name} did non damage to the {other_actor.name}.'

    def die(self):
        self.charac = '%'
        self.name = 'Dead ' + self.name
        self.dead = True
        self.blocks = False
