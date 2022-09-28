import requests
import pprint
import sys
import yaml
import os

class vdns:
    def __init__(self,conf_label):
        try:
         conf_file = os.environ['VDNS_CONF']
        except:
            conf_file = 'vdns.yml'
    

        with open(conf_file) as conf:
            try:
                conf_dict=(yaml.safe_load(conf))
            except yaml.YAMLError as exc:
                print(exc)
        self.domain = conf_dict[conf_label]['domain']
        key = conf_dict[conf_label]['token']
        self.vhost = 'api.vultr.com'
        self.dns_session=requests.Session()
        self.dns_session.headers.update({'Authorization':'Bearer {}'.format(key)})

    def __del__(self):
        del self.dns_session

    def update(self,hostname,addresslist):
        recordresponse = self.dns_session.get("https://{}/v2/domains/{}/records".format(self.vhost,self.domain))
        recordlist=[]
        for record in recordresponse.json()['records']:
            if record["name"] == hostname and  record['type'] == 'A':
                recordlist.append(record['id'])
        for id in recordlist:
            deleteresponse = self.dns_session.delete("https://{}/v2/domains/{}/records/{}".format(self.vhost,self.domain,id))

        pprint.pprint(recordlist)
        # need to do delete here
        for address in addresslist:
            body={
                'name':hostname,
                'type':'A',
                'data':address,
                'ttl': 120,
                'priority': 0
                }
            response = self.dns_session.post("https://{}/v2/domains/{}/records".format(self.vhost,self.domain),
                json=body
            )
            pprint.pprint(response.content)



def main():
    mydns = vdns('vultr-dns')
    result = mydns.update('test' , [])

    return 0

if __name__ == '__main__':
    sys.exit(main()) 