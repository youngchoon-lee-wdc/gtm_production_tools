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
    return parser.parse_args()

if __name__ == "__main__":
    status = 0
    try:
        options, args = add_parse_arguments()
        # project = options.project
        project = 'shuri'
        # jira_key = options.jira_key
        jira_key = 'SHURI-13034'
        print ("project:%s" % project)
        print ("jira_key:%s" % jira_key)

        jm = JIRAConnector.JIRAManager(project, None, True)
        
        jm.get_issue(jira_key)
        # jm.get_issue_with_agile_api(jira_key)

    except Exception as err:
        print (err)
        traceback.print_exc(limit=None)

    sys.exit(status)
