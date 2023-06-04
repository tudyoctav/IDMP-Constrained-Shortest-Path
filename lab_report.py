import collections
from copy import copy
import logging
import os
from pathlib import Path
from typing import Callable
from lab.reports import Report
from lab import tools
from lab.tools import Properties
import pandas as pd

class FunctionReport(Report):
    """Instead of writing the results to file calls the function with the read data"""

    def __init__(self, function: Callable, attributes=None, format="html", filter=None, **kwargs):
        super().__init__(attributes, format, filter, **kwargs)
        self.function = function
    
    def write(self):
        props: Properties = self.props.items()
        result = []
        for name, values in props:
            dictionary = copy(values)
            dictionary["id"] = name
            result.append(dictionary)
        result = pd.DataFrame(result)
        self.function(result, self.outfile)

def write_csv(frame: pd.DataFrame, outfile: str):
    frame.to_csv(outfile)

class CSVReport(FunctionReport):
    def __init__(self, attributes=None, filter=None, **kwargs):
        super().__init__(write_csv, attributes, "html", filter, **kwargs)
