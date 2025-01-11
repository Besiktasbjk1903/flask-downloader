from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import yt_dlp as youtube_dl
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Function to download a TikTok video using yt-dlp
def download_video_tiktok(url, format_choice):
    try:
        ydl_opts = {
            'format': 'bestaudio/best' if format_choice == 'mp3' else 'bestvideo+bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'extractaudio': True if format_choice == 'mp3' else False,
            'outtmpl': '-',
        }

        # Using yt-dlp to extract information about the TikTok video
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_data = ydl.urlopen(info_dict['url']).read()  # Stream the video data

            # Create a BytesIO buffer and write the video data into it
            video_buffer = BytesIO(video_data)
            filename = info_dict.get('title', 'download') + (".mp3" if format_choice == "mp3" else ".mp4")
            return video_buffer, filename

    except youtube_dl.DownloadError as e:
        flash(f"An error occurred while downloading the TikTok video: {e}", "error")
        return None, None
    except Exception as e:
        flash(f"An unexpected error occurred: {e}", "error")
        return None, None

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        url = request.form["url"]
        format_choice = request.form["format"]
        platform_choice = request.form["platform"]

        if not url:
            flash("Please enter a video URL.", "error")
            return redirect(url_for('home'))

        video_data = None
        filename = None

        if platform_choice == "TikTok":
            video_data, filename = download_video_tiktok(url, format_choice)

        if video_data:
            return send_file(video_data,
                             as_attachment=True,
                             download_name=filename,
                             mimetype='application/octet-stream')

        return redirect(url_for('home'))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
