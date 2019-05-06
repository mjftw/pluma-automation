from ..baseclasses import Farmclass


class FarmobjMock(Farmclass):
    def __init__(self, children=None):
        self.num_children = 0
        if isinstance(children, list):
            for child in children:
                self.add_child(child)
        if isinstance(children, Farmclass):
            self.add_child(children)

    def add_child(self, child):
        setattr(self, "child_{}".format(self.num_children), child)
        self.num_children += 1
