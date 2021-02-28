import ast
import numpy as np
from datetime import time, date 

class SampleClass(object):
    def __init__(self, argument1, keyword_argument = 'sample'):
        self.attribute1 = argument1
        self.attribute2 = self.__sample__private_function__(keyword_argument)
        self.sample_public_function(self.attribute1)
    def sample_public_function(self, argument):
        return self.attribute1, argument 

    def __sample_private_function__(self, argument):
        return argument