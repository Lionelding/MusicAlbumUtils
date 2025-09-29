// Global variables to store file data
let currentMP3File = null;
let currentCoverFile = null;
let originalMetadata = {};
let originalCoverUrl = null;

// Album mode variables
let albumMode = false;
let albumFiles = [];
let albumCoverFile = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    setupMP3DropZone();
    setupCoverDropZone();
    setupButtons();
    setupModeToggle();
    setupAlbumMode();
});

// Setup MP3 drag and drop
function setupMP3DropZone() {
    const dropzone = document.getElementById('mp3-dropzone');
    const input = document.getElementById('mp3-input');

    // Click to browse
    dropzone.addEventListener('click', () => input.click());

    // File input change
    input.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleMP3File(e.target.files[0]);
        }
        // Clear the input so the same file can be selected again
        e.target.value = '';
    });

    // Drag and drop events
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type === 'audio/mpeg') {
            handleMP3File(files[0]);
        } else {
            showStatus('Please drop a valid MP3 file', 'error');
        }
    });
}

// Setup album cover drag and drop
function setupCoverDropZone() {
    const dropzone = document.getElementById('cover-dropzone');
    const input = document.getElementById('cover-input');

    // Click to browse
    dropzone.addEventListener('click', () => input.click());

    // File input change
    input.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleCoverFile(e.target.files[0]);
        }
        // Clear the input so the same file can be selected again
        e.target.value = '';
    });

    // Drag and drop events
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            handleCoverFile(files[0]);
        } else {
            showStatus('Please drop a valid image file', 'error');
        }
    });
}

// Handle MP3 file selection
function handleMP3File(file) {
    currentMP3File = file;

    // Display file name
    document.getElementById('current-file').style.display = 'block';
    document.querySelector('.file-name').textContent = file.name;

    // Reset metadata and cover sections
    resetForm();

    showStatus('MP3 file loaded. Click "Scan Metadata" to continue.', 'success');
}

// Handle cover image file selection
function handleCoverFile(file) {
    if (!file.type.startsWith('image/')) {
        showStatus('Please select a valid image file', 'error');
        return;
    }

    currentCoverFile = file;

    // Use FileReader to preview the image
    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = document.getElementById('cover-preview');
        preview.src = e.target.result;
        preview.style.display = 'block';
        document.querySelector('.cover-placeholder').style.display = 'none';

        // Update status text
        document.getElementById('cover-status-text').textContent = `✅ New cover selected: ${file.name}`;
        document.getElementById('cover-status-text').style.color = '#48bb78';

        showStatus('New cover image selected', 'success');
    };
    reader.readAsDataURL(file);
}

// Setup button event listeners
function setupButtons() {
    // Scan button
    document.getElementById('scan-btn').addEventListener('click', scanMetadata);

    // Save button
    document.getElementById('save-btn').addEventListener('click', saveChanges);

    // Reset button
    document.getElementById('reset-btn').addEventListener('click', resetForm);
}

// Scan metadata from MP3 file
async function scanMetadata() {
    if (!currentMP3File) {
        showStatus('No MP3 file selected', 'error');
        return;
    }

    showStatus('Scanning metadata...', 'info');

    const formData = new FormData();
    formData.append('mp3_file', currentMP3File);


    try {
        const response = await fetch('/scan', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to scan metadata');
        }

        const data = await response.json();

        // Store original metadata
        originalMetadata = data.metadata || {};
        originalCoverUrl = data.cover_url;

        // Display metadata
        displayMetadata(data.metadata);

        // Display cover if exists
        if (data.cover_url) {
            displayCover(data.cover_url);
        }

        // Show sections
        document.getElementById('metadata-section').style.display = 'block';
        document.getElementById('cover-section').style.display = 'block';
        document.getElementById('action-buttons').style.display = 'block';

        showStatus('Metadata scanned successfully', 'success');
    } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
        console.error('Scan error:', error);
    }
}

// Display metadata in form fields
function displayMetadata(metadata) {
    document.getElementById('title').value = metadata.title || '';
    document.getElementById('artist').value = metadata.artist || '';
    document.getElementById('album').value = metadata.album || '';
    document.getElementById('year').value = metadata.year || '';
    document.getElementById('genre').value = metadata.genre || '';
    document.getElementById('track').value = metadata.track || '';
}

// Display album cover
function displayCover(coverUrl) {
    if (coverUrl) {
        const preview = document.getElementById('cover-preview');
        preview.src = coverUrl;
        preview.style.display = 'block';
        document.querySelector('.cover-placeholder').style.display = 'none';

        // Update status to show existing cover
        document.getElementById('cover-status-text').textContent = 'Current cover from file (drag new image to replace)';
        document.getElementById('cover-status-text').style.color = '#666';
    } else {
        // No cover in file
        document.getElementById('cover-status-text').textContent = 'No cover image in file';
        document.getElementById('cover-status-text').style.color = '#999';
    }
}

