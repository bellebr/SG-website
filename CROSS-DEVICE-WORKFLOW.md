# Cross-Device Development Workflow

This document explains how to work on the SOFTGRAM website seamlessly between your iMac and MacBook.

## Current Setup Status

✅ **MacBook** (Currently configured)
- Repository: `/Users/jiwonkim/Desktop/UI:UX/유저그래피/Projects/SG`
- Git connected to: `https://github.com/bellebr/SG-website`
- Netlify: Auto-deploy enabled

⚠️ **iMac** (Needs setup - follow instructions below)

## Setting Up Your iMac

When you get back to your iMac, follow these steps:

### 1. Clone the Repository
```bash
# Navigate to your preferred development directory
cd ~/Desktop/UI:UX/유저그래피/Projects  # or wherever you want the project

# Clone the repository
git clone https://github.com/bellebr/SG-website.git

# Enter the project directory
cd SG-website
```

### 2. Configure Git for Large Files
```bash
# Set up Git for handling image files efficiently
git config http.postBuffer 524288000
```

### 3. Set Up GitHub Authentication
You'll need to set up authentication on your iMac. Choose one of these methods:

**Option A: Personal Access Token**
```bash
# Set up the remote with your token (replace YOUR_TOKEN with actual token)
git remote set-url origin https://YOUR_TOKEN@github.com/bellebr/SG-website.git
```

**Option B: GitHub CLI (Recommended)**
```bash
# Install GitHub CLI (if not already installed)
brew install gh

# Authenticate with GitHub
gh auth login

# The remote will work automatically after authentication
```

### 4. Test the Setup
```bash
# Make a small test change
echo "<!-- iMac setup complete -->" >> README.md

# Commit and push
git add README.md
git commit -m "Test iMac setup"
git push origin main

# Check if it auto-deploys to Netlify
```

## Daily Workflow

### Starting Work (Any Device)

1. **Pull latest changes**:
   ```bash
   cd "/Users/jiwonkim/Desktop/UI:UX/유저그래피/Projects/SG"  # MacBook path
   # or
   cd ~/Desktop/UI:UX/유저그래피/Projects/SG-website        # iMac path (after setup)
   
   git pull origin main
   ```

2. **Check current status**:
   ```bash
   git status
   git log --oneline -5  # See recent commits
   ```

### Making Changes

1. **Edit files** using your preferred editor
2. **Test locally** (optional):
   ```bash
   python -m http.server 8000
   # Visit: http://localhost:8000
   ```

### Saving and Syncing Changes

1. **Stage changes**:
   ```bash
   git add .
   # or for specific files:
   git add index.html
   ```

2. **Commit with descriptive message**:
   ```bash
   git commit -m "Update hero section styling and mobile responsiveness"
   ```

3. **Push to GitHub** (auto-deploys to Netlify):
   ```bash
   git push origin main
   ```

4. **Verify deployment**:
   - Check your Netlify dashboard for build status
   - Visit: https://amazing-fenglisu-843d13.netlify.app

## Important Reminders

### 🔄 **Always Pull Before Starting**
```bash
git pull origin main
```
This prevents merge conflicts when switching between devices.

### 📝 **Use Descriptive Commit Messages**
Good examples:
- `Fix mobile navigation menu alignment`
- `Add new client logos to hero section`
- `Update contact form validation`

Avoid:
- `updates`
- `fixes`
- `changes`

### 🚨 **Handle Conflicts Carefully**
If you get merge conflicts:
```bash
# See which files have conflicts
git status

# Edit the conflicted files to resolve differences
# Look for markers like: <<<<<<< HEAD

# After resolving conflicts:
git add .
git commit -m "Resolve merge conflicts in [filename]"
git push origin main
```

### 🖼️ **Managing Images**
- Keep images in `img sources/` directory
- Use relative paths in HTML: `img sources/logo_example.png`
- Optimize images before adding (keep file sizes reasonable)

## Troubleshooting

### Problem: "Permission denied" or "Authentication failed"
**Solution**: Check your GitHub token or authentication
```bash
# Re-authenticate or update token
git remote set-url origin https://YOUR_NEW_TOKEN@github.com/bellebr/SG-website.git
```

### Problem: "Large file upload fails"
**Solution**: Increase Git buffer size
```bash
git config http.postBuffer 524288000
```

### Problem: "Repository not found" 
**Solution**: Check the remote URL
```bash
git remote -v
# Should show: https://github.com/bellebr/SG-website.git
```

### Problem: "Netlify not deploying"
**Solution**: 
1. Check Netlify dashboard for build logs
2. Ensure you're pushing to the `main` branch
3. Verify the GitHub connection in Netlify settings

## Quick Reference Commands

```bash
# Check status
git status

# Pull latest changes  
git pull origin main

# Add all changes
git add .

# Commit with message
git commit -m "Your message"

# Push to GitHub (auto-deploys)
git push origin main

# View recent commits
git log --oneline -10

# Check remote URLs
git remote -v

# Serve locally
python -m http.server 8000
```

## Success! 🎉

Once both devices are set up, you can seamlessly:
- Work on your iMac at home
- Continue on your MacBook when mobile
- Always have the latest version on both devices
- Automatic deployments to your live website

Your workflow is now optimized for professional cross-device development!