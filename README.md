# pyBGAPI_UART_DFU
Implementation of Host for DFU using Bluetooth NCP BGAPI DFU bootloader

Usage: bgapi_dfu.py [ -t <ipaddr> ][ -u <uart> ][ -x <xapi-file> ] <GBL-file>
  most options are mandatory!  Either ip address of WSTK or UART device must be specified.  
  If xapi file is not specifed, sl_bt.xapi in current working directory is default.
