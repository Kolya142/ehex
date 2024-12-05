#!/bin/python3
import sys
import os
import re
import math
data = []
start = 0x00
pointer = 0x00
lines = 0x04
print("ehex loading")
r = {"\r": "\\r", "\n": "\\n", "\t": "\\t", "\x1b": "\\x1b", "\0": "\\0"}
print("\x1b[2J\x1b[H", end='')

argc = len(sys.argv)
argv = sys.argv

def load():
    global data
    with open(sys.argv[1], 'rb') as f:
        data = list(f.read())
    print(f"loading")


if argc == 2:
    if not os.path.exists(sys.argv[1]):
        with open(sys.argv[1], 'wb') as f:
            f.write('')
    load()
else:
    data = []
def save():
    global data
    with open(sys.argv[1], 'wb') as f:
        f.write(bytes(data))
    print(f"saving")

def show_in_chars(i, j):
    global data, pointer, start
    g = ""
    for c in range(i, j):
        if c > len(data) - 1:
            break
        if c < 0:
            continue
        if data[c] in r:
            g += r[data[c]]
        else:
            g += chr(data[c])
    print(f' | {g}')

def draw():
    global data, pointer, start
    e = 0
    n = 0
    i = -1
    data = [0] + data
    print("note:\x1b[40m\x1b[30mfirst byte is fix, just ignore them\x1b[0m")
    for i, byte in enumerate(data):
        if i < start:
            continue
        if i // 16 > lines:
            break
        b = f'{byte:02x}'
        # b += f'[{byte}]'
        if i == pointer:
            print('\x1b[32m', end='')
            print(b, end='\x1b[0m ')
        else:
            print(b, end=' ')
        if (i - start + 1) % 16 == 0 or (i - start) == 0:
            ll = max(i - 15, 0)
            if not (i - start) == 0:
                show_in_chars(ll, i + 2)
            start_addr = hex(max(ll, 0))
            end_addr = hex(i + 1)
            print(f'\n\x1b[7m{start_addr}-{end_addr}\x1b[27m', end=' ')
            n += 1
        e += 1
    show_in_chars(max(i - 16 + 1, 0), i + 1)
    data = data[1:]
    print()
    print()
    return n

def hdraw():
    print('\x1b7\x1b[H', end='')
    for _ in range(4):
        print(' ' * os.get_terminal_size()[0])
    n = draw()
    print('\x1b8', end='')
    return n

