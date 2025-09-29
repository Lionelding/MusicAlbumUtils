# -*- coding: utf-8 -*-
import os
from os import listdir
import xml.etree.ElementTree as ET
import xmltodict
import shutil
import eyed3

XML_PATH = "/Users/liqiang.ding/Music/荒城岁月.xml"
MUSIC_FILE_PATH = "/Users/liqiang.ding/Music/荒城岁月"
NEW_FILE_PATH = "/Users/liqiang.ding/Music/荒城岁月_reordered"

eyed3.LOCAL_ENCODING = "utf-8"

def edit_music_info(music_path, metatag):

    audiofile = eyed3.load(music_path)

    if (audiofile.tag == None):
        audiofile.initTag()

    audiofile.tag.title = metatag
    audiofile.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION, encoding='utf-8')
    audiofile.tag.save()

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
        print(i, target_name)
        
        for j, music in enumerate(music_list):
            if target_name in music:
                old_name = os.path.join(MUSIC_FILE_PATH, music_list[j])
                new_name = os.path.join(NEW_FILE_PATH, f'{i}_{target_name}.mp3')
                shutil.copy(old_name, new_name)
                
                if i not in [183, 195, 468]:
                    edit_music_info(new_name, f'{i}_{target_name}')

                break
                

        print('lol') 

if __name__ == '__main__':
	main()