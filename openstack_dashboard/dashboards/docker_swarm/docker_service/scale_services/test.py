import threading


def setInterval(func, sec):
    def inner_function():
        func()  # call on it
        setInterval(func, sec)  # do the same function over and over again

    thread = threading.Timer(sec, inner_function)  # have it call inner ever x seconds
    thread.setDaemon(True)
    thread.start()
    return thread


def clearInterval(interval):
    interval.cancel()
    return True


def printX():
    print 1

x = printX()

setInterval(printX(),3000)