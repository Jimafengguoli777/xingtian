"""
XT init module.

We register all the system module in here.
"""
from xt.train import main as train
from xt.evaluate import main as evaluate
from xt.benchmarking import main as benchmarking
from zeus.common.util.register import register_xt_defaults
register_xt_defaults()

__version__ = '0.2.0'

__ALL__ = ["train", "evaluate", "benchmarking"]
