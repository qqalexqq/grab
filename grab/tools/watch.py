import os
import signal
import sys
import logging
import time

class Watcher(object):
    """this class solves two problems with multithreaded
    programs in Python, (1) a signal might be delivered
    to any thread (which is just a malfeature) and (2) if
    the thread that gets the signal is waiting, the signal
    is ignored (which is a bug).

    The watcher is a concurrent process (not thread) that
    waits for a signal and the process that contains the
    threads.  See Appendix A of The Little Book of Semaphores.
    http://greenteapress.com/semaphores/

    I have only tested this on Linux.  I would expect it to
    work on the Macintosh and not work on Windows.
    """
    
    def __init__(self):
        """ Creates a child thread, which returns.  The parent
            thread waits for a KeyboardInterrupt and then kills
            the child thread.
        """
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            logging.debug('Watcher process received KeyboardInterrupt')
            signals = (
                ('SIGUSR2', 1),
                ('SIGTERM', 3),
                ('SIGKILL', 5),
            )
            for sig, sleep_time in signals:
                if not os.path.exists('/proc/%d' % self.child):
                    logging.debug('Process terminated!')
                    break
                else:
                    logging.debug('Sending %s signal to child process' % sig)
                    try:
                        os.kill(self.child, getattr(signal, sig))
                    except OSError:
                        pass
                    logging.debug('Waiting 1 second after sending %s' % sig)
                    time.sleep(sleep_time)
        sys.exit()


def watch():
    Watcher()