def main():
    global pointer, lines, start, data, states
    dtop = False
    insert = False
    print("insert mode: false")
    states = []

    def save_change():
        global pointer, lines, start, data, states
        states.append((data.copy(), pointer, lines, start))
        if len(states) >= 6:
            states = states[1:]
    
    while True:
        try:
            if dtop:
                n = hdraw()
            cmd = input(">>>")
            sp = cmd.split()
            match sp[0]:
                case 'help':
                    print("sb  -  show bytes")
                    print("dta - show bytes on top active")
                    print("dtd - show bytes on top disable")
                    print("rm  -  remove prev byte")
                    print("gs  -  set start")
                    print("gt  -  goto byte")
                    print("gl  -  set lines")
                    print("sh  -  string to hex")
                    print("ld  -  reload this file")
                    print("sv  -  save this file")
                    print("ws  -  write string")
                    print("wh  -  write byte")
                    print("wb  -  write binary")
                    print("rs  -  reset file")
                    print("und -  undo last change")
                    print("nul - init <value> bytes with zero")
                    print("clc - calculate")
                    print("ins - invert insert mode")
                    print("qt  -  quit")
                    print("cls - clear screen")
                case 'sb':
                    draw()
                case 'cls' | 'c':
                    print('\x1b[H\x1b[2J', end='')
                    draw()
                case 'nul':
                    save_change()
                    if len(sp) < 2:
                        print("usage: nul <value>")
                        continue
                    if not sp[1].isnumeric():
                        print("2 arg is not dec number")
                        continue
                    data += [0] * int(sp[1])
                case 'ins':
                    insert = not insert
                    print(f"changing insert mode to {insert}")
                case 'qt':
                    break
                case 'und':
                    data, pointer, lines, start = states.pop()
                    print("unded")
                case 'dta':
                    print('\x1b[H')
                    n = hdraw()
                    print('\x1b[nB')
                    dtop = True
                case 'dtd':
                    dtop = False
                case 'clc':
                    if len(sp) < 4:
                        print("usage: clc <value> <t1> <t2>")
                        print("supported: hex(h), oct(o), dec(d), bin(b), char(c), string(s, replace space with '/sp')")
                        continue
                    v = sp[1]
                    t1 = sp[2]
                    t2 = sp[3]
                    match t1:
                        case 'h':
                            v = int(v, 16)
                        case 'o':
                            v = int(v, 8)
                        case 'd':
                            v = int(v)
                        case 'b':
                            v = int(v, 2)
                        case 'c':
                            v = ord(v)
                        case 's':
                            vi = v.replace('/sp', ' ')
                            v = 0
                            for c in vi:
                                v = v << 8 | ord(c)

                    match t2:
                        case 'h':
                            v = hex(v)[2:]
                            print(' '.join(re.findall('..', v)))
                        case 'o':
                            v = oct(v)[2:]
                            print(' '.join(re.findall('..', v)))
                        case 'd':
                            print(v)
                        case 'c':
                            print(chr(v))
                        case 's':
                            s = ''
                            sl = math.ceil(math.log2(v) / 8)
                            while sl >= 0:
                                s += chr(v >> (sl * 8) & 0xff)
                                sl -= 1
                            print(s)
                        case 'b':
                            v = bin(v)[2:]
                            v = v.zfill((len(v) + 7) // 8 * 8)
                            print(' '.join(re.findall('........', v)))
                case 'rm':
                    save_change()
                    data = data[:pointer] + data[pointer + 1:]
                    pointer = min(pointer, len(data) - 1)
                    if not dtop:
                        draw()
                case 'gt':
                    if len(cmd) < 2:
                        print("usage: gt <int>")
                    else:
                        pointer = int(sp[1])
                        if not dtop:
                            draw()
                case 'gs':
                    if len(cmd) < 2:
                        print("usage: gs <int>")
                    else:
                        start = int(sp[1])
                case 'gl':
                    if len(cmd) < 2:
                        print("usage: gl <int>")
                    else:
                        lines = int(sp[1])
                case 'sh':
                    if len(cmd) < 3:
                        print("usage: sh <string>")
                    else:
                        print('0x', end='')
                        for c in cmd[3:]:
                            print(hex(ord(c))[2:], end=' ')
                        print()
                case 'ld':
                    save_change()
                    load()
                case 'sv':
                    save_change()
                    save()
                case 'rs':
                    save_change()
                    data = [0]
                    pointer = 0
                    start = 0
                    lines = 3
                    print('file reseted')
                case 'ws':
                    save_change()
                    if len(cmd) < 3:
                        print("usage: ws <string>")
                    else:
                        for c in cmd[3:]:
                            if pointer >= len(data):
                                data.append('')
                            if not insert:
                                data[pointer] = ord(c)
                            else:
                                data = data[:pointer+1] + [ord(c)] + data[pointer+1:]
                            pointer += 1
                        if pointer >= len(data):
                            data.append(0)
                case 'wh':
                    save_change()
                    if len(sp) < 2:
                        print("usage: wh <hex>")
                    else:
                        for h in sp[1:]:
                            if pointer >= len(data):
                                data.append('')
                            if not insert:
                                data[pointer] = int(h, 16)
                            else:
                                data = data[:pointer+1] + [int(h, 16)] + data[pointer+1:]
                            pointer += 1
                            if pointer >= len(data):
                                data.append(0)
                case 'wb':
                    save_change()
                    if len(sp) < 2:
                        print("usage: wb <bin>")
                    else:
                        for h in sp[1:]:
                            if pointer >= len(data):
                                data.append('')
                            if not insert:
                                data[pointer] = int(h, 2)
                            else:
                                data = data[:pointer+1] + [int(h, 2)] + data[pointer+1:]
                            pointer += 1
                            if pointer >= len(data):
                                data.append(0)
            if dtop:
                hdraw()
        except Exception as e:
            print(f'\x1b[31m{e.__str__()}\x1b[0m')
            

draw()

main()
