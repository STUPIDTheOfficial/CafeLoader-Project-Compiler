
def round_up(x, y):
    return ((x - 1) | (y - 1)) + 1

symbols = {}
diffs = []

def parseAddrFile(lines):
    global text, data, textAddr, dataAddr
    for line in lines:
        line = line.strip().replace(' ', '')

        if not line or line.startswith('#'):
            pass

        elif line.startswith('text='): text = eval(line.split('text=')[1])
        elif line.startswith('data='): data = eval(line.split('data=')[1])
        
        elif line.startswith('-'):
            symentry = line.split('=')
            symbol, address = symentry[0][1:], eval(symentry[1])
            symbols[symbol] = address

        else:
            old, new = line.split(':Addr')
            starthex, endhex = old.split('-')
            start = int(starthex, 16)
            end = int(endhex, 16)
            diff = eval(new)
            diffs.append((start, end, diff))

    symbols['textAddr'] = round_up(symbols['textAddr'], 32)
    symbols['dataAddr'] = round_up(symbols['dataAddr'] + 4, 32)
    assert symbols['textAddr'] < symbols['dataAddr']

def loadAddrFile(name):
    global region
    region = name
    
    symbols.clear()
    del diffs[:]

    with open('addr_%s.txt' %name) as f:
        parseAddrFile(f.readlines())

def convert(address, fixWriteProtection=False):
    if address < 0x10000000:
        segment = text
    else:
        segment = data

    for diff in diffs:
        if diff[0] <= address < diff[1]:
            addr = address + diff[2] + segment
            return addr

    raise ValueError("Invalid or unimplemented address: 0x%x" %address)

def convertTable(oldfile, newfile):
    with open(oldfile) as f:
        lines = f.readlines()
    
    newlines = []
    for line in lines:
        line = line.strip()
        
        if line.endswith(';'):
            name, addr = line.strip(';').split(' = ')

            if name == '__deleted_virtual_called':
                __deleted_virtual_called = eval(addr)
            
            newaddr = convert(eval(addr))
            newlines.append('%s = 0x%x;\n' %(name, newaddr))
        else:
            newlines.append(line+'\n')

    with open(newfile, 'w') as f:
        f.writelines(newlines)
