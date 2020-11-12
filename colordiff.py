import difflib
try:
    from colorama import Fore, Back, Style, init
    init()
except ImportError:  # fallback so that the imported classes always exist
    class ColorFallback():
        __getattr__ = lambda self, name: ''
    Fore = Back = Style = ColorFallback()



def color_diff(diff):
    continueColoringBytes = False
    #I've been drinking and starting from 2 completely makes sense. Shush.
    unpackedDelimiterCount = 2
    for line in diff:
        #print(line)
        if line.startswith("+ b"):
            #Hit the initial trigger
            continueColoringBytes = True
            unpackedDelimiterCount += 1
            yield Fore.GREEN + str(line)  + Fore.RESET
        elif(line.startswith("+ '")):
            if(continueColoringBytes == True and (unpackedDelimiterCount % 2 == 0)):
                continueColoringBytes = False
                unpackedDelimiterCount += 1
                yield Fore.GREEN + str(line) + Fore.RESET
            else:
                unpackedDelimiterCount += 1
                yield Fore.GREEN + str(line) + Fore.RESET
        elif line.startswith('+'):
            yield Fore.GREEN + str(line) + Fore.RESET
        elif line.startswith('-'):
            yield Fore.RED + str(line) + Fore.RESET
        elif line.startswith('^'):
            yield Fore.YELLOW + str(line) + Fore.RESET
        else:
            if(continueColoringBytes):
                yield Fore.GREEN + str(line)  + Fore.RESET
            else:
                yield Fore.BLUE + str(line) + Fore.RESET

def packetdiff(firstBytes,secondBytes):
    diff = difflib.ndiff(firstBytes, secondBytes)
    diff = color_diff(diff)
    print(''.join(diff).replace(' ',''))
    #print(''.join(diff))