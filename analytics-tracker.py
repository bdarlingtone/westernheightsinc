#!/usr/bin/env python3
"""
Western Heights Inc. - Simple Content Management System
Manages website content, blog posts, and service pages
"""

import os
import json
import markdown
import yaml
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class ContentManager:
    """Manages website content including pages and blog posts"""
    
    def __init__(self, content_dir: str = 'content'):
        self.content_dir = Path(content_dir)
        self.setup_directories()
        
        # Content types and their templates
        self.templates = {
            'service_page': self.get_service_template(),
            'blog_post': self.get_blog_template(),
            'case_study': self.get_case_study_template()
        }
    
    def setup_directories(self):
        """Create content directory structure"""
        directories = [
            'services',
            'blog',
            'case-studies',
            'pages',
            'uploads/images',
            'uploads/documents',
            'templates'
        ]
        
        for directory in directories:
            (self.content_dir / directory).mkdir(parents=True, exist_ok=True)
        
        # Create default templates if they don't exist
        self.create_default_templates()
    
    def create_default_templates(self):
        """Create default HTML templates"""
        templates_dir = self.content_dir / 'templates'
        
        # Main template
        main_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}} | Western Heights Inc.</title>
    <meta name="description" content="{{description}}">
    <link rel="stylesheet" href="/css/main.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
</head>
<body>
    <!-- Header -->
    {{> header}}
    
    <!-- Main Content -->
    <main class="container">
        {{content}}
    </main>
    
    <!-- Footer -->
    {{> footer}}
    
    <script src="/js/main.js"></script>
