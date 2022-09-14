# Copyright 2016 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Uses watch to print the stream of events from list namespaces and list pods.
The script will wait for 10 events related to namespaces to occur within
the `timeout_seconds` threshold and then move on to wait for another 10 events
related to pods to occur within the `timeout_seconds` threshold.


Refer to the document below to understand the server-side & client-side
timeout settings for the watch request handler: ~

https://github.com/github.com/kubernetes-client/python/blob/master/examples/watch/timeout-settings.md
"""

from unicodedata import name
from kubernetes import client, config, watch
import pprint
import node_labels
import vdns
import edgiocdn



def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.  -- ~/. kube/config 
    config.load_kube_config()

    #v1 = client.CoreV1Api()
    net_client = client.NetworkingV1Api()
    core_client = client.CoreV1Api()
    count = 1000
    w = watch.Watch()

  #  for event in w.stream(v1.list_event_for_all_namespaces, namespace = "default",label_selector="myname=fred"):
    for event in w.stream(net_client.list_namespaced_ingress,namespace = "default",label_selector="cdn=edgio"):
       # print("Event: %s %s %s %s %s" % (
            #event['type'],
            #event['object'].kind,
            #event['object'].metadata.name,
            #event['object'].metadata.labels,
            #pprint.pprint(event['object'])
         #   pprint.pformat(event['object'].spec.ports)
        host=event['object'].spec.rules[0].host
        servicename=event['object'].spec.rules[0].http.paths[0].backend.service.name
        serviceportname=event['object'].spec.rules[0].http.paths[0].backend.service.port.name
        hostpath=event['object'].spec.rules[0].http.paths[0].path
        hostpathtype=event['object'].spec.rules[0].http.paths[0].path_type

        print("host={},servicename={},serviceportname={},path={},path_type={}".format(
            host,servicename,serviceportname,hostpath,hostpathtype))

        nsservice=core_client.list_namespaced_service(namespace="default",field_selector='metadata.name={}'.format(servicename))
        #pprint.pprint(nsservice)
        node_port=nsservice.items[0].spec.ports[0].node_port
        print("nodeport={}".format(node_port))


        if event['type'] == 'ADDED':
            address_list = node_labels.get_public_address_list(node_labels.get_current_node_list())
            print(address_list)
            dnshook = vdns.vdns('vultr-dns')
            result = dnshook.update(servicename ,address_list)
            source_hostname="{}.{}".format(servicename,'128bits.us')
            source_port=node_port
            mycdn = edgiocdn.EdgioCDN('cstradtman',host,hostpath)
            mycdn.update_origin_port(source_port)
            mycdn.update_origin_host(source_hostname)
          #  result = mycdn.get_template()
          # pprint.pprint(result)
            sresult = mycdn.submit()
            pprint.pprint(sresult)
            pprint.pprint(sresult.json)
              #  pprint.pprint(event['object'])
        count -= 1
        if not count:
            w.stop()



if __name__ == '__main__':
    main()