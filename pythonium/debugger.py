import os


def terminate():
    os.system("kill -9 %d" % os.getpid())
