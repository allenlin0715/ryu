from mininet.node import OVSKernelSwitch


class OVS12KernelSwitch(OVSKernelSwitch):
    def start(self, controllers):
        super(OVS12KernelSwitch, self).start(controllers)
        self.cmd('ovs-vsctl set Bridge', self,
                 "protocols='[OpenFlow10, OpenFlow12]'")

switches = {'ovs12': OVS12KernelSwitch}
