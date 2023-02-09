import os
import json
import subprocess

from . import ALL_CATEGORIES
from .tools import pause_btwn_upload, format_audio, playsound, convert_audio
from .clear import erase_bank

def upload(finp, bank_nb, erase=True):
    if erase:
        erase_bank(bank_nb)
        pause_btwn_upload()

    format_audio(finp, "./formatted.wav")
    filename = str(finp).split(".")[0]
    convert_audio("./formatted.wav", bank_nb, "./converted.wav")
    os.remove("./formatted.wav")
    playsound("./converted.wav")
    os.remove("./converted.wav")

def exec_upload(args):
    if len(args.set) == 0:
        raise Exception("No sets specified")

    metadata = {
        "ignore": dict(),
        "last_upload": dict(),
    }
    if os.path.isfile(args.metadata):
        with open(args.metadata, "r") as f:
            metadata.update(json.load(f))

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

    metadata["last_upload"] = dict()
    tot_sample_nb = sum([len(l) for l in all_samples.values()])
    i = 0
    for cat in ALL_CATEGORIES:
        flist = sorted(all_samples[cat], key=lambda x: x[1])
        for sample_set, file in flist:
            if sample_set in metadata["ignore"] and file in metadata["ignore"][sample_set] and metadata["ignore"][sample_set][file]:
                continue
            print(f"[{i}/{tot_sample_nb-1}] {os.path.basename(sample_set.rstrip('/'))}/{file}")
            upload(os.path.join(sample_set, file), i)
            metadata["last_upload"][i] = f"{sample_set}/{file}"
            pause_btwn_upload()
            print("")
            i += 1

    with open(args.metadata, "w") as f:
        json.dump(metadata, f, indent=2)

def exec_single(args):
    if not args.bank_nb:
        raise Exception("Bank number not specified")
    if not os.path.isfile(args.sample):
        raise Exception(f"Input file {args.sample} not found")
    upload(args.sample, args.bank_nb)

def exec_reload(args):
    print("TODO")
