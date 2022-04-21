import threading
import sys
import os
from numpy import sign
import pyautogui
class Capturing():
    def __init__(self,signal):
        self._stdout = None
        self._stderr = None
        self._r = None
        self._w = None
        self._thread = None
        self._on_readline_cb = None
        self.signal = signal
    def _handler(self):
        while not self._w.closed:
            try:
                while True:
                    line = self._r.readline()
                    if len(line) == 0: break
                    if self._on_readline_cb: 
                        # pyautogui.alert("Complete!",title=line)
                        try:
                            self.signal.emit(line)
                        except:
                            pyautogui.alert("Errors!",title=line)
                        self._on_readline_cb(line)
            except:
                break

    def print(self, s, end=""):
        print(s, file=self._stdout, end=end)

    def on_readline(self, callback):
        self._on_readline_cb = callback
        
    def start(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        r, w = os.pipe()
        r, w = os.fdopen(r, 'r'), os.fdopen(w, 'w', 1)
        self._r = r
        self._w = w
        sys.stdout = self._w
        sys.stderr = self._w
        self._thread = threading.Thread(target=self._handler)
        self._thread.start()

    def stop(self):
        self._w.close()
        if self._thread: self._thread.join()
        self._r.close()
        sys.stdout = self._stdout
        sys.stderr = self._stderr

if __name__ == "__main__":

    capturing = Capturing()

    def on_read(line):
        capturing.print("ddd"+line)

    capturing.on_readline(on_read)
    capturing.start()
    for i in range(10):
        print(i)
        print("xxxxxxx")
    capturing.stop()