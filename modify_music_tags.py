import os
import click
import eyed3


@click.group()
def run():
    pass

def add_cover_image_to_music(music_path, image_path, metatag):

	audiofile = eyed3.load(music_path)
	if (audiofile.tag == None):
	    audiofile.initTag()
    
	audiofile.tag.images.set(3, open(image_path,'rb').read(), 'image/jpeg')

	audiofile.tag.album = metatag
	audiofile.tag.album_artist = metatag
	audiofile.tag.artist = metatag
	audiofile.tag.composer = metatag
	audiofile.tag.publisher = metatag
	audiofile.tag.save()
	return


@run.command()
@click.option('--music_path', '-m', help='path to the music')
@click.option('--image_path', '-i', help='path to the image')
@click.option('--metatag', '-t', help='meta tag')
def main(music_path, image_path, metatag):
	add_cover_image_to_music(music_path, image_path, metatag)



if __name__ == '__main__':
	main()