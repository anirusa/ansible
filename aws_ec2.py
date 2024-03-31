#!/usr/bin/env python3

import boto3
import json

def get_ec2_inventory():
    session = boto3.Session(


    )

    ec2 = session.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )

    existing_inventory = {}
    try:
        with open('inventory.json', 'r') as existing_file:
            existing_inventory = json.load(existing_file)
    except FileNotFoundError:
        pass

    inventory = {}
    for instance in instances:
        hostname = instance.id

        os_name = next((tag['Value'] for tag in instance.tags if tag['Key'] == 'OS'), 'Unknown')

        ansible_user = 'ubuntu' if os_name == 'Ubuntu' else 'ec2-user'

        # Only add to inventory if 'OS' tag is present and instance is not in existing inventory
        if os_name != 'Unknown' and hostname not in existing_inventory:
            inventory[hostname] = {
                'ansible_host': instance.public_ip_address,
                'ansible_user': ansible_user
            }

    with open('inventory.json', 'w') as inventory_file:
        json.dump(inventory, inventory_file)


    return inventory

if __name__ == '__main__':
    print(json.dumps(get_ec2_inventory()))
