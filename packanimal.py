import argparse
import struct
import colordiff
from tqdm import tqdm
try:
    from colorama import Fore, Back, Style, init
    init()
except ImportError:  # fallback so that the imported classes always exist
    class ColorFallback():
        __getattr__ = lambda self, name: ''
    Fore = Back = Style = ColorFallback()

#Reverse Python types to CTypes table
python2CTypes = {
    "byte" : [
        {
            "ctype" : "char",
            "length" : 1,
            "pythonFormat" : "c"
        }
    ],
    "integer" : [
        {
            "ctype" : "signed char",
            "length" : 1,
            "pythonFormat" : "b"
        },
        {
            "ctype" : "unsigned char",
            "length" : 1,
            "pythonFormat" : "B"
        },
        {
            "ctype" : "short",
            "length" : 2,
            "pythonFormat" : "h"
        },
        {
            "ctype" : "unsigned short",
            "length" : 2,
            "pythonFormat" : "H"
        },
        {
            "ctype" : "int",
            "length" : 4,
            "pythonFormat" : "i"
        },
        {
            "ctype" : "unsigned int",
            "length" : 4,
            "pythonFormat" : "I"
        },
        {
            "ctype" : "long",
            "length" : 4,
            "pythonFormat" : "l"
        },
        {
            "ctype" : "unsigned long",
            "length" : 4,
            "pythonFormat" : "L"
        },
        {
            "ctype" : "long long",
            "length" : 8,
            "pythonFormat" : "q"
        }
    ],
    "bool" : [
        {
            "ctype" : "_Bool",
            "length" : 1,
            "pythonFormat" : "?"
        }
    ],
    "bytes" : [
        {
            "ctype" : "char[]",
            #This attribute is ignored as char[] is variable length
            "length" : "variable",
            "pythonFormat" : "s"
        }
    ]
}

def getBin(fileName):
    with open(fileName, 'rb') as f:
        packet = f.read()
        return packet

def integerWindows(structLength, packetBytes):
    #Collector
    output = []
    packetLength = len(packetBytes)

    #Rolls a windows through bytearray and accumulates chunks
    id = 0
    for window in range(packetLength):
        try:
            temp = {}
            temp['id'] = id
            temp['bytes'] = packetBytes[window:(window+structLength)]
            temp['start'] = window
            temp['end'] = window+structLength
            output.append(temp)
        except:
            None
        id+=1
    #Filter function
    def dropTooShort(window):
        if (len(window['bytes']) == structLength):
            return True
        else:
            return False
    
    #Drop any windows that don't match the strcutLength
    return filter(dropTooShort, output)

def bytesWindows(packetBytes):
    #Collector
    output = []
    packetLength = len(packetBytes)

    #Rolls a windows through bytearray and accumulates chunks
    for chunkLength in range(packetLength):
        for window in range(packetLength):
            temp = {}
            #print(packetBytes[window:(window+chunkLength)])
            try:
                temp['bytes'] = packetBytes[window:(window+chunkLength)]
                temp['start'] = window
                temp['end'] = window+chunkLength
                output.append(temp)
            except:
                None

    return output

def unpackCtypeInteger(window, formatString):
    output = None
    try:
        # ! is network (Big Endian)
        output = struct.unpack('!' + formatString, bytes(window))
    except:
        None
    return output 

def unpackCtypeBytes(window, formatString):
    output = None
    try:
        # ! is network (Big Endian)
        output = struct.unpack('!' + str(len(window)) + formatString, bytes(window))
    except:
        None
    return output 

def scanAdjacent(scanDirection, subWindow, packetBytes):
    
    if(scanDirection == '>'):
        #packetBytes = packetBytes[subWindow['end']:]
        for targetType in python2CTypes.keys():
            ctypes = python2CTypes[targetType]
            #Try each ctype for python type int
            for ctype in ctypes:
                if(ctype['ctype'] == 'char[]'):
                    window = packetBytes[subWindow['end']:subWindow['end']+1]
                    window2CType = unpackCtypeInteger(window, ctype['pythonFormat'])
                    if(window2CType != None):
                        print('CTYPE:')
                        print(ctype)
                        print('WINDOW:')
                        print(window)
                        print('UNPACKED VALUE:')
                        print(window2CType[0])

                        startUnpacked = str(bytes(packetBytes[:subWindow['end']]))[2:-1]
                        midUnpacked = str(window2CType[0])
                        endUnpacked = str(bytes(packetBytes[subWindow['end']+1:]))[2:-1]
                        unpacked = startUnpacked + midUnpacked + endUnpacked
                        colordiff.packetdiff(str(bytes(packetBytes))[2:-1], unpacked)  
                else:
                    window = packetBytes[subWindow['end']:subWindow['end']+ctype['length']]
                    window2CType = unpackCtypeInteger(window, ctype['pythonFormat'])
                    if(window2CType != None):
                        print('CTYPE:')
                        print(ctype)
                        print('WINDOW:')
                        print(window)
                        print('UNPACKED VALUE:')
                        print(window2CType[0])

                        startUnpacked = str(bytes(packetBytes[:subWindow['end']]))[2:-1]
                        midUnpacked = str(window2CType[0])
                        endUnpacked = str(bytes(packetBytes[subWindow['end']+ctype['length']:]))[2:-1]
                        unpacked = startUnpacked + midUnpacked + endUnpacked
                        colordiff.packetdiff(str(bytes(packetBytes))[2:-1], unpacked)
    #Scan left <
    else:
        #packetBytes = packetBytes[:subWindow['start']]
        for targetType in python2CTypes.keys():
            ctypes = python2CTypes[targetType]
            #Try each ctype for python type int
            for ctype in ctypes:
                if(ctype['ctype'] == 'char[]'):
                    window = packetBytes[subWindow['start']-1:subWindow['start']]
                    window2CType = unpackCtypeInteger(window, ctype['pythonFormat'])
                    if(window2CType != None):
                        print('CTYPE:')
                        print(ctype)
                        print('WINDOW:')
                        print(window)
                        print('UNPACKED VALUE:')
                        print(window2CType[0])

                        startUnpacked = str(bytes(packetBytes[:subWindow['end']]))[2:-1]
                        midUnpacked = str(window2CType[0])
                        endUnpacked = str(bytes(packetBytes[subWindow['end']+1:]))[2:-1]
                        unpacked = startUnpacked + midUnpacked + endUnpacked
                        colordiff.packetdiff(str(bytes(packetBytes))[2:-1], unpacked)  
                else:
                    window = packetBytes[subWindow['start']:subWindow['start']-ctype['length']]
                    window2CType = unpackCtypeInteger(window, ctype['pythonFormat'])
                    if(window2CType != None):
                        print('CTYPE:')
                        print(ctype)
                        print('WINDOW:')
                        print(window)
                        print('UNPACKED VALUE:')
                        print(window2CType[0])

                        startUnpacked = str(bytes(packetBytes[:subWindow['start']-ctype['length']]))[2:-1]
                        midUnpacked = str(window2CType[0])
                        endUnpacked = str(bytes(packetBytes[subWindow['start']:]))[2:-1]
                        unpacked = startUnpacked + midUnpacked + endUnpacked
                        colordiff.packetdiff(str(bytes(packetBytes))[2:-1], unpacked)





