from ..testbase import TestBase


class StockSensorsTest(TestBase):
    def __init__(self, board):
        super().__init__(board)

    def test_body(self):
        # TODO: Add check that board has command sensors (from lm-sensors), with json option
        self.data['sensors'] = self.board.console.get_json_data('sensors -j')
