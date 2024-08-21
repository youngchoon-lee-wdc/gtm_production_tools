import logging
import os, traceback, sys
from subprocess import Popen, PIPE, STDOUT
from optparse import OptionParser

_filepath = os.path.realpath(__file__)
print ("filepath:%s" % _filepath)
_current_dir = os.path.dirname(_filepath)

CVF_HOME=r"C:\Program Files (x86)\SanDisk\CVF_3.0_x64"

def add_parse_arguments():
    usage = """usage: GTM_CVF_Production.py [options] arg
            e.g.)GTM_CVF_Production.py -i Yes -c a123abc -p atlas"
            """
    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--commit_id", action="store", type="string", dest="commit_id")
    parser.add_option("-w", "--fw_version", action="store", type="string", dest="fw_version")
    parser.add_option("-i", "--isPerformanceApp", action="store", type="string", dest="isPerformanceApp")
    parser.add_option("-v", "--device_vendor", action="store", type="string", dest="device_vendor")
    parser.add_option("-s", "--device_serial_number", action="store", type="string", dest="device_serial_number")
    parser.add_option("-d", "--device_capacity", action="store", type="string", dest="device_capacity")
    parser.add_option("-r", "--project", action="store", type="string", dest="project")
    parser.add_option("-f", "--cvf_version", action="store", type="string", dest="cvf_version")

    return parser.parse_args()

if __name__ == "__main__":
    logger = logging.getLogger('GTM_Production')
    rc = -1
    try:
        log_path = './'
        log_file_name = 'gtm_production'
        fileHandler = logging.FileHandler("{0}/{1}.log".format(log_path, log_file_name),mode='w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)
        logger.addHandler(consoleHandler)
        log_level = logging.DEBUG
        logger.setLevel(log_level)        
        # if _current_dir.find(CVF_HOME) == -1:
        #     raise Exception("You have to run it in %s" % CVF_HOME)
        options, args = add_parse_arguments()
        commit_id = options.commit_id
        fw_version = options.fw_version
        isPerformanceApp = options.isPerformanceApp
        device_vendor = options.device_vendor
        device_serial_number = options.device_serial_number
        device_capacity = options.device_capacity
        project = options.project
        cvf_version = options.cvf_version
        if commit_id == '' or fw_version == '' or device_vendor == '' or device_serial_number == '' or device_capacity == '' or project == '' or cvf_version == '':
            raise Exception('No given option value are found')        
        if isPerformanceApp == '' or isPerformanceApp.lower() == 'no':
            raise Exception('GTM production tool supports to run Performance(CDM/IOMeter/SSW) only for now')        
        if len(commit_id) < 8:
            raise Exception('The commit id must be at least 8 characters long.')
        short_commit_id = commit_id[:8]
        gtm_production_bat = os.path.join(os.path.dirname(_filepath), 'gtm_production_%s.bat' % project.lower())    
        logger.debug(gtm_production_bat)
        run_bat_cmd = 'gtm_production_%s.bat %s %s %s %s %s %s' % (project, short_commit_id, device_vendor, device_serial_number, device_capacity, cvf_version, fw_version)
        logger.debug(run_bat_cmd)
        cmd_list = run_bat_cmd.split()
        p = Popen(cmd_list, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        while True:
            output = p.stdout.readline()
            if output == b'' and p.poll() is not None:
                break
            if output:
                logger.debug(output.decode().strip())  # Decode bytes to string for logging
            p.poll()

        rc = p.returncode 
        logger.info("rc:%d" % rc)
        if rc != 0:
            raise Exception("Failed to run the batch file")           

        # os.system("shutdown /r /t 2")

    except Exception as err:
        logger.error(err, exc_info=1)
        traceback.print_exc()
    
    sys.exit(rc)