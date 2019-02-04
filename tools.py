from math import sqrt

# Do I really need to put some docstring for this?
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

# Euclidean distance
def dst_euc(p1, p2=Point(0,0)):
    return sqrt(pow(p2.x - p1.x, 2) + pow(p2.y - p1.y, 2))

# Manhattan distance
def dst_man(p1, p2=Point(0,0)):
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)

def point_in(ptn, lst):
    for other_ptn in lst:
        if ptn.x == other_ptn.x and ptn.y == other_ptn.y:
            return True

    return False