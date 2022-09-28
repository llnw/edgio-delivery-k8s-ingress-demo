# Edgio delivery CDN Kubernetes Ingress Controller Demo Code

 This is a demo to show the use of the Edgio/Limelight API with the Kubernetes API to create Ingresses on demand based on the Kubernetes configuration

## Pieces needed

* Kuberntes cluster with credentials
* Edgio Legacy Limelight account with credentials
* Api controlled DNS server(s) - this example users Vultr



## Files in this demo

* watch.yml - configuration file for the actual ingress controller
* vdns.yml - configuration file for the Vultr DNS connector
* edgiocdn.yml - configuration file for the Edgio Legacy CDN connector
* list_addresses.py - utility routings to get address information from Kubernetes cluster
* listpods.py - utility to test connectivity to the Kubernetes cluster
* vdns.py - python class to manipulate the DNS resource records in Vultr DNS 
* edgiocdn.py - python class to manipulate the Edgio delivery CDN 
* watch.py the actual Edgio delivery CDN ingress controller implementation
* * in the real world this would be implemented within the cluster itself.  It's done standalone to make it easier to understand




