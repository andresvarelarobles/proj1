import requests
import urllib
import json
import numpy as np
import time
class work_agent:
    def __init__(self, api_url, sen_url, setup_file, task_data_file, sen_data_file, db_pass, db_ip):
        self.api_url = api_url
        self.sen_url = sen_url
        self.tfile = task_data_file
        self.sfile = sen_data_file
        self.db_pass = db_pass
        self.curr_req = 0
        self.reqs = []
        self.db_ip = db_ip

        self.setup(setup_file)

    def setup(self, setup_file):
        print('======================================================================================================')
        print('SETTING UP DATABASE FOR SIM FROM ' + setup_file)
        
        os.environ['PGPASSWORD']=self.db_pass
        os.system('psql -h ' + self.db_ip + ' -U docker -p 5432 -f ' + setup_file)
        print('======================================================================================================')

    def run_reqs(self):
        print('======================================================================================================')
        print('STARTING WORK')
        for req in self.reqs:
            resp = requests.post(self.api_url + '/task', json = req, timeout = 10.0)

            print('Starting req: ' + str(req))

            if resp.status_code != 202:
                print(resp.text)
                continue

            resp = None

            while resp == None:
                time.sleep(7.0)

                resp = requests.get(self.api_url + '/task/' + str(req['task_id']), timeout = 10.0)

                if resp.status_code == 200:
                    print('Received response from request [id, time, 0/1]:')
                    print(resp.json())
                    print('DEBUG: verify requests table on sensors is empty')
                    resp2 = requests.get(self.sen_url + '/dump_requests')
                    if resp2.status_code == 404:
                        print(resp2.text)
                    else:
                        print(resp2.json())
                    print('\n')
                else:
                    resp = None
    
    def getCurrentStatusVal(self): #Andres Varela part
        sta_url = self.base_url + 'status.json'
        res = requests.get(sta_url)
        self.curr_status_data = res.json()['curvals']
        # print(self.curr_status_data)
        
    def getAvailStatusVals(self): # Andres Varela Part
        sta_url = self.base_url + 'status.json?show_avail=1'
        res = requests.get(sta_url)
        self.avail_status_data = res.json()['avail']
        # print(self.avail_status_data)
    
        
    def run_all(self):
        print('======================================================================================================')
        print('STARTING STRESS TEST')
        for req in self.reqs:
            resp = requests.post(self.api_url + '/task', json = req, timeout = 10.0)

            print('Starting req: ' + str(req))

            time.sleep(1.0)

    def add_req(self, real_loc, target_loc, sensors_needed):
        self.curr_req += 1

        req_json = {
            'task_id': self.curr_req,
            'real_loc': real_loc,
            'target_loc': target_loc,
            'sensors_needed': sensors_needed,
            'overall_timeout': 600.0
        }

        self.reqs.append(req_json)

    def save_tasks(self):
        resp = requests.get(self.api_url + '/dump_tasks')
        if self.is_resp_json(resp):
            print(str(resp.json()), file=open(self.tfile, 'a'))
        else:
            print('Did not receive tasks DB dump.')

    def save_sensors(self):
        resp = requests.get(self.api_url + '/dump_sensors')
        if self.is_resp_json(resp):
            print(str(resp.json()), file=open(self.sfile, 'a'))
        else:
            print('Did not receive sensors DB dump.')

    ## is_resp_json
    #
    # Checks if a requests response is json
    #
    # [in] resp: Response from one of the get/post/delete methods in this static class
    # [out] True/False based on if the resp has Json
    def is_resp_json(self, resp):
        if resp is None: return False
        if 'application/json' in resp.headers.get('Content-Type'): return True
        return False
