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

def format_audio(finp, nbit=16, freq=33000, nac=1):
    fout = os.path.splitext(finp)[0] + "_ok.wav"
    cmd = f"ffmpeg -i {finp} -ac {nac} {FFMPEG_ARGS} -sample_fmt s{nbit} -ar {freq} {fout}"
    res = subprocess.Popen(cmd.split(" ")).wait()
    if res > 0:
        raise Exception(f"Audio conversion failed {res}")
    os.remove(finp)

def playsound(audiof):
    wave_obj = simpleaudio.WaveObject.from_wave_file(audiof)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def pause_btwn_upload():
    time.sleep(1)

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
    filename = str(finp).split(".")[0]
    file_out = f"{bank_nb}-{filename}-stream.wav"
    proc = subprocess.Popen([
        FULL_PATH_SCRIPT,
        file_out,
        f"s{bank_nb}c:" + finp
    ])
    res = proc.wait()
    if res > 0:
        raise Exception(f"Conversion failed {res}")
    playsound(file_out)
    os.remove(file_out)

def exec_upload_sample(args):
    if not args.bank_nb:
        raise Exception("Bank number not specified")
    if not os.path.isfile(args.sample):
        raise Exception(f"Input file {args.sample} not found")
    upload(args.sample, args.bank_nb)

def exec_upload_sets(args):
    if len(args.sets) == 0:
        raise Exception("No sets specified")
    flist = []
    for sample_set in args.sets:
        for root, dir, files in os.walk(os.path.join(args.upload_set, sample_set)):
            for file in [f for f in files if ".wav" in f]:
                flist.append((root, file))

    flist = sorted(flist, key=lambda x: x[1])[:100]
    if args.restart is not None:
        flist = flist[args.restart:]
        i = args.restart
    else:
        i = 0
    for sample_set, file in flist:
        print(f"[{i}/{len(flist)-1}] {sample_set.split('/')[-1]}/{file}")
        upload(os.path.join(sample_set, file), i)
        pause_btwn_upload()
        i += 1

def exec_format_audio(args):
    for root, _, files in os.walk(args.format):
        for f in files:
            if f.endswith("_ok.wav"):
                continue
            format_audio(os.path.join(root, f))

def exec_clear_samples():
    for i in range(100):
        clr_out = f"{i:0>3}-stream_clr.wav"
        proc = subprocess.Popen([
            FULL_PATH_SCRIPT,
            clr_out,
            f"e{i}:"
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

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f", "--format",
        type=str,
        help="Format all the audio files found in this directory to Volca-compatible format"
    )
    group.add_argument(
        "-u", "--upload-set",
        type=str,
        help="Path to directory containing samples to be uploaded"
    )
    group.add_argument(
        "-c", "--clear",
        action="store_true",
        help="Pass this for erasing all samples on the Volca Sample"
    )
    group.add_argument(
        "-s", "--sample",
        type=str,
        help="Path to the wav file containing the sample to upload"
    )
    parser.add_argument(
        "-r", "--restart",
        type=int,
        help="To which index (re)start the upload process")

    parser.add_argument(
        "-b", "--bank-nb",
        type=int,
        help="On which bank upload the given sample")

    parser.add_argument(
        "sets",
        type=str,
        help="Sets to upload",
        nargs="*",
    )

    args = parser.parse_args()

    if args.clear:
        exec_clear_samples()
    elif args.format:
        exec_format_audio(args)
    elif args.upload_set:
        exec_upload_sets(args)
    elif args.sample:
        exec_upload_sample(args)
    else:
        raise Exception("Unable to know what to do")
