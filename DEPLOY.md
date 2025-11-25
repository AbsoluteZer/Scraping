# Deployment Instructions for Render.com

## Quick Start

### 1. Prepare Your Repository

Ensure these files are in your repo:
- `app.py` - Flask application
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration
- `src/` - Source code
- `templates/` - HTML templates
- `.gitignore` - Ignore unnecessary files

### 2. Push to GitHub

```bash
cd C:\Users\User\Documents\Kerja\Scraping
git init
git add .
git commit -m "Add web app for Render deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/Scraping.git
git push -u origin main
```

### 3. Deploy on Render

1. Go to https://render.com
2. Sign in with GitHub account
3. Click "New +" button
4. Select "Web Service"
5. Connect your GitHub repository
6. Render will auto-detect `render.yaml`
7. Click "Create Web Service"
8. Wait for deployment (typically 2-5 minutes)
9. Visit your app URL (format: `https://adverse-event-scraper.onrender.com`)

## Configuration Files

### `requirements.txt`
Lists all Python package dependencies. Automatically installed during deployment.

### `render.yaml`
Defines deployment configuration:
- **Build command**: Installs dependencies
- **Start command**: Uses gunicorn to run Flask app
- **Environment**: Python 3.11
- **Plan**: Free tier

### `.gitignore`
Prevents large/sensitive files from being pushed to GitHub.

## File Upload & Download

- Files uploaded by users are stored in `/tmp` (temporary storage)
- Files are automatically deleted when the app restarts
- For persistent storage, upgrade to Render Standard plan and integrate AWS S3

## Important Notes

### Free Tier Limitations
- Apps spin down after 15 min of inactivity (slow first request)
- Max 15 minute request timeout
- 512MB RAM limit
- No persistent storage

### For Large Datasets (15,000+ rows)
- Use fewer concurrent workers (10-15 instead of 20)
- Process data in smaller batches
- Consider Render Standard plan

### Production Setup
For production use:
1. Upgrade to Render Standard plan ($7/month)
2. Add PostgreSQL for persistent storage
3. Integrate AWS S3 for file uploads/downloads
4. Add Celery for background job processing
5. Configure Redis for caching

## Monitoring

- View logs in Render dashboard
- Monitor resource usage (CPU, RAM)
- Set up alerts for deployment failures

## Troubleshooting

### Deployment Failed
- Check `render.yaml` syntax
- Verify `requirements.txt` contains all dependencies
- Check build logs in Render dashboard

### App crashes after upload
- File too large (>50MB)
- Insufficient RAM on free tier
- Upgrade to Standard plan or reduce worker threads

### "No module named 'src'"
- Ensure repo structure is correct
- Verify `__init__.py` exists in `src/` folder

## Support

- Render documentation: https://render.com/docs
- GitHub: https://github.com/AbsoluteZer/Learn
