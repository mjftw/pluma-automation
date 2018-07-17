class Farmclass():
    """ Contains functionality common to all farm objects """

    def log(self, message):
        print(message)

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

    def show_hier(self, indent_level=1, indent_size=4):
        """ Print all local vars, and get child farm objects to do the same """
        farmobjs = {}
        attrs = {}

        if(indent_level > 0):
            type_indent_level = indent_level - 1
        else:
            type_indent_level = indent_level

        print("-"*type_indent_level*indent_size +
              "{}:".format(type(self).__name__))

        farmobjs, attrs = self._get_hier()

        for key in attrs:
            print("-"*indent_level*indent_size +
                  "{}: {}".format(key, attrs[key]))
        for key in farmobjs:
            farmobjs[key].show_hier(indent_level + 1, indent_size)
