# coding=utf-8
#
# Copyright ( С ) 2013 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from lib import hatchery as Manager


class ResourcePool(object):
    def __init__(self, name):
        """
        ESXi resource pool instance
        :param manager: ESXi manager
        :param name: ESXi name of a resource pool
        :raise: AttributeException
        """
        self.logger = logging.getLogger(self.__module__)
        if name:
            self.name = name
        else:
            msg = "Couldn't specify the name of the resource pool"
            self.logger.error(msg)
            raise AttributeError(msg)

    def create(self, manager, host_name=None):
        """
        Creates a ESXi resource pool
        :raise: AttributeException, CreatorException
        """
        if not manager:
            msg = "Couldn't specify the ESX manager"
            self.logger.error(msg)
            raise AttributeError("Couldn't specify ESX manager")
        try:
            manager.create_resource_pool(name=self.name, esx_hostname=host_name)
            self.logger.info("Resource pool '{}' has been created successfully".format(self.name))
        except Manager.ExistenceException as e:
            self.logger.warning(e.message)
            raise
        except Manager.CreatorException as e:
            self.logger.error(e.message)
            raise

    def destroy(self, manager, with_vms=False):
        """
        Destroys the resource pool
        :param with_vms: if True  - deletes all vms in this resource pool
                         if False - save vms and move its to the up resource pool
        :raise: CreatorException
        """
        if not manager:
            msg = "Couldn't specify the ESX manager"
            self.logger.error(msg)
            raise AttributeError("Couldn't specify ESX manager")

        try:
            if with_vms:
                manager.destroy_resource_pool_with_vms(self.name)
                self.logger.info("Resource pool '%s' was destroyed successfully (VMs also destroyed)" % self.name)
            else:
                manager.destroy_resource_pool(self.name)
                self.logger.info("Resource pool '%s' was destroyed successfully (VMs not destroyed)" % self.name)
        except Manager.ExistenceException as e:
            msg = '%s. %s' % (e.message, 'Nothing could be destroyed')
            self.logger.warning(msg)
            raise
        except Manager.CreatorException as e:
            self.logger.error(e.message)
            raise