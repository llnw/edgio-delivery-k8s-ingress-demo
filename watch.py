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
Uses watch to print the stream of events from list namespaces
As changes occur it will use API calls to Vultr DNS and Edgio delivery to 
implement the changes in the CDN to reflect the state of the Kubernetes objects monitored
"""

from unicodedata import name
from kubernetes import client, config, watch
import pprint
import list_addresses
import vdns
import edgiocdn
import os 
import yaml



def main():

  try:
    conf_file = os.environ['WATCH_CONF']
  except:
      conf_file = 'watch.yml'
  
  with open(conf_file) as confs:
      try:
          conf_dict=(yaml.safe_load(confs))
      except yaml.YAMLError as exc:
          print(exc)

  shortname=conf_dict['shortname']
  source_domain=conf_dict['source_domain']

  # Configs can be set in Configuration class directly or using helper
  # utility. If no argument provided, the config will be loaded from
  # default location.  -- ~/. kube/config 
  config.load_kube_config()

  #v1 = client.CoreV1Api()
  net_client = client.NetworkingV1Api()
  core_client = client.CoreV1Api()
  count = 1000
  w = watch.Watch()

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
          address_list = list_addresses.get_public_address_list(list_addresses.get_current_node_list())
          print(address_list)
          dnshook = vdns.vdns('vultr-dns')
          result = dnshook.update(servicename ,address_list)
          source_hostname="{}.{}".format(servicename,source_domain)
          source_port=node_port
          print(shortname,host,hostpath)
          mycdn = edgiocdn.EdgioCDN(shortname,host,hostpath)
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