import math
from pluma.test.testbase import TestBase


class Maths(TestBase):
    def __init__(self, board, x):
        TestBase.__init__(self, board)
        self.x = x

    def prepare(self):
        self.save_data({
            'x_square': math.pow(self.x, 2),
            'sqrt_x': math.sqrt(self.x),
            'sin_x': round(math.sin(math.radians(self.x)), 2),
            'cos_x': round(math.cos(math.radians(self.x)), 2),
            'mystring': 'Hello'
        })