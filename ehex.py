#!/bin/python3
import sys
import os
data = []
start = 0x00
pointer = 0x00
lines = 0x04
print("ehex loading")
r = {"\r": "\\r", "\n": "\\n", "\t": "\\t", "\x1b": "\\x1b"}
print("\x1b[2J\x1b[H", end='')
if not os.path.exists(sys.argv[1]):
    with open(sys.argv[1], 'w') as f:
        f.write('')

def load():
    global data
    with open(sys.argv[1], 'r') as f:
        data = list(f.read())
    print(f"loading")

def save():
    global data
    with open(sys.argv[1], 'w') as f:
        f.write(''.join(data))
    print(f"saving")

def show_in_chars(i, j):
    global data, pointer, start
    g = ""
    for c in range(i, j):
        if data[c] in r:
            g += r[data[c]]
        else:
            g += data[c]
    print(f' | {g}')

def draw():
    global data, pointer, start
    e = 0
    for i, byte in enumerate(data):
        if i < start:
            continue
        if i // 16 > lines:
            break
        b = f'{ord(byte):02x}'
        # b += f'[{byte}]'
        if i == pointer:
            print('\x1b[32m', end='')
            print(b, end='\x1b[0m ')
        else:
            print(b, end=' ')
        if (i - start + 1) % 16 == 0 or (i - start) == 0:
            if not (i - start) == 0:
                show_in_chars(i - 16 + 1, i + 2)
            start_addr = hex(max(i - 16 + 1, 0))
            end_addr = hex(i + 1)
            print(f'\n\x1b[7m{start_addr}-{end_addr}\x1b[27m', end=' ')
        e += 1
    show_in_chars(max(i - 16 + 1, 0), i + 1)
    print()

def main():
    global pointer, lines, start, data
    while True:
        cmd = input(">>>")
        sp = cmd.split()
        match sp[0]:
            case 'help':
                print("sb -  show bytes")
                print("rm -  remove prev byte")
                print("gs -  set start")
                print("gt -  goto byte")
                print("gl -  set lines")
                print("sh -  string to hex")
                print("ld -  reload this file")
                print("sv -  save this file")
                print("ws -  write string")
                print("wh -  write byte")
                print("rs -  reset file")
                print("clc - calculate")
            case 'sb':
                draw()
            case 'clc':
                if len(cmd) < 4:
                    print("usage: clc <value> <t1> <t2>")
                    print("supported: hex(h), oct(o), dec(d), bin(b)")
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
                match t2:
                    case 'h':
                        print(hex(v))
                    case 'o':
                        print(oct(v))
                    case 'd':
                        print(v)
                    case 'b':
                        print(bin(v))
            case 'rm':
                data = data[:pointer] + data[pointer + 1:]
                pointer = min(pointer, len(data) - 1)
            case 'gt':
                if len(cmd) < 2:
                    print("usage: gt <int>")
                else:
                    pointer = int(sp[1])
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
                load()
            case 'sv':
                save()
            case 'rs':
                data = ['\0']
                pointer = 0
                start = 0
                lines = 3
                print('file reseted')
            case 'ws':
                if len(cmd) < 3:
                    print("usage: ws <string>")
                else:
                    for c in cmd[3:]:
                        if pointer >= len(data):
                            data.append('')
                        data[pointer] = c
                        pointer += 1
                    if pointer >= len(data):
                        data.append('\0')
            case 'wh':
                if len(sp) < 2:
                    print("usage: wh <hex>")
                else:
                    for h in sp[1:]:
                        if pointer >= len(data):
                            data.append('')
                        data[pointer] = chr(int(h, 16))
                        pointer += 1
                        if pointer >= len(data):
                            data.append('\0')

load()
draw()

main()
