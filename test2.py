from threading import Timer
ob={}

def a():
    ob["3"]=999
    print(ob)

Timer(3,a,()).start()