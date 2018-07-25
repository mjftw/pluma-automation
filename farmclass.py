import datetime
import os


class Farmclass():
    """ Contains functionality common to all farm objects """

    def __repr__(self):
        return self.show_hier(reccurse=False)

    def log(self, message):
        prefix = ''
        if hasattr(self, '_appendtype') and self._appendtype:
            prefix = '[{}]{}'.format(self._appendtype, prefix)
        if hasattr(self, 'logname') and self.logname:
            prefix = '{}{}'.format(self.logname, prefix)
        if hasattr(self, '_logtime') and self._logtime:
            timestr = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
            prefix = '{} {}'.format(timestr, prefix)
        if prefix != '':
            message = '{}: {}'.format(prefix, message)
        if hasattr(self, 'logfile') and self.logfile:
            logdir = os.path.dirname(self.logfile)
            if not os.path.exists(logdir):
                os.makedirs(logdir)
            with open(self.logfile, 'a') as logfd:
                logfd.write(message + '\n')
        else:
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

    def set_logger(self, logname=None, logfile=None,
                   appendtype=None, logtime=False, reccurse=False):
        self.logfile = logfile
        self.logname = logname
        self._logtime = logtime
        if appendtype:
            if isinstance(appendtype, bool):
                self._appendtype = '{}'.format(type(self).__name__)
            else:
                self._appendtype = '{}.{}'.format(
                        appendtype, type(self).__name__)

        if reccurse:
            farmobjs, __ = self._get_hier()
            for key in farmobjs:
                farmobjs[key].set_logger(
                    logname=self.logname,
                    logfile=logfile,
                    appendtype=self._appendtype,
                    logtime=self._logtime,
                    reccurse=reccurse,
                )

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
                hier_str += farmobjs[key].show_hier(
                    indent_level=indent_level+1,
                    indent_size=indent_size,
                    reccurse=reccurse)
            else:
                hier_str += ("-"*indent_level*indent_size +
                    "{}: {}\n".format(key, type(farmobjs[key]).__name__))

        return hier_str
