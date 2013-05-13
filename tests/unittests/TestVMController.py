import unittest
import logging
import lib.Hatchery as vmmanager
from deployment_system.TopologyReader import TopologyReader
from deployment_system.VMController import VMController
from deployment_system.VirtualMachine import VirtualMachine


class TestVMController(unittest.TestCase):
    def setUp(self):
        self.config_path = '../etc/topology.ini'
        self.rpname = 'rkhozinov'
        self.vmname = 'pipe_client'
        self.vmlogin = 'vyatta'
        self.vmpassword = 'vyatta'
        self.config = TopologyReader(self.config_path)
        self.manager = vmmanager.Creator(self.config.esx_host,
                                         self.config.esx_login,
                                         self.config.esx_password)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig()

    def test_create_instance(self):
        try:
            vms = self.config.get_virtual_machines()
            vm_ctrl = VMController(vm=vms[0],
                                   esx_host=self.config.esx_host,
                                   esx_login=self.config.esx_login,
                                   esx_password=self.config.esx_password)
            self.assertEqual(vm_ctrl.vm, vms[0])
            self.assertIsInstance(vm_ctrl.vm, VirtualMachine)
            self.assertIsInstance(vm_ctrl, VMController)
        except Exception as error:
            self.logger.critical(error.message)
            self.fail(error.message)


if __name__ == "__main__":
    unittest.main()