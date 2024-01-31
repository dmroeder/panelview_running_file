import pylogix
from pylogix.lgx_response import Response
from struct import pack, unpack_from

"""
The goal here is to get the name of the MED file saved on a PanelView's
\\Temp\\~MER.00 directory.

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

def get_platform_version(plc):
    """ Get the terminal firmware revision
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

    data = "HKEY_LOCAL_MACHINE\\Software\\Rockwell Software\\RSView Enterprise\\MEVersion\0"
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
        value = ret_data[52:-1]
        test = [str(chr(v)) for v in value]
        version = "".join(test).strip()
        version = version.split(".")
        version = [int(v) for v in version]
    else:
        version = [0,0,0,0]
        
    return Response(None, version, status)

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

    if status == 0:
        value = ret_data[52:]
        byte_count = unpack_from("<H", value, 0)[0]
        name_bytes = value[-byte_count:]

        count = int(byte_count/2)
        stuff = [unpack_from("<H", name_bytes, i*2)[0] for i in range(count)]

        file_name = [str(chr(c)) for c in stuff]
        file_name = "".join(file_name).strip()
        file_name.replace(".med", ".mer")
    else:
        file_name = ""

    return Response(None, file_name, status)


with pylogix.PLC("192.168.1.12") as comm:

    # request the version from the registry
    response = get_platform_version(comm)
    if response.Value[0] == 5:
        helper = "\\Storage Card\\Rockwell Software\\RSViewME\\RemoteHelper.DLL\0"
        output_location = "\\Storage Card\\Rockwell Software\\RSViewME\\Runtime\\DillyDilly.txt\0"
    else:
        helper = "\\Windows\\RemoteHelper.DLL\0"
        output_location = "\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\DillyDilly.txt\0"

    # command to get the file contents of a directory
    init_file = helper + "FileBrowse\0\\Temp\\~MER.00\\*.med::" + output_location
    # command to delete the file
    uninit_file = helper + "DeleteRemFile\0" + output_location

    # generate a file with directory information
    response = pv_test(comm, 0x50, 0x04fd, init_file)
    if response.Status == "Success":
        # create file on disk
        response = create_file(comm, output_location)

    if response.Status == "Success":
        # request the contents of the file
        response = get_med(comm)
        print(response)

    # delete file
    if response.Status == "Success":
        response = delete_file(comm)
    
    if response.Status == "Success":
        response = pv_test(comm, 0x50, 0x04fd, uninit_file)

