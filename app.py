import os
import tempfile
import base64
from io import BytesIO
from flask import Flask, render_template, request, jsonify, send_file
import eyed3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['JSON_AS_ASCII'] = False  # Allow non-ASCII characters in JSON responses

# Set eyed3 encoding
eyed3.log.setLevel("ERROR")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan_metadata():
    """Scan MP3 file and return metadata + cover"""
    try:
        if 'mp3_file' not in request.files:
            return jsonify({'error': 'No MP3 file provided'}), 400

        mp3_file = request.files['mp3_file']

        if mp3_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save temporarily
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(mp3_file.filename))
        mp3_file.save(temp_path)

        # Load with eyed3
        audiofile = eyed3.load(temp_path)

        metadata = {}
        cover_url = None

        if audiofile and audiofile.tag:
            # Use filename (without .mp3) as default title if no title is set
            filename_without_ext = mp3_file.filename.rsplit('.', 1)[0] if '.' in mp3_file.filename else mp3_file.filename
            default_title = audiofile.tag.title or filename_without_ext

            # Extract metadata
            metadata = {
                'title': default_title,
                'artist': audiofile.tag.artist or '',
                'album': audiofile.tag.album or '',
                'year': str(audiofile.tag.recording_date.year) if audiofile.tag.recording_date else '',
                'genre': audiofile.tag.genre.name if audiofile.tag.genre else '',
                'track': str(audiofile.tag.track_num[0]) if audiofile.tag.track_num and audiofile.tag.track_num[0] else ''
            }

            # Extract cover image if exists
            if audiofile.tag.images:
                for image in audiofile.tag.images:
                    img_data = image.image_data
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    mime_type = image.mime_type or 'image/jpeg'
                    cover_url = f'data:{mime_type};base64,{img_base64}'
                    break  # Use first image found

        # Clean up temp file
        os.remove(temp_path)

        return jsonify({
            'metadata': metadata,
            'cover_url': cover_url
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save', methods=['POST'])
def save_changes():
    """Save metadata changes and new cover to MP3 file"""
    temp_input = None
    temp_output = None

    try:
        if 'mp3_file' not in request.files:
            return jsonify({'error': 'No MP3 file provided'}), 400

        mp3_file = request.files['mp3_file']
        metadata_json = request.form.get('metadata', '{}')

        import json
        metadata = json.loads(metadata_json)

        # Generate unique temp filename to avoid conflicts
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        temp_input = os.path.join(app.config['UPLOAD_FOLDER'], f'input_{unique_id}_' + secure_filename(mp3_file.filename))
        mp3_file.save(temp_input)

        # Load with eyed3
        audiofile = eyed3.load(temp_input)

        if not audiofile:
            if temp_input and os.path.exists(temp_input):
                os.remove(temp_input)
            return jsonify({'error': 'Invalid MP3 file'}), 400

        # Initialize tag if doesn't exist
        if audiofile.tag is None:
            audiofile.initTag()

        # Update metadata fields (only if provided and not empty)
        # Ensure all strings are properly encoded as Unicode
        changes_made = []

        if metadata.get('title'):
            # Ensure Unicode string
            title = str(metadata['title'])
            audiofile.tag.title = title
            changes_made.append(f"Title: {title}")

        if metadata.get('artist'):
            artist = str(metadata['artist'])
            audiofile.tag.artist = artist
            changes_made.append(f"Artist: {artist}")

        if metadata.get('album'):
            album = str(metadata['album'])
            audiofile.tag.album = album
            changes_made.append(f"Album: {album}")

        if metadata.get('year'):
            try:
                year = int(metadata['year'])
                audiofile.tag.recording_date = eyed3.core.Date(year)
                changes_made.append(f"Year: {year}")
            except (ValueError, TypeError):
                pass

        if metadata.get('genre'):
            genre = str(metadata['genre'])
            audiofile.tag.genre = genre
            changes_made.append(f"Genre: {genre}")

        if metadata.get('track'):
            try:
                track_num = int(metadata['track'])
                audiofile.tag.track_num = (track_num, None)
                changes_made.append(f"Track: {track_num}")
            except (ValueError, TypeError):
                pass

        print(f"Changes made to {mp3_file.filename}: {changes_made}")

        # Handle cover image if provided
        if 'cover_image' in request.files:
            cover_file = request.files['cover_image']
            print(f"Received cover_image file: {cover_file.filename}")
            if cover_file and cover_file.filename != '':
                # Read image data
                img_data = cover_file.read()
                print(f"Read {len(img_data)} bytes from cover image")

                # Remove ALL existing images first
                if audiofile.tag.images:
                    # Clear all images
                    for img in audiofile.tag.images:
                        print(f"Removing existing image: {img.description}")
                    audiofile.tag.images.clear()
                    print("Cleared all existing images")

                # Determine mime type
                mime_type = cover_file.content_type
                if not mime_type:
                    if cover_file.filename.lower().endswith('.png'):
                        mime_type = 'image/png'
                    elif cover_file.filename.lower().endswith('.jpg') or cover_file.filename.lower().endswith('.jpeg'):
                        mime_type = 'image/jpeg'
                    else:
                        mime_type = 'image/jpeg'  # default fallback
                print(f"Using mime type: {mime_type}")

                # Add new cover (type 3 = front cover)
                audiofile.tag.images.set(3, img_data, mime_type, description=u'Front cover')
                changes_made.append(f"Cover: {cover_file.filename} ({len(img_data)} bytes)")
                print(f"Successfully added cover image: {cover_file.filename}, size: {len(img_data)} bytes")
            else:
                print("Cover file is empty or has no filename")
        else:
            print("No cover_image in request.files")

        # Save changes
        audiofile.tag.save(version=eyed3.id3.ID3_V2_4, encoding='utf-8')
        print(f"Saved tags to file")

        # Create output filename with unique prefix for temp storage
        temp_output = os.path.join(app.config['UPLOAD_FOLDER'], f'output_{unique_id}_' + secure_filename(mp3_file.filename))

        # Move modified file to output path
        os.rename(temp_input, temp_output)

        # Verify the image was saved
        verify_file = eyed3.load(temp_output)
        if verify_file and verify_file.tag and verify_file.tag.images:
            print(f"Verification: File has {len(verify_file.tag.images)} image(s)")
            for img in verify_file.tag.images:
                print(f"  - Image type: {img.picture_type}, size: {len(img.image_data)} bytes")
        else:
            print("Verification: No images found in saved file!")

        # Return JSON response with download URL instead of file directly
        # Extract just the filename without any folder path
        original_filename = os.path.basename(mp3_file.filename)
        return jsonify({
            'success': True,
            'download_url': f'/download/{os.path.basename(temp_output)}?original={original_filename}',
            'filename': original_filename
        })

    except Exception as e:
        # Clean up on error
        if 'temp_input' in locals() and os.path.exists(temp_input):
            os.remove(temp_input)
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download the processed MP3 file"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            # Get the original filename from query parameter
            original_filename = request.args.get('original', filename)

            return send_file(
                filepath,
                as_attachment=True,
                download_name=original_filename,
                mimetype='audio/mpeg'
            )
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.after_request
def cleanup_temp_files(response):
    """Clean up temporary files after sending response"""
    # Clean up any output files older than 1 minute
    import time
    temp_dir = app.config['UPLOAD_FOLDER']
    now = time.time()

    for filename in os.listdir(temp_dir):
        if filename.startswith('output_'):
            filepath = os.path.join(temp_dir, filename)
            if os.path.getmtime(filepath) < now - 60:  # 1 minute old
                try:
                    os.remove(filepath)
                except:
                    pass

    return response

if __name__ == '__main__':
    app.run(debug=True, port=5001)