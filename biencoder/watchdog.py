# TODO better to not start the watchdog thread at every message.
# the thread should stay alive

import time
import psutil
import threading
import signal

try:
    import torch
    SKIP_GPU = False
except ImportError:
    print('Cannot import torch. Skipping GPU watchdog.')
    SKIP_GPU = True

GLOBAL_EXCEPTION = None

class TimeoutException(Exception):
    pass

class MemoryLimitExceededException(Exception):
    pass

class GPUMemoryLimitExceededException(Exception):
    pass

class WatchdogThreadException(Exception):
    pass

class WatchdogThread(threading.Thread):
    def __init__(self, timeout, memory, gpu, loop_time = 10, alarm_time = 1, stop=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.timeout = timeout
        self.memory = memory
        self.gpu = gpu
        self.loop_time = loop_time
        self.alarm_time = alarm_time
        self.stop = stop

        self.stop_flag = False

    def set_handler(self):
        def handler(signum, frame):
            global GLOBAL_EXCEPTION
            if GLOBAL_EXCEPTION is None:
                raise WatchdogThreadException("Resource limit reached. BUT no more information.")
            else:
                raise GLOBAL_EXCEPTION
        signal.signal(signal.SIGALRM, handler)

    def reset_time(self):
        self.time_limit = time.time() + self.timeout

    def get_time(self):
        return time.time()

    def get_memory(self):
        return psutil.Process().memory_info().rss

    def get_gpu(self):
        if SKIP_GPU:
            return self.gpu - 1 # dummy value to never go over threshold
        return torch.cuda.memory_allocated()

    def check(self):
        global GLOBAL_EXCEPTION

        time = self.get_time()
        mem = self.get_memory()
        gpu = self.get_gpu()

        if time > self.time_limit:
            GLOBAL_EXCEPTION = TimeoutException("Function execution time exceeded: {} > {}".format(time, self.time_limit))
            print('raising timeout')
        if mem > self.memory:
            GLOBAL_EXCEPTION = MemoryLimitExceededException("Memory usage exceeded: {} > {}".format(mem, self.memory))
            print('rasing mem')
        if gpu > self.gpu:
            GLOBAL_EXCEPTION = GPUMemoryLimitExceededException("GPU Memory usage exceeded: {} > {}".format(gpu, self.gpu))
            print('raising gpu')

        if GLOBAL_EXCEPTION is not None:
            if self.stop:
                self.stop_flag = True
            signal.alarm(self.alarm_time)

    def run(self):
        self.reset_time()
        while not self.stop_flag:
            self.check()
            time.sleep(self.loop_time)
