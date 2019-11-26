#!/usr/bin/env python3
"""Run multiple runs with different random seeds."""

import argparse
import json
import multiprocessing
import os
import subprocess
from copy import deepcopy

from logzero import logger

formatter_class = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(formatter_class=formatter_class)

parser.add_argument(
    "--path",
    help="The path to the base config file.",
    type=str,
    default="experiments/config_compas.json",
)
parser.add_argument(
    "--runs", help="How many runs to perform.", type=int, default=5
)
parser.add_argument(
    "--offset", help="Offset for random seeds.", type=int, default=0
)
parser.add_argument(
    "--processes",
    help="How many processes to run in parallel.",
    type=int,
    default=3,
)

args = parser.parse_args().__dict__
config_path = os.path.abspath(args["path"])
offset = args["offset"]

# -------------------------------------------------------------------------
# region Load config file and parameters
# -------------------------------------------------------------------------
logger.info(f"Read base config file from {config_path}")
with open(config_path, "r") as f:
    config = json.load(f)

result_dir = config["results"]["result_dir"]
if not os.path.exists(result_dir):
    os.makedirs(result_dir)


def run_single(i):
    """Perform a single run as a subprocess."""
    tmp_config = deepcopy(config)
    tmp_config["seed"] = i + offset
    tmp_config["results"]["name"] = f"{i + offset:03d}"
    tmp_config_path = os.path.join(result_dir, f"config_{i + offset:03d}.json")
    with open(tmp_config_path, "w") as tmp_file:
        json.dump(tmp_config, tmp_file, indent=2)
    subprocess.run(
        ["python", "run.py", "--path", f"{tmp_config_path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


pool = multiprocessing.Pool(processes=args["processes"])
pool.map(run_single, range(args["runs"]))
