import unittest
import logging
from deployment_system.TopologyReader import TopologyReader
from deployment_system.VMController import VMController
from deployment_system.VirtualMachine import VirtualMachine


class TestVMController(unittest.TestCase):
    def setUp(self):
        self.config_path = '../etc/topology.ini'
        self.name = 'topology'
        self.config = TopologyReader(self.config_path)
        self.log = logging.getLogger(__name__)
        logging.basicConfig()

    def test_create_instance(self):

        try:
            vms = self.config.get_virtual_machines()
            for vm in vms:
                vm_ctrl = VMController(vm=vm,
                                       esx_host=self.config.esx_host,
                                       esx_login=self.config.esx_login,
                                       esx_password=self.config.esx_password)
                self.assertIsInstance(vm_ctrl, VMController)
        except Exception as error:
            self.assertFalse(True)
            self.log.critical(error.message)

    def test_vm_configure(self):

        vm = VirtualMachine()
        vmctrl = VMController(vm=vm,
                               esx_host=self.config.esx_host,
                               esx_login=self.config.esx_login,
                               esx_password=self.config.esx_password)
        self.assertEqual()

if __name__ == "__main__":
    unittest.main()