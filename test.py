import os
from os import listdir
import eyed3
import re
import shutil

OLD_FILE_PATH = "/Users/liqiang.ding/Music/2008_2011/F00/"
New_FILE_PATH = "/Users/liqiang.ding/Music/2008_2011_reordered"


def edit_music_info(music_path, metatag):

    audiofile = eyed3.load(music_path)

    # if (audiofile.tag == None):
    #     audiofile.initTag()

    audiofile.tag.title = metatag
    audiofile.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION, encoding='utf-8')
    audiofile.tag.save()

    return
def main():
    music_list = listdir(OLD_FILE_PATH)
    # import pdb;pdb.set_trace()

    music_list = [m for m in music_list if m.split('.')[-1]=="mp3" or m.split('.')[-1]=="mp3" == "m4a"]

    for song in music_list:
        # liqiang_index, song_name = song.split("_", 1)
        # print(liqiang_index, song_name)

        # liqiang_index = liqiang_index.zfill(3)
        # full_name = liqiang_index + "_" + song_name

        old_name = os.path.join(OLD_FILE_PATH, song)
        print(old_name, os.path.getsize(old_name))

        # audiofile = eyed3.load(old_name)
        # try:
        #     print(audiofile.tag.title, audiofile.tag.artist, audiofile.tag.album, audiofile.tag.album_artist)
        # except AttributeError:
        #     print('skip')
        # new_name = os.path.join(New_FILE_PATH, full_name)
        # shutil.copy(old_name, new_name)

        # import pdb;pdb.set_trace()

        # edit_music_info(new_name, full_name)
        # print('lol')


if __name__ == '__main__':
	main()