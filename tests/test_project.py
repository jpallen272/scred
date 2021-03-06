# Testing class project.RedcapProject

import os
import sys

import pytest
import pandas as pd

sys.path.insert(
    0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')
    )
)

from scred import RedcapProject
from . import testdata

# ---------------------------------------------------

def test_RedcapProject_init_with_token_and_url():
    faketoken = "ABCD9999DDDDXXZZ067JTP01Y44MSPD1"
    fakeurl = "https://redcap.botulism.org/api/"
    rp = RedcapProject(
        token=faketoken,
        url=fakeurl,
    )
