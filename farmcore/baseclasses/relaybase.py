from .farmclass import Farmclass


class RelayBase(Farmclass):
    def toggle(self, port, throw):
        raise NotImplimentedError(
            'This method must be implimented by inheriting class')

    def __bool__(self):
        ''' Base class is falsey. Must inherit'''
        return True if type(self) is not RelayBase else False