import os
import platform
import re
import sys
import time
import shutil
import traceback
import subprocess
import ntpath
import GetLocalTestnfo, CITaskMain
import CITaskGenerator
import CovBuild
import TidyBuild
import Utils
REQUIRED_PACKAGE = 'gitpython requests'
try:
    pack_list = REQUIRED_PACKAGE.split(' ')
    for module in pack_list:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])
except Exception as err:
    traceback.print_exc(limit=None)

ENABLE_LIVET_BUILD = [
    "atlas_ei", "atlas_b0_dev", "atlas_b0_sed_dev", "atlas_b0_ei", 
    "maia_ei", "maia", "maia_perf", 
    "calx3_ei", "calx3", "calx3_perf", 
    "atlasr_4tb_sed_dev", "atlasr_4tb_sed", "atlasr_sed_dev", "atlasr_sed",  "atlasr_4tb_sed_ei", "atlasr_sed_ei", "atlasr_4tb_sed_ext_dev", "atlasr_sed_ext_dev", "atlasr_sed_ext_ei", "atlasr_4tb_sed_ext_ei", "atlasr_4tb_ei"
]
BUILD_SHARED = r"\\seouniip01.sdcorp.global.sandisk.com\SSD_Builds"
UNOFFICIAL_BUILD_SHARED = BUILD_SHARED + r"\%s\Firmware\Releases\Unofficial_Builds\%s"
US_BUILD_SHARED = r"\\uls-op-fpgcss01.wdc.com\fpgcss_ci\%s\Firmware\Releases\Unofficial_Builds"
filepath = os.path.realpath(__file__)
CIToolsDir = os.path.dirname(filepath)
print ('filepath: %s' % (filepath))
print ('CIToolsDir: %s' % (CIToolsDir))
KR_ARTIFACTORY_URL = 'https://ksg-ep-art01.wdc.com/artifactory'
ARTIFACTORY_SVC_USER = 'svc-artifactory-kr@wdc.com'
ARTIFACTORY_SVC_USER_PASS = 'di6h9TgN6VmjiB4@'
# ARTIFACTORY_SVC_USER = 'youngchoon.lee@wdc.com'
# ARTIFACTORY_SVC_USER_PASS = 'Sandisk223'
UB_ARTIFACTORY_REPO = "fpg-css-fw-global/UB/%s/%s/%s"
FO_FILE = "filteroutput.txt"
FW_REPO_NAMES = {
    'ocl':'CE-CSSD-LAB-TOOL-ocl_automation',
    'atlas':'FPGCSS-cssh2p2',
    'atlas_refresh':'FPGCSS-cssh2p2',
    'atlas3':'FPGCSS-atlas3',
    'atlas3_8tb':'FPGCSS-atlas3',
    'maia':'FPGCSS-polaris3',
    'calx3':'FPGCSS-calx3',
    'vulcan':'polaris-plus',
}
GITHUB_FPE_URL= "git@github.com:fpe-products/%s.git"
KR_SHARED_SERVICE_ACCOUNT = "/user:AD\svc-seofirmware"
KR_SHARED_SERVICE_PASS = "SanDisk230517!"
FO_ERROR_FILE_NAME = "error"
FO_ARTIFACT_URL = "artifact_url"

def downloadArtifactory(artifactory_path, local_file_path):
    status = -1
    try:

        jfrog_path = '/usr/bin/jfrog'
        if platform.system() == 'Windows':
            jfrog_path = r"c:\utility\jfrog.exe"
            if os.path.exists(jfrog_path) == False:
                jfrog_path = r"C:\WDLABS\BuildTrees\workspace\ci_task_runner\CssCITools\jfrog.exe"

        os.system("%s rt config xArtifactory --url=%s --user=%s --password=%s" % (jfrog_path, KR_ARTIFACTORY_URL, ARTIFACTORY_SVC_USER, ARTIFACTORY_SVC_USER_PASS))
        if local_file_path:
            jfrogCmd = "%s rt dl %s %s" % (jfrog_path, artifactory_path, local_file_path)
        else: #download to current directory
            jfrogCmd = "%s rt dl %s" % (jfrog_path, artifactory_path)
        print ('Artifactory cmd: %s' % jfrogCmd)
        status = os.system(jfrogCmd)
        print ("Artifactory download status:%s" % status)
        if status == 0:
            print ("%s is downloaded to Artifactory sucessfully" % artifactory_path)
        else:
            print ("Downloading was failed : error code(%d)" % status)

    except Exception as e:
        print (e)
        traceback.print_exc()

    return status

