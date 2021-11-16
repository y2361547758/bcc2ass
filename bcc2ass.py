#!/usr/bin/env python
import os
import re
import sys
import json
from optparse import OptionParser

def sec2time(sec, type=''):
    h = int(sec) // 3600
    m = int(sec) // 60 % 60
    s = sec % 60
    f = int(sec * 1000) % 1000
    if type == 'srt':   return "%02d:%02d:%02d,%03d" % (h, m, int(s), f)
    elif type == 'ass': return "%d:%02d:%02d.%02d"   % (h, m, s, f // 10)
    elif type == 'lrc': return "%02d:%02d.%02d" % (int(sec) // 60, s, f // 10)
    return "%02d:%02d:%02.2f" % (h, m, s)

def color2asscolor(color, alpha = 0):
    return ("&H%02X" % alpha) + color[1:]

def bcc2ass(bcc, output, type):
    with open(output, 'w', encoding='utf-8') as f:
        count = 1
        if type == 'ass':
            print("[Script Info]", file=f)
            print(file=f)
            print("[V4+ Styles]", file=f)
            print("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding", file=f)
            location = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
            Alignment = 2
            for i in bcc['body']:
                location[i['location']] += 1
                if location[Alignment] < location[i['location']]: Alignment = i['location']
            print("Style: Default", "Arial", "%d" % (bcc['font_size'] * 10 + 10), color2asscolor(bcc['font_color']), "&H000000FF", color2asscolor(bcc['background_color'], int(bcc['background_alpha'] * 0xFF)), "&H00000000,0,0,0,0,100,100,0,0,1,2,2,%d,10,10,10,1" % Alignment, sep=',', file=f)
            print(file=f)
            print("[Events]", file=f)
            print("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text", file=f)
        if type == 'lrc':
            print('[ti:]', '[ar:]', '[al:]', '', sep="\n", file=f)
            last = 0
        
        for i in bcc['body']:
            if type == 'srt':
                print(count, file=f)
                print(sec2time(i['from'], type) + ' --> ' + sec2time(i['to'], type), file=f)
                print(i['content'], file=f)
                print(file=f)
                count += 1
            elif type == 'ass':
                align = '' if i['location'] == Alignment else '{\\a%d}' % i['location']
                print("Dialogue: 0," + sec2time(i['from'], type) + "," + sec2time(i['to'], type) + ",Default,,0,0,0,," + align + i['content'].replace('\n',r'\N'), file=f)
            elif type == 'lrc':
                if last != i['from']: print('[' + sec2time(last, type) + ']', file=f)
                print('[' + sec2time(i['from'], type) + ']' + i['content'], file=f)
                last = i['to']

def get_args():
    parser = OptionParser()
    parser.add_option('-i', '--input', dest='bcc_file', default='')
    parser.add_option('-o', '--output', dest='out_file', default='')
    parser.add_option('-t', '--type', dest='type', default='srt', help='output format')
    (options, args) = parser.parse_args()
    return options

if __name__ == '__main__':
    args = get_args()
    if not args.type in ['ass', 'srt', 'lrc']:
        print('Unsupport type:', args.type)
        exit(1)
    try:
        with open(args.bcc_file, encoding='utf8') as f: bcc=json.load(f)
    except:
        print("input file error")
        exit(2)
    output = args.out_file if len(args.out_file) != 0 else re.sub(r'\.bcc$', '', args.bcc_file)
    bcc2ass(bcc, output + "." + args.type, args.type)
