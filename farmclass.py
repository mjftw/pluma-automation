class Farmclass():
    """ Contains functionality common to all farm objects """

    def log(self, message):
        print(message)

    def __repr__(self):
        return self.show_hier(reccurse=False)

    def _get_hier(self):
        farmobjs = {}
        attrs = {}
        for m in dir(self):
            member = getattr(self, m)
            if isinstance(member, Farmclass):
                farmobjs[m] = member
            elif(not m.startswith("_") and
                    not callable(member)):
                attrs[m] = member
        return farmobjs, attrs

    def show_hier(self, indent_level=1, indent_size=4, reccurse=True):
        """ Print all local vars, and get child farm objects to do the same """
        farmobjs = {}
        attrs = {}
        hier_str = ''

        if(indent_level > 0):
            type_indent_level = indent_level - 1
        else:
            type_indent_level = indent_level

        hier_str += ("-"*type_indent_level*indent_size +
            "{}:\n".format(type(self).__name__))

        farmobjs, attrs = self._get_hier()

        for key in attrs:
            hier_str += ("-"*indent_level*indent_size +
                  "{}: {}\n".format(key, attrs[key]))
        for key in farmobjs:
            if reccurse:
                hier_str += farmobjs[key].show_hier(indent_level + 1, indent_size)
            else:
                hier_str += ("-"*indent_level*indent_size +
              "{}: {}\n".format(key, type(farmobjs[key]).__name__))

        return hier_str
