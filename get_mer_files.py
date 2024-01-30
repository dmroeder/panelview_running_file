import pylogix
from pylogix.lgx_response import Response
from struct import pack

"""
Some other data might be returned from the first packet that has to be used
in the "create" packet
"""


def pv_test(plc, s, c, data):

    conn = plc.conn.connect(False)
    if not conn[0]:
        return Response(None, None, conn[1])

    cip_service = s
    cip_service_size = 0x03
    cip_class_type = 0x21
    cip_class = c
    cip_instance_type = 0x24
    cip_instance = 0x00

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
    return Response(None, None, status)

def create_file(plc, entry):
    """
    Read multiple PowerFlex parameters
    
    returns Response class (.TagName, .Value, .Status)
    """
    conn = plc.conn.connect(False)
    if not conn[0]:
        return Response(None, None, conn[1])

    cip_service = 0x08
    cip_service_size = 0x03
    cip_class_type = 0x21
    cip_class = 0x04ff
    cip_instance_type = 0x24
    cip_instance = 0x00

    data = [ord(c) for c in entry]

    request = pack('<BBHHBBHH{}B'.format(len(data)),
                    cip_service,
                    cip_service_size,
                    cip_class_type,
                    cip_class,
                    cip_instance_type,
                    cip_instance,
                    0x00, 0x07c2,
                    #0x00, 0x00,
                    *data)

    status, ret_data = plc.conn.send(request, False)
    return Response(None, None, status)

def seems_important(plc):
    """
    Not sure what this does yet, but if I know comments, this
    will exist forever
    """
    conn = plc.conn.connect(False)
    if not conn[0]:
        return Response(None, None, conn[1])

    cip_service = 0x53
    cip_service_size = 0x03
    cip_class_type = 0x21
    cip_class = 0x04ff
    cip_instance_type = 0x24
    cip_instance = 0x01

    request = pack('<BBHHBBI',
                    cip_service,
                    cip_service_size,
                    cip_class_type,
                    cip_class,
                    cip_instance_type,
                    cip_instance,
                    0x02)

    status, ret_data = plc.conn.send(request, False)
    return Response(None, None, status)

def delete_file(plc):
    """
    Read multiple PowerFlex parameters
    
    returns Response class (.TagName, .Value, .Status)
    """
    conn = plc.conn.connect(False)
    if not conn[0]:
        return Response(None, None, conn[1])

    cip_service = 0x09
    cip_service_size = 0x03
    cip_class_type = 0x21
    cip_class = 0x04ff
    cip_instance_type = 0x24
    cip_instance = 0x01

    request = pack('<BBHHBB',
                    cip_service,
                    cip_service_size,
                    cip_class_type,
                    cip_class,
                    cip_instance_type,
                    cip_instance)

    status, ret_data = plc.conn.send(request, False)
    return Response(None, None, status)

def get_mers(plc):
    """
    Read multiple PowerFlex parameters
    
    returns Response class (.TagName, .Value, .Status)
    """
    conn = plc.conn.connect(False)
    if not conn[0]:
        return Response(None, None, conn[1])

    cip_service = 0x53
    cip_service_size = 0x03
    cip_class_type = 0x21
    cip_class = 0x04ff
    cip_instance_type = 0x24
    cip_instance = 0x01

    request = pack('<BBHHBBI',
                    cip_service,
                    cip_service_size,
                    cip_class_type,
                    cip_class,
                    cip_instance_type,
                    cip_instance,
                    0x01)

    status, ret_data = plc.conn.send(request, False)
    return Response(None, None, status)

with pylogix.PLC("192.168.1.12") as comm:

    pc = "HKEY_LOCAL_MACHINE\\Software\\Rockwell Software\\RSLinxNG\\CIP Identity\\ProductCode\0"
    pt = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Rockwell Software\\RSLinxNG\\CIP Identity\\ProductType\0"

    init_file = "\\Windows\\RemoteHelper.DLL\0FileBrowse\0\\Temp\\~MER.00\\*.med::\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\DillyDilly.txt\0"
    file_location = "\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\DillyDilly.txt\0"
    uninit_file = "\\Windows\\RemoteHelper.DLL\0DeleteRemFile\0\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\DillyDilly.txt\0"

    response = pv_test(comm, 0x50, 0x04fd, init_file)
    print(response)

    response = create_file(comm, file_location)
    print(response)

    response = pv_test(comm, 0x51, 0x04fe, pt)
    print(response)

    response = pv_test(comm, 0x51, 0x04fe, pc)
    print(response)

    response = get_mers(comm)
    print(response)

    response = seems_important(comm)
    print(response)

    response = delete_file(comm)
    print(response)

    response = pv_test(comm, 0x50, 0x04fd, uninit_file)
    print(response)
