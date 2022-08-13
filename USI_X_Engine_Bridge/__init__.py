"""
This file is part of USI_X_Engine_Bridge

Copyright (c) 2022 YuaHyodo

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

import subprocess as subpro

k = '\n'

class USI_X_Engine_Bridge:
    def __init__(self, engine_path):
        self.engine_path = engine_path
        self.info_get = False
        self.engine_message_list = []
        self.load_engine()

    def load_engine(self):
        self.engine = subpro.Popen(self.engine_path, stdin=subpro.PIPE, stdout=subpro.PIPE,
                                   universal_newlines=True, bufsize=1)
        self.send('usi')
        self.recv_word('usiok')
        return

    def send(self, command):
        if k not in command:
            command += k
        self.engine.stdin.write(command)
        return

    def recv(self):
        return self.engine.stdout.readline()

    def recv_word(self, word):
        while True:
            w = self.recv()
            if word in w:
                self.engine_message_list.append(w)
                break
            if 'info' in w and self.info_get:
                self.engine_message_list.append(w)
        return w

    def think(self, position, btime=1000, wtime=1000, binc=1000, winc=1000, byoyomi=0):
        command = 'position ' + position
        self.send(command)
        command = 'go btime ' + str(btime) + ' wtime ' + str(wtime) + ' binc ' + str(binc) + ' winc ' + str(winc) + ' byoyomi ' + str(byoyomi)
        self.send(command)
        bestmove = self.recv_word('bestmove')
        if 'pass' in bestmove:
            return 'pass'
        if 'resign' in bestmove:
            return 'resign'
        return bestmove[9] + bestmove[10]

    def setoption(self, name, value):
        self.send('setoption name ' + str(name) + ' value ' + str(value))
        return

    def stop(self):
        self.send('stop')
        self.send('quit')
        return
