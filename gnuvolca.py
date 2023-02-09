#!/usr/bin/env python

import time
import sys
import json
import argparse
import os
import subprocess
import platform
import signal
import simpleaudio

from src.upload import exec_upload, exec_single, exec_reload
from src.clear import exec_clear

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="gnuvolca",
        description="""
        Korg Volca Sample uploader for linux.
        Detects all .wav files in the specified directory, converts and reproduces all file uploads.
        """
    )

    subp = parser.add_subparsers(dest="cmd")

    upload_parser = subp.add_parser("upload")
    upload_parser.add_argument(
        "--metadata", "-m",
        type=str,
        help="Path to the metadata JSON file",
        default="metadata.json",
    )
    upload_parser.add_argument(
        "set",
        type=str,
        help="Set to upload",
        nargs="+",
    )

    clear_parser = subp.add_parser("clear")
    clear_parser.add_argument(
        "bank",
        type=int,
        help="Bank to clear",
        nargs="+",
    )

    single_parser = subp.add_parser("single")
    single_parser.add_argument(
        "-n", "--bank-nb",
        type=int,
        help="Bank number to upload the sample into",
    )
    single_parser.add_argument(
        "sample",
        type=str,
        help="Sample file to upload",
    )

    reload_parser = subp.add_parser("reload")
    reload_parser.add_argument(
        "sample",
        type=int,
        help="The sample to reload into the machine",
    )

    args = parser.parse_args()

    if args.cmd == "upload":
        exec_upload(args)
    elif args.cmd == "clear":
        exec_clear(args)
    elif args.cmd == "single":
        exec_single(args)
    elif args.cmd == "reload":
        exec_reload(args)
    else:
        raise Exception(f"Command not implemented: {args.cmd}")
