# pyBGAPI_UART_DFU
Implementation of Host for DFU using Bluetooth NCP BGAPI DFU bootloader

Usage: bgapi_dfu.py [ -t &lt;ipaddr&gt; ][ -u &lt;uart&gt; ][ -x &lt;xapi-file&gt; ] &lt;GBL-file&gt;
  
  most options are mandatory!  Either IP address of WSTK or UART device must be specified.  
  If xapi file is not specifed, sl_bt.xapi in current working directory is default.
