class Hierarchy():
    """ This class is inherited in order add Hierarchy to a class """

    def __init__(self):
        if isinstance(self, Hierarchy):
            raise AttributeError(
                'This is a base class, and must be inherited')

    @property
    def _recurse_hier(self):
        if hasattr(self, "__recurse_hier"):
            return self.__recurse_hier
        else:
            return False

    @_recurse_hier.setter
    def _recurse_hier(self, _recurse_hier):
        self.__recurse_hier = _recurse_hier
        self._children_set_attr("_recurse_hier", _recurse_hier)

    def _get_hier(self):
        children = {}
        attrs = {}
        for m in dir(self):
            member = getattr(self, m)
            if isinstance(member, Hierarchy):
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

    def show_hier(self, indent_level=1, indent_size=4, recurse=True, exclude=None):
        """ Return string containing all local vars, and get children to do the same """
        exclude = exclude or []
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
            if recurse:
                hier_str += children[key].show_hier(
                    indent_level=indent_level+1,
                    indent_size=indent_size,
                    recurse=recurse,
                    exclude=exclude
                )
            else:
                hier_str += ("-"*indent_level*indent_size +
                             "{}: {}\n".format(key, type(children[key]).__name__))

        return hier_str

# TODO: Not sure this is working. Check & Fix.


def hier_setter(f):
    def wrapper(*args):
        f(*args)
        self = args[0]
        if isinstance(self, Hierarchy):
            if self._recurse_hier:
                self._children_set_attr(
                    f.__name__, getattr(self, f.__name__))
    return wrapper
