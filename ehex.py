#!/bin/python3
import sys
import os
data = []
start = 0x00
pointer = 0x00
lines = 0x04
print("ehex loading")
os.system('clear')
if not os.path.exists(sys.argv[1]):
    with open(sys.argv[1], 'w') as f:
        f.write('')

def load():
    global data
    with open(sys.argv[1], 'r') as f:
        data = list(f.read())
    print(f"loading {sys.argv[1]}")

def save():
    global data
    with open(sys.argv[1], 'w') as f:
        f.write(''.join(data))
    print(f"saving {sys.argv[1]}")

def draw():
    global data, pointer, start
    for i, byte in enumerate(data):
        if i < start:
            continue
        if i // 16 > lines:
            break
        b = hex(ord(byte))[2:]
        if b == '':
            b = '00'
        if len(b) == 1:
            b = '0' + b
        # b += f'[{byte}]'
        if i == pointer:
            print('\x1b[32m', end='')
            print(b, end='\x1b[0m ')
        else:
            print(b, end=' ')
        if i % 16 == 0:
            if i != 0:
                print(f'\n{hex(i - 16)}-{hex(i)} ', end='')
            else:
                print()
    print()

def loop():
    global pointer, lines, start, data
    cmd = input(">>>")
    sp = cmd.split()
    match sp[0]:
        case 'help':
            print("sb - show bytes")
            print("gs - set start")
            print("gt - goto byte")
            print("gl - set lines")
            print("sh - sting to hex")
            print("ld - reload this file")
            print("sv - save this file")
            print("ws - write string")
            print("rs - reset file")
        case 'sb':
            draw()
        case 'gt':
            if len(cmd) < 2:
                print("usage: gt <int>")
            else:
                pointer = int(sp[1])
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
            if len(sp) != 2:
                print("usage: wh <hex>")
            else:
                if pointer >= len(data):
                    data.append('')
                data[pointer] = chr(int(sp[1], 16))
                pointer += 1
                if pointer >= len(data):
                    data.append('\0')

load()
draw()

while True:
    loop()
