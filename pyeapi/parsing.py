import pyeapi
from pprint import pprint
import json

pyeapi.load_config("nodes.conf")

continues = pyeapi.client.config.connections

merge_data = {}



for name in continues[:-1]:
    node = pyeapi.connect_to(name)

    cmd = ['show hostname', 'show ip interface brief', 'show vlan']
    vlan_raw_data = node.enable(cmd)

    hostname = vlan_raw_data[0]['result']['hostname']
    merge_data.setdefault(hostname, {
    "hostname": hostname,
    "interfaces": [],
    "vlan": []
    })

    int_data = vlan_raw_data[1]['result']['interfaces']
    for int_name, details in int_data.items():
        name = details.get('name')
        ip_addr = details.get('interfaceAddress').get('ipAddr').get('address')
        ip_mask = details.get('interfaceAddress').get('ipAddr').get('maskLen')
        protocol = details.get('lineProtocolStatus')

        merge_data[hostname]['interfaces'].append({
            'name': name,
            'address': ip_addr,
            'mask': ip_mask,
            'network': f'{ip_addr}/{ip_mask}',
            'protocol': protocol
        })

    vlans_data = vlan_raw_data[2]['result']['vlans']
    for instance, details in vlans_data.items():
        vlan_interfaces = list(details['interfaces'].keys()) or None

        merge_data[hostname]['vlan'].append({
            "instance": instance,
            "interfaces": vlan_interfaces
        })

merge_data = list(merge_data.values())

with open('./report.json', 'w') as f:
    json.dump(merge_data, f, indent=4)