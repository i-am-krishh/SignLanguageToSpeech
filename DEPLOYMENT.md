# Deployment Guide for Sign Language to Speech Conversion

This guide will help you deploy the Sign Language to Speech Conversion project on Streamlit Community Cloud.

## Prerequisites

1. A GitHub account
2. Your project code pushed to a GitHub repository
3. A free Streamlit Community Cloud account

## Step-by-Step Deployment Guide

### 1. Prepare Your GitHub Repository

1. Create a new repository on GitHub
2. Initialize Git in your local project:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

### 2. Set Up Streamlit Community Cloud

1. Go to [Streamlit Community Cloud](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click on "New app"
4. Select your repository, branch (main), and file (app.py)
5. Click "Deploy"

### 3. Environment Configuration

The `requirements.txt` file in your repository will automatically be used to install dependencies. Make sure it includes all necessary packages and excludes conflicting ones:

```
streamlit>=1.24.0
numpy>=1.24.3
opencv-python-headless==4.7.0.72  # Use headless version for Streamlit Cloud
mediapipe>=0.10.0
tensorflow>=2.13.0
cvzone>=1.6.1
pyttsx3>=2.90
googletrans==3.1.0a0
pyenchant>=3.2.2
Pillow>=10.0.0

# Explicitly exclude other OpenCV versions to avoid conflicts
opencv-python
opencv-contrib-python
```

> **Important Notes**: 
> - We use `opencv-python-headless` instead of `opencv-python` because the headless version is specifically designed for server environments like Streamlit Cloud that don't require GUI components.
> - Make sure to exclude other OpenCV packages to prevent version conflicts.
> - The main application file must be named `app.py` (not `Application.py`) and be located in the repository root.

### 4. Advanced Settings (Optional)

In Streamlit Community Cloud dashboard:
1. Click on your app's menu (⋮)
2. Select "Settings"
3. Configure:
   - Python version
   - Memory limits
   - Secrets management (if needed)
   - Custom subdomains

### 5. Monitoring

- View app logs in the Streamlit Cloud dashboard
- Monitor app performance and usage
- Check deployment status and health

## Troubleshooting

1. If deployment fails:
   - Check logs in Streamlit Cloud dashboard
   - Verify all dependencies are in `requirements.txt`
   - Ensure `app.py` is in the repository root
   - If you encounter OpenCV import errors, make sure you're using `opencv-python-headless` instead of `opencv-python`

2. If app crashes:
   - Check memory usage
   - Verify all model files are included
   - Ensure paths are relative to project root

## Maintenance

1. Update your app:
   - Push changes to GitHub
   - Streamlit Cloud automatically redeploys

2. Best practices:
   - Keep dependencies updated
   - Monitor resource usage
   - Regularly backup data
   - Test locally before pushing changes

## Support

For issues:
1. Check [Streamlit documentation](https://docs.streamlit.io)
2. Visit [Streamlit Community Forum](https://discuss.streamlit.io)
3. Review [Streamlit Cloud FAQ](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app)