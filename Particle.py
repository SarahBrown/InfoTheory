# class to store particle information
class Particle():
    def __init__(self, pos_x, pos_y, theta, weight):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.theta = theta
        self.weight = weight
        self.r = None

    def __str__(self):
        return f"{self.pos_x}, {self.pos_y}, {self.theta}"