// Save changes to MP3 file
async function saveChanges() {
    if (!currentMP3File) {
        showStatus('No MP3 file to save', 'error');
        return;
    }

    showStatus('Saving changes...', 'info');

    const formData = new FormData();
    formData.append('mp3_file', currentMP3File);

    // Get current metadata values
    const metadata = {
        title: document.getElementById('title').value,
        artist: document.getElementById('artist').value,
        album: document.getElementById('album').value,
        year: document.getElementById('year').value,
        genre: document.getElementById('genre').value,
        track: document.getElementById('track').value
    };

    // Include all non-empty fields (not just changed ones)
    const changedMetadata = {};
    for (const [key, value] of Object.entries(metadata)) {
        if (value !== '') {
            changedMetadata[key] = value;
        }
    }

    formData.append('metadata', JSON.stringify(changedMetadata));

    // Add new cover if selected
    if (currentCoverFile) {
        console.log('Adding cover image to form:', currentCoverFile.name, currentCoverFile.size, 'bytes');
        formData.append('cover_image', currentCoverFile);
    } else {
        console.log('No new cover image selected');
    }

    try {
        const response = await fetch('/save', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to save changes');
        }

        if (data.success && data.download_url) {
            // Download the modified file
            const downloadUrl = data.download_url;
            const a = document.createElement('a');
            a.href = downloadUrl;
            // Force the browser to use original filename
            a.download = currentMP3File.name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            showStatus(`Changes saved! Downloaded as: ${currentMP3File.name}`, 'success');
            console.log(`Downloaded: ${currentMP3File.name} from URL: ${data.download_url}`);

            // Don't reset immediately to let user see the message
            setTimeout(() => {
                if (confirm('File downloaded successfully! Do you want to edit another file?')) {
                    resetForm();
                }
            }, 1500);
        } else {
            throw new Error('Invalid response from server');
        }

    } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
        console.error('Save error:', error);
    }
}

// Reset the form
function resetForm() {
    // Hide sections
    document.getElementById('metadata-section').style.display = 'none';
    document.getElementById('cover-section').style.display = 'none';
    document.getElementById('action-buttons').style.display = 'none';

    // Clear metadata fields
    document.querySelectorAll('.metadata-field').forEach(field => {
        field.value = '';
    });

    // Clear cover preview
    const preview = document.getElementById('cover-preview');
    preview.src = '';
    preview.style.display = 'none';
    document.querySelector('.cover-placeholder').style.display = 'block';

    // Clear cover status
    document.getElementById('cover-status-text').textContent = '';

    // Reset file variables
    currentCoverFile = null;
    originalMetadata = {};
    originalCoverUrl = null;

    showStatus('Form reset', 'info');
}

// Show status messages
function showStatus(message, type = 'info') {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
    statusDiv.style.display = 'block';

    // Auto-hide after 5 seconds for non-error messages
    if (type !== 'error') {
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
}

// Setup mode toggle functionality
function setupModeToggle() {
    const singleModeBtn = document.getElementById('single-mode-btn');
    const albumModeBtn = document.getElementById('album-mode-btn');
    const singleSection = document.getElementById('single-mode-section');
    const albumSection = document.getElementById('album-mode-section');

    singleModeBtn.addEventListener('click', () => {
        albumMode = false;
        singleModeBtn.classList.add('active');
        albumModeBtn.classList.remove('active');
        singleSection.style.display = 'block';
        albumSection.style.display = 'none';
    });

    albumModeBtn.addEventListener('click', () => {
        albumMode = true;
        albumModeBtn.classList.add('active');
        singleModeBtn.classList.remove('active');
        singleSection.style.display = 'none';
        albumSection.style.display = 'block';
    });
}

// Setup Album Mode functionality
function setupAlbumMode() {
    const folderDropzone = document.getElementById('folder-dropzone');
    const folderInput = document.getElementById('folder-input');
    const albumCoverDropzone = document.getElementById('album-cover-dropzone');
    const albumCoverInput = document.getElementById('album-cover-input');

    // Folder selection
    folderDropzone.addEventListener('click', () => folderInput.click());

    folderInput.addEventListener('change', (e) => {
        handleFolderSelection(e.target.files);
        e.target.value = '';
    });

    // Album cover selection
    albumCoverDropzone.addEventListener('click', () => albumCoverInput.click());

    albumCoverInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleAlbumCoverFile(e.target.files[0]);
        }
        e.target.value = '';
    });

    // Album cover drag and drop
    albumCoverDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        albumCoverDropzone.classList.add('dragover');
    });

    albumCoverDropzone.addEventListener('dragleave', () => {
        albumCoverDropzone.classList.remove('dragover');
    });

    albumCoverDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        albumCoverDropzone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            handleAlbumCoverFile(files[0]);
        }
    });

    // Batch buttons
    document.getElementById('batch-save-btn').addEventListener('click', batchSaveAlbum);
    document.getElementById('batch-reset-btn').addEventListener('click', resetAlbumMode);
}

