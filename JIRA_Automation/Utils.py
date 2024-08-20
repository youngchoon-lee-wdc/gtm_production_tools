import os
import platform
import re
import shutil
import traceback
import json
import CICommon
import sys

jira_automation_path = os.path.abspath('JIRA_Automation')
sys.path.append(jira_automation_path)

import JIRAConnector

US_BUILD_SHARED = r"\\uls-op-fpgcss01.wdc.com\fpgcss_ci\%s\Firmware\Releases\Unofficial_Builds"

filepath = os.path.realpath(__file__)
print ("filepath:%s" % filepath)
localub_dir = os.path.dirname(filepath)

def load_config(config_file):
    config_data = None
    try:
        config_path = os.path.join(JIRAConnector.jira_automation_config_dir, config_file)
        print ("configuration file : %s " % config_path)
        if os.path.exists(config_path):
            with open(config_path, 'r') as data_file:
                config_data = json.load(data_file)
    except Exception as e:
        print (e)
        traceback.print_exc()
    return config_data

def CopyFileToKRShared(commit_id, src, project):
    status = -1
    try:
        kr_shared_folder= CICommon.UNOFFICIAL_BUILD_SHARED % (project, commit_id)
        network_map_cmd = r"net use Y: %s %s %s" % (kr_shared_folder, CICommon.KR_SHARED_SERVICE_ACCOUNT, CICommon.KR_SHARED_SERVICE_PASS)
        print ("network_map_cmd:%s" % network_map_cmd)
        os.system(network_map_cmd)
        dest = 'Y:/'
        if os.path.exists(dest) == False:
            os.mkdir(dest)

        shutil.copy2(src, dest)
        print (r"dest folder:%s" % kr_shared_folder)
        status = 0

    except Exception as e:
        status = 1
        print (e)
        traceback.print_exc()
    finally:
        delete_network_map = r"net use Y: /delete"
        os.system(delete_network_map)

    return status


def getJiraInfoFromKRShared(project, commit_id, build_id):
    jira_info = ''
    try:
        jira_create_filename = build_id + '.txt'
        kr_shared_folder= CICommon.UNOFFICIAL_BUILD_SHARED % (project, commit_id)
        network_map_cmd = r"net use Y: %s %s %s" % (kr_shared_folder, CICommon.KR_SHARED_SERVICE_ACCOUNT, CICommon.KR_SHARED_SERVICE_PASS)
        print ("network_map_cmd:%s" % network_map_cmd)
        os.system(network_map_cmd)
        jira_info_file = r"Y:\\%s" % (jira_create_filename)
        print (jira_info_file)
        if os.path.exists(jira_info_file) == True:
            with open(jira_info_file, 'r') as fp:
                jira_info = fp.read()
                print (jira_info)

    except Exception as e:
        print (e)
        traceback.print_exc()
    finally:
        delete_network_map = r"net use Y: /delete"
        os.system(delete_network_map)

    return jira_info

def getModelGLURLInfoFromKRShared(project, commit_id, build_id):
    model_gl_url_info = ''
    try:
        model_gl_url_filename = build_id + '_model_gl.txt'
        kr_shared_folder= CICommon.UNOFFICIAL_BUILD_SHARED % (project, commit_id)
        network_map_cmd = r"net use Y: %s %s %s" % (kr_shared_folder, CICommon.KR_SHARED_SERVICE_ACCOUNT, CICommon.KR_SHARED_SERVICE_PASS)
        print ("network_map_cmd:%s" % network_map_cmd)
        os.system(network_map_cmd)
        model_gl_url_info_file = r"Y:\\%s" % model_gl_url_filename
        print (model_gl_url_info_file)
        if os.path.exists(model_gl_url_info_file) == True:
            with open(model_gl_url_info_file, 'r') as fp:
                model_gl_url_info = fp.read()
                print (model_gl_url_info)

    except Exception as e:
        print (e)
        traceback.print_exc()
    finally:
        delete_network_map = r"net use Y: /delete"
        os.system(delete_network_map)

    return model_gl_url_info

