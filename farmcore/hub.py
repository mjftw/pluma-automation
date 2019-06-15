import re
from graphviz import Digraph

from .baseclasses import Farmclass
from .usb import USB, puctx


class Hub(Farmclass, USB):
    def __init__(self, usb_device):
        USB.__init__(self, usb_device)

    @property
    def devinfo(self):
        return self._pack_devinfo(self.get_device())

    @property
    def downstream(self):
        infolist = []

        downstream_devs = puctx.list_devices(
            parent=self.get_device())

        for dev in downstream_devs:
            info = self._pack_devinfo(dev)
            if info:
                infolist.append(self._pack_devinfo(dev))

        return infolist

    def _pack_devinfo(self, device):
        devinfo = {}

        path = device.device_path.split('/')
        if self.usb_device not in path:
            return {}

        devinfo['usbpath'] = None
        for p in path[path.index(self.usb_device):]:
            devpath = re.match(pattern='[0-9\-\.]{'+f'{len(p)}'+'}', string=p)
            if devpath:
                devinfo['usbpath'] = devpath.string
            elif devinfo['usbpath']:
                break

        if not devinfo['usbpath']:
            return {}

        devinfo['devnode'] = device.device_node
        devinfo['subsystem'] = device.subsystem
        devinfo['vendor'] = device.get('ID_VENDOR')
        devinfo['vendor_long'] = device.get('ID_VENDOR_FROM_DATABASE')
        devinfo['major'] = device.get('MAJOR')
        devinfo['minor'] = device.get('MINOR')
        devinfo['serial'] = device.get('ID_SERIAL_SHORT')
        devinfo['model'] = device.get('ID_MODEL')
        devinfo['pid'] = device.get('ID_MODEL_ID')
        devinfo['vid'] = device.get('ID_VENDOR_ID')

        devinfo['devtype'] = device.get('DEVTYPE')
        if(devinfo['devtype'] == 'disk' or
           devinfo['devtype'] == 'partition'):
            devinfo['size'] = int(device.attributes.get('size'))

        return devinfo

    def filter_downstream(self, filters={}, excludes={}):
        return self._filter_dictarr(
            filters=filters, excludes=excludes, dictarr=self.downstream)

    def _filter_dictarr(self, filters={}, excludes={}, dictarr=[{}]):
        match_vals = []
        for d in dictarr:
            match = True
            # Check match list.
            # If the dict array queried DOES NOT HAVE the required
            # field, OR the field HAS A DIFFERENT value, do not match
            for k, v in filters.items():
                if not match:
                    break
                if k not in d or d[k] != v:
                    match = False

            # Check exclude list
            # If the dict array queried HAS the required filed AND
            # the field has the SAME VALUE, do not match
            for k, v in excludes.items():
                if not match:
                    break
                if k in d and d[k] == v:
                    match = False

            if match:
                match_vals.append(d)

        return match_vals

    def plot_downstream(self, image_file=None, image_format=None):
        image_format = image_format or 'x11'
        fileless_formats = ['xlib', 'x11']

        if not image_file and image_format not in fileless_formats:
            raise AttributeError(
                f'Must supply image_file if format is not one of {fileless_formats}')

        devices = {
            'Hub': self.get_hub(index=None),
            'Serial': self.get_serial(index=None),
            'Relay': self.get_relay(index=None),
            'Block': self.get_block(index=None),
            'Partition': self.get_part(index=None),
            'Ethernet': self.get_ethernet(index=None),
            'SD-Wire': self.get_sdwire(index=None),
            'Unknown-Device': self.get_misc_devices(index=None)
        }

        # Graphivz attributes can be found at:
        #   https://www.graphviz.org/doc/info/attrs.html
        # Colour names:
        #   https://www.graphviz.org/doc/info/colors.html
        node_attrs = {
            'Hub': {'fillcolor': 'deepskyblue'},
            'Serial': {'fillcolor': 'darkseagreen'},
            'Relay': {'fillcolor': 'cadetblue'},
            'Block': {'fillcolor': 'darkorange'},
            'Partition': {'fillcolor': 'firebrick1'},
            'Ethernet': {'fillcolor': 'chartreuse3'},
            'SD-Wire': {'fillcolor': 'gold'},
            'Unknown-Device': {}
        }
        node_default_attrs = {'style': 'filled,solid'}

        graph_attrs = {
            'splines': 'curved'
        }
        edge_attrs = {}

        dot = Digraph(
            format=image_format,
            comment=f'Root Hub[{self.usb_device}] downstream devices',
            graph_attr=graph_attrs)

        class DeviceNode():
            def __init__(self, device, devtype, index,
                    parent=None, linelabel=None, extra_info=None):
                self.device = device
                self.devtype = devtype
                self.index = index
                self.parent = parent
                self.linelabel = linelabel
                self.extra_info = extra_info

            @property
            def vendor(self):
                return self.device["vendor_long"] or self.device["vendor"]

            @property
            def devpath(self):
                return self.device['usbpath']

            @property
            def devpathlist(self):
                return self.devpath.split('.')

            @property
            def prefix(self):
                return self.devtype

            @property
            def devname(self):
                return f'{self.prefix}{self.index}'

            @property
            def devlabel(self):
                devlabel = f'[{self.devpath}]\n{self.devtype}{self.index}'

                if self.device['devnode'] and self.device['devnode'].startswith('/dev'):
                    devlabel += f' - {self.device["devnode"]}'

                devlabel += f'\n{self.vendor}\n{self.device["model"]}'

                if self.extra_info:
                    devlabel += f'\n{self.extra_info}'
                return devlabel

        def build_device_nodes(devices):
            # Build device info
            nodes = []
            for devtype in devices:
                for i, device in enumerate(
                        [d for d in devices[devtype] if devices[devtype]]):

                    node = DeviceNode(device, devtype, i, self.usb_device)

                    if devtype == 'Block' or devtype == 'Partition':
                        node.extra_info = f'Size: {node.device["size"]}B'

                    nodes.append(node)

            return nodes

        def plot_device_nodes(nodes):
            # Build tree from device info
            nodes.sort(key=lambda x: x.devpath)
            for node in nodes:
                dot.node(node.devname, node.devlabel,
                    {**node_default_attrs, **node_attrs.get(node.devtype, {})})

                node.parent = None
                # Connect partitions to block devices
                if not node.parent and node.devtype == 'Partition':
                    filtered_nodes = [n for n in nodes
                        if n != node and
                            n.devtype == 'Block' and
                            n.devpath == node.devpath]

                    if filtered_nodes:
                        node.parent = filtered_nodes[0]

                        devnode = node.device['devnode']
                        pdevnode = node.parent.device['devnode']
                        part_num = devnode[pdevnode.find(devnode):]

                        node.linelabel = f'Partition {part_num}'

                # Connect block devices to SDWires
                if not node.parent and node.devtype == 'Block':
                    filtered_nodes = [n for n in nodes
                        if n != node and
                            n.devtype == 'SD-Wire' and
                            n.devpathlist[:-1] == node.devpathlist[:-1]]

                    if filtered_nodes:
                        node.parent = filtered_nodes[0]

                # Connect device nodes to parent hubs
                if not node.parent:
                    # Find upstream hubs
                    filtered_nodes = [n for n in nodes
                        if n != node and
                            n.devtype == 'Hub' and
                            node.devpath.startswith(n.devpath)]

                    if filtered_nodes:
                        # Find node.parent hub (hub with longest matching path)
                        filtered_nodes.sort(key=lambda x: len(x.devpathlist), reverse=True)
                        node.parent = filtered_nodes[0]

                        path = node.devpath
                        ppath = node.parent.devpath
                        port = path[ppath.find(path):]

                        node.linelabel = f'Port {port}'


                if node.parent:
                    dot.edge(node.parent.devname, node.devname,
                        label=node.linelabel, **edge_attrs)

            return dot


        nodes = build_device_nodes(devices)
        dot = plot_device_nodes(nodes)
        dot.render(image_file)

        return dot.source

    def _filter_devinfo(self, devinfo, key, index):
        filtered = None

        if devinfo:
            if len(devinfo) > 1:
                # Sort devinfo list by USB path, this corresponds to
                #   USB port number on hub
                devinfo.sort(key=lambda x:x['usbpath'])
            if key:
                if index is None:
                    filtered = [info[key] for info in devinfo]
                else:
                    filtered = devinfo[index][key]
            else:
                if index is None:
                    filtered = devinfo
                else:
                    filtered = devinfo[index]
        else:
            if index is None:
                filtered = []

        return filtered

    def get_serial(self, key=None, index=0):
        ttyUSB_major = '188'
        serial_vendors = ['FTDI', 'Prolific_Technology_Inc.']

        for vendor in serial_vendors:
            devinfo = self.filter_downstream({
                'subsystem': 'tty',
                'major': ttyUSB_major,
                'vendor': vendor
            })
            if not devinfo:
                devinfo = self.filter_downstream({
                    'major': ttyUSB_major,
                    'vendor': vendor
                })
            if devinfo:
                break

        return self._filter_devinfo(devinfo, key, index)

    def get_relay(self, key=None, index=0):
        devinfo = self.filter_downstream({
            'subsystem': 'tty',
            'vendor': 'DLP_Design'
        })
        if not devinfo:
            devinfo = self.filter_downstream({
                'vendor': 'DLP_Design'
            })

        return self._filter_devinfo(devinfo, key, index)

    def get_block(self, key=None, index=0):
        devinfo = self.filter_downstream({
            'subsystem': 'block',
            'devtype': 'disk'
        }, {
            'size': 0
        })
        return self._filter_devinfo(devinfo, key, index)

    def get_part(self, key=None, index=0):
        devinfo = self.filter_downstream({
            'subsystem': 'block',
            'devtype': 'partition'
        }, {
            'size': 0
        })

        return self._filter_devinfo(devinfo, key, index)

    def get_sdwire(self, key=None, index=0):
        devinfo = self.filter_downstream({
            'model': 'sd-wire'
        })

        return self._filter_devinfo(devinfo, key, index)

    def get_ethernet(self, key=None, index=0):
        vendors = ['ASIX_Elec._Corp.']

        for vendor in vendors:
            devinfo = self.filter_downstream({
                'subsystem': 'net',
                'vendor': vendor
            })
            if devinfo:
                break

        return self._filter_devinfo(devinfo, key, index)

    def get_hub(self, key=None, index=0):
        devinfo = self.filter_downstream({
                'devtype': 'usb_device',
            })
        hubs = []
        for d in devinfo:
            if 'USB' in d['model'] and 'Hub' in d['model']:
                hubs.append(d)

        return self._filter_devinfo(hubs, key, index)

    def get_misc_devices(self, key=None, index=0):
        get_funcs = [
            'get_serial',
            'get_relay',
            'get_block',
            'get_part',
            'get_sdwire',
            'get_ethernet',
            'get_hub'
        ]

        categorised = []
        for func_name in get_funcs:
            func = getattr(self, func_name, None)
            if func:
                categorised.extend(func(index=None))

        # Filter out known devices
        uncategorised = []
        for device in self.downstream:
            if device not in categorised:
                matching = [c for c in categorised
                    if c['usbpath'] == device['usbpath'] and c['serial'] == device['serial']]
                if not matching:
                    uncategorised.append(device)

        devinfo = self._filter_dictarr(
            filters={'devtype': 'usb_device'}, dictarr=uncategorised)

        return self._filter_devinfo(devinfo, key, index)

    def get_parent(self):
        dev = self.get_device()
        pdev = dev.find_parent(subsystem='usb', device_type='usb_device')
        return None if not pdev else pdev.sys_name

    def show_ancestry(self):
        dev = self.get_device()
        if dev is None:
            return None

        while dev.parent:
            p = dev.parent
            print(dir(p))
            print(p.driver, p.subsystem, p.sys_name, p.device_path, p.sys_path)
            subprocess.run(['ls', "{}/driver".format(p.sys_path)])
            dev = p
