#!/usr/bin/env python

import argparse
from ctypes import cdll
from PyQt4 import QtCore, QtGui
import signal
import sys
import time

# Switch from Python's signal handler to the default one, to allow ^C to
# work even if this thread is in the ctype function.
#
# NOTE: to affect all signals, iterate over range(1, signal.NSIG)
for sig in (signal.SIGINT,):
    try:
        signal.signal(sig, signal.SIG_DFL)
    except RuntimeError:
        pass

libloop = cdll.LoadLibrary('./libloop.so')


def time_qthread(f):
    def f_wrapper(*args, **kwargs):
        self = QtCore.QThread.currentThread()
        start = time.time()
        print >> sys.stderr, 'Start %s' % self

        retval = f(*args, **kwargs)

        end = time.time()
        print >> sys.stderr, 'Finish %s in %.1fs' % (self, end-start)

    return f_wrapper


class Worker(QtCore.QObject):
    def __init__(self):
        super(Worker, self).__init__()

    @time_qthread
    @QtCore.pyqtSlot()
    def run_ctype(self):
        libloop.do_loop()

    @time_qthread
    @QtCore.pyqtSlot()
    def run_py(self):
        for i in xrange(200000000):
            j = i

class MyWindow(QtGui.QWidget):
    def __init__(self, num_thread, ftype, parent=None):
        """
        :param num_thread: Number of worker threads.
        :type num_thread: int

        :param ftype: Worker function is run_<ftype>
        :type ftype: str
        """
        super(MyWindow, self).__init__(parent)

        self.worker = map(lambda x: Worker(), [None]*num_thread)
        self.thread = map(lambda x: QtCore.QThread(), [None]*num_thread)

        for w,t in zip(self.worker, self.thread):
            w.moveToThread(t)

            worker_f = getattr(w, 'run_' + ftype)
            t.started.connect(worker_f)
            t.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test impact of GIL on '
            'Python\'s shared-memory parallelism')
    parser.add_argument('num_thread', metavar='NUM_THREAD', type=int, nargs=1,
                        help='Number of QThread(s)')
    parser.add_argument('ftype', metavar='FUNC', type=str, nargs=1,
                        choices=['ctype', 'py'],
                        help='Value must be either ctype or py')
    args = parser.parse_args()
    args.num_thread = args.num_thread[0]
    args.ftype = args.ftype[0]
    print args.num_thread, args.ftype
 
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('MyWindow')
    main = MyWindow(args.num_thread, args.ftype)
    main.show()
    sys.exit(app.exec_())
