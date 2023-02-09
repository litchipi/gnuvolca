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

ALL_CATEGORIES = [
    "kick",
    "bass",
    "snare",
    "hat",
    "ride",
    "perc",
    "instrument",
    "synth",
    "melody",
    "fx",
    "signal",
]

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

FFMPEG_ARGS = "-y -hide_banner -loglevel error -nostats"

def warn(msg):
    print(f"WARN\t{msg}")

def pause_btwn_upload():
    time.sleep(0.8)

def format_audio(finp, fout, nbit=16, freq=33000, nac=1):
    cmd = f"ffmpeg -i {finp} -ac {nac} {FFMPEG_ARGS} -sample_fmt s{nbit} -ar {freq} {fout}"
    res = subprocess.Popen(cmd.split(" ")).wait()
    if res > 0:
        raise Exception(f"Audio conversion failed {res}")

    # Maximize the volume of the audio
    res = subprocess.Popen([
        os.path.join(CWD, "bin", "maximize_volume"),
        "{fout}"
    ]).wait()

def playsound(audiof):
    wave_obj = simpleaudio.WaveObject.from_wave_file(audiof)
    play_obj = wave_obj.play()
    play_obj.wait_done()

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
    #  os.remove("./formatted.wav")
    playsound("./converted.wav")
    #  os.remove("./converted.wav")

def exec_sample(args):
    if not args.bank_nb:
        raise Exception("Bank number not specified")
    if not os.path.isfile(args.sample):
        raise Exception(f"Input file {args.sample} not found")
    upload(args.sample, args.bank_nb)

def exec_upload(args):
    if len(args.set) == 0:
        raise Exception("No sets specified")

    if os.path.isfile(args.metadata):
        with open(args.metadata, "r") as f:
            metadata = json.load(f)
    else:
        metadata = {
            "ignore": dict(),
            "last_upload": list(),
        }

    # TODO      Make configurable
    all_samples = {cat:list() for cat in ALL_CATEGORIES}

    for sample_set in args.set:
        if not os.path.isdir(sample_set):
            raise Exception(f"Sample set directory {sample_set} not found")
        for root, dir, files in os.walk(sample_set):
            for file in [f for f in files if ".wav" in f]:
                category = file.rstrip(".wav")[:-2].lower()
                if category not in ALL_CATEGORIES:
                    warn(f"File {root}/{file} has unknown category {category}, ignoring ...")
                    continue
                all_samples[category].append((root, file))

    metadata["last_upload"] = list()
    tot_sample_nb = sum([len(l) for l in all_samples.values()])
    i = 0
    for cat in ALL_CATEGORIES:
        flist = sorted(all_samples[cat], key=lambda x: x[1])
        for sample_set, file in flist:
            if sample_set in metadata["ignore"] and file in metadata["ignore"][sample_set] and metadata["ignore"][sample_set][file]:
                continue
            print(f"[{i}/{tot_sample_nb-1}] {os.path.basename(sample_set.rstrip('/'))}/{file}")
            upload(os.path.join(sample_set, file), i)
            metadata["last_upload"].append(f"{i}: {sample_set}/{file}")
            pause_btwn_upload()
            print("")
            i += 1

    with open(args.metadata, "w") as f:
        json.dump(metadata, f, indent=2)

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
        exec_sample(args)
    else:
        raise Exception(f"Command not implemented: {args.cmd}")
