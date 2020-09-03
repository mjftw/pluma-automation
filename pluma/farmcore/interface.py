from pyroute2 import IPRoute


class NetInterface():
    def __init__(self, interface):
        self.interface = interface

    @property
    def ip_address(self):
        with IPRoute() as ipr:
            index = ipr.link_lookup(ifname=self.interface)[0]
            try:
                ip_addr = ipr.get_addr(index=index)[0].get_attrs('IFA_ADDRESS')[0]
            except IndexError:
                return None

            return ip_addr or None

    def up(self):
        with IPRoute() as ipr:
            index = ipr.link_lookup(ifname=self.interface)[0]
            ipr.link('set', index=index, state='up')

    def down(self):
        with IPRoute() as ipr:
            index = ipr.link_lookup(ifname=self.interface)[0]
            ipr.link('set', index=index, state='down')

    def set_ip_address(self, ip_address):
        with IPRoute() as ipr:
            index = ipr.link_lookup(ifname=self.interface)[0]
            ipr.flush_addr(index=index)
            ipr.addr('add', index, address=ip_address, mask=24)