def get_latest_commit_id(repo_name, branch_name):
    from git import Repo
    latest_commit_id = None
    try:
        repository_url = GITHUB_FPE_URL % repo_name
        print (repository_url)
        repo = Repo(repository_url)
        remote_name = 'origin'
        repo.create_remote(remote_name, repository_url)
        branch = repo.heads[branch_name]
        commit = branch.commit
        latest_commit_id = commit.hexsha
    except Exception as e:
        print (e)
        traceback.print_exc()
    return latest_commit_id

def GetGitCommitInfo(FwWsDir):
    try:

        print ('Getting Git branch and commit ID in CI')
        os.chdir(FwWsDir)

        repo = ""
        branch = ""
        commitID = ""

        configFile = os.path.join(FwWsDir, ".git", "config")
        print ("git config:%s" % configFile)
        f = file(configFile)
        lines = f.readlines()
        for aLine in lines:
            print (aLine)
            if aLine.find("url") > -1:
                splits = aLine.split("/")  # get the last repo git name from bitbucket
                repo = splits[len(splits) - 1]
                repo = repo.split('.')[0]  # remove .git
                break
        f.close()

        status = os.system("git rev-parse --abbrev-ref HEAD > gitinfo.txt")
        if status:
            print ('error git rev-parse to get branch info')
            sys.exit(1)

        f = file("gitinfo.txt")
        line = f.readline()
        f.close()
        branch = line[:-1]

        os.system("git log -n1 > gitinfo.txt")
        f = file("gitinfo.txt")
        lines = f.readlines()
        f.close()

        for aLine in lines:
            splits = aLine.split()
            if aLine.find("commit") > -1:
                full_commit_id = splits[1]
                commitID = splits[1][0:7]
                break

        print ('repo = %s' % (repo))
        print ('branch = %s' % (branch))
        print ('commit ID = %s' % (commitID))

        os.environ["COMMIT_ID"] = commitID

        os.system('del gitinfo.txt > NUL 2> NUL')

        return repo, branch, commitID, full_commit_id

    except Exception as e:
        print (e)
        traceback.print_exc()

def ExitError(msg):
    """
    exit with error message
    """
    filepath = os.path.realpath(__file__)
    CIToolsDir = os.path.dirname(filepath)
    errFile = os.path.join(CIToolsDir, "CIErrors.txt")
    
    print (msg)
    f = open(errFile, 'a')
    f.write(msg)
    f.close()
    sys.exit(1)

def copyBatchFile(wsDir):
    build_batch_file = ''
    try:
        GetGitCommitInfo(wsDir)
        project = os.getenv("PROJECT")
        copyto = os.getenv("COPY_TO")
        if copyto == None or copyto == '' or copyto == 'None':
            copyto = 'KR'

        exclude_files = os.path.join(CIToolsDir,  'excludeFiles.txt')
        print ("exclude_files:%s" % exclude_files)
        build_batch_file = os.path.join(CIToolsDir, "Unofficial_hw_release_%s_%s.bat" % (project, copyto))
        print ("build_batch_file:%s" % build_batch_file)
        shutil.copy2(exclude_files, os.path.dirname(wsDir))
        shutil.copy2(build_batch_file, os.path.dirname(wsDir))
        print ("All files to build are copied successfully")

    except Exception as e:
        print (e)
        traceback.print_exc()

    return build_batch_file


def copyFileToShared(copy_to, project, src, commit_id):
    status = 0
    try:
        shared_folder= US_BUILD_SHARED % project
        network_map_cmd = r"net use Y: %s 8=#2Mu{EqwId_8on /user:AD\svc-FPG-CSS-CI" % (shared_folder)

        print ("network_map_cmd:%s" % network_map_cmd)
        os.system(network_map_cmd)
        dest = 'Y:/' + commit_id
        if os.path.exists(dest) == False:
            os.mkdir(dest)

        shutil.copy2(src, dest)
        print (r"dest folder:%s\%s" %(shared_folder, commit_id))

    except Exception as e:
        status = 1
        print (e)
        traceback.print_exc()
    finally:
        delete_network_map = r"net use Y: /delete"
        os.system(delete_network_map)

    return status

