# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 19:36:58 2016
DupFiler
V1.0Beta
@author: Mike

add #!/usr/bin/env python on first line of python script to make exe on nix
//also chmod +x leduh
"""
import hashlib #needed to hash files
import base64 #for encoding shit
import os
import sys
import datetime # For timestamps on logging
# http://stackoverflow.com/questions/26455616/how-can-i-create-basic-timestamps-or-dates-python-3-4
#http://www.tutorialspoint.com/python/python_files_io.htm
#http://pythoncentral.io/finding-duplicate-files-with-python/
import shutil


def SHA(fName): #This is the main hash function
    """ Notes:
    Can store in model like this:
    class Document(models.Model):
    hash = models.CharField(max_length=44L, unique=True )
    - See more at: http://blog.wculver.com/webdev/django-python-storing-a-sha256-hash-of-a-file-as-a-base64-encoded-string/#sthash.zs2mcMPx.dpuf
    """
    with open(fName, "rb") as f: #read file in binary mode
        m = hashlib.sha256()
        m.update(f.read())
        sha = m.digest()
        hash = base64.b64encode(sha)
    f.closed #close the damn file!!!!!!111
    return hash
    
def SHA2(fName):
    with open(fName, "rb") as f:
        m = hashlib.sha256(fName)
    f.closed
    return m.hexdigest()
    
def hashFile(fName, blocksize = 65536):
#    stolen from:
#    http://pythoncentral.io/finding-duplicate-files-with-python/
#    http://pythoncentral.io/hashing-files-with-python/
    afile = open(fName, 'rb')
    #hasher = hashlib.md5()
    hasher = hashlib.sha256()    
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()

def testMode():
    '''
    Find dups in dir 1 and 2, print a report text file
        - need to organize, these files in some dir, not just clusterfuck of shit
    '''
    print('Test Mode:')
    
    ### Setup Folders ###
    slave_path = './slavebackup'
    master_path = './masterbackup'
    printFilesHash(slave_path)    
    printFilesHash(master_path)        
    #files_list = getFilesList('.')
    #files_dict = getFilesDict('.')      
    dupdict_test = {}
    dupdict_test2 = {}
    # fuck it no moar lists
    slave_files_dict = getFilesDict(slave_path)
    master_files_dict = getFilesDict(master_path)
    # Add exclude folder option to ^^
    
    ### Logging ###
    # The only thing that should be printed/displayed is progress or fatal errors
    log_folder = 'DupFiler Logs'    
    folder_exists = False
    
    try:
        os.mkdir(log_folder)
    except FileExistsError:
        #print('Folder already exists')
        folder_exists = True
        
    main_log_name = 'main_log.txt'
    master_dup_log = 'master_dups.txt'
    duplicates_log = 'duplicates.txt'
    global MAIN_LOG_PATH    
    global MASTER_DUP_PATH
    global DUP_PATH
    global TIMESTAMP
    MAIN_LOG_PATH = './' + log_folder + '\\' + main_log_name
    MASTER_DUP_PATH = './' + log_folder + '\\' + master_dup_log    
    DUP_PATH = './' + log_folder + '\\' + duplicates_log    
    TIMESTAMP = '[{:%b-%d-%Y %H:%M:%S}] '.format(datetime.datetime.now())
    main_log = open(MAIN_LOG_PATH, 'w')
    main_log.write(TIMESTAMP + '------------ Main Log Begin ------------\n\n')
    if folder_exists == True:
        main_log.write(TIMESTAMP + 'Information: Folder: "' + log_folder + '" already exists.\n')
    main_log.close()
    
    ### Excluding ###
    # TODO: add text file entry, also exclude itself from search
    exclude_list = [] 
    #master_path + '\\' + log_folder, 
    # Be VERY CAREFUL with this, as any matched string will be excluded
    # Ideally, keep backups in an archive that will have different hash altogether
    exclude_list = [master_path + '\exclude', master_path + '\exclude2\\']
    
    # Remove folders that are on exclude list
    master_files_dict = removeExclusions(master_files_dict, exclude_list)
    
    # First check master for dups and decide which to move to
    if checkForDups(master_files_dict) == True:
        sys.exit('Remove the duplicates found in "' + MASTER_DUP_PATH + '" before proceeding!')
        
    dup_log = open(DUP_PATH, 'w')
    
    dup_list = []
    # Master is assumed to have more shit, so want to iterate through less
    for entries in master_files_dict:
        for possdups in slave_files_dict:
            #if (possdups in slave_files_dict == entries in master_files_dict):
             #   print(possdups + entries)
            if (master_files_dict[entries] == slave_files_dict[possdups]):
                print('Dup Detected!!:')
                #print('Master: ' + master_files_dict[entries] + '\nSlave:' + slave_files_dict[possdups])
                print('Master: ' + entries + '\nSlave:' + possdups)
                
                dupdict_test[entries] = possdups #dict of master:slave dups
                # This does not work WTF. Missing the duplicate inside folder
                    # Because cannot have duplicate keys, where keys:values
                # Try a list, maybe some weird shit with dict datastructure
                dupdict_test2[possdups] = entries #This works.
                dup_list.append([possdups, entries])
                dup_log.write(TIMESTAMP + 'Duplicates:\n\t\t\t\tMaster: "' + entries + '"\n\t\t\t\tSlave:  "' + possdups + '\n\n')
                # Need try catch for actual copying so can throw exception
                # Test dups in master and dups in slave
    
    dup_log.close()    
        
    return slave_files_dict, master_files_dict, dupdict_test, dupdict_test2, dup_list

def analysisMode():
    '''
    Find dups in dir 1 and 2, print a report text file
        - need to organize, these files in some dir, not just clusterfuck of shit
    '''
    print('Analysis Mode:')
    dupdict_test = {}
    dupdict_test2 = {}
    
    ### Setup Folders ###
    slave_path = './slave'
    master_path = './master'
    printFilesHash(slave_path)    
    printFilesHash(master_path)        
    
    # fuck it no moar lists
    slave_files_dict = getFilesDict(slave_path)
    master_files_dict = getFilesDict(master_path)
    # Add exclude folder option to ^^
    
    ### Logging ###
    # The only thing that should be printed/displayed is progress or fatal errors
    log_folder = 'DupFiler Logs'    
    folder_exists = False
    
    try:
        os.mkdir(log_folder)
    except FileExistsError:
        #print('Folder already exists')
        folder_exists = True
        
    main_log_name = 'main_log.txt'
    master_dup_log = 'master_dups.txt'
    duplicates_log = 'duplicates.txt'
    global MAIN_LOG_PATH    
    global MASTER_DUP_PATH
    global DUP_PATH
    global TIMESTAMP
    MAIN_LOG_PATH = './' + log_folder + '\\' + main_log_name
    MASTER_DUP_PATH = './' + log_folder + '\\' + master_dup_log    
    DUP_PATH = './' + log_folder + '\\' + duplicates_log    
    TIMESTAMP = '[{:%b-%d-%Y %H:%M:%S}] '.format(datetime.datetime.now())
    main_log = open(MAIN_LOG_PATH, 'w')
    main_log.write(TIMESTAMP + '------------ Main Log Begin ------------\n\n')
    if folder_exists == True:
        main_log.write(TIMESTAMP + 'Information: Folder: "' + log_folder + '" already exists.\n')
    main_log.close()
    
    ### Excluding ###
    # TODO: add text file entry, also exclude itself from search
    exclude_list = [] 
    #master_path + '\\' + log_folder, 
    # Be VERY CAREFUL with this, as any matched string will be excluded
    # Ideally, keep backups in an archive that will have different hash altogether
    exclude_list = [master_path + '\exclude', master_path + '\exclude2\\']
    
    # Remove folders that are on exclude list
    master_files_dict = removeExclusions(master_files_dict, exclude_list)
    
    # First check master for dups and decide which to move to
    if checkForDups(master_files_dict) == True:
        sys.exit('Remove the duplicates found in "' + MASTER_DUP_PATH + '" before proceeding!')
        
    dup_log = open(DUP_PATH, 'w')
    
    dup_list = []
    # Master is assumed to have more shit, so want to iterate through less
    for entries in master_files_dict:
        for possdups in slave_files_dict:
            #if (possdups in slave_files_dict == entries in master_files_dict):
             #   print(possdups + entries)
            if (master_files_dict[entries] == slave_files_dict[possdups]):
                print('Dup Detected!!:')
                #print('Master: ' + master_files_dict[entries] + '\nSlave:' + slave_files_dict[possdups])
                print('Master: ' + entries + '\nSlave:' + possdups)
                
                dupdict_test[entries] = possdups #dict of master:slave dups
                # This does not work WTF. Missing the duplicate inside folder
                    # Because cannot have duplicate keys, where keys:values
                # Try a list, maybe some weird shit with dict datastructure
                dupdict_test2[possdups] = entries #This works.
                dup_list.append([possdups, entries]) # Slave, master
                dup_log.write(TIMESTAMP + 'Duplicates:\n\t\t\t\tMaster: "' + entries + '"\n\t\t\t\tSlave:  "' + possdups + '\n\n')
                # Need try catch for actual copying so can throw exception
                # Test dups in master and dups in slave

    dup_log.close()
    
    print('Please review the list of duplicates found in: "' + DUP_PATH + '". If you aren\'t ABSOLUTELY SURE these can be overwritten, do not continue.  Continue? (y/n)\n' )
    user_input = input()
    if user_input == ('n' or 'N'):
        main_log = open(MAIN_LOG_PATH, 'a')
        main_log.write(TIMESTAMP + 'Information: User ended program without moving duplicates\n')
        main_log.close()
        sys.exit('User terminated.')
    
    dup_log = open(DUP_PATH, 'a')    
    for files in dup_list:
        shutil.copy2(files[0], files[1])
        os.remove(files[0])
        dup_log.write(TIMESTAMP + 'Duplicate file: "' + files[0] + '" moved to: "' + files[1] + '"\n')
                
    dup_log.close()    
        
    return slave_files_dict, master_files_dict, dupdict_test, dupdict_test2, dup_list

def removeExclusions(some_dict, exclude_list):
    main_log = open(MAIN_LOG_PATH, 'a')
    editable_dict = dict(some_dict)    
    for entries in some_dict:
        for exclusions in exclude_list:
            if exclusions in entries:
                try:
                    del editable_dict[entries]
                except KeyError:
                    #print('key error detected, value already taken care of.')
                    main_log.write(TIMESTAMP + 'Information: Key Error when "' + exclusions + '" in "' + entries + '", deleting "' + entries + '" from master dict\n')
                    #main_log.write('towel')
    main_log.close()
    return editable_dict
    
def removeKey(d, key):
    r = dict(d)
    del r[key]
    return r
    
def checkForDups(dict_of_file_w_hash):
    main_log = open(MAIN_LOG_PATH, 'a')
    dup_log = open(MASTER_DUP_PATH, 'w')
    
    dup_found = False    
    identicaldict = dict_of_file_w_hash
    # Needed to stop duplicates of duplicates detection    
    copies = []    
    
    for entries in dict_of_file_w_hash:
        for dupentries in identicaldict:
            # If the key is the same, and the path is not, and has not been handled before
            if ((dict_of_file_w_hash[entries] == identicaldict[dupentries]) & (entries != dupentries) & (entries not in copies)):
                #print('File: ' + entries + 'Has another copy, here: ' + dupentries)
                dup_log.write(TIMESTAMP + 'File: "' + entries + '" Has another copy, here: "' + dupentries + '"\n')     
                
                copies.append(dupentries)
                dup_found = True
    if dup_found == True:
        dup_log.write(TIMESTAMP + 'ERROR: Remove duplicates within master before proceeding (program doesn\'t know where to put dups from slave!)\n')        
        main_log.write(TIMESTAMP + 'ERROR: Dup on Master. See "' + MASTER_DUP_PATH+ '". Remove, exclude or archive these to proceed.\n')
        #print('Dups detected in master, take care of before running')
    elif dup_found == False:
        dup_log.write(TIMESTAMP + 'No duplicate files found within master!\n')        
        main_log.write(TIMESTAMP + 'Information: No duplicate files found on master. Proceeding with requested operations.\n')
        #print('No dups detected in Master') # Put actual path maybe?
    
    dup_log.close()    
    main_log.close()    
    return dup_found
                
                
def printFilesHash(path):
    # A test function for getting files list/dict
    print('\nPrinting files in path: "' + path + '"')
    # topdown=False searches dirs first ( I do it manually set to True)
    for root, dirs, files in os.walk(path, topdown=True): 
        # Removed because dir is listed in name in files
        #print("Dirs:")
        #for name in dirs:
        #    print(os.path.join(root, name) + ' //dir')
            
            #print("Files:")
        for name in files:
            #print(os.path.join(root, name), 'SHA256: ', SHA(name))
            print(os.path.join(root, name), 'SHA256: ', hashFile(os.path.join(root,name)))
            #print(os.path.join(root,name) + ' //file')
           
def getFilesList(path):
    files_list  = []
    for root, dirs, files in os.walk(path, topdown=True): 
        for name in files:
            files_list.append([os.path.join(root, name), hashFile(os.path.join(root,name))])
            
            
    return files_list
    
def getFilesDict(path):
    files_dict = {}
    for root, dirs, files in os.walk(path, topdown=True): 
        for name in files:
            files_dict[os.path.join(root, name)] = hashFile(os.path.join(root,name))
            # need paths fo both not key
                       
    return files_dict


#print('Input filename to de-stuff:') #,end="", flush=True  //for buffer issues?
#usrInput = input()
#f = open(usrInput, 'w')
#print(f) #test importing of file before string analysis

# Dirs for file ops.  These must stay hard coded to prevent accidents from wrong pwd
master_dir = 'C:/shit'
slave_dir = 'C:/shit2/duplicateshit'

#testDir =pwd

 # check this out
# http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python

"""
#http://www.tutorialspoint.com/python/os_file_methods.htm
os.getcwd() #pwd
os.chdir("New Towel") #change dir
os.mkdir("New Towel") #make dir
os.rmdir() #rm dir, rm the contents first
os.rename(src,dst) #rename file/dir src to dst
os.renames(old,new) #recursive file/dir rename
os.walk...
Special:
os.symlink(src,dst)

http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python?rq=1

http://www.pydanny.com/why-doesnt-python-have-switch-case.html
"""

print('How would you like to proceed? "1" for testrun, "2" analysis mode with copy/move')
user_input = input()
# Test mode, analysis mode (with copy/move?), silent/move

if user_input == '1':
    Mode = 1
    slavevar, mastervar, movedict, movedict2, movelist = testMode()
    #testMode()
elif user_input == '2':
    Mode = 2
    slavevar, mastervar, movedict, movedict2, movelist = analysisMode()
else:
    sys.exit('Invalid input, fucktard. lol')


#print('IGNORE BELOW')1

## TODO: Change this to master/slave dir
#for root, dirs, files in os.walk(".", topdown=False):
#    #print("Files:")
#    for name in files:
#        #print(os.path.join(root, name), 'SHA256: ', SHA(name))
#        #print(os.path.join(root, name), 'SHA256: ', hashFile(os.path.join(root,name)))
#        print(os.path.join(root,name) + ' //file')
#    #print("Dirs:")
#    for name in dirs:
#        print(os.path.join(root, name) + ' //dir')
#print('</IGNORE>')
##print(SHA('test1.txt'))