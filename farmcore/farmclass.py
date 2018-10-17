import datetime
import os

DEFAULT_LOG_TIMEFORMAT = "%y-%m-%d %H:%M:%S"
class Farmclass():
    """ Contains functionality common to all farm objects """

    def __repr__(self):
        return self.show_hier(reccurse=False)

    @property
    def log_on(self):
        if hasattr(self, "_log_on"):
            return self._log_on
        else:
            return False

    @log_on.setter
    def log_on(self, log_on):
        self._log_on = log_on
        if self.log_reccurse:
            self._children_set_attr("log_on", log_on)

    @property
    def log_name(self):
        if hasattr(self, "_log_name"):
            return self._log_name
        else:
            return None

    @log_name.setter
    def log_name(self, log_name):
        self._log_name = log_name
        if self.log_reccurse:
            self._children_set_attr("log_name", log_name)

    @property
    def log_time(self):
        if hasattr(self, "_log_time"):
            return self._log_time
        else:
            return False

    @log_time.setter
    def log_time(self, log_time):
        self._log_time = log_time
        if self.log_reccurse:
            self._children_set_attr("log_time", log_time)

    @property
    def log_file(self):
        if hasattr(self, "_log_file"):
            return self._log_file
        else:
            return None

    @log_file.setter
    def log_file(self, log_file):
        self._log_file = log_file
        if self.log_reccurse:
            self._children_set_attr("log_file", log_file)

    @property
    def log_echo(self):
        if hasattr(self, "_log_echo"):
            return self._log_echo
        else:
            return False

    @log_echo.setter
    def log_echo(self, log_echo):
        self._log_echo = log_echo
        if self.log_reccurse:
            self._children_set_attr("log_echo", log_echo)

    @property
    def log_hier_path(self):
        if hasattr(self, "_log_hier_path"):
            return self._log_hier_path
        else:
            return False

    @log_hier_path.setter
    def log_hier_path(self, log_hier_path):
        if log_hier_path:
            if isinstance(log_hier_path, bool):
                self._log_hier_path = '{}'.format(type(self).__name__)
            else:
                self._log_hier_path = '{}.{}'.format(
                        log_hier_path, type(self).__name__)
        else:
            self._log_hier_path = False

        if self.log_reccurse:
            self._children_set_attr("log_hier_path", self.log_hier_path)

    @property
    def log_reccurse(self):
        if hasattr(self, "_log_reccurse"):
            return self._log_reccurse
        else:
            return False

    @log_reccurse.setter
    def log_reccurse(self, log_reccurse):
        self._log_reccurse = log_reccurse
        self._children_set_attr("log_reccurse", log_reccurse)

    def log(self, message):
        prefix = ''
        if self.log_on:
            if self.log_hier_path:
                prefix = '[{}]{}'.format(self.log_hier_path, prefix)
            if self.log_name:
                prefix = '{}{}'.format(self.log_name, prefix)
            if self.log_time:
                timestr = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
                prefix = '{} {}'.format(timestr, prefix)
            if prefix:
                message = '{}: {}'.format(prefix, message)
            if self.log_file:
                logdir = os.path.dirname(self.log_file)
                if logdir and not os.path.exists(logdir):
                    os.makedirs(logdir)
                with open(self.log_file, 'a') as logfd:
                    logfd.write(message + '\n')
            if self.log_echo:
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

    def _children_set_attr(self, attr, value):
        farmobjs, __ = self._get_hier()
        for key in farmobjs:
            child = farmobjs[key]
            setattr(child, attr, value)
            child._children_set_attr(attr, value)

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
