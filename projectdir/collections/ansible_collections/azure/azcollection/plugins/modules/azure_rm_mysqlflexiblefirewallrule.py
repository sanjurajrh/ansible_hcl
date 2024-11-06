#!/usr/bin/python
#
# Copyright (c) 2024 xuzhang3 (@xuzhang3), Fred-sun (@Fred-sun)
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: azure_rm_mysqlflexiblefirewallrule
version_added: "2.7.0"
short_description: Manage MySQL flexible firewall rule instance
description:
    - Create, update and delete instance of MySQL flexible firewall rule.

options:
    resource_group:
        description:
            - The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.
        required: True
        type: str
    server_name:
        description:
            - The name of the server.
        required: True
        type: str
    name:
        description:
            - The name of the MySQL flexible firewall rule.
        required: True
        type: str
    start_ip_address:
        description:
            - The start IP address of the MySQL flexible firewall rule. Must be IPv4 format.
            - Required when creating.
        type: str
    end_ip_address:
        description:
            - The end IP address of the MySQL flexible firewall rule. Must be IPv4 format.
            - Required when creating.
        type: str
    state:
        description:
            - Assert the state of the MySQL flexible firewall rule. Use C(present) to create or update a rule and C(absent) to ensure it is not present.
        default: present
        type: str
        choices:
            - absent
            - present

extends_documentation_fragment:
    - azure.azcollection.azure

author:
    - xuzhang3 (@xuzhang3)
    - Fred-sun (@Fred-sun)

'''

EXAMPLES = '''
- name: Create (or update) MySQL flexible firewall rule
  azure_rm_mysqlflexiblefirewallrule:
    resource_group: myResourceGroup
    server_name: testserver
    name: rule1
    start_ip_address: 10.0.0.17
    end_ip_address: 10.0.0.20

- name: Delete the MySQL flexible firewall rule
  azure_rm_mysqlflexiblefirewallrule:
    resource_group: myResourceGroup
    server_name: testserver
    name: rule1
    state: absent
'''

RETURN = '''
id:
    description:
        - Resource ID.
    returned: always
    type: str
    sample: "/subscriptions/xxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.DBforMySQL/flexibleservers/testserver/firewallRules/rule1"
server_name:
    description:
        - The name of the server.
    returned: always
    type: str
    sample: testserver
name:
    description:
        - Resource name.
    returned: always
    type: str
    sample: rule1
start_ip_address:
    description:
        - The start IP address of the MySQL flexible firewall rule.
    returned: always
    type: str
    sample: 10.0.0.16
end_ip_address:
    description:
        - The end IP address of the MySQL flexible firewall rule.
    returned: always
    type: str
    sample: 10.0.0.18
