import os

import click
import eyed3

# DEFAULT_PATH = "/Users/liqiangding/Music/2020/"

@click.group()
def run():
    pass

def add_cover_image_to_music(music_path, image_path, metatag):

	audiofile = eyed3.load(music_path)
	# import pdb;pdb.set_trace()

	# if (audiofile.tag == None):
	# audiofile.initTag()
	
	audiofile.tag.images.set(3, open(image_path,'rb').read(), 'image/jpeg')
	audiofile.tag.title = os.path.basename(music_path)[:-4]
	audiofile.tag.save()
	return


@run.command()
@click.option('--music_path', '-m', help='path to the music')
@click.option('--image_path', '-i', help='path to the image')
@click.option('--metatag', '-t', help='meta tag')
def main(music_path, image_path, metatag):
	music_name = music_path.split("/")[-1]
	music_name = music_path.split(".")[0]
	add_cover_image_to_music(music_path, image_path, music_name)



if __name__ == '__main__':
	main()