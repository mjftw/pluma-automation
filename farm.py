from farmclass import Farmclass


class Farm(Farmclass):
    def __init__(self, boards):
        self.boards = boards

    def __repr__(self):
        return "Farm: {}".format(self.boards)

    def board_info(self):
        for b in self.boards:
            ud = b.hub.usb
            print("\n =============== Device [{} - {}] =============".format(
                ud.device, b.name))
            ud.show_info()
