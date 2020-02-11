import sqlite3
import threading
import os

def instance_exists(func):
    def wraper(self, *args, **kwargs):
        if threading.get_ident() not in self.instances:
            self.instances[threading.get_ident()] = sqlite3.connect(self.file)
        func(self, self.instances[threading.get_ident()], *args, **kwargs)

    return wraper

class Database:
    def __init__(self, file):
        self.file = os.path.join(os.getcwd(),file)
        self.instances = {}

    @instance_exists
    def execute(self,instance,*args,**kwargs):
        return instance.execute(*args,**kwargs)

    @instance_exists
    def commit(self,instance,*args,**kwargs):
        return instance.commit(*args,**kwargs)

    @instance_exists
    def close(self,instance,*args,**kwargs):
        return instance.close(*args,**kwargs)