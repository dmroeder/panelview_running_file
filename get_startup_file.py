import pylogix
from pylogix.lgx_response import Response
from struct import pack


def get_startup_mer(plc):
    """
    Reads the registry entry on the PanelView Plus that contains the application that is
    configured to run at startup.  This assumes that there is one configured to load at
    startup and someone hasn't switched applications after it booted.
    """
    conn = plc.conn.connect(False)
    if not conn[0]:
        return Response(None, None, conn[1])

    cip_service = 0x51
    cip_service_size = 0x03
    cip_class_type = 0x21
    cip_class = 0x04fe
    cip_instance_type = 0x24
    cip_instance = 0x00

    data = "HKEY_LOCAL_MACHINE\\Software\\Rockwell Software\\RSViewME\\Startup Options\\CurrentApp\0"
    data = [ord(c) for c in data]

    request = pack('<BBHHBB{}B'.format(len(data)),
                   cip_service,
                   cip_service_size,
                   cip_class_type,
                   cip_class,
                   cip_instance_type,
                   cip_instance,
                   *data)

    status, ret_data = plc.conn.send(request, False)

    if status == 0:
        temp = ret_data.split(b"\\")
        try:
            name = temp[-1].decode("utf-8").strip()
        except (Exception,):
            name = None
            status = -1
    else:
        name = None
        status = -1

    return Response(None, name, status)


with pylogix.PLC("192.168.1.12") as comm:

    response = get_startup_mer(comm)
    print(response)
