# GNU volca

Remake of the tool [gnuvolca](https://github.com/grafuls/gnuvolca), 95% of the work here has to be
credited to `grafuls` as it's taken from here.

To upload samples to your volca, this tool will convert them to the WAV format
supported by your volca sample, maximize the sound of the sample without any distortion
(see project [maximize_volume](https://github.com/litchipi/maximize_wav_volume.git)),
convert it to the format understood by the machine, and "play" the data into your device's input.

## Dependencies

Because of all the dependencies and tools required to make this project work, the best way is
to install `nix` and use the pre-defined scripts in the flake (see below)

## Usage

**BEFORE DOING ANYTHING, PLUG A JACK CABLE TO YOUR VOLCA, DO NOT DAMAGE YOUR EAR OR DEVICES**

In a `.all_categories.json` file, place the categories of sample you want to use.  
The idea is to store samples with a filename `<category><number>.wav` inside folder,
and then upload them all together so all the `kick` samples are together, even if splitted
in your folder architecture.

### Example

```
.all_categories.json
[
  "kick",
  "snare",
  "bass",
]
```

```
Your folders
samples/
 | trance/
 | | Kick01.wav
 | | Snare01.wav
 | | Snare02.wav
 | 
 | edm/
 | | Kick01.wav
 | | Kick02.wav
 | | Snare01.wav
```

Then run `nix run .#upload -- ./samples/trance ./samples/edm` and once completed, all your kicks are together, all your snares are together. Tadaa !

## Upload a single sample to the device

Use the command `nix run .#single -- <sample_path> <bank_number>` to upload it

## Remove sample from a bank

Use the command `nix run .#clear -- <bank_number> [other bank numbers]`

## Check which sample has been uploaded to which bank

To know which sample is on which bank, check the generated file `metadata.json`.  
Inside it you will find the data related to the latest upload, and will be able to add samples you wish to ignore when uploading whole folders.
