"""
date: 1/23/2020 
Version 1
Todo: fix bugs when found and finish up syslogng option.
Revision: 
"""
desc = 'This script will read an input file of ip addresses or individual ip and create corresponding folder and syslog.log file for data input into for splunk from syslog. . i.e(path.to.logs/10.1.1.1/syslog.log)'
import os,sys, getopt,argparse
import ipaddress

#rsyslog/syslogng location
rsyslog = "/etc/rsyslog.conf"
syslogng = "/etc/syslog-ng/syslog-ng.conf"

#parser info 
parser = argparse.ArgumentParser(description = desc)
parser.add_argument("-v","--version",help="show version",action='version',version='%(prog)s 1.0')
parser.add_argument("-i","--input",help="input file/location",type=str,dest="input")
parser.add_argument("-r","--rsyslog",help="add to ryslog",action="store_true",dest="rsyslog")
#parser.add_argument("-n","--syslogng",help="add to syslogng",action="store_true",dest="syslogng")
parser.add_argument("-ip","--ip",help="add a single ip",type=str,dest="ip",default='')
parser.add_argument("-d","--dest",help="destination for folder creation; if none declared current path will be used " + os.getcwd(),type=str,dest="dest",default=os.getcwd())

#read argumetns from cli
args = parser.parse_args()

#print(args.dest)

#if no arguments display help
if len(sys.argv[1:])==0:
    parser.print_help()
    # parser.print_usage() # for just the usage line
    parser.exit()

#check if -ip & -i are used together 
if (args.input and args.ip):
    print("Error use -i or -ip seperate not together")
    parser.exit()

#check if ip address is a valid ip
def ipcheck(ipAddress):
    try:
        ipaddress.IPv4Network(ipAddress)
        return True
    except ValueError:
        return False

def createFolder(ipAddress):
    try: 
        os.mkdir(args.dest+'/'+ipAddress)  
        createFile = open(args.dest+'/'+ipAddress+'/'+'syslog.log',"w")
        os.chmod(args.dest+'/'+ipAddress+'/'+'syslog.log', 0o744) #set it to -rwx-r--r--
        createFile.close()
        return True
    except (FileExistsError,FileNotFoundError): #if folder exists or can't do anything return false
        return False

def readFile(inputFile):
    newlist=[]
    try:
        with open(inputFile,'r') as f:
            data = f.readlines() #use readlines to read it line by line 
            for list in data: #remove \n from list
                newlist.append(list.replace("\n",""))
            f.close()
        return newlist #returns data from cleaned up list 
    except (FileNotFoundError):
        return False

#open rsyslog.conf and append if($fromhost-ip=='ipaddress') then path.to/syslog.log \n & stop \n
def writeRsyslog(ipAddress,dest,rsyslog): 
    try:
        rsyslogFile = open("/opt/rsyslog.conf", "a+")
        rsyslogFile.write("\nif($fromhost-ip=='%s') then %s/%s/syslog.log\n& stop\n" % (ipAddress,dest,ipAddress))
        rsyslogFile.close()
        return True
    except:
        return False

#def writeSyslogng(ipAddress,dest,syslogng):
#    try:
#        syslogng = open("/opt")

def rsyslog(ipAddress,dest):
    return print("if($fromhost-ip=='%s') then %s/%s/syslog.log\n& stop" % (args.ip,args.dest,args.ip))

#if input is used   
if args.input:
    print('Using file: %s/%s' % (args.dest,args.input))
    for entry in readFile(args.input): 
        if(createFolder(entry)):
            print("creating folder for %s at location: %s/%s" %(entry,args.dest,args.ip ))
        else:
            print("Error folder exists or some other error")

#if ip address is supplied
if args.ip:
    #testing if ip address is real or not 
    if ipcheck(args.ip):
        print("using ip address of %s" % args.ip)
        if createFolder(args.ip):
            print("create folder for %s/%s" %(args.dest, args.ip))
            #print("folder %s has been created" % args.ip)
        else:
            print("Error folder exists or some other error")
    else:
        print("Not a ip address")


if args.rsyslog:
    rsyslog(args.ip,args.dest)
    if writeRsyslog(args.ip,args.dest,rsyslog):
        print("added to rsyslog.conf file")
    else:
        print("error")
else:
    print("error")

#if args.syslogng:
#    print("using syslog-ng")
