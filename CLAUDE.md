# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SOFTGRAM fintech company website - a professional Korean financial technology company landing page with responsive design and modern UI.

**Live Site**: https://amazing-fenglisu-843d13.netlify.app  
**Repository**: https://github.com/bellebr/SG-website  
**Main File**: `index.html`

## Technology Stack

- **Frontend**: Pure HTML5, CSS3, JavaScript (ES6+)
- **Icons**: Lucide Icons (loaded via CDN)
- **Fonts**: Inter font family
- **Deployment**: Netlify (auto-deploy from GitHub)
- **Version Control**: Git + GitHub

## Project Structure

```
SG/
├── index.html                    # Main website (production)
├── README.md                     # Project documentation
├── CLAUDE.md                     # This file
├── .gitignore                    # Git ignore rules
├── about.html                    # About page
├── img sources/                  # All image assets
│   ├── logo_*.png/jpg/svg       # Client company logos
│   ├── services_*.jpg           # Service section images
│   └── bg_hero.png              # Hero background image
├── agents/                       # Python development tools
│   ├── accessibility-auditor.py # A11y testing
│   ├── performance-analyzer.py  # Performance monitoring
│   ├── code-validator.py        # HTML/CSS validation
│   └── requirements.txt         # Python dependencies
└── [other HTML variations]      # Testing versions
```

## Development Commands

Since this is a static HTML/CSS/JS website, no build process is required.

### Local Development
```bash
# Serve locally (Python 3)
python -m http.server 8000

# Serve locally (Python 2)  
python -m SimpleHTTPServer 8000

# Then visit: http://localhost:8000
```

### Git Workflow
```bash
# Make changes, then:
git add .
git commit -m "Your change description"
git push origin main
# → Automatically deploys to Netlify
```

### Cross-Device Development
This project is set up for seamless development between iMac and MacBook:

**On MacBook** (current setup):
```bash
cd "/Users/jiwonkim/Desktop/UI:UX/유저그래피/Projects/SG"
# Make changes, commit, push
```

**On iMac** (to set up):
```bash
git clone https://github.com/bellebr/SG-website.git
cd SG-website
# Make changes, commit, push
```

## Important Configuration

### Git Configuration (for large files)
```bash
git config http.postBuffer 524288000  # Increase buffer for image uploads
```

### Netlify Settings
- **Repository**: bellebr/SG-website
- **Branch**: main  
- **Build command**: (none - static site)
- **Publish directory**: / (root)
- **Auto-deploy**: Enabled

## File Guidelines

- **Main production file**: `index.html`
- **Images**: Use relative paths like `img sources/filename.ext`
- **Testing**: Create new HTML files for A/B testing variations
- **Commit messages**: Use descriptive messages for deployment tracking

## Architecture Notes

- **Responsive Design**: Mobile-first approach with CSS Grid and Flexbox
- **Performance**: Optimized images and minimal external dependencies  
- **SEO**: Proper semantic HTML and meta tags
- **Accessibility**: ARIA labels and keyboard navigation support
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)