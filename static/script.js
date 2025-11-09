document.addEventListener('DOMContentLoaded', function() {
    const urlForm = document.getElementById('url-form');
    const videoUrlInput = document.getElementById('video-url');
    const generateBtn = document.getElementById('generate-btn');
    const loadingElement = document.getElementById('loading');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    const resultContainer = document.getElementById('result-container');
    const videoThumbnail = document.getElementById('video-thumbnail');
    const platformBadge = document.getElementById('platform-badge');
    const videoTitle = document.getElementById('video-title');
    const videoUploader = document.getElementById('video-uploader');
    const videoDuration = document.getElementById('video-duration');
    const videoUploaderContainer = document.getElementById('video-uploader-container');
    const videoDurationContainer = document.getElementById('video-duration-container');
    const formatList = document.getElementById('format-list');
    const newSearchBtn = document.getElementById('new-search-btn');
    
    // REMOVED: Hamburger menu functionality - this is now handled in menu.js
    
    // URL validation for supported platforms
    function isValidUrl(url) {
        const platformRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be|facebook\.com|fb\.com|fb\.watch|instagram\.com|twitter\.com|x\.com)\/.+/;
        return platformRegex.test(url);
    }

    // Reset UI state
    function resetUI() {
        resultContainer.style.display = 'none';
        errorContainer.style.display = 'none';
        loadingElement.style.display = 'none';
        videoUrlInput.value = '';
        formatList.innerHTML = '';
    }

    // Handle form submission
    if (urlForm) {
        urlForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = videoUrlInput.value.trim();
            
            if (!url) {
                errorContainer.style.display = 'block';
                errorMessage.textContent = 'Please enter a video URL';
                return;
            }
            
            if (!isValidUrl(url)) {
                errorContainer.style.display = 'block';
                errorMessage.textContent = 'Please enter a valid URL from YouTube, Facebook, Instagram, or Twitter';
                return;
            }
            
            // Hide previous results and show loading
            resultContainer.style.display = 'none';
            errorContainer.style.display = 'none';
            loadingElement.style.display = 'flex';
            
            // Disable the button during processing
            generateBtn.disabled = true;
            generateBtn.textContent = 'Processing...';
            
            // Generate download links
            generateLinks(url);
        });
    }

    // Generate download links
    function generateLinks(url) {
        const formData = new FormData();
        formData.append('url', url);
        
        fetch('/generate-link', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            loadingElement.style.display = 'none';
            
            // Reset button
            generateBtn.disabled = false;
            generateBtn.textContent = 'Download';
            
            if (data.success) {
                // Populate video information
                videoThumbnail.src = data.thumbnail || '/static/no-thumbnail.jpg';
                videoTitle.textContent = data.title;
                
                // Set platform badge
                if (data.platform) {
                    platformBadge.className = 'platform-badge ' + data.platform;
                    // Fix for Twitter/X display
                    const platformName = data.platform === 'twitter' ? 'Twitter/X' : capitalizeFirstLetter(data.platform);
                    platformBadge.textContent = platformName;
                    platformBadge.style.display = 'block';
                } else {
                    platformBadge.style.display = 'none';
                }
                
                // Handle uploader info
                if (data.uploader && data.uploader !== 'Unknown') {
                    videoUploader.textContent = data.uploader;
                    videoUploaderContainer.style.display = 'block';
                } else {
                    videoUploaderContainer.style.display = 'none';
                }
                
                // Handle duration info
                if (data.duration && data.duration !== 'Unknown') {
                    videoDuration.textContent = data.duration;
                    videoDurationContainer.style.display = 'block';
                } else {
                    videoDurationContainer.style.display = 'none';
                }
                
                // Create format list
                formatList.innerHTML = '';
                
                if (data.formats && data.formats.length > 0) {
                    // Create a table for formats
                    const table = document.createElement('table');
                    table.className = 'formats-table';
                    
                    // Create table header
                    const thead = document.createElement('thead');
                    thead.innerHTML = `
                        <tr>
                            <th>Quality</th>
                            <th>Format</th>
                            <th>Size</th>
                            <th>Download</th>
                        </tr>
                    `;
                    table.appendChild(thead);
                    
                    // Create table body
                    const tbody = document.createElement('tbody');
                    
                    data.formats.forEach(format => {
                        const tr = document.createElement('tr');
                        
                        // Quality/Resolution column
                        const tdQuality = document.createElement('td');
                        tdQuality.textContent = format.resolution || 'Audio';
                        tr.appendChild(tdQuality);
                        
                        // Format column
                        const tdFormat = document.createElement('td');
                        tdFormat.textContent = format.ext.toUpperCase();
                        tr.appendChild(tdFormat);
                        
                        // Size column
                        const tdSize = document.createElement('td');
                        tdSize.textContent = format.filesize;
                        tr.appendChild(tdSize);
                        
                        // Download button column
                        const tdDownload = document.createElement('td');
                        const downloadBtn = document.createElement('a');
                        downloadBtn.href = format.url;
                        downloadBtn.className = 'download-btn';
                        downloadBtn.setAttribute('download', '');
                        downloadBtn.target = '_blank';
                        downloadBtn.textContent = 'Download';
                        
                        // Add title to make filename nicer
                        let suggestedFilename = data.title.replace(/[^\w\s]/gi, '');
                        if (format.is_audio_only) {
                            suggestedFilename += ` (Audio).${format.ext}`;
                        } else {
                            suggestedFilename += ` (${format.resolution || 'Video'}).${format.ext}`;
                        }
                        
                        // Add platform prefix
                        if (data.platform) {
                            suggestedFilename = `${capitalizeFirstLetter(data.platform)}_${suggestedFilename}`;
                        }
                        
                        downloadBtn.setAttribute('download', suggestedFilename);
                        
                        tdDownload.appendChild(downloadBtn);
                        tr.appendChild(tdDownload);
                        
                        tbody.appendChild(tr);
                    });
                    
                    table.appendChild(tbody);
                    formatList.appendChild(table);
                } else {
                    const noFormats = document.createElement('p');
                    noFormats.textContent = 'No download links available for this media.';
                    formatList.appendChild(noFormats);
                }
                
                // Show results
                resultContainer.style.display = 'block';
                
                // Scroll to results
                resultContainer.scrollIntoView({ behavior: 'smooth' });
            } else {
                // Show error
                errorContainer.style.display = 'block';
                errorMessage.textContent = data.error || 'Failed to generate download links.';
            }
        })
        .catch(error => {
            // Hide loading indicator
            loadingElement.style.display = 'none';
            
            // Reset button
            generateBtn.disabled = false;
            generateBtn.textContent = 'Download';
            
            // Show error
            errorContainer.style.display = 'block';
            errorMessage.textContent = 'An error occurred. Please try again.';
            console.error('Error:', error);
        });
    }
    
    // Helper function to capitalize first letter
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    
    // New search button
    if (newSearchBtn) {
        newSearchBtn.addEventListener('click', function() {
            resetUI();
            videoUrlInput.focus();
        });
    }
    
    // Handle errors on thumbnail load
    if (videoThumbnail) {
        videoThumbnail.addEventListener('error', function() {
            this.src = '/static/no-thumbnail.jpg';
        });
    }
    
    // Add example click handlers for the platform examples
    const platformExamples = document.querySelectorAll('.feature-item');
    platformExamples.forEach(item => {
        item.addEventListener('click', function() {
            const platformType = this.querySelector('.feature-icon').className.split(' ')[1];
            let exampleUrl = '';
            
            switch(platformType) {
                case 'youtube-icon':
                    exampleUrl = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';
                    break;
                case 'youtube-mp4':
                    exampleUrl = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';
                    break;
                case 'youtube-shorts':
                    exampleUrl = 'https://www.youtube.com/shorts/dQw4w9WgXcQ';
                    break;
                case 'youtube-mp3':
                    exampleUrl = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';
                    break;
                // Can add more examples for other platforms here
            }
            
            if (exampleUrl) {
                videoUrlInput.value = exampleUrl;
                videoUrlInput.focus();
            }
        });
    });
});
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/service-worker.js");
  });
}
