import argparse
import struct

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
            "ctype" : "unsigned short",
            "length" : 2,
            "pythonFormat" : "H"
        }
    ]
}

def getBin(fileName):
    with open(fileName, 'rb') as f:
        packet = f.read()
        return packet

def windows(structLength, packetBytes):
    #Collector
    output = []
    packetLength = len(packetBytes)

    #Rolls a windows through bytearray and accumulates chunks
    for window in range(packetLength):
        try:
            temp = packetBytes[window:(window+structLength)]
            output.append(temp)
        except:
            None
    #Filter function
    def dropTooShort(window):
        if (len(window) == structLength):
            return True
        else:
            return False
    
    #Drop any windows that don't match the strcutLength
    return filter(dropTooShort, output)

def unpackCtype(window, formatString):
    output = None
    try:
        # ! is network (Big Endian)
        output = struct.unpack('!' + formatString, bytes(window))
    except:
        None
    return output 



def main():
    #Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--bf', required=True, help='Binary file containing a single packet layer')
    parser.add_argument('--obyte', required=False, help='Oracle integer value to search for')
    parser.add_argument('--oint', required=False, type=int, help='Oracle integer value to search for')
    parser.add_argument('--obool', required=False, help='Oracle bool value to search for')
    parser.add_argument('--ofloat', required=False, help='Oracle float value to search for')
    parser.add_argument('--obytes', required=False, help='Oracle bytes value to search for')

    args = parser.parse_args()
    #Get packet data
    packet = getBin(args.bf)
    print('Searching Packet:')
    print(packet)
    packetBytes = bytearray(packet)
    #packetBytes = bytearray(b'\x00\x01\x00\x02\x00\x03')
    
    #Handle --oint
    if(args.oint != None):
        ctypes = python2CTypes['integer']
        #Try each ctype for python type int
        for ctype in ctypes:
            print(ctype)
            #Try each rolling window
            for window in windows(ctype['length'], packetBytes):
                #print(window)
                window2CType = unpackCtype(window, ctype['pythonFormat'])
                if(window2CType != None):
                    #print(window2CType)
                    if(args.oint in window2CType):
                        print('FOUND OINT ORACLE: ' + str(args.oint))
                        print(window)
                        print(window2CType)
    


if __name__ == '__main__':
    main()

