# PBX

SERVER

  1. Launch server:
       python3 PBX_Server.py

  2. Launch control client on another machine or terminal:
       python3 PBX_Client.py locahost 45000 control

     The control client allows to control the incoming connections. It accepts the following commands:
       list  --> lists the opened ports and their status
       bind <portA> <portB> --> binds the 2 ports, e.g. "bind 40001 50002"
       unlink <port> --> unbinds a linked port, e.g. "unlink 40001" removes the link between 40001 and 50002

NOTES:
- The client is developed for test purpouses only, it is not intended for production.
- The server may be further developed by adding:
    - Aliases for the OE Tools ports (e.g. "FIAT", "VW", etc.
    - Commands to set the CANbus configuration info (pin numbers, speed)