'''

import time

try:
    from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase
    from azure.core.exceptions import ResourceNotFoundError
    from azure.core.polling import LROPoller
except ImportError:
    # This is handled in azure_rm_common
    pass


class Actions:
    NoAction, Create, Update, Delete = range(4)


class AzureRMMySqlFlexibleFirewallRule(AzureRMModuleBase):
    """Configuration class for an Azure RM MySQL flexible firewall rule resource"""

    def __init__(self):
        self.module_arg_spec = dict(
            resource_group=dict(
                type='str',
                required=True
            ),
            server_name=dict(
                type='str',
                required=True
            ),
            name=dict(
                type='str',
                required=True
            ),
            start_ip_address=dict(
                type='str'
            ),
            end_ip_address=dict(
                type='str'
            ),
            state=dict(
                type='str',
                default='present',
                choices=['present', 'absent']
            )
        )

        self.resource_group = None
        self.server_name = None
        self.name = None
        self.start_ip_address = None
        self.end_ip_address = None

        required_if = [('state', 'present', ['start_ip_address', 'end_ip_address'])]
        self.results = dict(changed=False)
        self.state = None
        self.parameters = dict()
        self.to_do = Actions.NoAction

        super(AzureRMMySqlFlexibleFirewallRule, self).__init__(derived_arg_spec=self.module_arg_spec,
                                                               supports_check_mode=True,
                                                               required_if=required_if,
                                                               supports_tags=False)

    def exec_module(self, **kwargs):
        """Main module execution method"""

        for key in list(self.module_arg_spec.keys()):
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
                if key in ['start_ip_address', 'end_ip_address']:
                    self.parameters[key] = kwargs[key]

        old_response = None
        response = None

        old_response = self.get_firewallrule()

        if not old_response:
            self.log("MySQL flexible firewall rule instance doesn't exist")
            if self.state == 'absent':
                self.log("Old instance didn't exist")
            else:
                self.to_do = Actions.Create
        else:
            self.log("MySQL flexible firewall rule instance already exists")
            if self.state == 'absent':
                self.to_do = Actions.Delete
            elif self.state == 'present':
                self.log("Need to check if MySQL flexible firewall rule instance has to be deleted or may be updated")
                if (self.start_ip_address is not None) and (self.start_ip_address != old_response['start_ip_address']):
                    self.to_do = Actions.Update
                if (self.end_ip_address is not None) and (self.end_ip_address != old_response['end_ip_address']):
                    self.to_do = Actions.Update

        if (self.to_do == Actions.Create) or (self.to_do == Actions.Update):
            self.log("Need to Create / Update the MySQL flexible firewall rule instance")

            if self.check_mode:
                self.results['changed'] = True
                return self.results

            response = self.create_update_firewallrule()

            if not old_response:
                self.results['changed'] = True
            else:
                self.results['changed'] = old_response.__ne__(response)
            self.log("Creation / Update done")
        elif self.to_do == Actions.Delete:
            self.log("MySQL flexible firewall rule instance deleted")
            self.results['changed'] = True

            if self.check_mode:
                return self.results

            self.delete_firewallrule()
            # make sure instance is actually deleted, for some Azure resources, instance is hanging around
            # for some time after deletion -- this should be really fixed in Azure
            while self.get_firewallrule():
                time.sleep(20)
        else:
            self.log("MySQL flexible firewall rule instance unchanged")
            self.results['changed'] = False
            response = old_response

        if response:
            self.results["id"] = response["id"]
            self.results['name'] = self.name
            self.results['resource_group'] = self.resource_group
            self.results['server_name'] = self.server_name
            self.results['start_ip_address'] = response['start_ip_address']
            self.results['end_ip_address'] = response['end_ip_address']

        return self.results

    def create_update_firewallrule(self):
        '''
        Creates or updates MySQL flexible firewall rule with the specified configuration.

        :return: deserialized MySQL flexible firewall rule instance state dictionary
        '''
        self.log("Creating / Updating the MySQL flexible firewall rule instance {0}".format(self.name))

        try:
            response = self.mysql_flexible_client.firewall_rules.begin_create_or_update(resource_group_name=self.resource_group,
                                                                                        server_name=self.server_name,
                                                                                        firewall_rule_name=self.name,
                                                                                        parameters=self.parameters)
            if isinstance(response, LROPoller):
                response = self.get_poller_result(response)

        except Exception as exc:
            self.log('Error attempting to create the MySQL flexible firewall rule instance.')
            self.fail("Error creating the MySQL flexible firewall rule instance: {0}".format(str(exc)))
        return response.as_dict()

    def delete_firewallrule(self):
        '''
        Deletes specified MySQL flexible firewall rule instance in the specified subscription and resource group.

        :return: True
        '''
        self.log("Deleting the MySQL flexible firewall rule instance {0}".format(self.name))
        try:
            response = self.mysql_flexible_client.firewall_rules.begin_delete(resource_group_name=self.resource_group,
                                                                              server_name=self.server_name,
                                                                              firewall_rule_name=self.name)
        except Exception as e:
            self.log('Error attempting to delete the MySQL flexible firewall rule instance.')
            self.fail("Error deleting the MySQL flexible firewall rule instance: {0}".format(str(e)))

        return True

    def get_firewallrule(self):
        '''
        Gets the properties of the specified MySQL flexible firewall rule.

        :return: deserialized MySQL flexible firewall rule instance state dictionary
        '''
        self.log("Checking if the MySQL flexible firewall rule instance {0} is present".format(self.name))
        found = False
        try:
            response = self.mysql_flexible_client.firewall_rules.get(resource_group_name=self.resource_group,
                                                                     server_name=self.server_name,
                                                                     firewall_rule_name=self.name)
            found = True
            self.log("Response : {0}".format(response))
            self.log("MySQL flexible firewall rule instance : {0} found".format(response.name))
        except ResourceNotFoundError as e:
            self.log('Did not find the MySQL flexible firewall rule instance.')
        if found is True:
            return response.as_dict()

        return False


def main():
    """Main execution"""
    AzureRMMySqlFlexibleFirewallRule()


if __name__ == '__main__':
    main()
