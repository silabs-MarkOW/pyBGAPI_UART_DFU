import sys
import bgapi
import getopt
import time

OTA_SERVICE_UUID = 0x1d14d6eefd634fa1bfa48f47b42119f0
OTA_CONTROL_UUID = 0xf7bf3564fb6d4e5388a45e37e0326063
ignored_events = ['bt_evt_connection_parameters',
                  'bt_evt_connection_phy_status',
                  'bt_evt_connection_remote_used_features']

xapi = 'sl_bt.xapi'
connector = None
baudrate = 115200
target = {'address':None}
state = 'start'
duration = 10
timeout = None
app_rssi = None
verbose = 0
ota_mode = False
match_service = 0x1509
match_name = None
list_mode = False
devices = {}

def exit_help(error=None) :
    if None != error :
        print('Error: %s'%(error))
        print('Usage %s [ -h ][ -v ][ -t <ip-address> ][ -u <uart> ][ -b baudrate ]')
        print('         [ -x <api-xml> ][ -d <duration> ][ -n <complete-local-name> ]')
        print('         [ --ota ][ -a <bd-addr> ][ -l ]')
        quit()
        
opts,params = getopt.getopt(sys.argv[1:],'hvlt:u:x:b:a:n:d:',['ota'])
for opt,param in opts :
    if '-h' == opt :
        exit_help()
    if '-v' == opt :
        verbose += 1
    elif '-t' == opt :
        connector = bgapi.SocketConnector((param,4901))
    elif '-u' == opt :
        connector = bgapi.SerialConnector(param,baudrate=baudrate)
    elif '-x' == opt :
        xapi = param
    elif '-b' == opt :
        baudrate = int(param)
    elif '-l' == opt :
        list_mode = True
    elif '-d' == opt :
        duration = float(param)
    elif '-n' == opt :
        match_name = param
        match_service = None
        match_address = None
    elif '-a' == opt :
        match_address = param
        match_service = None
        match_name = None
    elif '--ota' == opt :
        ota_mode = True
    else :
        exit_help('Unrecognized option "%s"'%(opt))

if 1 != len(params) :
    exit_help('GBL file not specified')


fh = open(params[0],'rb')
text = fh.read()
fh.close()
if 0 != (len(text) % 4) :
    exit_help('GBL file "%s" length is not multiple of word size'%(params[0]))
    
if None == connector :
    exit_help('Either -t or -u is required')

try :
    dev = bgapi.BGLib(connection=connector,apis=xapi)
except FileNotFoundError :
    exit_help('xml file defining API, %s, not found. See -x option')

def setState(new_state) :
    global state
    print('set_state: %s -> %s'%(state,new_state))
    state = new_state

def sl_bt_on_event(evt) :
    global text
    if 'bt_evt_system_boot' == evt :
        print('system-boot: BLE SDK %dv%dp%db%d'%(evt.major,evt.minor,evt.patch,evt.build))
        setState('done')
    elif 'bt_evt_dfu_boot_failure' == evt :
        print('dfu.boot_failure: reason 0x%x'%(evt.reason))
    elif 'bt_evt_dfu_boot' == evt :
        print('dfu.boot: version = 0x%08x'%(evt.version))
        if 'reset' == state :
            print('Beginning upload of %s'%(params[0]))
            dev.bt.dfu.flash_set_address(0)
            total = len(text)
            packets = 0
            while len(text) :
                if len(text) > 128 :
                    toSend = text[:128]
                    text = text[128:]
                else :
                    toSend = text
                    text = b''
                dev.bt.dfu.flash_upload(toSend)
                packets += 1
                print('.',end='',flush=True)
            dev.bt.dfu.flash_upload_finish()
            dev.bt.system.reset(0)
            print('%d bytes sent in %d packets'%(total,packets))
            setState('reset-to-app')
        else :
            setState('confused')
    else :
        unhandled = True
        for ignore in ignored_events :
            if ignore == evt :
                unhandled = False
        if unhandled :
            print('Unhandled event: %s'%(evt.__str__()))
    return state != 'confused'

dev.open()
dev.bt.system.reset(0)
setState('reset')

# keep scanning for events
while 'done' != state :
    try:
        # print('Starting point...')
        evt = dev.get_events(max_events=1)
        if evt:
            if not sl_bt_on_event(evt[0]) :
                break
    except(KeyboardInterrupt, SystemExit) as e:
        if dev.is_open():
            dev.close()
            print('Exiting...')
            sys.exit(1)

if dev.is_open():
    dev.close()

