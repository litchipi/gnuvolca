import os
import subprocess

from .tools import playsound, FULL_PATH_SCRIPT

def erase_bank(nb):
    clr_out = f"{nb}clear.wav"
    proc = subprocess.Popen([
        FULL_PATH_SCRIPT,
        clr_out,
        f"e{nb}:"
    ])
    res = proc.wait()
    if res > 0:
        raise Exception(f"Bank clear failed: {res}")
    playsound(clr_out)
    os.remove(clr_out)

def exec_clear(args):
    for nbank in args.bank:
        print(f"Clearing bank {nbank}")
        clr_out = f"{nbank}-stream_clr.wav"
        proc = subprocess.Popen([
            FULL_PATH_SCRIPT,
            clr_out,
            f"e{nbank}:"
        ])
        proc.wait()
        playsound(clr_out)
        os.remove(clr_out)
        print("")
