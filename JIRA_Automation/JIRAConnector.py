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

# Get the path of the subfolder

import CICommon
import Utils
import LocalUnofficialBuild

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

    def __init__(self, project, bi, dev):
        try:
            self.project = project
            self.request_cnt = 0
            print ("project:%s" % project)
            if bi:
                self.bi = bi
            else:
                print ('No build information')

            self.config_data = None
            self.ext_config_data = None
            self.dev = dev
            if self.dev == 'true':
                config_file = os.path.join(jira_automation_config_dir, project + '_dev.json')
            else:
                config_file = os.path.join(jira_automation_config_dir, project + '.json')
            self.config_data = Utils.load_config(config_file)

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
    
    def create_issue(self):
        rc = -1
        jira_key = ''
        try:
            json_file = os.path.join(jira_automation_config_dir,  self.project + '_jira_issue_template.json')
            jira_type = self.bi.get_jira_type()
            if jira_type == 'GL':
                desc_file = os.path.join(jira_automation_config_dir, self.project + '_jira_gl_desc.txt')
            else:
                desc_file = os.path.join(jira_automation_config_dir, self.project + '_jira_desc.txt')

            json_data = None
            with open(json_file, 'r') as jira_json_data:
                json_data = jira_json_data.read()

            today = date.today()

            created = date(day=today.day, month=today.month, year=today.year).strftime('%b %d')
            if self.dev == 'true':
                summary = '[JIRA_CREATION_TEST]'
            else:
                summary = ''

            summary += "%s on %s (Commit ID: %s)" % (jira_type, created, self.bi.get_commitid())

            duedate = date(day=today.day, month=today.month, year=today.year).strftime('%Y-%m-%d')
            json_data = json_data.replace('[JIRA_DUEDATE]', duedate)
            json_data = json_data.replace('[JIRA_SUMMARY]', summary)
            if self.project == 'atlas_refresh':
                #Atlas sprint
                sprint = jm.get_current_sprint(ATLAS_SPRINT_BOARD_ID)
                sprint_id = sprint["id"]
                sprint_name = sprint["name"]
                json_data = json_data.replace('[JIRA_SPRINT_ID]', str(sprint_id))
                json_data = json_data.replace('[JIRA_SPRINT_NAME]', sprint_name)

            jira_assignee = get_assignee(self.project, self.config_data)
            json_data = json_data.replace('[JIRA_ASSIGNEE]', str(jira_assignee))

            description = None
            with open(desc_file, 'r') as file_data:
                description = file_data.read()            
            description = description.replace('[JIRA_BRANCH]', self.bi.get_branch())
            description = description.replace('[JIRA_COMMITID]', self.bi.get_commitid())
            description = description.replace('[JIRA_COMMITID]', self.bi.get_commitid())

            kr_shared_path = 'NA'
            kr_shared_path = LocalUnofficialBuild.UB_BUILD_OUTPUT_PATH % (self.project, self.bi.get_commitid())

            description = description.replace('[JIRA_KR_SHARED_PATH]', kr_shared_path)
            description = description.replace('[WDCKIT_FFU]', self.bi.get_wdckit_ffu())
            description = description.replace('[FVT_FFU]', self.bi.get_fvt_ffu())
            json_data = json_data.replace('[JIRA_DESCRIPTION]', json.dumps(description))
            print (json_data)
            with open('jira_issue.json', 'w') as json_file:
                json_file.write(json_data)

            url = CEJIRA_REST_API_URL + 'issue'
            print (url)
            res = requests.post(url, headers=HEADERS, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASS), verify=False, data=json_data)
            print ("jira creation return code:%s" % res.status_code)
            res_data = json.loads(res.text)
            print (res_data)
            if res.status_code == 204 or res.status_code == 201:
                jira_key = res_data['key']
                msg = "Created jira:%s" % jira_key
                jira_watchers = self.config_data[self.project]['JIRA_watchers']
                for watcher in jira_watchers:
                    (rc, msg) = self.add_watcher(watcher, jira_key)
                    if rc != 0:
                        print ("WARNING:%s" % msg)
                    time.sleep(2)   
            else:
                msg = "Failed to create a jira"
                raise Exception(msg)

            rc = 0

        except Exception as err:
            print (err)
            traceback.print_exc(limit=None)
            rc = 1

        return (rc, jira_key)

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
        st_dmpmm = args.st_dmpmm
        st_platform = args.st_platform
        st_oakgate = args.st_oakgate
        st_perf = args.st_perf
        st_rdt = args.st_rdt
        main_jira = args.main_jira
        fvt_ffu = args.fvt_ffu
        wdckit_ffu = args.wdckit_ffu
        main_build_id = args.main_build_id
        print ("project:%s" % project)
        print ("branch:%s" % branch)
        print ("jira_type:%s" % jira_type)
        print ("st_dmpmm:%s" % st_dmpmm)
        print ("st_platform:%s" % st_platform)
        print ("st_oakgate:%s" % st_oakgate)
        print ("st_perf:%s" % st_perf)
        print ("st_rdt:%s" % st_rdt)
        print ("main_jira:%s" % main_jira)
        print ("fvt_ffu:%s" % fvt_ffu)
        print ("wdckit_ffu:%s" % wdckit_ffu)
        commit_id = ''
        short_commit_id = ''
        if args.commit_id and args.commit_id != '' and args.commit_id != 'None':
            commit_id = args.commit_id
        else:
            repo_name = CICommon.FW_REPO_NAMES[project]
            commit_id = CICommon.get_latest_commit_id(repo_name, branch)
        short_commit_id = commit_id[:8]
        print ("commit_id:%s" % commit_id)

        bi = CompactBuildInfoVO(project, branch, commit_id, jira_type, 'KR', fvt_ffu, wdckit_ffu)            
        jm = JIRAManager(project, bi, DRYRUN)
        # jm.get_all_sprint(ATLAS_SPRINT_BOARD_ID)
        jira_key = None
        is_main_jira_created = False
        if main_jira and main_jira.lower().find('-') != -1: # if main jira is exsisted, skip to create jira 
            is_main_jira_created = True
            jira_key = main_jira.strip().replace(',', '')

        if DRYRUN == 'true' and is_main_jira_created == False:
            jira_key = 'ATLAS-7583' #TODO:If you want to creat a jira, remove hard-coded jira key and enable to call create_issue()

        if is_main_jira_created == False:
            (status, jira_key) = jm.create_issue()
            if status != 0:
                raise Exception('Failed to create main jira')              
            filepath = os.path.realpath(__file__)
            currentDir = os.path.dirname(filepath)
            jira_create_filename = main_build_id + '.txt'
            jira_create_file = os.path.join(currentDir, jira_create_filename)
            with open(jira_create_file, 'w') as jfile:
                resultLine = "JIRA: %s" % CEJIRA_URL % jira_key
                jfile.write(resultLine)

            status = Utils.CopyFileToKRShared(commit_id[:7], jira_create_file, project)


        if status == 0 or is_main_jira_created == True:
            sub_task_creation_list = []
            if st_dmpmm == 'true':
                sub_task_creation_list.append('D')
            if st_platform == 'true':
                sub_task_creation_list.append('P')
            if st_oakgate == 'true':
                sub_task_creation_list.append('O')
            if st_perf == 'true':
                sub_task_creation_list.append('M')
            if st_rdt == 'true':
                sub_task_creation_list.append('R')
            print (sub_task_creation_list)
            for sub_task_type in sub_task_creation_list:
                (status, st_jira_key) = jm.create_sub_task_issue(jira_key, sub_task_type)  
                if status != 0:
                    raise Exception('Failed to create sub-task jira')  

            print (CEJIRA_URL % jira_key)

        # jm.get_issue(jira_key)
        # jm.update_field(project, 'status', '3', jira_key)

    except Exception as err:
        status = 1
        print (err)
        traceback.print_exc(limit=None)

    sys.exit(status)