def check_item_in_list(check_type, check_item, item_list):
    print ("check_type:%s" % check_type)
    print ("check_item:%s" % check_item)
    print ("item_list:%s" % item_list)
    if check_type == 'true':
        if item_list and item_list != '' and item_list != 'None':
            item_list = item_list.split(',')
            filtered_item_list = list(map(str.strip, item_list))
            check_type = 'false'
            for item in filtered_item_list:
                print(item)
                if check_item.lower() == item.lower():
                    check_type = 'true'
                    break
    return check_type


def doFW(wsDir, product):
    status = 1
    project = os.getenv("PROJECT")
    commit_id = os.getenv("COMMIT_ID") #short commit id(7 char)
    livet_build = os.getenv("LIVET_BUILD" ,'false')
    relpkg = os.getenv("RELPKG" ,'false')
    build_id = os.getenv('BUILD_ID')
    main_build_id = os.getenv('MAIN_BUILD_ID')
    try:
        build_batch_file = copyBatchFile(wsDir)

        os.chdir(os.path.join(wsDir, 'Make'))
        print ("current dir:%s" % os.getcwd())
        print ("product:%s" % product)
        print ("livet_build:%s" % livet_build)
        build_batch_file_path = os.path.join(os.path.dirname(wsDir), os.path.basename(build_batch_file))
        print ("build_batch_file_path:%s" % build_batch_file_path)
        bullseye_build = 'false'
        if product.lower().find('bullseye') > -1 and product.lower().find('livet') > -1:
            bullseye_build = 'true'

        relpkg_products = os.getenv("RELPKG_PRODUCTS")
        relpkg = check_item_in_list(relpkg, product, relpkg_products)

        livet_build_products = os.getenv("LIVET_BUILD_PRODUCTS")
        livet_build = check_item_in_list(livet_build, product, livet_build_products)

        unofficial_hw_build_cmd = r"call %s %s %s %s %s" % (build_batch_file_path, product, bullseye_build, livet_build, relpkg)
        print ("unofficial_hw_build_cmd:%s" % unofficial_hw_build_cmd)
        status = os.system(unofficial_hw_build_cmd)
        print ("build status:%d" % status)
        if status is not 0:
            raise Exception()

        outputs_shared_folder = os.getenv('UNOFFICIAL_BUILD_SHARED_ROOT')
        if outputs_shared_folder and outputs_shared_folder != '' and outputs_shared_folder != 'None':
            build_shared_path = os.getenv('UNOFFICIAL_BUILD_SHARED_ROOT') + '/' + commit_id
        else:
            build_shared_path = UNOFFICIAL_BUILD_SHARED % (project, commit_id)

        print ('build_shared_path:%s' % build_shared_path)
        os.environ["UNOFFICIAL_BUILD_SHARED"] = build_shared_path

        if relpkg == 'true':
            output_dir = os.path.join(wsDir, '_out')
            out_file_list = os.listdir(output_dir)
            for file_name in out_file_list:
                print(file_name)
                if file_name.startswith('RelPkg_') and file_name.endswith('.zip'):
                    relpkg_file = os.path.join(output_dir, file_name)
                    (status, relpkg_zip_url) = uploadArtifactory(project, commit_id, relpkg_file)
                    break
            if status is not 0:
                raise Exception("Failed to upload Relpkg zip file to Artifactory")
            
            artifact_url_filename = '%s_%s_%s.txt' % (main_build_id, build_id, FO_ARTIFACT_URL) 
            artifact_url_filepath = os.path.join(CIToolsDir, artifact_url_filename)
            print ("artifact_url:%s" % relpkg_zip_url)

            with open(artifact_url_filepath, 'w') as artifact_url_fh:
                artifact_url_fh.write(relpkg_zip_url)

            copy_status = Utils.CopyFileToKRShared(commit_id, artifact_url_filepath, project)
            if copy_status is not 0:
                print ("Copying error file is failed.")
                    

    except Exception as e:
        print (e)
        traceback.print_exc()
        if status != 0:
            error_file = '%s_%s_%s.txt' % (main_build_id, build_id, FO_ERROR_FILE_NAME) 
            error_filepath = os.path.join(CIToolsDir, error_file)
            console_url = 'https://ksg-ep-jenm01.wdc.com/job/ci_task_runner_unofficial_build/%s/console' % build_id
            print ("console_url:%s" % console_url)

            with open(error_filepath, 'w') as efile:
                efile.write(console_url)

            copy_status = Utils.CopyFileToKRShared(commit_id, error_filepath, project)
            if copy_status is not 0:
                print ("Copying error file is failed.")
    return status

