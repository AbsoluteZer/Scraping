# Adverse Event Scraper

A web-based application for screening entities against a database of adverse event keywords using DuckDuckGo search.

## Features

- **Web Interface**: User-friendly Flask web app
- **File Upload**: Upload Excel files (.xlsx)
- **Custom Filters**: Edit and manage search keywords
- **Concurrent Processing**: Process multiple entries in parallel
- **Real-time Progress**: Track processing status in real-time
- **Download Results**: Download processed results as Excel file

## Local Setup

### Prerequisites
- Python 3.11+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/scraping.git
cd scraping
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the app:
```bash
python app.py
```

5. Open browser to: `http://localhost:5000`

## Deployment to Render.com

### Prerequisites
- GitHub account
- Render.com account

### Steps

1. **Push to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/scraping.git
git push -u origin main
```

2. **Deploy on Render:**
   - Go to https://render.com/dashboard
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Click "Create Web Service"

3. **Monitor deployment:**
   - Watch logs in Render dashboard
   - Once deployed, visit your app URL

## Project Structure

```
.
├── app.py                 # Flask web application
├── main.py               # Command-line entry point
├── requirements.txt      # Python dependencies
├── render.yaml          # Render deployment config
├── .gitignore           # Git ignore rules
├── src/
│   ├── handle_excel.py   # Excel processing
│   ├── handle_scraping.py # DuckDuckGo search logic
│   └── __pycache__/
├── templates/
│   └── index.html       # Web UI
├── tests/
│   └── output/          # Output directory
└── uploads/             # Temporary uploads
```

## Configuration

### Filter Keywords
Edit keywords in the web UI or in `app.py` `DEFAULT_FILTER` list.

### Worker Threads
Adjust `max_workers` parameter (default: 20) in web UI based on your machine:
- Lower values (5-10): Less resource intensive
- Higher values (20-50): Faster processing

## Limitations

### Render Free Tier
- No persistent storage (files deleted after app stops)
- 15 minute max request time
- App spins down after 15 min inactivity
- 512MB RAM limit

### Production Recommendations
- Upgrade to Render Standard plan
- Add external storage (AWS S3)
- Implement caching layer (Redis)
- Use background job queue (Celery)

## Troubleshooting

### "No module named 'src'"
Make sure you're running from the project root directory.

### Upload fails on Render
- Check file size (keep under 50MB)
- Ensure correct .xlsx format

### Processing timeout
- Use fewer workers
- Upgrade Render plan
- Process data in smaller batches

## Support

For issues or questions, please open an issue on GitHub.

## License

MIT License
