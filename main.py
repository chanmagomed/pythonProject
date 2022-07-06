# importing libraries
import speech_recognition as sr

import os

from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.silence import get_time
from deep_translator import MyMemoryTranslator
podcasts = os.listdir("podcasts")
def ms2s(ms):
    mspart = ms % 1000
    mspart = str(mspart).zfill(3)
    spart = (ms // 1000) % 60
    spart = str(spart).zfill(2)
    mpart = (ms // 1000) // 60
    mpart = str(mpart).zfill(2)

    # srt time format
    stype = "00:" + mpart + ":" + spart + "," + mspart
    return stype





# a function that splits the audio file into chunks
# and applies speech recognition

def silence_based_conversion(path="podcast.mp3", voids=500, db=-45,addDb=0):
    # open the audio file stored in
    # the local system as a wav file.
    song = AudioSegment.from_wav(path)
    co = get_time(song, min_silence_len=voids, silence_thresh=db, keep_silence=100, seek_step=1)
    # open a file where we will concatenate
    # and store the recognized text
    try:
        os.mkdir('subs')
    except(FileExistsError):
        pass
    textPath = ("subs/"+path[9:-3]+"srt")
    fh = open(textPath, "w+", encoding="utf-8")

    # split track where silence is 0.5 seconds
    # or more and get chunks
    chunks = split_on_silence(song,
                              # must be silent for at least 0.5 seconds
                              # or 500 ms. adjust this value based on user
                              # requirement. if the speaker stays silent for
                              # longer, increase this value. else, decrease it.
                              min_silence_len=voids,

                              # consider it silent if quieter than -16 dBFS
                              # adjust this per requirement
                              silence_thresh=db,
                              keep_silence=200
                              )

    # create a directory to store the audio chunks.
    try:
        os.mkdir('audio_chunks')
    except(FileExistsError):
        pass


    # move into the directory to
    # store the audio files.
    os.chdir('audio_chunks')

    i = 0
    # process each chunk
    print(len(chunks))
    for chunk in chunks:

        # Create 0.5 seconds silence chunk
        chunk_silent = AudioSegment.silent(duration=1000)

        # add 0.5 sec silence to beginning and
        # end of audio chunk. This is done so that
        # it doesn't seem abruptly sliced.
        audio_chunk = chunk_silent + chunk + chunk_silent
        audio_chunk = audio_chunk+addDb

        # export audio chunk and save it in
        # the current directory.
        print("saving chunk{0}.wav".format(i))
        # specify the bitrate to be 192 k
        audio_chunk.export("./chunk{0}.wav".format(i), bitrate='192k', format="wav")

        # the name of the newly created chunk
        filename = 'chunk' + str(i) + '.wav'

        print("Processing chunk " + str(i))

        # get the name of the newly created chunk
        # in the AUDIO_FILE variable for later use.
        file = filename

        # create a speech recognition object
        r = sr.Recognizer()

        # recognize the chunk
        with sr.AudioFile(file) as source:
            # remove this if it is not working
            # correctly.
            r.adjust_for_ambient_noise(source)
            audio_listened = r.listen(source)

        try:
            # try converting it to text
            rec = r.recognize_google(audio_listened)
            # write the output to the file.
            #rec = MyMemoryTranslator( source="en", target='ru').translate(rec)
            fh.write(str(i)+"\n")
            fh.write(ms2s(co[0][i]) + " --> " + ms2s(co[1][i])+"\n")
            fh.write(rec + ".\n \n")

        # catch any errors.
        except sr.UnknownValueError:
            print("Could not understand audio")

        except sr.RequestError as e:
            print("Could not request results. check your internet connection")

        i += 1

    os.chdir('..')


if __name__ == '__main__':
    print('enter db')
    db = 0-int(input())
    print('enter voidc')
    voids = int(input())
    print('enter addDb')
    addDb = int(input())

    for podcast in podcasts:
        silence_based_conversion("podcasts/"+podcast, voids=voids, db=db, addDb=addDb)