def doCovBuild(project, wsDir, product):
    status = 1
    try:
        status = CovBuild.run(project, wsDir, product)

    except Exception as e:
        print (e)
        traceback.print_exc()

    return status

def doTidyBuild(wsDir, product):
    status = 1
    try:
        (status, tidy_summary_file_url, tidy_errs_file_url) = TidyBuild.run(wsDir, product)

    except Exception as e:
        print (e)
        traceback.print_exc()

    return (status, tidy_summary_file_url, tidy_errs_file_url)

def doFilterOutput(project, wsDir, commitIDs, committers, commitTimes, commitFiles, commitMsgs):
    try:
        """
        Process logs for summary data
        """
        os.chdir(wsDir)

        artUrl = os.getenv('ARTIFACTORY_URL')
        repo = os.getenv("REPO")
        branch = os.getenv('BUILD_BRANCH')
        status = 0

        outFile = os.path.join(wsDir, FO_FILE)
        print ("outFile:%s" % outFile)
        if os.path.exists(outFile):
            fout = open(outFile, 'a')
            print ("outFile is already existed")
        else:
            fout = open(outFile, 'w')
            print ("outFile is created")

        doPack(wsDir, fout)

        notify = []
        indexOpen = committers[0].find("<")
        indexClose = committers[0].find(">")
        commiterEmail = committers[0][indexOpen + 1:indexClose]
        notify.append(commiterEmail)

        notifyStr = ""
        for anEmail in notify:
            notifyStr += anEmail + ", "

        fout.write("Notify=%s<br>" % (notifyStr))
        fout.close()

        os.system("c:\\utility\\jfrog rt config xArtifactory --url=%s/artifactory --user=%s --password=%s" % (artUrl, ARTIFACTORY_SVC_USER, ARTIFACTORY_SVC_USER_PASS))
        jfrogCmd = "c:\\utility\\jfrog rt upload %s fpg-css-fw-global/triton16/CI/builds/%s" % (outFile, commitIDs[0][:7])
        print ('Artifactory cmd: ', jfrogCmd)
        status = os.system(jfrogCmd)

        if status:
            print ('there is failure, not saving data')
        return status

    except Exception as e:
        print (e)
        traceback.print_exc()

def doPack(wsDir, fout, saveFolder):
    try:
        """
        finalize package distribution
        """

        os.chdir(wsDir)

        repo = os.getenv("REPO")
        branch = os.getenv('BUILD_BRANCH')
        commitId = os.getenv('COMMIT_ID')

        project = os.getenv("PROJECT")
        saveFolder = UNOFFICIAL_BUILD_SHARED % (project, commitId)
        print ("saveFolder:%s" % saveFolder)

        if os.path.exists(saveFolder):
            print ("%s found" % (saveFolder))

        msg = ""
        logfolder = os.path.join(saveFolder, "BuildLogs", repo, commitId)
        if os.path.exists(logfolder):  # confirm if there is a fail log in log folder
            for logfile in os.listdir(logfolder):
                if logfile.find("_FAIL") > -1:
                    msg = '\nWarning!!! A failure log %s found, some process inconsistency exists\n' % (logfile)
                    print (msg)
                    fout.write(msg)
                    break

        fout.write("<br>--------------------------<br>")
        fout.write("<br>Artifactory: https://ksg-ep-art01.wdc.com/artifactory/webapp/#/artifacts/browse/tree/General/fpg-css-fw-ksg/triton16/CI/builds/%s<br>" %(commitId))

    except Exception as e:
        print (e)
        traceback.print_exc()


def uploadArtifactoryWOCommitID(filepath, repo_path="fpg-css-fw-global/triton16/CI/builds"):

    try:

        artUrl = os.getenv('ARTIFACTORY_URL', r'https://ksg-ep-art01.wdc.com')

        config_cmd = "c:\\utility\\jfrog rt config xArtifactory --url=%s/artifactory --user=%s --password=%s" % (artUrl, ARTIFACTORY_SVC_USER, ARTIFACTORY_SVC_USER_PASS)
        print ("arti_config_cmd:%s" % config_cmd)
        os.system(config_cmd)
        filename = ntpath.basename(filepath)
        upload_cmd = "c:\\utility\\jfrog rt upload %s %s/%s" % (filepath, repo_path, filename)
        print ("upload_cmd:%s" % upload_cmd)
        os.system(upload_cmd)
        file_url = "%s/artifactory/%s/%s" % (artUrl, repo_path, filename)
        print("file_url:%s" % file_url)
        return file_url

    except Exception as e:
        print (e)
        traceback.print_exc()

