import os
import yt_dlp
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Directories
TEMPLATES_DIR = "templates"
STATIC_DIR = "static"

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Load templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-link")
async def generate_link(url: str = Form(...)):
    """Generate download links for the given URL (YouTube, Facebook, Instagram, Twitter)."""
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Add http/https prefix if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        # Detect platform from URL
        platform = "unknown"
        if "youtube.com" in url or "youtu.be" in url:
            platform = "youtube"
        elif "facebook.com" in url or "fb.com" in url or "fb.watch" in url:
            platform = "facebook"
        elif "instagram.com" in url:
            platform = "instagram"
        elif "twitter.com" in url or "x.com" in url:
            platform = "twitter"
            
        # Extract video information without downloading
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,  # Don't download, just get info
            "format": "best/bestvideo+bestaudio"
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Get video information
            title = info.get('title', 'Unknown Title')
            thumbnail = info.get('thumbnail', '')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            
            # Format duration as HH:MM:SS (if available)
            duration_formatted = "Unknown"
            if duration:
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)
                duration_formatted = f"{hours:02}:{minutes:02}:{seconds:02}" if hours else f"{minutes:02}:{seconds:02}"
            
            # Get available formats
            formats = []
            if 'formats' in info:
                for f in info['formats']:
                    # Skip formats without url
                    if not f.get('url'):
                        continue
                    
                    # Skip incompatible formats based on platform
                    if platform == "youtube" and f.get('acodec') == 'none':
                        continue
                    
                    # Create a readable format name
                    format_id = f.get('format_id', '')
                    ext = f.get('ext', '')
                    resolution = f.get('resolution', '')
                    if not resolution and 'height' in f and 'width' in f:
                        resolution = f"{f['width']}x{f['height']}"
                    
                    # Get file size (if available)
                    filesize = f.get('filesize', 0)
                    if not filesize:
                        filesize = f.get('filesize_approx', 0)
                    
                    # Format filesize as MB
                    if filesize:
                        filesize_mb = round(filesize / (1024 * 1024), 2)
                        filesize_str = f"{filesize_mb} MB"
                    else:
                        filesize_str = "Unknown"
                    
                    # Create format description
                    is_audio_only = "audio only" in f.get('format', '').lower()
                    
                    if is_audio_only:
                        format_name = f"Audio only ({ext})"
                    else:
                        format_name = f"{resolution} ({ext})" if resolution else f"{ext.upper()} file"
                    
                    formats.append({
                        "format_id": format_id,
                        "format_name": format_name,
                        "url": f.get('url', ''),
                        "ext": ext,
                        "resolution": resolution,
                        "filesize": filesize_str,
                        "is_audio_only": is_audio_only
                    })
            
            # Sort formats based on platform and type
            video_formats = [f for f in formats if not f['is_audio_only']]
            audio_formats = [f for f in formats if f['is_audio_only']]
            
            # Sort video formats by resolution (trying to get higher resolutions first)
            video_formats.sort(key=lambda x: x.get('format_id', '0'), reverse=True)
            
            # Sort audio formats (usually by quality)
            audio_formats.sort(key=lambda x: x.get('format_id', '0'), reverse=True)
            
            # Combine sorted formats
            sorted_formats = video_formats + audio_formats
            
            # Limit to a reasonable number of options
            sorted_formats = sorted_formats[:10] if len(sorted_formats) > 10 else sorted_formats
            
            return JSONResponse({
                "success": True,
                "title": title,
                "thumbnail": thumbnail,
                "duration": duration_formatted,
                "uploader": uploader,
                "platform": platform,
                "formats": sorted_formats
            })
    
    except Exception as e:
        error_message = str(e)
        return JSONResponse({
            "success": False,
            "error": error_message
        }, status_code=400)