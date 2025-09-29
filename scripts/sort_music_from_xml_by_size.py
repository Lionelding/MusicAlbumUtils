# -*- coding: utf-8 -*-
import os
from os import listdir
import xml.etree.ElementTree as ET
import xmltodict
import shutil
import eyed3
import mutagen

MUSIC_FILE_PATH = "/Users/liqiang.ding/Music/2008_2011"
SONGS_TO_IGNORE = [159, 222, 233, 270, 357, 358]

# XML_PATH = "/Users/liqiang.ding/Music/SONGS.xml"
# NEW_FILE_PATH = "/Users/liqiang.ding/Music/2008_2011_SONGS_reordered"

# XML_PATH = "/Users/liqiang.ding/Music/Romantic Piano.xml"
# NEW_FILE_PATH = "/Users/liqiang.ding/Music/2008_2011_Piano_reordered"

# XML_PATH = "/Users/liqiang.ding/Music/dream.xml"
# NEW_FILE_PATH = "/Users/liqiang.ding/Music/2008_2011_dream_reordered"

XML_PATH = "/Users/liqiang.ding/Music/VOA special.xml"
NEW_FILE_PATH = "/Users/liqiang.ding/Music/2008_2011_VoaSpecial_reordered"


eyed3.LOCAL_ENCODING = "utf-8"

# eyed3.log.setLevel("ERROR")

def edit_music_info(music_path, tilte, artist, album):

    audiofile = eyed3.load(music_path)

    if (audiofile.tag == None):
        audiofile.initTag()

    audiofile.tag.title = tilte
    audiofile.tag.artist = artist
    audiofile.tag.album = album
    audiofile.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION, encoding='utf-8')
    audiofile.tag.save()

    return

def edit_music_info_mutagen(music_path, title, artist, album):
    audiofile = mutagen.File(music_path)
    audiofile['©nam'] = [title]
    audiofile['©ART'] = [artist]
    audiofile['©alb'] = [album]
    audiofile.save()

    return 

def main():
    """
    REF: https://stackoverflow.com/questions/48821725/xml-parsers-expat-expaterror-not-well-formed-invalid-token
    """
    tree = ET.parse(XML_PATH)
    xml_data = tree.getroot()
    xmlstr = ET.tostring(xml_data, encoding='utf-8', method='xml')

    data_dict = dict(xmltodict.parse(xmlstr, process_namespaces=True))

    music_list = listdir(MUSIC_FILE_PATH)

    for i, song in enumerate(data_dict['plist']['dict']['array']['dict']['array']['dict']):
        Track_ID = song['integer']

        apple_index = data_dict['plist']['dict']['dict']['key'].index(Track_ID)
        apple_information = data_dict['plist']['dict']['dict']['dict'][apple_index]

        assert apple_information['integer'][0] == Track_ID
        
        target_name = apple_information['string'][0]
        target_size = int(apple_information['integer'][1])
        target_artist = apple_information['string'][1]
        target_album = apple_information['string'][2]
        print(i, target_name)
        
        for j, music in enumerate(music_list):

            if target_size == os.path.getsize(os.path.join(MUSIC_FILE_PATH, music)):
                # import pdb;pdb.set_trace()

                old_name = os.path.join(MUSIC_FILE_PATH, music_list[j])
                old_format = old_name.split(".")[-1]
                liqiang_index = str(i).zfill(3)
                new_name = os.path.join(NEW_FILE_PATH, f'{liqiang_index}_{target_name}.{old_format}')

                new_name = new_name.replace("http://www.rrting", "")
                new_name = new_name.replace(" xmkiss.com/box", "")
                shutil.copy(old_name, new_name)

                if i not in SONGS_TO_IGNORE:
                    if old_format == 'mp3':
                        edit_music_info(new_name, f'{liqiang_index}_{target_name}', target_artist, target_album)
                    elif old_format == 'm4a':
                        edit_music_info_mutagen(new_name, f'{liqiang_index}_{target_name}', target_artist, target_album)


                break
                

        print('lol') 

if __name__ == '__main__':
	main()