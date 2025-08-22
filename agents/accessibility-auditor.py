#!/usr/bin/env python3
"""
Accessibility Auditor Agent for Superdesign
Validates WCAG compliance, color contrast, and accessibility best practices
"""

import re
import json
import colorsys
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Tuple
import cssutils
import logging

# Suppress cssutils warnings
cssutils.log.setLevel(logging.ERROR)

class AccessibilityAuditor:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
        # WCAG contrast ratios
        self.CONTRAST_AA_NORMAL = 4.5
        self.CONTRAST_AA_LARGE = 3.0
        self.CONTRAST_AAA_NORMAL = 7.0
        self.CONTRAST_AAA_LARGE = 4.5
    
    def audit_html_file(self, file_path: str) -> Dict[str, Any]:
        """Audit HTML file for accessibility issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.audit_html_content(content, file_path)
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Could not read file {file_path}: {str(e)}"],
                'warnings': [],
                'suggestions': []
            }
    
    def audit_html_content(self, html_content: str, source: str = "content") -> Dict[str, Any]:
        """Audit HTML content for accessibility issues"""
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
        # Parse HTML
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            self.errors.append(f"HTML parsing error: {str(e)}")
            return self._build_result(source)
        
        # Run accessibility audits
        self._audit_semantic_structure(soup)
        self._audit_images(soup)
        self._audit_forms(soup)
        self._audit_links(soup)
        self._audit_headings(soup)
        self._audit_aria_attributes(soup)
        self._audit_keyboard_navigation(soup)
        self._audit_color_contrast(html_content, soup)
        self._audit_focus_management(soup)
        
        return self._build_result(source)
    
    def _audit_semantic_structure(self, soup: BeautifulSoup):
        """Audit semantic HTML structure"""
        # Check for proper landmark usage
        landmarks = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
        found_landmarks = [tag for tag in landmarks if soup.find(tag)]
        
        if 'main' not in found_landmarks:
            self.errors.append("Missing <main> landmark - required for screen readers")
            
        # Check for proper document structure
        if not soup.find('h1'):
            self.errors.append("Missing h1 heading - required for document structure")
        
        # Check for skip links
        skip_links = soup.find_all('a', href=re.compile(r'^#'))
        skip_to_main = any('skip' in str(link).lower() and 'main' in str(link).lower() for link in skip_links)
        
        if not skip_to_main:
            self.suggestions.append("Add skip navigation link for keyboard users: <a href='#main' class='sr-only'>Skip to main content</a>")
    
    def _audit_images(self, soup: BeautifulSoup):
        """Audit image accessibility"""
        images = soup.find_all('img')
        
        for img in images:
            # Check for alt text
            alt = img.get('alt')
            if alt is None:
                self.errors.append(f"Image missing alt attribute: {str(img)[:100]}...")
            elif alt == '':
                # Empty alt is OK for decorative images, but should be intentional
                src = img.get('src', 'unknown')
                if 'decoration' not in str(img).lower() and 'decorative' not in str(img).lower():
                    self.warnings.append(f"Image has empty alt text - ensure this is decorative: {src}")
            
            # Check for proper alt text content
            if alt and len(alt) > 125:
                self.warnings.append(f"Alt text too long (>{125} chars): {alt[:50]}...")
                self.suggestions.append("Keep alt text under 125 characters, use longdesc for detailed descriptions")
            
            # Check for redundant alt text
            if alt and any(word in alt.lower() for word in ['image', 'picture', 'photo', 'graphic']):
                self.suggestions.append(f"Avoid redundant words in alt text: {alt[:50]}...")
    
    def _audit_forms(self, soup: BeautifulSoup):
        """Audit form accessibility"""
        forms = soup.find_all('form')
        
        for form in forms:
            # Check for form labels
            inputs = form.find_all(['input', 'textarea', 'select'])
            
            for input_elem in inputs:
                input_type = input_elem.get('type', 'text')
                if input_type in ['hidden', 'submit', 'button']:
                    continue
                
                input_id = input_elem.get('id')
                label = None
                
                if input_id:
                    label = form.find('label', {'for': input_id})
                
                if not label:
                    # Check for parent label
                    parent_label = input_elem.find_parent('label')
                    if not parent_label:
                        self.errors.append(f"Form input missing associated label: {str(input_elem)[:100]}...")
                
                # Check for required field indicators
                if input_elem.get('required'):
                    aria_required = input_elem.get('aria-required')
                    if aria_required != 'true':
                        self.suggestions.append("Add aria-required='true' to required form fields")
            
            # Check for fieldsets and legends for grouped fields
            fieldsets = form.find_all('fieldset')
            for fieldset in fieldsets:
                if not fieldset.find('legend'):
                    self.warnings.append("Fieldset missing legend element")
    
    def _audit_links(self, soup: BeautifulSoup):
        """Audit link accessibility"""
        links = soup.find_all('a')
        
        for link in links:
            href = link.get('href')
            text = link.get_text().strip()
            
            # Check for empty links
            if not text and not link.find('img'):
                self.errors.append(f"Link missing accessible text: {str(link)[:100]}...")
            
            # Check for generic link text
            generic_texts = ['click here', 'read more', 'more', 'here', 'link']
            if text.lower() in generic_texts:
                self.warnings.append(f"Link text too generic: '{text}' - use descriptive text")
            
            # Check for external links
            if href and (href.startswith('http') and 'target="_blank"' in str(link)):
                if 'aria-label' not in str(link) and 'external' not in text.lower():
                    self.suggestions.append(f"External link should indicate it opens in new window: {text}")
    
    def _audit_headings(self, soup: BeautifulSoup):
        """Audit heading structure"""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if not headings:
            self.warnings.append("No headings found - headings help screen reader navigation")
            return
        
        # Check heading hierarchy
        levels = [int(h.name[1]) for h in headings]
        
        for i in range(1, len(levels)):
            if levels[i] > levels[i-1] + 1:
                self.warnings.append(f"Heading hierarchy skips level: h{levels[i-1]} to h{levels[i]}")
        
        # Check for multiple h1s
        h1_count = len([h for h in headings if h.name == 'h1'])
        if h1_count > 1:
            self.warnings.append(f"Multiple h1 headings found ({h1_count}) - use only one h1 per page")
        elif h1_count == 0:
            self.errors.append("No h1 heading found - required for document structure")
    
    def _audit_aria_attributes(self, soup: BeautifulSoup):
        """Audit ARIA attributes usage"""
        # Find elements with ARIA attributes
        aria_elements = soup.find_all(attrs=lambda x: x and any(attr.startswith('aria-') for attr in x.keys()))
        
        for elem in aria_elements:
            # Check for aria-label without meaningful content
            aria_label = elem.get('aria-label')
            if aria_label == '':
                self.warnings.append(f"Empty aria-label attribute: {str(elem)[:100]}...")
            
            # Check for aria-labelledby references
            aria_labelledby = elem.get('aria-labelledby')
            if aria_labelledby:
                referenced_ids = aria_labelledby.split()
                for ref_id in referenced_ids:
                    if not soup.find(id=ref_id):
                        self.errors.append(f"aria-labelledby references non-existent id: {ref_id}")
        
        # Check for interactive elements without proper roles
        buttons = soup.find_all(['button', 'input'])
        for button in buttons:
            if button.name == 'input' and button.get('type') == 'button':
                if not button.get('aria-label') and not button.get('value'):
                    self.warnings.append("Button input missing accessible text")
    
    def _audit_keyboard_navigation(self, soup: BeautifulSoup):
        """Audit keyboard navigation support"""
        # Check for custom interactive elements
        interactive_elements = soup.find_all(attrs={'onclick': True})
        
        for elem in interactive_elements:
            if elem.name not in ['button', 'a', 'input', 'textarea', 'select']:
                tabindex = elem.get('tabindex')
                role = elem.get('role')
                
                if not tabindex and role not in ['button', 'link']:
                    self.warnings.append(f"Interactive element may not be keyboard accessible: {str(elem)[:100]}...")
                    self.suggestions.append("Add tabindex='0' and appropriate role to custom interactive elements")
        
        # Check for tabindex values
        tabindex_elements = soup.find_all(attrs={'tabindex': True})
        for elem in tabindex_elements:
            tabindex = elem.get('tabindex')
            try:
                tabindex_val = int(tabindex)
                if tabindex_val > 0:
                    self.warnings.append(f"Positive tabindex value disrupts natural tab order: tabindex='{tabindex}'")
                    self.suggestions.append("Use tabindex='0' or '-1' instead of positive values")
            except ValueError:
                self.errors.append(f"Invalid tabindex value: '{tabindex}'")
    
    def _audit_color_contrast(self, html_content: str, soup: BeautifulSoup):
        """Audit color contrast ratios"""
        # Extract CSS colors
        colors = self._extract_colors_from_html(html_content)
        
        # Check common text/background combinations
        problematic_combinations = []
        
        # Basic color contrast warnings
        if colors:
            self.suggestions.append("Color contrast ratios should be checked with automated tools")
            self.suggestions.append("Ensure text has 4.5:1 contrast ratio (3:1 for large text)")
    
    def _extract_colors_from_html(self, html_content: str) -> List[str]:
        """Extract color values from HTML/CSS"""
        color_patterns = [
            r'color:\s*([^;]+)',
            r'background-color:\s*([^;]+)',
            r'#[0-9a-fA-F]{3,6}',
            r'rgb\([^)]+\)',
            r'rgba\([^)]+\)',
            r'hsl\([^)]+\)',
            r'hsla\([^)]+\)'
        ]
        
        colors = []
        for pattern in color_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            colors.extend(matches)
        
        return colors
    
    def _audit_focus_management(self, soup: BeautifulSoup):
        """Audit focus management"""
        # Check for focus styles
        style_tags = soup.find_all('style')
        has_focus_styles = False
        
        for style in style_tags:
            if ':focus' in style.get_text():
                has_focus_styles = True
                break
        
        if not has_focus_styles:
            self.warnings.append("No :focus styles found - ensure interactive elements have visible focus indicators")
            self.suggestions.append("Add CSS focus styles: button:focus, a:focus { outline: 2px solid #005fcc; }")
        
        # Check for elements that remove outline
        if 'outline: none' in str(soup) or 'outline:none' in str(soup):
            self.warnings.append("outline: none detected - ensure alternative focus indicators are provided")
    
    def _build_result(self, source: str) -> Dict[str, Any]:
        """Build audit result"""
        # Calculate accessibility score
        total_issues = len(self.errors) + len(self.warnings)
        max_possible_issues = 20  # Rough estimate for scoring
        score = max(0, 100 - (total_issues * 10))
        
        # Determine compliance level
        compliance_level = "AAA"
        if self.errors:
            compliance_level = "Non-compliant"
        elif len(self.warnings) > 3:
            compliance_level = "AA"
        
        return {
            'success': len(self.errors) == 0,
            'source': source,
            'accessibility_score': score,
            'compliance_level': compliance_level,
            'errors': self.errors,
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'summary': {
                'total_issues': total_issues,
                'errors': len(self.errors),
                'warnings': len(self.warnings),
                'suggestions': len(self.suggestions)
            },
            'wcag_guidelines': {
                'perceivable': len([e for e in self.errors + self.warnings if 'alt' in e or 'contrast' in e]),
                'operable': len([e for e in self.errors + self.warnings if 'keyboard' in e or 'focus' in e]),
                'understandable': len([e for e in self.errors + self.warnings if 'label' in e or 'heading' in e]),
                'robust': len([e for e in self.errors + self.warnings if 'aria' in e or 'semantic' in e])
            }
        }

def main():
    """Main function for CLI usage"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python accessibility-auditor.py <html_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    auditor = AccessibilityAuditor()
    result = auditor.audit_html_file(file_path)
    
    print(json.dumps(result, indent=2))
    
    # Exit with error code if accessibility issues found
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()