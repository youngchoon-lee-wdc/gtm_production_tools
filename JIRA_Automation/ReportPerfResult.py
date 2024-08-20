import os
import re
import json
import sys
import traceback
from optparse import OptionParser
import JIRAConnector

def add_parse_arguments():
    usage = """usage: JIRAConnector.py [options] arg
            e.g.) JIRAConnector.py -p atlasr"
            """
    parser = OptionParser(usage=usage)
    parser.add_option("-p", "--project", action="store", type="string", dest="project")
    parser.add_option("-j", "--jira_key", action="store", type="string", dest="jira_key")
    parser.add_option("-f", "--perf_fw", action="store", type="string", dest="perf_fw")
    parser.add_option("-c", "--perf_compare_fw", action="store", type="string", dest="perf_compare_fw")
    return parser.parse_args()

if __name__ == "__main__":
    status = 0
    try:
        options, args = add_parse_arguments()
        # TODO : set params from STAR
        # project = options.project
        # jira_key = options.jira_key
        # perf_fw = options.perf_fw
        # perf_compare_fw = options.perf_compare_fw
        project = 'shuri'
        jira_key = 'SHURI-14139'
        perf_fw = '15057ALP'
        perf_compare_fw = '15205ALP'

        print ("project:%s" % project)
        print ("jira_key:%s" % jira_key)
        print ("perf_fw:%s" % perf_fw)
        print ("perf_compare_fw:%s" % perf_compare_fw)

        jm = JIRAConnector.JIRAManager(project)
        comment = "PowerBI link for performance result : %s"
        powerbi_baselink=f"https://app.powerbi.com/groups/91708856-83d7-4d9d-9cdc-86b962fc1663/reports/0b7e0094-d0be-4f9a-967d-b9e7fa7a9aca/217ad86801d9b1664bb3?experience=power-bi&filter=Test_x0020_-_x0020_Program%2FProgram_x0020_Name%20in%20('Shuri_KR')%20and%20Test_x0020_-_x0020_Firmware%2FFirmware%20in%20('{perf_compare_fw}','{perf_fw}'%29"
        comment = comment % powerbi_baselink
        jm.add_comment(comment, jira_key)        

    except Exception as err:
        print (err)
        traceback.print_exc(limit=None)

    sys.exit(status)
