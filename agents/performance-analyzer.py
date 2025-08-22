#!/usr/bin/env python3
"""
Performance Analyzer Agent for Superdesign
Analyzes CSS/HTML for performance optimization opportunities
"""

import re
import json
import os
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Tuple
import cssutils
import logging
from urllib.parse import urlparse
import gzip

# Suppress cssutils warnings
cssutils.log.setLevel(logging.ERROR)

class PerformanceAnalyzer:
    def __init__(self):
        self.warnings = []
        self.suggestions = []
        self.optimizations = []
        self.metrics = {}
        
    def analyze_html_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze HTML file for performance issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_size = os.path.getsize(file_path)
            return self.analyze_html_content(content, file_path, file_size)
        except Exception as e:
            return {
                'success': False,
                'error': f"Could not read file {file_path}: {str(e)}",
                'warnings': [],
                'suggestions': []
            }
    
    def analyze_html_content(self, html_content: str, source: str = "content", file_size: int = None) -> Dict[str, Any]:
        """Analyze HTML content for performance issues"""
        self.warnings = []
        self.suggestions = []
        self.optimizations = []
        self.metrics = {}
        
        # Calculate basic metrics
        if file_size is None:
            file_size = len(html_content.encode('utf-8'))
        
        self.metrics['file_size'] = file_size
        self.metrics['file_size_kb'] = round(file_size / 1024, 2)
        
        # Parse HTML
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            return {
                'success': False,
                'error': f"HTML parsing error: {str(e)}",
                'warnings': [],
                'suggestions': []
            }
        
        # Run performance analysis
        self._analyze_file_size(file_size)
        self._analyze_css_performance(html_content, soup)
        self._analyze_javascript_performance(soup)
        self._analyze_images(soup)
        self._analyze_fonts(soup)
        self._analyze_external_resources(soup)
        self._analyze_render_blocking(soup)
        self._analyze_critical_path(soup)
        self._calculate_performance_score()
        
        return self._build_result(source)
    
    def _analyze_file_size(self, file_size: int):
        """Analyze overall file size"""
        size_kb = file_size / 1024
        
        if size_kb > 500:
            self.warnings.append(f"Large HTML file size: {size_kb:.1f}KB - consider code splitting")
        elif size_kb > 200:
            self.suggestions.append(f"HTML file size: {size_kb:.1f}KB - monitor for growth")
        
        # Estimate gzipped size (rough approximation)
        gzipped_size = len(gzip.compress(str(file_size).encode())) * (file_size / len(str(file_size)))
        compression_ratio = (file_size - gzipped_size) / file_size * 100
        
        self.metrics['estimated_gzipped_size'] = round(gzipped_size / 1024, 2)
        self.metrics['compression_ratio'] = round(compression_ratio, 1)
        
        if compression_ratio < 60:
            self.suggestions.append("Enable gzip compression on your server for better performance")
    
    def _analyze_css_performance(self, html_content: str, soup: BeautifulSoup):
        """Analyze CSS performance"""
        # Count CSS resources
        css_links = soup.find_all('link', rel='stylesheet')
        style_tags = soup.find_all('style')
        
        self.metrics['external_css_files'] = len(css_links)
        self.metrics['inline_css_blocks'] = len(style_tags)
        
        # Check for too many CSS files
        if len(css_links) > 5:
            self.warnings.append(f"Too many CSS files ({len(css_links)}) - consider concatenation")
            self.optimizations.append("Bundle CSS files to reduce HTTP requests")
        
        # Analyze inline CSS
        total_inline_css = sum(len(style.get_text()) for style in style_tags)
        self.metrics['inline_css_size'] = round(total_inline_css / 1024, 2)
        
        if total_inline_css > 10000:  # 10KB
            self.warnings.append(f"Large amount of inline CSS ({total_inline_css/1024:.1f}KB)")
            self.suggestions.append("Move large CSS blocks to external files for better caching")
        
        # Check for unused CSS (basic detection)
        self._analyze_unused_css(html_content, soup)
        
        # Check for CSS minification
        for style in style_tags:
            css_content = style.get_text()
            if self._is_unminified_css(css_content):
                self.suggestions.append("Minify CSS to reduce file size")
                break
    
    def _analyze_unused_css(self, html_content: str, soup: BeautifulSoup):
        """Detect potentially unused CSS"""
        style_tags = soup.find_all('style')
        
        for style in style_tags:
            css_content = style.get_text()
            
            # Extract CSS selectors (basic)
            selectors = re.findall(r'([.#]?[a-zA-Z][\w-]*)\s*{', css_content)
            
            unused_selectors = []
            for selector in selectors[:10]:  # Check first 10 to avoid performance issues
                if selector.startswith('.'):
                    # Check for class usage
                    class_name = selector[1:]
                    if f'class="{class_name}"' not in html_content and f"class='{class_name}'" not in html_content:
                        unused_selectors.append(selector)
                elif selector.startswith('#'):
                    # Check for ID usage
                    id_name = selector[1:]
                    if f'id="{id_name}"' not in html_content and f"id='{id_name}'" not in html_content:
                        unused_selectors.append(selector)
            
            if unused_selectors:
                self.suggestions.append(f"Potentially unused CSS selectors found: {', '.join(unused_selectors[:3])}")
                self.optimizations.append("Remove unused CSS to reduce file size")
    
    def _is_unminified_css(self, css_content: str) -> bool:
        """Check if CSS appears to be unminified"""
        lines = css_content.split('\n')
        
        # Check for formatting that suggests unminified CSS
        has_indentation = any(line.startswith('  ') or line.startswith('\t') for line in lines)
        has_comments = '/*' in css_content
        has_spacing = ' {' in css_content or '{ ' in css_content
        
        return has_indentation or has_comments or has_spacing
    
    def _analyze_javascript_performance(self, soup: BeautifulSoup):
        """Analyze JavaScript performance"""
        # Count JS resources
        js_scripts = soup.find_all('script', src=True)
        inline_scripts = soup.find_all('script', src=False)
        
        # Remove empty scripts
        inline_scripts = [s for s in inline_scripts if s.get_text().strip()]
        
        self.metrics['external_js_files'] = len(js_scripts)
        self.metrics['inline_js_blocks'] = len(inline_scripts)
        
        # Check for too many JS files
        if len(js_scripts) > 7:
            self.warnings.append(f"Too many JavaScript files ({len(js_scripts)}) - consider bundling")
            self.optimizations.append("Bundle JavaScript files to reduce HTTP requests")
        
        # Check for render-blocking scripts
        blocking_scripts = [s for s in js_scripts if not s.get('async') and not s.get('defer')]
        if blocking_scripts:
            self.warnings.append(f"{len(blocking_scripts)} render-blocking JavaScript files")
            self.suggestions.append("Add 'defer' or 'async' attributes to non-critical JavaScript")
        
        # Analyze inline JavaScript size
        total_inline_js = sum(len(script.get_text()) for script in inline_scripts)
        self.metrics['inline_js_size'] = round(total_inline_js / 1024, 2)
        
        if total_inline_js > 5000:  # 5KB
            self.suggestions.append(f"Large amount of inline JavaScript ({total_inline_js/1024:.1f}KB)")
    
    def _analyze_images(self, soup: BeautifulSoup):
        """Analyze image performance"""
        images = soup.find_all('img')
        self.metrics['image_count'] = len(images)
        
        # Check for missing lazy loading
        non_lazy_images = [img for img in images if not img.get('loading')]
        if len(non_lazy_images) > 3:
            self.suggestions.append(f"Consider adding loading='lazy' to {len(non_lazy_images)} images")
            self.optimizations.append("Implement lazy loading for images below the fold")
        
        # Check for image formats
        jpg_images = [img for img in images if img.get('src', '').lower().endswith(('.jpg', '.jpeg'))]
        png_images = [img for img in images if img.get('src', '').lower().endswith('.png')]
        
        if jpg_images or png_images:
            self.suggestions.append("Consider using modern image formats (WebP, AVIF) for better compression")
        
        # Check for missing dimensions
        missing_dimensions = [img for img in images if not img.get('width') or not img.get('height')]
        if missing_dimensions:
            self.warnings.append(f"{len(missing_dimensions)} images missing width/height attributes")
            self.suggestions.append("Add width/height attributes to prevent layout shifts")
    
    def _analyze_fonts(self, soup: BeautifulSoup):
        """Analyze font performance"""
        # Check for Google Fonts
        google_fonts = soup.find_all('link', href=re.compile(r'fonts\.googleapis\.com'))
        self.metrics['google_fonts_count'] = len(google_fonts)
        
        if len(google_fonts) > 2:
            self.warnings.append(f"Multiple Google Fonts imports ({len(google_fonts)}) - consider combining")
            self.optimizations.append("Combine Google Fonts requests into single URL")
        
        # Check for font preloading
        font_preloads = soup.find_all('link', rel='preload', attrs={'as': 'font'})
        if google_fonts and not font_preloads:
            self.suggestions.append("Consider preloading critical fonts to reduce render delay")
        
        # Check for font-display
        style_tags = soup.find_all('style')
        has_font_display = any('font-display' in style.get_text() for style in style_tags)
        
        if (google_fonts or font_preloads) and not has_font_display:
            self.suggestions.append("Add font-display: swap to CSS for better font loading performance")
    
    def _analyze_external_resources(self, soup: BeautifulSoup):
        """Analyze external resource performance"""
        # Count external resources
        external_links = soup.find_all(['link', 'script'], src=True) + soup.find_all('link', href=True)
        
        external_domains = set()
        for resource in external_links:
            url = resource.get('src') or resource.get('href')
            if url and url.startswith('http'):
                domain = urlparse(url).netloc
                external_domains.add(domain)
        
        self.metrics['external_domains'] = len(external_domains)
        
        if len(external_domains) > 5:
            self.warnings.append(f"Too many external domains ({len(external_domains)}) - increases DNS lookups")
            self.suggestions.append("Consider DNS prefetching: <link rel='dns-prefetch' href='//domain.com'>")
        
        # Check for CDN usage
        cdn_domains = ['cdn.', 'cdnjs.', 'jsdelivr.', 'unpkg.']
        using_cdn = any(any(cdn in str(resource) for cdn in cdn_domains) for resource in external_links)
        
        if using_cdn:
            self.metrics['using_cdn'] = True
        else:
            self.suggestions.append("Consider using CDN for better global performance")
    
    def _analyze_render_blocking(self, soup: BeautifulSoup):
        """Analyze render-blocking resources"""
        # CSS in head (render-blocking)
        css_in_head = soup.head.find_all('link', rel='stylesheet') if soup.head else []
        
        # Check for critical CSS inlining
        if len(css_in_head) > 0:
            self.suggestions.append("Consider inlining critical CSS and loading non-critical CSS asynchronously")
        
        # JavaScript in head without defer/async
        js_in_head = soup.head.find_all('script', src=True) if soup.head else []
        blocking_js_in_head = [s for s in js_in_head if not s.get('async') and not s.get('defer')]
        
        if blocking_js_in_head:
            self.warnings.append(f"{len(blocking_js_in_head)} render-blocking scripts in <head>")
            self.optimizations.append("Move non-critical JavaScript to bottom of page or add defer attribute")
    
    def _analyze_critical_path(self, soup: BeautifulSoup):
        """Analyze critical rendering path"""
        # Check for resource hints
        resource_hints = soup.find_all('link', rel=['preload', 'prefetch', 'preconnect', 'dns-prefetch'])
        self.metrics['resource_hints'] = len(resource_hints)
        
        if len(resource_hints) == 0:
            self.suggestions.append("Consider using resource hints (preload, prefetch, preconnect) for key resources")
        
        # Check for viewport meta tag
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport_meta:
            self.warnings.append("Missing viewport meta tag - affects mobile performance")
    
    def _calculate_performance_score(self):
        """Calculate overall performance score"""
        score = 100
        
        # Deduct points for issues
        score -= len(self.warnings) * 10
        score -= len(self.suggestions) * 5
        
        # Bonus points for optimizations
        if self.metrics.get('using_cdn'):
            score += 5
        if self.metrics.get('resource_hints', 0) > 0:
            score += 5
        
        self.metrics['performance_score'] = max(0, min(100, score))
    
    def _build_result(self, source: str) -> Dict[str, Any]:
        """Build analysis result"""
        return {
            'success': True,
            'source': source,
            'performance_score': self.metrics.get('performance_score', 0),
            'metrics': self.metrics,
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'optimizations': self.optimizations,
            'summary': {
                'total_issues': len(self.warnings) + len(self.suggestions),
                'warnings': len(self.warnings),
                'suggestions': len(self.suggestions),
                'optimizations': len(self.optimizations)
            },
            'recommendations': {
                'high_priority': [opt for opt in self.optimizations],
                'medium_priority': [warn for warn in self.warnings],
                'low_priority': [sugg for sugg in self.suggestions]
            }
        }

def main():
    """Main function for CLI usage"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python performance-analyzer.py <html_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyzer = PerformanceAnalyzer()
    result = analyzer.analyze_html_file(file_path)
    
    print(json.dumps(result, indent=2))
    
    # Exit code based on performance score
    score = result.get('performance_score', 0)
    sys.exit(0 if score >= 70 else 1)

if __name__ == "__main__":
    main()