import argparse
import os
import re
import json
import sys
import time
import requests
from optparse import OptionParser
from requests.auth import HTTPBasicAuth
from datetime import date
from datetime import datetime
import traceback

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
localub_folder_path = os.path.join(parent_folder_path, 'LocalUB')
sys.path.append(parent_folder_path)
sys.path.append(localub_folder_path)

FW_REPO_NAMES = {
    'ocl':'CE-CSSD-LAB-TOOL-ocl_automation',
    'atlas':'FPGCSS-cssh2p2',
    'atlas_refresh':'FPGCSS-cssh2p2',
    'atlas3':'FPGCSS-atlas3',
    'atlas3_8tb':'FPGCSS-atlas3',
    'maia':'FPGCSS-polaris3',
    'calx3':'FPGCSS-calx3',
    'vulcan':'polaris-plus',
    'shuri':'FPGCSS-vega',
}

CEJIRA_REST_API_URL = r"https://cejira.sandisk.com/rest/api/2/"
CEJIRA_AGILE_REST_API_URL = r"https://cejira.sandisk.com/rest/agile/1.0/"
CEJIRA_URL = r"https://cejira.sandisk.com/browse/%s"
JIRA_USER = 'svc-ep-jenm01@wdc.com'
JIRA_PASS = '6uDR3wRBc7grfD6@'
HEADERS = {
    'Content-Type': 'application/json',
}

EMAIL_BODY = """
    <font face='verdana' size='2'>
    <font color=red>Owner for this cycle</font> should update the changes in this regression to the folloing jira and confirm if all information in the jira are correct.<br>
    And, <font color=red>lab engineer</font> can start measuring performance with the artifactory link to update the result.
    <br>
    <hr>
    JIRA issue for this regression cycle : %s 
"""

TEXT_FAIL = "{color:red}FAIL{color}"
TEXT_PASS = "{color:green}PASS{color}"
TEXT_NA = "{color:gray}N/A{color}"

LAUNCH_FAIL = "{color:red}Launch failed{color}"
LAUNCH_PASS = "{color:green}Launch passed{color}"
ATLAS_SPRINT_BOARD_ID = "1123"
REQ_MAX_CNT = 3
EXT_CONFIG_DATA = None

filepath = os.path.realpath(__file__)
print ("filepath:%s" % filepath)
jira_automation_dir = os.path.dirname(filepath)
jira_automation_config_dir = os.path.join(jira_automation_dir, 'config')

class CompactBuildInfoVO:
    def __init__(self, project, branch, commitid, jira_type, copy_to, fvt_ffu, wdckit_ffu):
        self.project = project
        self.branch = branch
        self.commitid = commitid
        self.jira_type = jira_type
        self.copy_to = copy_to
        self.fvt_ffu = fvt_ffu
        self.wdckit_ffu = wdckit_ffu

    def get_project(self):
       return self.project

    def get_branch(self):
       return self.branch

    def get_commitid(self):
       return self.commitid

    def get_jira_type(self):
       return self.jira_type

    def get_copy_to(self):
       return self.copy_to

    def get_fvt_ffu(self):
       return self.fvt_ffu

    def get_wdckit_ffu(self):
       return self.wdckit_ffu