def uploadArtifactory(project, commit_id, filepath, repo_path=None):
    status = -1
    file_url = None
    try:

        config_cmd = "c:\\utility\\jfrog rt config xArtifactory --url=%s --user=%s --password=%s" % (KR_ARTIFACTORY_URL, ARTIFACTORY_SVC_USER, ARTIFACTORY_SVC_USER_PASS)
        print ("arti_config_cmd:%s" % config_cmd)
        os.system(config_cmd)
        filename = ntpath.basename(filepath)
        if repo_path is None or repo_path == '':
            repo_path = UB_ARTIFACTORY_REPO % (project, commit_id, filename)
        upload_cmd = "c:\\utility\\jfrog rt upload %s %s" % (filepath, repo_path)
        print ("upload_cmd:%s" % upload_cmd)
        os.system(upload_cmd)
        file_url = "%s/%s" % (KR_ARTIFACTORY_URL, repo_path)
        print("file_url:%s" % file_url)
        status = 0
    except Exception as e:
        status = 1
        print (e)
        traceback.print_exc()
    return (status, file_url)

def generateBuildResult(wsDir, product):
    status = 1
    try:
        os.chdir(wsDir)
        project = os.getenv("PROJECT")
        repo = os.getenv("REPO")
        branch = os.getenv('BUILD_BRANCH')
        main_build_id = os.getenv('MAIN_BUILD_ID')
        print (os.getenv("StartTime"))
        startTime = float(os.getenv("StartTime"))
        print (time.time())
        duration = time.time() - startTime
        print (duration)
        durhrs = int (duration/3600)
        durmins = int ((duration - durhrs * 3600) / 60)
        dursecs = int (duration - (durhrs * 3600 + durmins * 60))

        giturl = ""
        f = open(os.path.join(wsDir, ".git", "config"), 'r')
        lines = f.readlines()
        for aLine in lines:
            if aLine.find("url") > -1:
                splits = aLine.split("=")
                giturl = splits[1]

        commitIDs = []
        committers = []
        commitMsgs = []
        commitTimes = []
        commitFiles = []

        os.system("git log -n2 > gitlog.txt")

        f = open("gitlog.txt", 'r')
        lines = f.readlines()

        for aLine in lines:
            splits = aLine.split()
            if aLine.find("commit") == 0:
                commitIDs.append(splits[1])
            elif aLine.find("Author:") > -1:
                index = aLine.find(":")
                committers.append(aLine[8:-1])
            elif aLine.find("Date:") > -1:
                commitTimes.append(aLine[8:-6])

        os.system("git log --pretty=format:\"%h - %an, %ar : %s\" -n2 > gitlog.txt")
        f = open("gitlog.txt", 'r')
        lines = f.readlines()
        for aLine in lines:
            index = aLine.find(":")
            commitMsgs.append(aLine[index+2:-1])

        os.system("git diff %s %s --name-only > gitlog.txt" %(commitIDs[0], commitIDs[1]))
        f = open("gitlog.txt", 'r')
        lines = f.readlines()
        for aLine in lines:
            commitFiles.append(aLine)

        commit_id = os.getenv("COMMIT_ID")

        local_bot_path = os.path.join(wsDir, CITaskGenerator.SANDISK_OUTPUT, product, 'BOT', 'CFG.bot')
        print ("local_bot_path:%s"  % local_bot_path)
        (bot_commit_id, fw_version) = GetLocalTestnfo.readBotFile(local_bot_path)
        print ("fw_version:%s"  % fw_version)
        bot_commit_id = bot_commit_id[:7].lower()
        print ("bot_commit_id:%s"  % bot_commit_id)

        if commit_id.lower() != bot_commit_id:
            err_msg = "Given commit id(%s) and commit id(%s) in Bot file did not match" % (commit_id, bot_commit_id)
            print (err_msg)
            if project != 'calypsox':
                raise Exception(err_msg)
            else:
                # WA: calypsox bot file has an issue that is set always 0xFFFFFFFF commit id, so the error is ignored until correct commit id is set
                print ('WARNING:' + err_msg)

        outFile = os.path.join(wsDir, main_build_id + "_filteroutput.txt")
        fout = open(outFile,'w')

        fout.write("<font face='verdana' size='2'>")
        fout.write("Repository: %s<br>" %(repo))
        fout.write("Branch: %s<br>" %(branch))
        fout.write("Last commit: %s<br>" %(commit_id))
        fout.write("FW version: %s<br>" %(fw_version))
        fout.write("Build output path: %s<br>" %(os.getenv("UNOFFICIAL_BUILD_SHARED", "")))
        fout.write("Date of build: %s<br>" %(os.getenv("BUILD_TIMESTAMP", "NA")))
        fout.write("Build time: %02d:%02d:%02d<br>" %(durhrs, durmins, dursecs))
        fout.write("Last commit time: %s<br>" %(commitTimes[0]))
        fout.write("Last commit msg: %s<br>" %(commitMsgs[0]))
        fout.write("Author: %s<br>" %(committers[0]))
        fout.write("GIT URL: %s<br>" %(giturl))
        fout.close()
        uploadArtifactoryWOCommitID(outFile, UB_ARTIFACTORY_REPO)

        status = 0

    except Exception as e:
        print (e)
        traceback.print_exc()
    return status

