from ll_sdk.utils.config_api_helper.deliver import DeliverServiceInstanceObj
from ll_sdk.config_api import ConfigApiClient
import pprint
import sys
from urllib.parse import urlencode
import yaml



class EdgioCDN:
    """
    A class that represents the Edgio Limelight CDN


    """

    def __init__(self,shortname,published_host,published_path):
        """
    Parameters
    ----------
    shortname: str
        The shortname being manipluated by the object
    published_host: str
        The public facing hostname for the ingress
    published_path: str
        The public facing path associated with the published host
        """
        with open("credentials.yml") as creds:
            try:
                cred_dict=(yaml.safe_load(creds))
            except yaml.YAMLError as exc:
                print(exc)
        
        self.username=cred_dict['edgio-llnw']['username']
        self.shared_key=cred_dict['edgio-llnw']['key']

        self.shortname = shortname

        self.cl = ConfigApiClient('apis.llnw.com', self.username, self.shared_key)
        self.published_hostname = published_host
        self.published_path = published_path
        self.delivery_json = self.find_service_instance()
        print(len(self.delivery_json['results']))
        if len(self.delivery_json['results']) == 0:
            self.delivery_object = DeliverServiceInstanceObj()
            self.delivery_object.generate_default(self.shortname, self.published_hostname,  profile_name='LLNW-Generic')
            self.delivery_object._set_delivery_svc_instance(publishedUrlPath=self.published_path)
            self.cdn_uuid=None
        else:
            self.cdn_uuid=self.delivery_json['results'][0]['uuid']
            self.delivery_object = DeliverServiceInstanceObj()
            self.delivery_object.process_response(self.delivery_json['results'][0])
            print(self.cdn_uuid)
            print(type(self.delivery_object))
        pprint.pprint(self.delivery_object)


    def update_origin_port(self,source_port):
        self.delivery_object.clear_protocol_set()
        self.delivery_object.add_protocol_set(published_protocol='https',source_protocol='http',published_port=443,source_port=source_port)
        print(self.delivery_object)
    
    def update_origin_path(self,source_path):
        self.delivery_object._set_delivery_svc_instance(sourceUrlPath=source_path)

    def update_origin_host(self,source_host):
        self.delivery_object._set_delivery_svc_instance(sourceHostname=source_host)
    
    def get_template(self):
        return(self.delivery_object)
    
    def find_service_instance(self):
        # this only checks for matching published host anme and published url path
        # assuming anything else is a change to and existing ingress
        # edgio api automatically prepends / if not there.
        if self.published_path[0] != '/':
            self.published_path = '/{}'.format(self.published_path)
        searchtuplelist = {
            'body.publishedUrlPath': self.published_path,
            'body.publishedHostname':self.published_hostname
        }
        print(searchtuplelist)
        searchstring =  urlencode(searchtuplelist)
        finstance = self.cl.search_delivery_service_instance('cstradtman',parameters=searchstring)
        print(finstance.status_code)
        print(finstance.json())
        return finstance.json()

    def submit(self):
        if self.cdn_uuid is None:
            result = self.cl.create_delivery_service_instance(self.delivery_object)
        else:
            result = self.cl.update_delivery_service_instance(uuid=self.cdn_uuid,delivery_config=self.delivery_object)
        print(result.json())
        return result



def main():
    mycdn = EdgioCDN('cstradtman','cstradtman.s.llnwi.net','/bob/')
    mycdn.update_origin_port(80)
    mycdn.update_origin_host('shorty.1tp.us')
    result = mycdn.get_template()
   # pprint.pprint(result)
    sresult = mycdn.submit()
    pprint.pprint(sresult)
    pprint.pprint(sresult.json)
    return 0

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit


