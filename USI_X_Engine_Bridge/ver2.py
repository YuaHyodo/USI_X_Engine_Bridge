"""
This file is part of USI_X_Engine_Bridge

Copyright (c) 2023 YuaHyodo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from datetime import datetime
import subprocess as subpro
import codecs
import os

k = '\n'#改行

class USI_X_Engine_Bridge:
    def __init__(self, path, log_file=None):
        self.engine_path = path
        self.log_file = log_file
        self.info_mes_list = []
        cwd = os.path.dirname(path)
        if cwd == '':
            cwd = None
        self.engine = subpro.Popen(path, stdin=subpro.PIPE, stdout=subpro.PIPE,
                                   universal_newlines=True, bufsize=1,
                                   cwd=cwd, encoding='utf-8')
        self.send('usi')
        self.recv_word('usiok')

    def write_log(self, word):
        if self.log_file is not None:
            print(word, file=codecs.open(self.log_file, 'a', 'utf-8'))
        return

    def send(self, word):
        w = '<usix_send> | ' + str(datetime.now()) + ' | ' + word
        self.write_log(w)
        if k not in word:
            word += k
        self.engine.stdin.write(word)
        return

    def recv_word(self, word, get_bestmove=False):
        while True:
            try:
                r = self.engine.stdout.readline()
            except:
                print('info string readline error')
                continue
            if 'info' in r:
                self.info_mes_list.append(r)
                w = '<usix_recv> | ' + str(datetime.now()) + ' | ' + r
                self.write_log(w)
            if word in r:
                w = '<usix_recv> | ' + str(datetime.now()) + ' | ' + r
                self.write_log(w)
                if get_bestmove:
                    if word in r.split(' ')[0]:
                        break
                    continue
                break
        return r

    def setoption(self, name, value):
        self.send('setoption name ' + name + ' value ' + value)
        return

    def score_scale_and_type(self):
        self.send('score_scale_and_type')
        r = self.recv_word('scoretype').split(' ')
        score_type = r[1]
        min_score = int(r[3])
        max_score = int(r[5])
        return score_type, max_score, min_score

    def stop(self):
        self.send('stop')
        self.send('quit')
        return

    def newgame(self):
        self.send('isready')
        self.recv_word('readyok')
        self.send('usinewgame')
        return

    def get_move(self, score=False):
        r = self.engine.stdout.readline()
        if 'bestmove' in r.split(' ')[0]:
            w = '<usix_recv> | ' + str(datetime.now()) + ' | ' + r
            self.write_log(w)
            move = r.split(' ')[1]
        else:
            move = self.recv_word('bestmove', get_bestmove=True).split(' ')[1]
        bestmove = ''.join(move.splitlines())
        if score:
            score = None
            for mes in reversed(self.info_mes_list):
                if 'score' in mes:
                    score = int(mes.split('score ')[1].split(' ')[0])
                    break
            return bestmove, score
        else:
            return bestmove
