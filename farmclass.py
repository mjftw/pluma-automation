class Farmclass():
    """ Contains functionality common to all farm objects """
    def log(self, message):
        print(message)

    def show_hier(self, indent_level=0, indent_size=4):
        """ Print all local vars, and get child farm objects to do the same """
        farmobjs = {}
        attrs = {}
        for m in dir(self):
            member = getattr(self, m)
            if isinstance(member, Farmclass):
                farmobjs[m] = member
            elif(not m.startswith("_") and
                    not callable(member)):
                attrs[m] = member
        for key in attrs:
            print("-"*indent_level*indent_size +
                  " {}: {}".format(key, attrs[key]))
        for key in farmobjs:
            print("-"*(indent_level*indent_size - 1) +
                  "| {} : {}".format(key, farmobjs[key]))
            farmobjs[key].show_hier(indent_level + 1, indent_size)
