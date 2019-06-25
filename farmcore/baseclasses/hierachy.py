class Hierachy():
    """ This class is inherited in order add hierachy to a class """

    def __init__(self):
        if type(self) is Hierachy:
            raise AttributeError(
                'This is a base class, and must be inherited')

    @property
    def _reccurse_hier(self):
        if hasattr(self, "__reccurse_hier"):
            return self.__reccurse_hier
        else:
            return False

    @_reccurse_hier.setter
    def _reccurse_hier(self, _reccurse_hier):
        self.__reccurse_hier = _reccurse_hier
        self._children_set_attr("_reccurse_hier", _reccurse_hier)

    def _get_hier(self):
        children = {}
        attrs = {}
        for m in dir(self):
            member = getattr(self, m)
            if isinstance(member, Hierachy):
                children[m] = member
            elif(not m.startswith("_") and
                    not callable(member)):
                attrs[m] = member
        return children, attrs

    def _children_set_attr(self, attr, value):
        children, __ = self._get_hier()
        for key in children:
            child = children[key]
            setattr(child, attr, value)
            child._children_set_attr(attr, value)

    def show_hier(self, indent_level=1, indent_size=4, reccurse=True,
            exclude=[]):
        """ Return string containing all local vars, and get children to do the same """
        children = {}
        attrs = {}
        hier_str = ''

        if(indent_level > 0):
            type_indent_level = indent_level - 1
        else:
            type_indent_level = indent_level

        hier_str += ("-"*type_indent_level*indent_size +
            "{}:\n".format(type(self).__name__))

        children, attrs = self._get_hier()

        exclude_children = []
        for k in children:
            if children[k] in exclude:
                attrs[k] = '(Circular reference hidden)'
                exclude_children.append(k)

        for k in exclude_children:
            del children[k]

        exclude.append(self)

        for key in attrs:
            hier_str += ("-"*indent_level*indent_size +
                  "{}: {}\n".format(key, attrs[key]))
        for key in children:
            if reccurse:
                hier_str += children[key].show_hier(
                    indent_level=indent_level+1,
                    indent_size=indent_size,
                    reccurse=reccurse,
                    exclude=exclude
                )
            else:
                hier_str += ("-"*indent_level*indent_size +
                    "{}: {}\n".format(key, type(children[key]).__name__))

        return hier_str

#TODO: Not sure this is working. Check & Fix.
def hier_setter(f):
    def wrapper(*args):
        f(*args)
        self = args[0]
        if isinstance(self, Hierachy):
            if self._reccurse_hier:
                self._children_set_attr(
                    f.__name__, getattr(self, f.__name__))
    return wrapper
