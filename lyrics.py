#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Lyrics converter
#
# version: 2017.4.17.2
# author: @shiracamus
# github: https://github.com/shiracamus/lyrics_converter
#
# Need to install mutagen module
#     $ python3 -m pip install mutagen
# or
#     $ sudo python3 -m pip install mutagen
#

import os
import sys
import argparse
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp4 import MP4, MP4StreamInfoError


def read_lyrics_in_mp3(path):
    try:
        tags = ID3(path)
        for key in tags:
            if key.startswith('USLT'):
                return tags[key].text
    except ID3NoHeaderError:
        pass
    return None


def read_lyrics_in_mp4(path):
    try:
        tags = MP4(path).tags
        if '\xa9lyr' in tags:
            return tags['\xa9lyr'][0]
    except MP4StreamInfoError:
        pass
    return None


def read_lyrics(path):
    return (read_lyrics_in_mp3(path) or
            read_lyrics_in_mp4(path) or
            None)


class Lyrics:

    def __init__(self, path):
        self.path = path
        self.path_base, self.path_ext = os.path.splitext(path)
        self.text = read_lyrics(path)
        self.exists = bool(self.text)

    def __repr__(self):
        return '<base="%s", ext="%s", lyrics=%s>' % (self.path_base,
                                                     self.path_ext,
                                                     self.exists)


class LRC:
    ext = '.lrc'

    def __init__(self, path):
        self.path = path
        self.exists = os.path.exists(self.path)

    def save(self, text):
        with open(self.path, 'w') as f:
            f.write(text)
        self.exists = True


def show_filename(lyrics):
    print(lyrics.path)


def show_lyrics(lyrics):
    print('=' * 30)
    print(lyrics.path)
    print('-' * 30)
    print(lyrics.text)
    print()


def save_lrc(lyrics, replace=False):
    lrc = LRC(lyrics.path_base + LRC.ext)
    if not lrc.exists or replace:
        lrc.save(lyrics.text)
        print('Saved "%s"' % lrc.path)
    else:
        print('Already exists "%s"' % lrc.path)


def pathes(file_or_directories):
    for file_or_directory in file_or_directories:
        if os.path.isfile(file_or_directory):
            yield file_or_directory
        elif os.path.isdir(file_or_directory):
            for root, dirs, files in os.walk(file_or_directory):
                for filename in files:
                    yield os.path.join(root, filename)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-l', '--list', action='store_true',
                   help='show file names containing lyrics (default)')
    p.add_argument('-s', '--show', action='store_true',
                   help='show lyrics')
    p.add_argument('-c', '--create', action='store_true',
                   help='create "*.lrc" lyrics files if it does not exist')
    p.add_argument('-r', '--replace', action='store_true',
                   help='create or replace "*.lrc" lyrics files')
    p.add_argument('file', nargs='+', default='.',
                   help='file or directory name')
    args = p.parse_args()
    if not (args.show or args.create or args.replace):
        args.list = True
    return args


def main(args):
    for path in pathes(args.file):
        lyrics = Lyrics(path)
        if not lyrics.text:
            continue
        if args.list:
            show_filename(lyrics)
        if args.show:
            show_lyrics(lyrics)
        if args.create or args.replace:
            save_lrc(lyrics, replace=args.replace)

if __name__ == '__main__':
    main(parse_args())
