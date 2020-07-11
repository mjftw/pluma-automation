from farmtest import TestBase


class EmptyTest(TestBase):
    def __init__(self, board, parameters={}):
        super().__init__(self)

    def test_body(self):
        print(self.board)


class TestBoot1(TestBase):
    def __init__(self, board, parameters={}):
        super().__init__(self)

    def test_body(self):
        print(self.board)


class TestBoot2(TestBase):
    def __init__(self, board, parameters={}):
        super().__init__(self)

    def test_body(self):
        pass
