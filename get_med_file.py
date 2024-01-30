import pylogix
from pylogix.lgx_response import Response
from struct import pack, unpack_from

"""
The goal here is to get the name of the MED file saved on a PanelView's
\Temp\~MER.00 directory.

This is accomplished by calling a DLL file that will list all files in the
requested directory.  We'll put the results in an output file, request the
results of the file, then delete it.
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
    Create result file

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

def delete_file(plc):
    """
    Delete result file

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

def get_med(plc):
    """
    Request the results of the file that was generated

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

    value = ret_data[52:]
    byte_count = unpack_from("<H", value, 0)[0]
    name_bytes = value[-byte_count:]

    count = int(byte_count/2)
    stuff = [unpack_from("<H", name_bytes, i*2)[0] for i in range(count)]

    file_name = [str(chr(c)) for c in stuff]
    file_name = "".join(file_name).strip()
    file_name.replace(".med", ".mer")

    return Response(None, file_name, status)


with pylogix.PLC("192.168.1.12") as comm:

    init_file = "\\Windows\\RemoteHelper.DLL\0FileBrowse\0\\Temp\\~MER.00\\*.med::\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\DillyDilly.txt\0"
    file_location = "\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\DillyDilly.txt\0"
    uninit_file = "\\Windows\\RemoteHelper.DLL\0DeleteRemFile\0\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\DillyDilly.txt\0"

    response = pv_test(comm, 0x50, 0x04fd, init_file)
    if response.Status == "Success":
        response = create_file(comm, file_location)

    if response.Status == "Success":
        response = get_med(comm)
        print(response)

    if response.Status == "Success":
        response = delete_file(comm)
    
    if response.Status == "Success":
        response = pv_test(comm, 0x50, 0x04fd, uninit_file)
