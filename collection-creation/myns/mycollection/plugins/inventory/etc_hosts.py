import os
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleError

DOCUMENTATION = '''
    name: etc_hosts
    plugin_type: inventory
    short_description: Ansible dynamic inventory plugin that reads from /etc/hosts
    description:
        - This plugin reads /etc/hosts and converts it into an Ansible inventory.
    author: Your Name
    options:
        plugin:
            description: Name of the plugin
            required: true
            choices: ['etc_hosts']
'''

EXAMPLES = '''
# Use /etc/hosts as inventory source
plugin: etc_hosts
'''

class InventoryModule(BaseInventoryPlugin):
    NAME = 'etc_hosts'

    def verify_file(self, path):
        """Verify if this is a valid source for this plugin"""
        if super(InventoryModule, self).verify_file(path):
            return path.endswith(('etc_hosts.yml', 'etc_hosts.yaml'))
        return False

    def parse(self, inventory, loader, path, cache=True):
        """Parse the /etc/hosts file and add it to the inventory"""
        super(InventoryModule, self).parse(inventory, loader, path)

        etc_hosts_file = "/etc/hosts"

        if not os.path.exists(etc_hosts_file):
            raise AnsibleError(f"{etc_hosts_file} not found")

        with open(etc_hosts_file, 'r') as f:
            for line in f:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # The hosts file format: IP Address followed by hostnames
                parts = line.split()
                if len(parts) < 2:
                    continue

                ip_address = parts[0]
                hostnames = parts[1:]

                # Add the first hostname as the main host
                primary_host = hostnames[0]
                inventory.add_host(primary_host)

                # Add the IP address as a host variable
                inventory.set_variable(primary_host, 'ansible_host', ip_address)

                # Add aliases as group members
                for alias in hostnames[1:]:
                    inventory.add_host(alias)
                    inventory.set_variable(alias, 'ansible_host', ip_address)