</body>
</html>'''
        
        with open(templates_dir / 'main.html', 'w') as f:
            f.write(main_template)
    
    def get_service_template(self) -> Dict:
        """Get service page template structure"""
        return {
            'metadata': {
                'title': '',
                'description': '',
                'keywords': [],
                'service_category': '',
                'icon': 'fas fa-cog',
                'hero_image': '',
                'published': True,
                'featured': False,
                'order': 0
            },
            'content': {
                'hero': {
                    'title': '',
                    'subtitle': '',
                    'cta_button': 'Learn More'
                },
                'overview': {
                    'title': '',
                    'content': '',
                    'image': ''
                },
                'features': [],
                'benefits': [],
                'cta': {
                    'title': '',
                    'content': '',
                    'button_text': 'Get Started'
                }
            }
        }
    
    def get_blog_template(self) -> Dict:
        """Get blog post template structure"""
        return {
            'metadata': {
                'title': '',
                'slug': '',
                'author': '',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'category': 'Technology',
                'tags': [],
                'featured_image': '',
                'excerpt': '',
                'published': True
            },
            'content': {
                'introduction': '',
                'sections': [],
                'conclusion': '',
                'related_posts': []
            }
        }
    
    def create_service_page(self, service_data: Dict) -> str:
        """Create a new service page"""
        # Generate filename from service name
        service_name = service_data['metadata']['title']
        slug = self.slugify(service_name)
        filename = f"{slug}.json"
        filepath = self.content_dir / 'services' / filename
        
        # Merge with template
        service_page = {**self.templates['service_page'], **service_data}
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(service_page, f, indent=2)
        
        # Generate HTML page
        html_content = self.generate_service_html(service_page)
        html_filepath = self.content_dir / 'services' / f"{slug}.html"
        
        with open(html_filepath, 'w') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def generate_service_html(self, service_data: Dict) -> str:
        """Generate HTML from service data"""
        metadata = service_data['metadata']
        content = service_data['content']
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata['title']} | Western Heights Inc.</title>
    <meta name="description" content="{metadata['description']}">
    <meta name="keywords" content="{', '.join(metadata['keywords'])}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --deep-emerald: #0c5c46;
            --rich-gold: #d4af37;
            --soft-white: #f8f9fa;
        }}
        body {{ font-family: 'Inter', sans-serif; }}
        h1, h2, h3 {{ font-family: 'Poppins', sans-serif; color: var(--deep-emerald); }}
        .service-hero {{ 
            background: linear-gradient(135deg, #0c5c46 0%, #1a7d5e 100%);
            color: white;
            padding: 100px 20px;
            text-align: center;
        }}
        .feature-card {{
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 30px;
            margin: 20px 0;
            transition: transform 0.3s ease;
        }}
        .feature-card:hover {{ transform: translateY(-5px); }}
        .cta-button {{
            background: linear-gradient(135deg, #d4af37 0%, #f8c537 100%);
            color: black;
            padding: 12px 30px;
            border-radius: 4px;
            text-decoration: none;
            display: inline-block;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <section class="service-hero">
        <div class="container">
            <i class="{metadata['icon']}" style="font-size: 4rem; margin-bottom: 20px;"></i>
            <h1 style="color: white;">{content['hero']['title'] or metadata['title']}</h1>
            <p style="font-size: 1.2rem;">{content['hero']['subtitle']}</p>
            <a href="#contact" class="cta-button">{content['hero']['cta_button']}</a>
        </div>
    </section>
    
    <div class="container" style="max-width: 1200px; margin: 0 auto; padding: 50px 20px;">
        <section class="overview">
            <h2>{content['overview']['title']}</h2>
            <p>{content['overview']['content']}</p>
        </section>
        
        <section class="features">
            <h2>Key Features</h2>
            <div class="features-grid">
                {self.generate_features_html(content['features'])}
            </div>
        </section>
        
        <section class="benefits">
            <h2>Benefits</h2>
            <ul>
                {''.join([f'<li>{benefit}</li>' for benefit in content['benefits']])}
            </ul>
        </section>
        
        <section class="cta" style="background: #f8f9fa; padding: 50px; text-align: center; border-radius: 10px; margin-top: 50px;">
            <h2>{content['cta']['title']}</h2>
            <p>{content['cta']['content']}</p>
            <a href="#contact" class="cta-button">{content['cta']['button_text']}</a>
        </section>
    </div>
</body>
</html>'''
        
        return html
    
    def generate_features_html(self, features: List[Dict]) -> str:
        """Generate HTML for features list"""
        html = ''
        for feature in features:
            html += f'''
            <div class="feature-card">
                <i class="{feature.get('icon', 'fas fa-check-circle')}" style="color: #0c5c46; font-size: 2rem; margin-bottom: 15px;"></i>
                <h3>{feature.get('title', '')}</h3>
                <p>{feature.get('description', '')}</p>
            </div>
            '''
        return html
    
    def create_blog_post(self, post_data: Dict) -> str:
        """Create a new blog post"""
        # Generate slug from title
        title = post_data['metadata']['title']
        slug = post_data['metadata'].get('slug', self.slugify(title))
        
        # Create markdown file
        filename = f"{slug}.md"
        filepath = self.content_dir / 'blog' / filename
        
        # Format as markdown with frontmatter
        markdown_content = self.format_blog_markdown(post_data)
        
        with open(filepath, 'w') as f:
            f.write(markdown_content)
        
        # Convert to HTML
        html_content = markdown.markdown(markdown_content.split('---', 2)[2])
        html_filepath = self.content_dir / 'blog' / f"{slug}.html"
        
        with open(html_filepath, 'w') as f:
            f.write(self.wrap_blog_html(post_data, html_content))
        
        return str(filepath)
    
    def format_blog_markdown(self, post_data: Dict) -> str:
        """Format blog post as markdown with YAML frontmatter"""
        metadata = post_data['metadata']
        content = post_data['content']
        
        # Create YAML frontmatter
        frontmatter = yaml.dump(metadata, default_flow_style=False)
        
        # Build markdown content
        markdown_content = f'''---
{frontmatter}---
        
# {metadata['title']}
        
*By {metadata['author']} | {metadata['date']}*
        
{content['introduction']}
        
'''
        
        # Add sections
        for section in content['sections']:
            markdown_content += f'''## {section['title']}
            
{section['content']}
            
'''
        
        # Add conclusion
        markdown_content += f'''## Conclusion
        
{content['conclusion']}
        
---
        
**Tags:** {', '.join(metadata['tags'])}
        
*Western Heights Inc. - Elevating Innovation*'''
        
        return markdown_content
    
    def wrap_blog_html(self, post_data: Dict, content_html: str) -> str:
        """Wrap blog content in HTML template"""
        metadata = post_data['metadata']
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata['title']} | Western Heights Inc. Blog</title>
    <meta name="description" content="{metadata['excerpt']}">
    <style>
        :root {{
            --deep-emerald: #0c5c46;
            --rich-gold: #d4af37;
        }}
        body {{ 
            font-family: 'Inter', sans-serif; 
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        .blog-header {{
            background: linear-gradient(135deg, #0c5c46 0%, #1a7d5e 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
            margin-bottom: 40px;
            border-radius: 10px;
        }}
        .blog-content {{ font-size: 1.1rem; }}
        .blog-meta {{
            color: #6c757d;
            font-size: 0.9rem;
            margin-bottom: 30px;
            border-bottom: 1px solid #e9ecef;
            padding-bottom: 20px;
        }}
        .tag {{
            display: inline-block;
            background: #e9ecef;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-right: 5px;
        }}
    </style>
</head>
<body>
    <div class="blog-header">
        <h1 style="color: white; margin: 0;">{metadata['title']}</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">{metadata['excerpt']}</p>
    </div>
    
    <div class="blog-meta">
        <p><strong>Author:</strong> {metadata['author']} | 
           <strong>Date:</strong> {metadata['date']} | 
           <strong>Category:</strong> {metadata['category']}</p>
        <div class="tags">
            {' '.join([f'<span class="tag">{tag}</span>' for tag in metadata['tags']])}
        </div>
    </div>
    
    <div class="blog-content">
        {content_html}
    </div>
    
    <div style="margin-top: 50px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
        <h3>About Western Heights Inc.</h3>
        <p>We provide innovative technology solutions across Africa, helping businesses transform and grow through cutting-edge IT services.</p>
        <p><strong>Contact us:</strong> bdarlingtone@westernheights.inc | +265 884 560 048</p>
    </div>
</body>
</html>'''
    
    def get_all_services(self) -> List[Dict]:
        """Get all service pages"""
        services = []
        services_dir = self.content_dir / 'services'
        
        for filepath in services_dir.glob('*.json'):
            with open(filepath, 'r') as f:
                service_data = json.load(f)
                services.append({
                    'file': filepath.name,
                    'metadata': service_data['metadata'],
                    'content_preview': service_data['content']['overview']['content'][:200] + '...'
                })
        
        # Sort by order
        services.sort(key=lambda x: x['metadata'].get('order', 0))
        return services
    
    def get_recent_blog_posts(self, limit: int = 5) -> List[Dict]:
        """Get recent blog posts"""
        posts = []
        blog_dir = self.content_dir / 'blog'
        
        for filepath in blog_dir.glob('*.md'):
            with open(filepath, 'r') as f:
                content = f.read()
                # Parse frontmatter
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    posts.append({
                        'file': filepath.name,
                        'metadata': metadata,
                        'excerpt': metadata.get('excerpt', '')
                    })
        
        # Sort by date (newest first)
        posts.sort(key=lambda x: x['metadata'].get('date', ''), reverse=True)
        return posts[:limit]
    
    def slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    def generate_sitemap(self) -> str:
        """Generate XML sitemap for SEO"""
        base_url = "https://westernheights.inc"
        urls = []
        
        # Add main pages
        main_pages = ['', 'about', 'services', 'contact', 'careers', 'support']
        for page in main_pages:
            urls.append({
                'loc': f"{base_url}/{page}",
                'lastmod': datetime.now().strftime('%Y-%m-%d'),
                'changefreq': 'weekly',
                'priority': '1.0' if page == '' else '0.8'
            })
        
        # Add service pages
        services = self.get_all_services()
        for service in services:
            slug = service['file'].replace('.json', '')
            urls.append({
                'loc': f"{base_url}/services/{slug}",
                'lastmod': datetime.now().strftime('%Y-%m-%d'),
                'changefreq': 'monthly',
                'priority': '0.7'
            })
        
        # Add blog posts
        posts = self.get_recent_blog_posts(limit=50)
        for post in posts:
            slug = post['file'].replace('.md', '')
            date = post['metadata'].get('date', datetime.now().strftime('%Y-%m-%d'))
            urls.append({
                'loc': f"{base_url}/blog/{slug}",
                'lastmod': date,
                'changefreq': 'monthly',
                'priority': '0.6'
            })
        
        # Generate XML
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'''
        
        for url in urls:
            xml += f'''
    <url>
        <loc>{url['loc']}</loc>
        <lastmod>{url['lastmod']}</lastmod>
        <changefreq>{url['changefreq']}</changefreq>
        <priority>{url['priority']}</priority>
    </url>'''
        
        xml += '\n</urlset>'
        
        # Save sitemap
        sitemap_path = self.content_dir.parent / 'sitemap.xml'
        with open(sitemap_path, 'w') as f:
            f.write(xml)
        
        return str(sitemap_path)

# Example usage
if __name__ == "__main__":
    # Initialize content manager
    cm = ContentManager()
    
    # Example: Create a service page
    cloud_service = {
        'metadata': {
            'title': 'Cloud Computing Solutions',
            'description': 'Secure and scalable cloud infrastructure for African businesses',
            'keywords': ['cloud', 'computing', 'infrastructure', 'africa'],
            'service_category': 'Infrastructure',
            'icon': 'fas fa-cloud',
            'published': True,
            'featured': True,
            'order': 1
        },
        'content': {
            'hero': {
                'title': 'Cloud Computing Solutions',
                'subtitle': 'Transform your business with secure, scalable cloud infrastructure',
                'cta_button': 'Get Cloud Consultation'
            },
            'overview': {
                'title': 'Modern Cloud Infrastructure',
                'content': 'Our cloud computing services provide African businesses with enterprise-grade cloud solutions that are secure, scalable, and cost-effective.',
                'image': ''
            },
            'features': [
                {
                    'title': 'Cloud Migration',
                    'description': 'Seamless migration of applications and data to the cloud',
                    'icon': 'fas fa-server'
                },
                {
                    'title': 'Cloud Security',
                    'description': 'Advanced security measures to protect your cloud assets',
                    'icon': 'fas fa-shield-alt'
                }
            ],
            'benefits': [
                'Reduced IT infrastructure costs',
                'Improved scalability and flexibility',
                'Enhanced security and compliance',
                '24/7 monitoring and support'
            ],
            'cta': {
                'title': 'Ready for the Cloud?',
                'content': 'Contact our cloud experts to discuss your migration strategy',
                'button_text': 'Schedule Consultation'
            }
        }
    }
    
    # Create the service page
    service_file = cm.create_service_page(cloud_service)
    print(f"Service page created: {service_file}")
    
    # Example: Create a blog post
    blog_post = {
        'metadata': {
            'title': 'The Future of Cybersecurity in Africa',
            'slug': 'future-cybersecurity-africa',
            'author': 'Benjamin Darlingtone',
            'date': '2023-11-15',
            'category': 'Cybersecurity',
            'tags': ['security', 'africa', 'technology', 'cybersecurity'],
            'excerpt': 'Exploring the evolving cybersecurity landscape across African businesses',
            'published': True
        },
        'content': {
            'introduction': 'As African businesses continue their digital transformation journey, cybersecurity has become a critical concern. This article explores the current landscape and future trends.',
            'sections': [
                {
                    'title': 'Current Threat Landscape',
                    'content': 'African businesses face unique cybersecurity challenges...'
                },
                {
                    'title': 'Emerging Technologies',
                    'content': 'AI and machine learning are transforming cybersecurity...'
                }
            ],
            'conclusion': 'The future of cybersecurity in Africa requires collaboration, investment, and continuous adaptation to emerging threats.'
        }
    }
    
    # Create the blog post
    blog_file = cm.create_blog_post(blog_post)
    print(f"Blog post created: {blog_file}")
    
    # Get all services
    services = cm.get_all_services()
    print(f"\nTotal services: {len(services)}")
    
    # Get recent blog posts
    posts = cm.get_recent_blog_posts()
    print(f"Recent blog posts: {len(posts)}")
    
    # Generate sitemap
    sitemap = cm.generate_sitemap()
    print(f"Sitemap generated: {sitemap}")
    
    print("\nContent management system ready!")