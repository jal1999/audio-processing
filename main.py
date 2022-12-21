import wave
import struct


def backwards(sound):
    samples: list[float] = sound['samples'][:]
    samples.reverse()
    return {'rate': sound['rate'], 'samples': samples}


def mix(sound1, sound2, p):
    if sound1['rate'] != sound2['rate']:
        return None
    sample_len: int = min(len(sound1['samples']), len(sound2['samples']))
    new_samples: list[float] = list()
    for i in range(sample_len):
        first_val: float = sound1['samples'][i] * p
        second_val: float = sound2['samples'][i] * (1 - p)
        new_samples.append(first_val + second_val)
    return {'rate': sound1['rate'], 'samples': new_samples}


def pan(sound):
    new_sound = {'rate': sound['rate'], 'left': sound['left'][:], 'right': sound['right'][:]}
    left, right = new_sound['left'], new_sound['right']
    for i in range(len(left)):
        left[i] *= 1 - (i / (len(left) - 1))
        right[i] *= i / (len(right) - 1)
    return new_sound


def remove_vocals(sound):
    new_sound = {'rate': sound['rate'], 'samples': [left - right for left, right in zip(sound['left'], sound['right'])]}
    return new_sound


def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left.append(struct.unpack("<h", frame[:2])[0])
                right.append(struct.unpack("<h", frame[2:])[0])
            else:
                datum = struct.unpack("<h", frame)[0]
                left.append(datum)
                right.append(datum)

        out["left"] = [i / (2 ** 15) for i in left]
        out["right"] = [i / (2 ** 15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left = struct.unpack("<h", frame[:2])[0]
                right = struct.unpack("<h", frame[2:])[0]
                samples.append((left + right) / 2)
            else:
                datum = struct.unpack("<h", frame)[0]
                samples.append(datum)

        out["samples"] = [i / (2 ** 15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2 ** 15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l, r in zip(sound["left"], sound["right"]):
            l = int(max(-1, min(1, l)) * (2 ** 15 - 1))
            r = int(max(-1, min(1, r)) * (2 ** 15 - 1))
            out.append(l)
            out.append(r)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    meow = load_wav("sounds/meow.wav")
    adam = load_wav("sounds/mystery.wav")
    write_wav(backwards(adam), "adamreverse.wav")
    synth = load_wav("sounds/synth.wav")
    water = load_wav("sounds/water.wav")
    write_wav(mix(synth, water, 0.2), "synthwater.wav")
    chick = load_wav("sounds/chickadee.wav")
