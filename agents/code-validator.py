#!/usr/bin/env python3
"""
Code Validator Agent for Superdesign
Validates HTML/CSS/JS syntax and cross-browser compatibility
"""

import re
import json
from bs4 import BeautifulSoup
from typing import Dict, List, Any
import cssutils
import logging

# Suppress cssutils warnings
cssutils.log.setLevel(logging.ERROR)

class CodeValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
    def validate_html_file(self, file_path: str) -> Dict[str, Any]:
        """Validate HTML file for syntax and best practices"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.validate_html_content(content, file_path)
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Could not read file {file_path}: {str(e)}"],
                'warnings': [],
                'suggestions': []
            }
    
    def validate_html_content(self, html_content: str, source: str = "content") -> Dict[str, Any]:
        """Validate HTML content for syntax and best practices"""
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
        # Parse HTML
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            self.errors.append(f"HTML parsing error: {str(e)}")
            return self._build_result(source)
        
        # Validate HTML structure
        self._validate_html_structure(soup)
        self._validate_semantic_html(soup)
        self._validate_responsive_design(soup)
        self._validate_css_in_html(html_content)
        self._validate_js_in_html(html_content)
        
        return self._build_result(source)
    
    def _validate_html_structure(self, soup: BeautifulSoup):
        """Validate basic HTML structure"""
        # Check for DOCTYPE
        if not soup.find('html'):
            self.errors.append("Missing <html> tag")
        
        if not soup.find('head'):
            self.errors.append("Missing <head> tag")
            
        if not soup.find('body'):
            self.errors.append("Missing <body> tag")
            
        # Check for meta viewport (required for responsive design)
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport_meta:
            self.warnings.append("Missing viewport meta tag for responsive design")
            self.suggestions.append("Add: <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        
        # Check for title
        title = soup.find('title')
        if not title or not title.get_text().strip():
            self.warnings.append("Missing or empty <title> tag")
            
        # Check for charset
        charset_meta = soup.find('meta', attrs={'charset': True}) or soup.find('meta', attrs={'http-equiv': 'Content-Type'})
        if not charset_meta:
            self.warnings.append("Missing charset declaration")
            self.suggestions.append("Add: <meta charset='UTF-8'>")
    
    def _validate_semantic_html(self, soup: BeautifulSoup):
        """Validate semantic HTML usage"""
        # Check for semantic tags
        semantic_tags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
        used_semantic_tags = [tag for tag in semantic_tags if soup.find(tag)]
        
        if len(used_semantic_tags) < 2:
            self.suggestions.append("Consider using more semantic HTML5 tags (header, nav, main, section, article, aside, footer)")
        
        # Check for alt attributes on images
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt'):
                self.warnings.append(f"Image missing alt attribute: {str(img)[:100]}...")
                
        # Check for proper heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if headings:
            first_heading = headings[0]
            if first_heading.name != 'h1':
                self.warnings.append("Page should start with h1 heading")
    
    def _validate_responsive_design(self, soup: BeautifulSoup):
        """Validate responsive design patterns"""
        # Check for responsive classes (common patterns)
        responsive_patterns = [
            r'sm:', r'md:', r'lg:', r'xl:',  # Tailwind
            r'col-', r'row-',  # Bootstrap grid
            r'flex', r'grid'   # CSS Flexbox/Grid
        ]
        
        html_string = str(soup)
        has_responsive = any(re.search(pattern, html_string) for pattern in responsive_patterns)
        
        if not has_responsive:
            self.suggestions.append("Consider adding responsive design classes or CSS media queries")
        
        # Check for fixed widths that might break responsiveness
        fixed_width_pattern = r'width:\s*\d+px'
        if re.search(fixed_width_pattern, html_string):
            self.warnings.append("Found fixed pixel widths that may not be responsive")
            self.suggestions.append("Consider using relative units (%, em, rem, vw, vh) instead of fixed pixels")
    
    def _validate_css_in_html(self, html_content: str):
        """Validate CSS within HTML"""
        # Extract CSS from style tags
        style_pattern = r'<style[^>]*>(.*?)</style>'
        css_blocks = re.findall(style_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        for css_block in css_blocks:
            self._validate_css_content(css_block.strip())
        
        # Extract inline styles
        inline_style_pattern = r'style=["\']([^"\']*)["\']'
        inline_styles = re.findall(inline_style_pattern, html_content, re.IGNORECASE)
        
        if len(inline_styles) > 5:
            self.suggestions.append("Consider moving inline styles to CSS classes for better maintainability")
    
    def _validate_css_content(self, css_content: str):
        """Validate CSS syntax and best practices"""
        try:
            # Parse CSS
            sheet = cssutils.parseString(css_content)
            
            # Check for vendor prefixes
            vendor_prefixes = ['-webkit-', '-moz-', '-ms-', '-o-']
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    for prop in rule.style:
                        prop_name = prop.name
                        if any(prefix in prop_name for prefix in vendor_prefixes):
                            self.suggestions.append(f"Consider using autoprefixer instead of manual vendor prefixes: {prop_name}")
            
        except Exception as e:
            self.errors.append(f"CSS parsing error: {str(e)}")
    
    def _validate_js_in_html(self, html_content: str):
        """Basic JavaScript validation"""
        # Extract JavaScript from script tags
        script_pattern = r'<script[^>]*>(.*?)</script>'
        js_blocks = re.findall(script_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        for js_block in js_blocks:
            js_content = js_block.strip()
            if js_content:
                self._validate_js_content(js_content)
    
    def _validate_js_content(self, js_content: str):
        """Basic JavaScript syntax validation"""
        # Check for common issues
        if 'console.log' in js_content:
            self.suggestions.append("Remove console.log statements before production")
        
        # Check for missing semicolons (basic check)
        lines = js_content.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.endswith((';', '{', '}', ')', ',')) and not line.startswith(('if', 'else', 'for', 'while', 'function', '//')):
                self.suggestions.append(f"Consider adding semicolon at line {i}: {line[:50]}...")
                break  # Only report first occurrence
    
    def _build_result(self, source: str) -> Dict[str, Any]:
        """Build validation result"""
        return {
            'success': len(self.errors) == 0,
            'source': source,
            'errors': self.errors,
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'summary': {
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
        print("Usage: python code-validator.py <html_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    validator = CodeValidator()
    result = validator.validate_html_file(file_path)
    
    print(json.dumps(result, indent=2))
    
    # Exit with error code if validation failed
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()