def getErrorList(project, commit_id, main_build_id):
    errorList = []
    try:
        kr_shared_folder= CICommon.UNOFFICIAL_BUILD_SHARED % (project, commit_id)
        network_map_cmd = r"net use Y: %s %s %s" % (kr_shared_folder, CICommon.KR_SHARED_SERVICE_ACCOUNT, CICommon.KR_SHARED_SERVICE_PASS)

        print ("network_map_cmd:%s" % network_map_cmd)
        os.system(network_map_cmd)
        dest = 'Y:/'
        fileList = os.listdir(dest)
        for file in fileList:
            if file.startswith(main_build_id) == True and file.endswith('_%s.txt' % CICommon.FO_ERROR_FILE_NAME) == True:
                print(file)
                errorFilePath = os.path.join(dest, file)
                with open(errorFilePath, 'r') as efile:
                    error_console_url = efile.read()
                    print (error_console_url)
                    errorList.append(error_console_url)
                
                # clean file
                os.remove(errorFilePath)
                print ("Deleted error console file:%s" % errorFilePath)

    except Exception as e:
        print (e)
        traceback.print_exc()
    finally:
        delete_network_map = r"net use Y: /delete"
        os.system(delete_network_map)

    return errorList

def getArtifactsURLList(project, commit_id, build_id):
    artifact_url_list = []
    try:
        kr_shared_folder= CICommon.UNOFFICIAL_BUILD_SHARED % (project, commit_id)
        network_map_cmd = r"net use Y: %s %s %s" % (kr_shared_folder, CICommon.KR_SHARED_SERVICE_ACCOUNT, CICommon.KR_SHARED_SERVICE_PASS)

        print ("network_map_cmd:%s" % network_map_cmd)
        os.system(network_map_cmd)
        dest = 'Y:/'
        fileList = os.listdir(dest)
        for file in fileList:
            if file.startswith(build_id) == True and file.endswith('_%s.txt' % CICommon.FO_ARTIFACT_URL) == True:
                print(file)
                artifact_url_file = os.path.join(dest, file)
                with open(artifact_url_file, 'r') as afile:
                    artifact_url = afile.read()
                    print (artifact_url)
                    artifact_url_list.append(artifact_url)
                
                # clean file
                os.remove(artifact_url_file)
                print ("Deleted artifact URL file:%s" % artifact_url_file)

    except Exception as e:
        print (e)
        traceback.print_exc()
    finally:
        delete_network_map = r"net use Y: /delete"
        os.system(delete_network_map)

    return artifact_url_list

def uploadArtifactory(upload_path, file_path):
    status = -1
    try:

        jfrog_path = '/usr/bin/jfrog'
        if platform.system() == 'Windows':
            jfrog_path = r"c:/utility/jfrog.exe"
            if os.path.exists(jfrog_path) == False:
                jfrog_path = r"C:/WDLABS/BuildTrees/workspace/Dev_JIRA_CREATION/automation/tools/jfrog.exe"

        os.system("%s rt config xArtifactory --url=%s --user=%s --password=%s" % (jfrog_path, CICommon.KR_ARTIFACTORY_URL, CICommon.ARTIFACTORY_SVC_USER, CICommon.ARTIFACTORY_SVC_USER_PASS))
        jfrogCmd = "%s rt upload %s %s" % (jfrog_path, file_path, upload_path)
        print ('Artifactory cmd: ', jfrogCmd)
        status = os.system(jfrogCmd)
        print ("Artifactory upload status:%s" % status)
        if status == 0:
            print ("%s is uploaded to Artifactory sucessfully" % file_path)
        else:
            print ("Uploading was failed : error code(%d)" % status)

    except Exception as e:
        print (e)
        traceback.print_exc()

    return status

def get_only_keyname(url):
    try:
        key = re.findall(r'(sx3.*)_.*.zip', url)
        keyname = key[0]
        return keyname

    except Exception as e:
        print (e)
        traceback.print_exc()


def remove_special_char(origin):
    if origin:
        ret_str = origin.strip()
        ret_str = ret_str.replace("\"", "")
        return ret_str.lower()
    else:
        return ''