def main():
    #Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--bf', required=True, help='Binary file containing a single packet layer')
    parser.add_argument('--obyte', required=False, type=str, help='Oracle integer value to search for')
    parser.add_argument('--oint', required=False, type=int, help='Oracle integer value to search for')
    parser.add_argument('--obool', required=False, help='Oracle bool value to search for')
    parser.add_argument('--ofloat', required=False, help='Oracle float value to search for')
    parser.add_argument('--obytes', required=False, help='Oracle bytes value to search for')
    parser.add_argument('--oencoding', required=False, type=str, help='Byte encoding of Oracle for --obytes EX: "ascii", "utf8"')


    args = parser.parse_args()
    #Get packet data
    packet = getBin(args.bf)
    print('Searching Packet:')
    print(packet)
    packetBytes = bytearray(packet)
    #packetBytes = bytearray(b'\x00\x01\x00\x02\x00\x03')
    
    #Handle --oint
    if(args.oint is not None):
        ctypes = python2CTypes['integer']
        #Try each ctype for python type int
        for ctype in ctypes:
            #Try each rolling window
            for window in integerWindows(ctype['length'], packetBytes):
                #print(window)
                window2CType = unpackCtypeInteger(window['bytes'], ctype['pythonFormat'])
                if(window2CType != None):
                    #print(window2CType)
                    if(args.oint in window2CType):
                        print(Fore.YELLOW + 'FOUND OINT ORACLE: ' + str(args.oint) + Fore.RESET)
                        print('CTYPE:')
                        print(ctype)
                        print('WINDOW:')
                        print(window)
                        print('UNPACKED VALUE:')
                        print(window2CType[0])

                        startUnpacked = str(bytes(packetBytes[:window['start']]))[2:-1]
                        midUnpacked = str(window2CType[0])
                        endUnpacked = str(bytes(packetBytes[window['end']:]))[2:-1]
                        unpacked = startUnpacked + midUnpacked + endUnpacked
                        colordiff.packetdiff(str(packet)[2:-1], unpacked)

                        selectedWindow = input('Select Window? [y/n]: ')
                        if(selectedWindow == 'y'):
                            scanDirection = input('Scan Direction? [</>]: ')
                            scanAdjacent(scanDirection, window, packetBytes)
    
    #Handle --obytes
    if(args.obytes is not None):
        if(args.oencoding is not None):
            ctypes = python2CTypes['bytes']
            #Try each ctype for python type int
            for ctype in ctypes:
                #Try each rolling window
                for window in bytesWindows(packetBytes):
                    #print(window)
                    window2CType = unpackCtypeBytes(window['bytes'], ctype['pythonFormat'])
                    if(window2CType != None):
                        #print(window2CType)
                        if(bytes(args.obytes, encoding=args.oencoding) in window2CType):
                            print(fore.YELLOW + 'FOUND OBYTES ORACLE: ' + str(args.obytes) + Fore.RESET)
                            print('CTYPE:')
                            print(ctype)
                            print('WINDOW:')
                            print(window)
                            print('UNPACKED VALUE:')
                            print(window2CType[0])

                            startUnpacked = str(bytes(packetBytes[:window['start']]))[2:-1]
                            midUnpacked = str(window2CType[0])
                            endUnpacked = str(bytes(packetBytes[window['end']:]))[2:-1]
                            unpacked = startUnpacked + midUnpacked + endUnpacked
                            colordiff.packetdiff(str(packet)[2:-1], unpacked)

                            selectedWindow = input('Select Window? [y/n]: ')
                            if(selectedWindow == 'y'):
                                scanDirection = input('Scan Direction? [</>]: ')
                                scanAdjacent(scanDirection, window, packetBytes)
        else:
            print("WARN: --obytes must be paired with --oencoding")
    


if __name__ == '__main__':
    main()

