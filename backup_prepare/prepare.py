#!/opt/Python-3.3.2/bin/python3

# Backup Prepare and Copy-Back Script
# Originally Developed by
# Shahriyar Rzayev -> http://www.mysql.az
# / rzayev.sehriyar@gmail.com / rzayev.shahriyar@yandex.com

import configparser
import os
import shlex
import subprocess
import shutil
import time
from general_conf.generalops import GeneralClass

import logging
logger = logging.getLogger(__name__)

class Prepare(GeneralClass):
    def __init__(self):
        GeneralClass.__init__(self)
        from master_backup_script.check_env import CheckEnv
        self.check_env_obj = CheckEnv()
        self.result = self.check_env_obj.check_systemd_init()

    def recent_full_backup_file(self):
        # Return last full backup dir name

        if len(os.listdir(self.full_dir)) > 0:
            return max(os.listdir(self.full_dir))
        else:
            return 0

    def check_inc_backups(self):
        # Check for Incremental backups

        if len(os.listdir(self.inc_dir)) > 0:
            return 1
        else:
            return 0


    #############################################################################################################
    # PREPARE ONLY FULL BACKUP
    #############################################################################################################

    def prepare_only_full_backup(self):
        if self.recent_full_backup_file() == 0:
            logger.debug("####################################################################################################")
            logger.debug("You have no FULL backups. First please take FULL backup for preparing - - - - - - - - - - - - - -  #")
            logger.debug("####################################################################################################")
            exit(0)
        elif self.check_inc_backups() == 0:
            logger.debug("################################################################################################")
            logger.debug("Preparing Full backup 1 time - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #")
            logger.debug("################################################################################################")
            time.sleep(3)
            args = '%s %s %s/%s' % (self.backup_tool, self.xtrabck_prepare, self.full_dir, self.recent_full_backup_file())
            status, output = subprocess.getstatusoutput(args)
            if status == 0:
                logger.debug(output[-27:])
                logger.debug("################################################################################################")
                logger.debug("Preparing Again Full Backup for final usage. - - - - - - - - - - - - - - - - - - - - - - - - - #")
                logger.debug("################################################################################################")

                args2 = '%s --apply-log %s/%s' % (self.backup_tool, self.full_dir, self.recent_full_backup_file())
                status2, output2 = subprocess.getstatusoutput(args2)
                if status2 == 0:
                    logger.debug(output2[-27:])
                    return True
                else:
                    logger.error("FULL BACKUP 2nd PREPARE FAILED!")
                    time.sleep(5)
                    logger.error(output2)
                    return False
            else:
                logger.error("FULL BACKUP 1st PREPARE FAILED!")
                time.sleep(5)
                logger.error(output)
                return False

        else:
            logger.debug("Preparing Full backup 1 time. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#\n"
                  "Final prepare,will occur after preparing all inc backups - - - - - - - - - - - - - - - - -  - - - -#")
            logger.debug("####################################################################################################")
            time.sleep(3)
            args = '%s %s %s/%s' % (self.backup_tool, self.xtrabck_prepare, self.full_dir, self.recent_full_backup_file())
            status, output = subprocess.getstatusoutput(args)
            if status == 0:
                logger.debug(output[-27:])
                return True
            else:
                logger.error("One time FULL BACKUP PREPARE FAILED!")
                time.sleep(5)
                logger.error(output)
                return False


    ##############################################################################################################
    # PREPARE INC BACKUPS
    ##############################################################################################################

    def prepare_inc_full_backups(self):
        if self.check_inc_backups() == 0:
            logger.debug("################################################################################################")
            logger.debug("You have no Incremental backups. So will prepare only latest Full backup - - - - - - - - - - - #")
            logger.debug("################################################################################################")
            time.sleep(3)
            self.prepare_only_full_backup()
        else:
            logger.debug("####################################################################################################")
            logger.debug("You have Incremental backups. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#")
            time.sleep(3)
            if self.prepare_only_full_backup():
                logger.debug("####################################################################################################")
                logger.debug("Preparing Incs: ")
                time.sleep(3)
                list_of_dir = sorted(os.listdir(self.inc_dir))

                for i in list_of_dir:
                    if i != max(os.listdir(self.inc_dir)):
                        logger.debug("Preparing inc backups in sequence. inc backup dir/name is %s" % i)
                        logger.debug("####################################################################################################")
                        time.sleep(3)
                        args = '%s %s %s/%s --incremental-dir=%s/%s' % (self.backup_tool, self.xtrabck_prepare,
                                                                        self.full_dir, self.recent_full_backup_file(),
                                                                        self.inc_dir, i)


                        status, output = subprocess.getstatusoutput(args)
                        if status == 0:
                            logger.debug(output[-27:])
                        else:
                            logger.error("Incremental BACKUP PREPARE FAILED!")
                            time.sleep(5)
                            logger.error(output)
                            return False

                    else:
                        logger.debug("####################################################################################################")
                        logger.debug("Preparing last incremental backup, inc backup dir/name is %s" % i)
                        logger.debug("####################################################################################################")
                        time.sleep(3)
                        args2 = '%s --apply-log %s/%s --incremental-dir=%s/%s' % (self.backup_tool,
                                                                                 self.full_dir,
                                                                                 self.recent_full_backup_file(),
                                                                                 self.inc_dir, i)
                        status2, output2 = subprocess.getstatusoutput(args2)
                        if status2 == 0:
                            logger.debug(output2[-27:])
                        else:
                            logger.error("Incremental BACKUP PREPARE FAILED!")
                            time.sleep(5)
                            logger.error(output2)
                            return False

            logger.debug("####################################################################################################")
            logger.debug("The end of Prepare Process. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#")
            logger.debug("Preparing FULL backup Again: - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #")
            logger.debug("####################################################################################################")
            time.sleep(3)

            args3 = '%s --apply-log %s/%s' % (self.backup_tool, self.full_dir, self.recent_full_backup_file())

            status3, output3 = subprocess.getstatusoutput(args3)
            if status3 == 0:
                logger.debug(output3[-27:])
                return True
            else:
                logger.error("Full BACKUP PREPARE FAILED!")
                time.sleep(5)
                logger.error(output3)
                return False

    #############################################################################################################
    # COPY-BACK PREPARED BACKUP
    #############################################################################################################

    def shutdown_mysql(self):

        # Shut Down MySQL
        logger.debug("####################################################################################################")
        logger.debug("Shutting Down MySQL server: - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#")
        logger.debug("####################################################################################################")
        time.sleep(3)


        if self.result == 3:
            args = self.systemd_stop_mariadb
        elif self.result == 4:
            args = self.stop_mysql
        elif self.result == 5:
            args = self.systemd_stop_mysql
        elif self.result == 6:
            args = self.stop_mysql

        status, output = subprocess.getstatusoutput(args)
        if status == 0:
            logger.debug(output)
            return True
        else:
            logger.deberrorug("Could not Shutdown MySQL!")
            logger.error("Refer to MySQL Error log file")
            logger.error(output)
            return False


    def move_datadir(self):

        # Move datadir to new directory
        logger.debug("####################################################################################################")
        logger.debug("Moving MySQL datadir to /tmp/mysql: - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#")
        logger.debug("####################################################################################################")
        time.sleep(3)
        if os.path.isdir(self.tmpdir):
            rmdirc = 'rm -rf %s' % self.tmpdir
            status, output = subprocess.getstatusoutput(rmdirc)

            if status == 0:
                logger.debug("Emptied /tmp/mysql directory ...")

                try:
                    shutil.move(self.datadir, self.tmp)
                    logger.debug("Moved datadir to /tmp/mysql ...")
                except shutil.Error as err:
                    logger.error("Error occurred while moving datadir")
                    logger.error(err)
                    return False

                logger.debug("Creating an empty data directory ...")
                makedir = self.mkdir_command
                status2, output2 = subprocess.getstatusoutput(makedir)
                if status2 == 0:
                    logger.debug("/var/lib/mysql Created! ...")
                else:
                    logger.error("Error while creating datadir")
                    logger.error(output2)
                    return False

                return True

            else:
                logger.error("Could not delete /tmp/mysql directory")
                logger.error(output)
                return False

        else:
            try:
                shutil.move(self.datadir, self.tmp)
                logger.debug("Moved datadir to /tmp/mysql ...")
            except shutil.Error as err:
                logger.error("Error occurred while moving datadir")
                logger.error(err)
                return False

            logger.debug("Creating an empty data directory ...")
            makedir = self.mkdir_command
            status2, output2 = subprocess.getstatusoutput(makedir)
            if status2 == 0:
                logger.debug("/var/lib/mysql Created! ...")
                return True
            else:
                logger.error("Error while creating datadir")
                logger.error(output2)
                return False


    def run_xtra_copyback(self):
        # Running Xtrabackup with --copy-back option

        copy_back = '%s --copy-back %s/%s' % (self.backup_tool,
                                                  self.full_dir,
                                                  self.recent_full_backup_file())

        status, output = subprocess.getstatusoutput(copy_back)

        if status == 0:
            logger.debug("####################################################################################################")
            logger.debug("Data copied back successfully! - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #")
            logger.debug("####################################################################################################")
            return True
        else:
            logger.error("Error occurred while copying back data!")
            logger.error(output)
            return False


    def giving_chown(self):
        # Changing owner of datadir to mysql:mysql
        time.sleep(3)
        give_chown = self.chown_command
        status, output = subprocess.getstatusoutput(give_chown)

        if status == 0:
            logger.debug("####################################################################################################")
            logger.debug("New copied-back data now owned by mysql:mysql - - - - - - - - - - - - - - - - - - - - - - - - - - -#")
            logger.debug("####################################################################################################")
            return True
        else:
            logger.error("Error occurred while changing owner!")
            logger.error(output)
            return False


    def start_mysql_func(self):
        # Starting MySQL/Mariadb
        logger.debug("####################################################################################################")
        logger.debug("Starting MySQL/MariaDB server: ")
        logger.debug("####################################################################################################")
        time.sleep(3)

        if self.result == 3:
            args = self.systemd_start_mariadb
        elif self.result == 4:
            args = self.start_mysql
        elif self.result == 5:
            args = self.systemd_start_mysql
        elif self.result == 6:
            args = self.start_mysql




        start_command = args
        status, output = subprocess.getstatusoutput(start_command)
        if status == 0:
            logger.debug("Starting MySQL ...")
            logger.debug(output)
            return True
        else:
            logger.error("Error occurred while starting MySQL!")
            logger.error(output)
            return False



    def copy(self):

        logger.debug("####################################################################################################")
        logger.debug("Copying Back Already Prepared Final Backup: - - - - - - - - - - - - - - - - - - - - - - - - - - - -#")
        logger.debug("####################################################################################################")
        time.sleep(3)
        if len(os.listdir(self.datadir)) > 0:
            logger.debug("MySQL Datadir is not empty!")
            return False
        else:
            if self.run_xtra_copyback():
                if self.giving_chown():
                    if self.start_mysql_func():
                        return True
                    else:
                        "Error Occurred!"




    def copy_back(self):

        if self.shutdown_mysql():
            if self.move_datadir():
                if self.copy():
                    logger.debug("####################################################################################################")
                    logger.debug("All data copied back successfully your MySQL server is UP again. \n"
                            "Congratulations. \n"
                            "Backups are life savers")
                    logger.debug("####################################################################################################")
                    return True
                else:
                    logger.error("Error Occurred!")




    ##############################################################################################################
    # FINAL FUNCTION FOR CALL: PREPARE/PREPARE AND COPY-BACK/COPY-BACK
    ##############################################################################################################


    def prepare_backup_and_copy_back(self):
    # Recovering/Copying Back Prepared Backup
        #print("#####################################################################################################")
        print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-")
        print("")
        print("Preparing full/inc backups!")
        print("What do you want to do?")
        print("1. Prepare Backups and keep for future usage. NOTE('Once Prepared Backups Can not be prepared Again')")
        print("2. Prepare Backups and restore/recover/copy-back immediately")
        print("3. Just copy-back previously prepared backups")

        prepare = int(input("Please Choose one of options and type 1 or 2 or 3: "))
        print("")
        print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-")
        time.sleep(3)
        #print("####################################################################################################")
        if prepare == 1:
            self.prepare_inc_full_backups()
        elif prepare == 2:
            self.prepare_inc_full_backups()
            self.copy_back()
        elif prepare == 3:
            self.copy_back()
        else:
            print("Please type 1 or 2 or 3 and nothing more!")


# a = Prepare()
# a.prepare_backup_and_copy_back()