#!/usr/bin/env python

import pandas as pd
import numpy as np
import os
from abc import ABC, abstractmethod

# Line inherits from image which inherits from sample 

class SampleBase(ABC):
    
    @property
    def name():

class Sample(SampleBase):
    def __init__(self):
        # set sample name
        # determine if regular name or full name

class Image:
    def __init__(self):
        # set image location
    
    def parse_lines():
        # pasrse rows of line data

class Line:
    def __init__(self):
        # set index
        # set null for length, label, and intercepts
    
    def parseline():
        # clean; call setlabel(), setlength(), setinctercepts() 

    def set_label(cleaned):
        label =  
    def set_length(cleaned):
        length = 
    def set_intercepts(cleaned):
        intercepts =