class JIRAManager():

    def __init__(self, project):
        try:
            self.project = project
            print ("project:%s" % project)

        except Exception as err:
            print (err)
            traceback.print_exc(limit=None)

    def add_comment(self, body, issue_key):
        print (body)
        post_data = {}
        post_data['body'] = body
        post_data = json.dumps(post_data)
        url = CEJIRA_REST_API_URL + 'issue/%s/comment' % (issue_key)
        print (url)
        res = requests.post(url, headers=HEADERS, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASS), verify=False, data=post_data)
        res_data = json.loads(res.text)
        print (res_data)

    def add_watcher(self, name, issue_key):
        rc = -1
        try:
            post_data = '\"' + name + '\"'
            print (post_data)
            url = CEJIRA_REST_API_URL + 'issue/%s/watchers' % (issue_key)
            print (url)
            res = requests.post(url, headers=HEADERS, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASS), verify=False, data=post_data)
            if res.status_code == 204:
                msg = "Added an watcher:%s" % name
                rc = 0
            else:
                msg = "Failed to add an watcher:%s" % name
                rc = 1
        except Exception as err:
            print (err)
            traceback.print_exc(limit=None)
            rc = 1

        return (rc, msg)
    

    def create_sub_task_issue(self, parent_jira_key, sub_task_type):
        rc = -1
        subtask_jira_key = ''
        try:
            json_file = os.path.join(jira_automation_config_dir, self.project + '_jira_issue_sub_task_template.json')
            json_data = open(json_file).read()
            
            if self.dev == 'true':
                summary = '[JIRA_CREATION_TEST]'
            else:
                summary = ''

            if sub_task_type == 'D':
                summary += "DM PMM test"

            if sub_task_type == 'P':
                summary += "Platform test"

            if sub_task_type == 'O':
                summary += "Oakgate test"

            if sub_task_type == 'M':
                summary += "Performance test"

            if sub_task_type == 'R':
                summary += "RDT test"

            json_data = json_data.replace('[JIRA_SUMMARY]', summary)
            json_data = json_data.replace('[JIRA_PARENT_KEY]', parent_jira_key)
            print (json_data)
            with open('sub_task_issue.json', 'w') as json_file:
                json_file.write(json_data)

            url = CEJIRA_REST_API_URL + 'issue'
            print (url)
            res = requests.post(url, headers=HEADERS, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASS), verify=False, data=json_data)
            print ("jira creation return code:%s" % res.status_code)
            res_data = json.loads(res.text)
            print (res_data)
            if res.status_code == 204 or res.status_code == 201:
                subtask_jira_key = res_data['key']
                msg = "Created jira:%s" % subtask_jira_key
                subtask_jira_watchers = self.config_data[self.project]['sub_task_watchers']
                for watcher in subtask_jira_watchers:
                    self.add_watcher(watcher, subtask_jira_key)
                    time.sleep(2)
                rc = 0                     
            else:
                msg = "Failed to create a jira"
                raise Exception(msg)

            print (msg)

        except Exception as err:
            print (err)
            traceback.print_exc(limit=None)
            rc = 1

        return (rc, subtask_jira_key)

    def get_all_sprint(self, id):
        try:
            url = CEJIRA_AGILE_REST_API_URL + 'board/%s/sprint' % id
            print (url)
            res = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASS), verify=False)
            res_data = json.loads(res.text)
            print (res_data)
            return res_data

        except Exception as err:
            print (err)
            traceback.print_exc(limit=None)
            self.request_cnt += 1
            if self.request_cnt < REQ_MAX_CNT:
                print ("request count for getting all sprints : %d " % self.request_cnt)
                time.sleep(30)
                self.get_all_sprint(id)

    def get_date_format(self, rdate):
        split_day = rdate.split('/')
        month = split_day[0]
        day = split_day[1]
        if len(month) == 1:
            month = '0'+ month
        if len(day) == 1:
            day = '0'+ day
        return month+day

    def is_today_in_range(self, year, sprint_name):
        ret = False
        try:
            today = date.today()
            today = int(today.strftime("%Y%m%d"))
            print("today =%d"% today)
            print("year =%s"% year)
            print("sprint_name =%s"% sprint_name)
            extract_range = re.findall(r"\((.*?)\)", sprint_name)
            print (extract_range[0])
            split_range = extract_range[0].split('~')
            start = split_range[0].strip()
            end = split_range[1].strip()
            start_date = int(year + self.get_date_format(start))
            end_date = int(year + self.get_date_format(end))
            print("start_date =%d"% start_date)
            print("end_date =%d"% end_date)

            if start_date <= end_date:
                return start_date <= today <= end_date
            else:
                return start_date <= today or today <= end_date 
        
        except Exception as err:
            print (err)
            traceback.print_exc(limit=None)

    # get sprint belong to today
    def get_current_sprint(self, id):
        try:
            sprint = {}
            sprint_data = self.get_all_sprint(id)
            if sprint_data:
                for sprint in sprint_data["values"]:
                    sprint_id = sprint["id"]
                    name = sprint["name"]
                    state = sprint["state"]
                    startDate = sprint["startDate"]
                    print (str(sprint_id) + ":" + name + ":" + state + "\r\n")
                    year = startDate[0:4]
                    is_today_in_range = self.is_today_in_range(year, name)
                    if is_today_in_range == True:
                        break
            else:
                # default value for error
                sprint = {"id":0, "name":"None"}

            return sprint
        except Exception as err:
            print (err)
            traceback.print_exc(limit=None)

    def get_issue(self, issue_key):
        url = CEJIRA_REST_API_URL + 'issue/%s' % (issue_key)
        print (url)
        res = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASS), verify=False)
        res_data = json.loads(res.text)
        print (res_data)

    def get_issue_with_agile_api(self, issue_key):
        url = CEJIRA_AGILE_REST_API_URL + 'issue/%s' % (issue_key)
        print (url)
        res = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASS), verify=False)
        res_data = json.loads(res.text)
        print (res_data)

    def attach_file(self, issue_key, attach_file_path):
        url = CEJIRA_REST_API_URL + 'issue/%s/attachments' % (issue_key)
        print (url)
        headers = {'X-Atlassian-Token': 'no-check'}
        content_type = 'multipart/form-data'
        files = {'file': (os.path.basename(attach_file_path), open(attach_file_path, 'rb'), content_type)}
        res = requests.post(url, headers=headers, files=files, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASS))
        res_data = json.loads(res.text)
        print (res_data)

    def update_status_in_progress(self, issue_key):
        try:
            data = {
                'transition': {
                    'id': '11'
                }
            }
            comment = 'Automatic transition to change status to In Progress'
            data['update'] = {'comment': [{'add': {'body': comment}}]} # type: ignore

            url = CEJIRA_REST_API_URL + 'issue/%s/transitions' % (issue_key)
            print (url)
            json_data=json.dumps(data)
            print (json_data)
            res = requests.post(url, headers=HEADERS, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASS), verify=False, data=json_data)
            print (res)
            return res

        except Exception as err:
            print (err)
            traceback.print_exc(limit=None)        

