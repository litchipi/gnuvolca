import os
import time
import simpleaudio
import subprocess
import platform

SYRO_SCRIPT = "syro_volcasample_example.%s" % platform.machine()
CWD = os.getcwd()

FULL_PATH_SCRIPT = os.path.join(CWD, "bin", SYRO_SCRIPT)
FFMPEG_ARGS = "-y -hide_banner -loglevel error -nostats"

def playsound(audiof):
    wave_obj = simpleaudio.WaveObject.from_wave_file(audiof)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def convert_audio(finp, bank_nb, fout):
    res = subprocess.Popen([
        FULL_PATH_SCRIPT,
        fout,
        f"s{bank_nb}c:{finp}"
    ]).wait()
    if res > 0:
        raise Exception(f"Conversion failed: {res}")

def warn(msg):
    print(f"WARN\t{msg}")

def pause_btwn_upload():
    time.sleep(0.8)

def format_audio(finp, fout, nbit=16, freq=33000, nac=1):
    fout = os.path.abspath(fout)
    cmd = f"ffmpeg -i {finp} -ac {nac} {FFMPEG_ARGS} -sample_fmt s{nbit} -ar {freq} {fout}"
    res = subprocess.Popen(cmd.split(" ")).wait()
    if res > 0:
        raise Exception(f"Audio conversion failed {res}")

    # Maximize the volume of the audio
    res = subprocess.Popen([
        os.path.join(CWD, "bin", "maximize_volume"),
        fout
    ]).wait()
    if res > 0:
        raise Exception(f"Volume maximization failed {res}")
