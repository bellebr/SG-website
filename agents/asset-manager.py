#!/usr/bin/env python3
"""
Asset Manager Agent for Superdesign
Manages and validates images, fonts, and external assets
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, urljoin
import os
import time

class AssetManager:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []
        self.assets = {}
        
        # Known CDN domains for optimization
        self.cdn_domains = [
            'cdn.jsdelivr.net',
            'cdnjs.cloudflare.com',
            'unpkg.com',
            'fonts.googleapis.com',
            'fonts.gstatic.com'
        ]
        
        # Optimized image services
        self.image_services = [
            'unsplash.com',
            'images.unsplash.com',
            'via.placeholder.com',
            'placehold.co',
            'picsum.photos'
        ]
    
    def manage_assets_in_file(self, file_path: str) -> Dict[str, Any]:
        """Manage assets in HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.manage_assets_in_content(content, file_path)
        except Exception as e:
            return {
                'success': False,
                'error': f"Could not read file {file_path}: {str(e)}",
                'errors': [],
                'warnings': [],
                'suggestions': []
            }
    
    def manage_assets_in_content(self, html_content: str, source: str = "content") -> Dict[str, Any]:
        """Manage assets in HTML content"""
        self.errors = []
        self.warnings = []
        self.suggestions = []
        self.assets = {
            'images': [],
            'fonts': [],
            'css_files': [],
            'js_files': [],
            'external_resources': []
        }
        
        # Parse HTML
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            return {
                'success': False,
                'error': f"HTML parsing error: {str(e)}",
                'errors': [],
                'warnings': [],
                'suggestions': []
            }
        
        # Analyze different asset types
        self._analyze_images(soup)
        self._analyze_fonts(soup)
        self._analyze_css_files(soup)
        self._analyze_js_files(soup)
        self._analyze_external_resources(soup)
        self._validate_asset_urls()
        self._suggest_optimizations()
        
        return self._build_result(source)
    
    def _analyze_images(self, soup: BeautifulSoup):
        """Analyze image assets"""
        images = soup.find_all('img')
        
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            loading = img.get('loading', '')
            
            image_info = {
                'src': src,
                'alt': alt,
                'loading': loading,
                'element': str(img)[:100] + '...',
                'issues': []
            }
            
            # Validate image URL
            if not src:
                image_info['issues'].append('Missing src attribute')
                self.errors.append("Image missing src attribute")
            elif self._is_placeholder_service(src):
                image_info['service'] = self._get_image_service(src)
                image_info['optimized'] = True
            else:
                # Check if it's a valid URL
                if src.startswith('http'):
                    if not self._is_valid_url(src):
                        image_info['issues'].append('Invalid or unreachable URL')
                        self.errors.append(f"Image URL not accessible: {src}")
                
            # Check for modern formats
            if src and not any(ext in src.lower() for ext in ['.webp', '.avif']):
                if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png']):
                    image_info['issues'].append('Consider modern format (WebP/AVIF)')
                    self.suggestions.append(f"Consider WebP/AVIF format for better compression: {src}")
            
            # Check for lazy loading
            if not loading and len(self.assets['images']) > 2:  # Don't lazy load first few images
                image_info['issues'].append('Consider lazy loading')
                self.suggestions.append("Add loading='lazy' for images below the fold")
            
            self.assets['images'].append(image_info)
    
    def _analyze_fonts(self, soup: BeautifulSoup):
        """Analyze font assets"""
        # Google Fonts links
        google_fonts = soup.find_all('link', href=re.compile(r'fonts\.googleapis\.com'))
        
        for font_link in google_fonts:
            href = font_link.get('href', '')
            
            font_info = {
                'type': 'google_fonts',
                'href': href,
                'preconnect': False,
                'display_swap': False,
                'issues': []
            }
            
            # Check for preconnect
            preconnect = soup.find('link', rel='preconnect', href='https://fonts.googleapis.com')
            preconnect_static = soup.find('link', rel='preconnect', href='https://fonts.gstatic.com')
            
            if preconnect and preconnect_static:
                font_info['preconnect'] = True
            else:
                font_info['issues'].append('Missing preconnect for Google Fonts')
                self.suggestions.append("Add preconnect links for Google Fonts performance")
            
            # Check for font-display in CSS
            style_tags = soup.find_all('style')
            has_font_display = any('font-display:' in style.get_text().replace(' ', '') or 
                                 'font-display :' in style.get_text() for style in style_tags)
            
            if has_font_display:
                font_info['display_swap'] = True
            else:
                font_info['issues'].append('Consider font-display: swap')
                self.suggestions.append("Add font-display: swap for better font loading")
            
            self.assets['fonts'].append(font_info)
        
        # Local font files
        font_files = soup.find_all('link', href=re.compile(r'\.(woff2?|ttf|otf|eot)'))
        for font_file in font_files:
            href = font_file.get('href', '')
            
            font_info = {
                'type': 'local_font',
                'href': href,
                'preload': font_file.get('rel') == 'preload',
                'issues': []
            }
            
            # Check format preference (WOFF2 is best)
            if '.woff2' not in href.lower():
                font_info['issues'].append('WOFF2 format preferred for better compression')
                self.suggestions.append(f"Use WOFF2 format for better compression: {href}")
            
            self.assets['fonts'].append(font_info)
    
    def _analyze_css_files(self, soup: BeautifulSoup):
        """Analyze CSS file assets"""
        css_links = soup.find_all('link', rel='stylesheet')
        
        for css_link in css_links:
            href = css_link.get('href', '')
            
            css_info = {
                'href': href,
                'external': href.startswith('http'),
                'cdn': self._is_cdn_url(href),
                'issues': []
            }
            
            # Validate URL if external
            if css_info['external'] and not self._is_valid_url(href):
                css_info['issues'].append('URL not accessible')
                self.errors.append(f"CSS file not accessible: {href}")
            
            # Check for CDN usage
            if css_info['external'] and not css_info['cdn']:
                css_info['issues'].append('Consider using CDN')
                self.suggestions.append(f"Consider using CDN for CSS: {href}")
            
            self.assets['css_files'].append(css_info)
    
    def _analyze_js_files(self, soup: BeautifulSoup):
        """Analyze JavaScript file assets"""
        js_scripts = soup.find_all('script', src=True)
        
        for script in js_scripts:
            src = script.get('src', '')
            
            js_info = {
                'src': src,
                'external': src.startswith('http'),
                'cdn': self._is_cdn_url(src),
                'async': script.get('async') is not None,
                'defer': script.get('defer') is not None,
                'issues': []
            }
            
            # Validate URL if external
            if js_info['external'] and not self._is_valid_url(src):
                js_info['issues'].append('URL not accessible')
                self.errors.append(f"JavaScript file not accessible: {src}")
            
            # Check for loading optimization
            if js_info['external'] and not js_info['async'] and not js_info['defer']:
                js_info['issues'].append('Consider async or defer')
                self.suggestions.append(f"Add async/defer to non-critical JavaScript: {src}")
            
            # Check for CDN usage
            if js_info['external'] and not js_info['cdn']:
                js_info['issues'].append('Consider using CDN')
                self.suggestions.append(f"Consider using CDN for JavaScript: {src}")
            
            self.assets['js_files'].append(js_info)
    
    def _analyze_external_resources(self, soup: BeautifulSoup):
        """Analyze other external resources"""
        # Lucide icons or other icon libraries
        icon_scripts = soup.find_all('script', src=re.compile(r'(lucide|feather|heroicons|fontawesome)'))
        
        for icon_script in icon_scripts:
            src = icon_script.get('src', '')
            
            resource_info = {
                'type': 'icon_library',
                'src': src,
                'cdn': self._is_cdn_url(src),
                'issues': []
            }
            
            if not resource_info['cdn']:
                resource_info['issues'].append('Use CDN for icon libraries')
                self.suggestions.append(f"Use CDN for icon library: {src}")
            
            self.assets['external_resources'].append(resource_info)
    
    def _validate_asset_urls(self):
        """Validate asset URLs (basic check without making actual requests)"""
        # This is a lightweight validation - in production, you might want to make HEAD requests
        all_urls = []
        
        # Collect all URLs
        for image in self.assets['images']:
            if image['src'].startswith('http'):
                all_urls.append(image['src'])
        
        for font in self.assets['fonts']:
            if font.get('href', '').startswith('http'):
                all_urls.append(font['href'])
        
        # Basic URL format validation
        for url in all_urls:
            if not self._is_well_formed_url(url):
                self.warnings.append(f"Malformed URL detected: {url}")
    
    def _suggest_optimizations(self):
        """Suggest asset optimizations"""
        # Image optimization suggestions
        if len(self.assets['images']) > 10:
            self.suggestions.append("Consider image lazy loading for better performance")
        
        # Font optimization
        google_fonts_count = len([f for f in self.assets['fonts'] if f['type'] == 'google_fonts'])
        if google_fonts_count > 2:
            self.suggestions.append("Consider reducing number of Google Fonts for better performance")
        
        # CSS/JS bundling suggestions
        if len(self.assets['css_files']) > 3:
            self.suggestions.append("Consider bundling CSS files to reduce HTTP requests")
        
        if len(self.assets['js_files']) > 5:
            self.suggestions.append("Consider bundling JavaScript files to reduce HTTP requests")
    
    def _is_placeholder_service(self, url: str) -> bool:
        """Check if URL is from a known placeholder service"""
        return any(service in url for service in self.image_services)
    
    def _get_image_service(self, url: str) -> str:
        """Get the image service name"""
        for service in self.image_services:
            if service in url:
                return service
        return 'unknown'
    
    def _is_cdn_url(self, url: str) -> bool:
        """Check if URL is from a known CDN"""
        return any(cdn in url for cdn in self.cdn_domains)
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation (without making HTTP requests)"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
        except:
            return False
    
    def _is_well_formed_url(self, url: str) -> bool:
        """Check if URL is well-formed"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme)
        except:
            return False
    
    def optimize_assets_suggestions(self) -> List[str]:
        """Generate optimization suggestions"""
        optimizations = []
        
        # Image optimizations
        non_optimized_images = [img for img in self.assets['images'] if not img.get('optimized')]
        if non_optimized_images:
            optimizations.append(f"Optimize {len(non_optimized_images)} images with modern formats")
        
        # Font optimizations
        fonts_without_preload = [f for f in self.assets['fonts'] if not f.get('preload')]
        if fonts_without_preload:
            optimizations.append("Add font preloading for critical fonts")
        
        return optimizations
    
    def _build_result(self, source: str) -> Dict[str, Any]:
        """Build asset management result"""
        total_assets = sum(len(assets) for assets in self.assets.values())
        
        return {
            'success': len(self.errors) == 0,
            'source': source,
            'assets': self.assets,
            'errors': self.errors,
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'optimizations': self.optimize_assets_suggestions(),
            'summary': {
                'total_assets': total_assets,
                'images': len(self.assets['images']),
                'fonts': len(self.assets['fonts']),
                'css_files': len(self.assets['css_files']),
                'js_files': len(self.assets['js_files']),
                'external_resources': len(self.assets['external_resources']),
                'total_issues': len(self.errors) + len(self.warnings),
                'errors': len(self.errors),
                'warnings': len(self.warnings),
                'suggestions': len(self.suggestions)
            }
        }

def main():
    """Main function for CLI usage"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python asset-manager.py <html_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    manager = AssetManager()
    result = manager.manage_assets_in_file(file_path)
    
    print(json.dumps(result, indent=2))
    
    # Exit with error code if asset issues found
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()