def generateTidyBuildResult(wsDir, product, tidy_summary_file_url, tidy_errs_file_url):
    status = 1
    try:
        print(wsDir)
        os.chdir(wsDir)
        project = os.getenv("PROJECT")
        repo = os.getenv("REPO")
        branch = os.getenv('BUILD_BRANCH')
        print (os.getenv("StartTime"))
        startTime = float(os.getenv("StartTime"))
        print (time.time())
        duration = time.time() - startTime
        print (duration)
        durhrs = int (duration/3600)
        durmins = int ((duration - durhrs * 3600) / 60)
        dursecs = int (duration - (durhrs * 3600 + durmins * 60))

        giturl = ""
        f = open(os.path.join(wsDir, ".git", "config"), 'r')
        lines = f.readlines()
        for aLine in lines:
            print(aLine)
            if aLine.find("url") > -1:
                splits = aLine.split("=")
                giturl = splits[1]

        commitIDs = []
        committers = []
        commitMsgs = []
        commitTimes = []
        commitFiles = []

        os.system("git log -n2 > gitlog.txt")

        f = open("gitlog.txt", 'r')
        lines = f.readlines()
        print('gitlog.txt file exsits')
        for aLine in lines:
            print(aLine)
            splits = aLine.split()
            if aLine.find("commit") == 0:
                commitIDs.append(splits[1])
            elif aLine.find("Author:") > -1:
                index = aLine.find(":")
                committers.append(aLine[8:-1])
            elif aLine.find("Date:") > -1:
                commitTimes.append(aLine[8:-6])

        os.system("git log --pretty=format:\"%h - %an, %ar : %s\" -n2 > gitlog.txt")
        f = open("gitlog.txt", 'r')
        lines = f.readlines()
        for aLine in lines:
            index = aLine.find(":")
            commitMsgs.append(aLine[index+2:-1])

        os.system("git diff %s %s --name-only > gitlog.txt" %(commitIDs[0], commitIDs[1]))
        f = open("gitlog.txt", 'r')
        lines = f.readlines()
        for aLine in lines:
            commitFiles.append(aLine)

        commit_id = commitIDs[0][:7]
        outFile = os.path.join(wsDir,"filteroutput_tidy.txt")
        fout = open(outFile,'w')

        fout.write("Repository: %s \n" %(repo))
        fout.write("Branch: %s \n" %(branch))
        fout.write("Last commit: %s \n" %(commit_id))
        fout.write("Date of build: %s \n" %(os.getenv("BUILD_TIMESTAMP", "NA")))
        fout.write("Build time: %02d:%02d:%02d \n" %(durhrs, durmins, dursecs))
        fout.write("Last commit time: %s \r\n" %(commitTimes[0]))
        fout.write("Last commit msg: %s \n" %(commitMsgs[0]))
        fout.write("Author: %s \r\n" %(committers[0]))
        fout.write("GIT URL: %s \n" %(giturl))
        fout.write("Tidy Summary file URL: %s \n" %(tidy_summary_file_url))
        fout.write("Tidy Error file URL: %s \n" %(tidy_errs_file_url))
        fout.close()

        (status, file_url) = uploadArtifactory(project, commit_id, outFile)

    except Exception as e:
        print (e)
        traceback.print_exc()
    return status

if __name__ == "__main__":
    wsDir=r"C:\WDLABS\BuildTrees\workspace\NVMeCITasks"
    product="atlas_t16"
    doFW(wsDir, product)
    

