import boto3
import os
from contextlib import closing

VOICE = "Matthew"
HOME_DIR = os.path.dirname(os.path.realpath(__file__))
TXT_FILES_DIR = os.path.join(HOME_DIR, "text-files")
MP3_FILES_DIR = os.path.join(HOME_DIR, "audio-files")
MP3_FILES_ARCHIVE = os.path.join(MP3_FILES_DIR, "archive")

def main():

    txt_files = os.listdir(TXT_FILES_DIR)
    mp3_files = os.listdir(MP3_FILES_ARCHIVE)    # mp3s are kept in two folders
    mp3_files.extend(os.listdir(MP3_FILES_DIR))

    txt_files = [os.path.join(TXT_FILES_DIR, f) for f in txt_files if ".txt" in f]
    audio_files = [os.path.join(MP3_FILES_DIR, f) for f in mp3_files if ".mp3" in f]
    txt = [(f, get_text(f)) for f in txt_files]
    for txtfile, text in txt:
        fname = txtfile_to_mp3_fname(txtfile)
        if fname not in audio_files:
            txt_to_mp3(text, fname)
        else:
            print("Already converted {}.".format(fname.split("/")[-1]))


def txtfile_to_mp3_fname(txtfile):
    # these come in with full path '/Users/.../file.txt'

    # remove full path and keep only file name i.e. 'file.txt'
    fname_txt = txtfile.split("/")[-1]

    # remvoe .txt and add .mp3
    fname_mp3 = fname_txt.split(".")[0] + ".mp3"

    # return full path
    return os.path.join(MP3_FILES_DIR, fname_mp3)


def get_text(fname):
    with open(fname, "r") as f:
        text = f.read()
    return text


def txt_to_mp3(text, fname):
    print("Converting {}".format(fname))
    rest = text

    # from the AWS polly tutorial:
    # because single invocation of the polly synthesize_speech api can
    # transform text with about 1,500 characters, we are dividing the
    # post into blocks of approximately 1,000 characters.
    textBlocks = []
    while len(rest) > 1100:
        begin = 0
        end = rest.find(".", 1000)
        if end == -1:
            end = rest.find(" ", 1000)
        end += 1  # this includes the period with the sentence of interest
        textBlock = rest[begin:end]
        rest = rest[end:]
        textBlocks.append(textBlock)
    textBlocks.append(rest)

    # for each block, invoke Polly API, which will transform text into audio
    output = os.path.join(os.getcwd(), "audio-files", fname)
    polly = boto3.client("polly", region_name="us-east-1")

    for textBlock in textBlocks:
        response = polly.synthesize_speech(
            OutputFormat="mp3", Text=textBlock, VoiceId=VOICE
        )
        print("received a response")
        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                with open(output, "ab") as f:
                    f.write(stream.read())


if __name__ == "__main__":
    main()

