
class FarmBase():
    
    logfile = None
    def clog(self, s):
        m = "[{}]: {}".format(self, s)
        print(m)


    # Consdier testing for board name here as well --
    def log(self, s):

        if not isinstance(s, str):
            s = str(s)

        # If there IS a logfile, we don't need the prefix
        if self.logfile:
            m = s.encode('ascii')
            self.logfile.write('\n'.encode('ascii'))
            self.logfile.write(m)
            self.logfile.flush()
        else:
            self.clog(s)

    def err(self, s):
        self.log(s)
        raise RuntimeError(s)