def add_parse_arguments():
    usage = """usage: JIRAConnector.py [options] arg
            e.g.) JIRAConnector.py -p atlasr"
            """
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('--project', help='Set project name')
    parser.add_argument('--branch', help='Set branch name')
    parser.add_argument('--commit_id', help='Set commit id (7 chars or higher)', required=False)
    parser.add_argument('--jira_type', help='Set cycle type of GL|FWR|DebugFWR')
    parser.add_argument('--dryrun', help='If you want to take a dryrun, set true', required=False)
    parser.add_argument('--st_dmpmm', help='If you want to run DMPMM, set true')
    parser.add_argument('--st_platform', help='If you want to run Platform test, set true')
    parser.add_argument('--st_oakgate', help='If you want to run Oakgate test, set true')
    parser.add_argument('--st_perf', help='If you want to run Performance test, set true')
    parser.add_argument('--st_rdt', help='If you want to run RDT test, set true')
    parser.add_argument('--main_jira', help='If you already created the JIRA for cycle request, set the JIRA key', required=False)
    parser.add_argument('--fvt_ffu', help='If you want to run FVT FFU tests, set true', required=False)
    parser.add_argument('--wdckit_ffu', help='If you want to run WDCKit test, set true', required=False)
    parser.add_argument('--main_build_id', help='Set build id of parent job')
    return parser.parse_args()

def get_watchers(project, config_data):
    try:
        jira_watchers = config_data[project]['JIRA_watchers']
        return jira_watchers

    except Exception as err:
        print (err)
        traceback.print_exc(limit=None)

def get_assignee(project, config_data):
    try:
        jira_assignee = config_data[project]['JIRA_assignee']
        return jira_assignee

    except Exception as err:
        print (err)
        traceback.print_exc(limit=None)

if __name__ == "__main__":
    status = -1
    try:
        args = add_parse_arguments()
        project = args.project
        branch = args.branch
        jira_type = args.jira_type
        DRYRUN = args.dryrun
        print ("project:%s" % project)
        print ("branch:%s" % branch)
        print ("jira_type:%s" % jira_type)

        jm = JIRAManager(project)

    except Exception as err:
        status = 1
        print (err)
        traceback.print_exc(limit=None)

    sys.exit(status)
