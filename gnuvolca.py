#!/usr/bin/env python

import time
import sys
import argparse
import os
import subprocess
import platform
import signal
import simpleaudio

SYRO_SCRIPT = "syro_volcasample_example.%s" % platform.machine()
CWD = os.getcwd()
FULL_PATH_SCRIPT = os.path.join(CWD, "bin", SYRO_SCRIPT)

# https://trac.ffmpeg.org/wiki/AudioChannelManipulation
STEREO_TO_MONO_FILTERGRAPH=' -af "' + ",".join([
    "asplit[a]",
    "aphasemeter=video=0",
    "ametadata=select:key=lavfi.aphasemeter.phase:value=-0.005:function=less",
    "pan=1c|c0=c0",
    "aresample=async=1:first_pts=0",
    "[a]amix",
]) + '"'

FFMPEG_ARGS = "-y -hide_banner -loglevel error -nostats" # + STEREO_TO_MONO_FILTERGRAPH

def format_audio(finp, fout, nbit=16, freq=33000, nac=1):
    cmd = f"ffmpeg -i {finp} -ac {nac} {FFMPEG_ARGS} -sample_fmt s{nbit} -ar {freq} {fout}"
    res = subprocess.Popen(cmd.split(" ")).wait()
    if res > 0:
        raise Exception(f"Audio conversion failed {res}")

def playsound(audiof):
    wave_obj = simpleaudio.WaveObject.from_wave_file(audiof)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def pause_btwn_upload():
    time.sleep(0.5)

def erase_bank(nb):
    clr_out = f"{nb}clear.wav"
    proc = subprocess.Popen([
        FULL_PATH_SCRIPT,
        clr_out,
        f"e{nb}:"
    ])
    res = proc.wait()
    if res > 0:
        raise Exception(f"Conversion failed {res}")
    playsound(clr_out)
    os.remove(clr_out)

def upload(finp, bank_nb, erase=True):
    if erase:
        erase_bank(bank_nb)
        pause_btwn_upload()

    format_audio(finp, "./formatted.wav")
    filename = str(finp).split(".")[0]
    proc = subprocess.Popen([
        FULL_PATH_SCRIPT,
        "./converted.wav",
        f"s{bank_nb}c:./formatted.wav"
    ])
    res = proc.wait()
    if res > 0:
        raise Exception(f"Conversion failed {res}")
    os.remove("./formatted.wav")
    playsound("./converted.wav")
    os.remove("./converted.wav")

def exec_sample(args):
    if not args.bank_nb:
        raise Exception("Bank number not specified")
    if not os.path.isfile(args.sample):
        raise Exception(f"Input file {args.sample} not found")
    upload(args.sample, args.bank_nb)

def exec_upload(args):
    if len(args.set) == 0:
        raise Exception("No sets specified")
    flist = []
    for sample_set in args.set:
        if not os.path.isdir(sample_set):
            raise Exception(f"Sample set directory {sample_set} not found")
        for root, dir, files in os.walk(sample_set):
            for file in [f for f in files if ".wav" in f]:
                flist.append((root, file))

    flist = sorted(flist, key=lambda x: x[1])[:100]
    if len(flist) == 0:
        raise Exception("No file to upload")
    for i, (sample_set, file) in enumerate(flist):
        print(f"[{i}/{len(flist)-1}] {os.path.basename(sample_set.rstrip('/'))}/{file}")
        upload(os.path.join(sample_set, file), i)
        pause_btwn_upload()

def exec_clear(args):
    for nbank in args.bank:
        clr_out = f"{nbank}-stream_clr.wav"
        proc = subprocess.Popen([
            FULL_PATH_SCRIPT,
            clr_out,
            f"e{nbank}:"
        ])
        proc.wait()
        playsound(clr_out)
        os.remove(clr_out)

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

    sample_parser = subp.add_parser("sample")
    sample_parser.add_argument(
        "-n", "--bank-nb",
        type=int,
        help="Bank number to upload to sample into",
    )
    sample_parser.add_argument(
        "sample",
        type=str,
        help="Sample file to upload",
    )

    args = parser.parse_args()

    if args.cmd == "upload":
        exec_upload(args)
    elif args.cmd == "clear":
        exec_clear(args)
    elif args.cmd == "sample":
        exec_clear(args)
    else:
        raise Exception(f"Command not implemented: {args.cmd}")
