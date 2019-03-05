from math import sqrt

# Do I really need to put some docstring for this?
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

# Do I really need to put some docstring for this?
class Rect:
    def __init__(self, x, y, w, h, size_x, size_y):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        # Because this will be easier to use
        self.top = y
        self.left = x
        self.bottom = y+h
        self.right = x+w

        self.top_left = Point(self.left, self.top)
        self.top_right = Point(self.right, self.top)
        self.bottom_right = Point(self.right, self.bottom)
        self.bottom_left = Point(self.left, self.bottom)



        # Pixels values (true value for the window)
        self.pv_x = x * size_x
        self.pv_y = y * size_y
        self.pv_w = w * size_x
        self.pv_h = h * size_y

        self.pv_top = self.pv_y
        self.pv_left = self.pv_x
        self.pv_bottom = self.pv_y + self.pv_h
        self.pv_right = self.pv_x + self.pv_w

        self.pv_top_left = Point(self.pv_left, self.pv_top)
        self.top_right = Point(self.pv_right, self.pv_top)
        self.bottom_right = Point(self.pv_right, self.pv_bottom)
        self.pv_top_left = Point(self.pv_left, self.pv_top)



    def inside(self, pt):
        return pt.x > self.x and pt.x < self.x + self.w and pt.y > self.y and pt.y < self.y + self.h

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