// Handle folder selection
function handleFolderSelection(files) {
    // Filter MP3 files and sort by name
    albumFiles = Array.from(files)
        .filter(file => file.type === 'audio/mpeg' || file.name.toLowerCase().endsWith('.mp3'))
        .sort((a, b) => a.name.localeCompare(b.name));

    if (albumFiles.length === 0) {
        showStatus('No MP3 files found in the selected folder', 'error');
        return;
    }

    // Extract folder name from path
    const folderName = albumFiles[0].webkitRelativePath.split('/')[0];
    document.getElementById('album-name').value = folderName;

    // Display songs list
    displaySongsList(albumFiles);

    // Show preview and metadata sections
    document.getElementById('songs-preview').style.display = 'block';
    document.getElementById('album-metadata').style.display = 'block';

    showStatus(`Found ${albumFiles.length} MP3 files in folder: ${folderName}`, 'success');
}

// Display songs list with editable titles
function displaySongsList(files) {
    const songsList = document.getElementById('songs-list');
    songsList.innerHTML = '';

    files.forEach((file, index) => {
        // Use full filename without .mp3 extension as title
        const filename = file.name.replace('.mp3', '').replace('.MP3', '');

        // Extract track number from filename (e.g., "01_Song" -> "01")
        const trackMatch = filename.match(/^(\d+)[_\s\-]/);
        const trackNumber = trackMatch ? trackMatch[1] : String(index + 1);

        const songItem = document.createElement('div');
        songItem.className = 'song-item';
        songItem.innerHTML = `
            <span class="song-filename" title="${file.name}">${file.name}</span>
            <span class="song-track">${trackNumber}</span>
            <div class="song-title">
                <input type="text" class="song-title-input" value="${filename}" data-index="${index}" data-track="${trackNumber}">
            </div>
        `;
        songsList.appendChild(songItem);
    });
}

// Handle album cover file
function handleAlbumCoverFile(file) {
    if (!file.type.startsWith('image/')) {
        showStatus('Please select a valid image file', 'error');
        return;
    }

    albumCoverFile = file;

    // Preview the image
    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = document.getElementById('album-cover-preview');
        preview.src = e.target.result;
        preview.style.display = 'block';
        document.querySelector('.album-cover-placeholder').style.display = 'none';
        showStatus('Album cover selected', 'success');
    };
    reader.readAsDataURL(file);
}

// Batch save all songs in album
async function batchSaveAlbum() {
    if (albumFiles.length === 0) {
        showStatus('No files to save', 'error');
        return;
    }

    const albumMetadata = {
        artist: document.getElementById('album-artist').value,
        album: document.getElementById('album-name').value,
        year: document.getElementById('album-year').value,
        genre: document.getElementById('album-genre').value
    };

    // Get all song titles and track numbers
    const songData = [];
    document.querySelectorAll('.song-title-input').forEach((input) => {
        songData.push({
            title: input.value,
            track: input.getAttribute('data-track')
        });
    });

    showStatus('Processing album files...', 'info');

    // Process each file
    for (let i = 0; i < albumFiles.length; i++) {
        const file = albumFiles[i];

        const formData = new FormData();
        formData.append('mp3_file', file);

        // Combine metadata
        const metadata = {
            ...albumMetadata,
            title: songData[i].title,
            track: songData[i].track
        };

        formData.append('metadata', JSON.stringify(metadata));

        // Add album cover if selected
        if (albumCoverFile) {
            formData.append('cover_image', albumCoverFile);
        }

        try {
            const response = await fetch('/save', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success && data.download_url) {
                // Download the file with original name
                const a = document.createElement('a');
                a.href = data.download_url;
                a.download = file.name;  // Force the original filename
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);

                console.log(`Downloaded: ${file.name} from URL: ${data.download_url}`);
            }

            showStatus(`Processed ${i + 1}/${albumFiles.length}: ${file.name}`, 'success');

            // Small delay between files to avoid conflicts
            await new Promise(resolve => setTimeout(resolve, 100));
        } catch (error) {
            showStatus(`Error processing ${file.name}: ${error.message}`, 'error');
        }
    }

    showStatus(`Album processing complete! All ${albumFiles.length} files processed.`, 'success');
}

// Reset album mode
function resetAlbumMode() {
    albumFiles = [];
    albumCoverFile = null;

    document.getElementById('songs-preview').style.display = 'none';
    document.getElementById('album-metadata').style.display = 'none';
    document.getElementById('songs-list').innerHTML = '';

    // Clear metadata fields
    document.getElementById('album-artist').value = '';
    document.getElementById('album-name').value = '';
    document.getElementById('album-year').value = '';
    document.getElementById('album-genre').value = '';

    // Clear album cover
    document.getElementById('album-cover-preview').src = '';
    document.getElementById('album-cover-preview').style.display = 'none';
    document.querySelector('.album-cover-placeholder').style.display = 'block';

    showStatus('Album mode reset', 'info');
}