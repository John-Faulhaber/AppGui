'''
Module containing subclass of pySerial with MUTEX locking around resource opening and closing.
'''
# BUilt-in
import threading
# pySerial
import serial


class MutexSerial(serial.Serial):
    '''
    Subclass of serial.Serial adding mutex lock to entry and exit context manager methods.
    __enter__ and __exit__ methods taken directly from pySerial repository.
    '''
    # Add MUTEX lock object as a class attribute
    # Inherit the rest of serial.Serial
    def __init__(self, *args, **kwargs):
#        print("MutexSerial initiated")
        self.my_lock = threading.Lock()
        super().__init__(*args, **kwargs)  # Inherit parent class while passing all arguments to Parent class constructor - allows parent class methods to receive their required args that were passed into instance of child class
#        print("serial inherited")

    # Context manager entry with acquire mutex lock
    def __enter__(self):
        self.my_lock.acquire()
#        print(f'Am I locked? {self.my_lock.locked()}')
        if not self.is_open:
            self.open()
        return self

    # Context manager exit with release mutex lock
    def __exit__(self, *args, **kwargs):
        self.close()
        self.my_lock.release()
#        print(f'Am I unlocked? {self.my_lock.locked()}')