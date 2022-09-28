

"""
This example demonstrates the following:
    - Get a list of all the cluster nodes
    - Iterate through each node list item
    - Return the list of node with labels
"""

from kubernetes import client, config
import pprint
import requests

def get_node_external_address(node):
    for address_data in node.status.addresses:
        if address_data.type == 'ExternalIP':
            return address_data.address
    return None

def get_public_address_list(node_list):
    addresslist=[]
    for node in node_list.items:
        public_address = get_node_external_address(node)
        if public_address:
            addresslist.append(public_address)
    return addresslist

def get_current_node_list():
    config.load_kube_config()
    api_instance = client.CoreV1Api()
    node_list=api_instance.list_node()
    return node_list


def main():
    config.load_kube_config()

    api_instance = client.CoreV1Api()

    # Listing the cluster nodes
    node_list = api_instance.list_node()

    print(get_public_address_list(node_list))





if __name__ == '__main__':
    main()