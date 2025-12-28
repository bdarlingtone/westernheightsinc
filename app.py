#!/usr/bin/env python3
"""
Western Heights Inc. - Main Flask Application
Combines all scripts into one web application
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from datetime import datetime

# Import our custom modules
from contact_handler import ContactFormHandler
from analytics_tracker import WebsiteAnalytics
from content_manager import ContentManager

# Initialize Flask app
app = Flask(__name__, 
           static_folder='static',
           template_folder='templates')

# Initialize our modules
contact_handler = ContactFormHandler()
analytics = WebsiteAnalytics()
content_manager = ContentManager()

# Configuration
app.config['SECRET_KEY'] = 'western-heights-inc-2023-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# ====================
# HELPER FUNCTIONS
# ====================

def get_client_info():
    """Extract client information from request"""
    return {
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'referrer': request.referrer or ''
    }

def track_page_view(page_name):
    """Track page view for analytics"""
    client_info = get_client_info()
    session_id = request.cookies.get('session_id', 'unknown')
    
    analytics.track_page_view({
        'session_id': session_id,
        'page_url': request.url,
        'page_title': page_name,
        'referrer': client_info['referrer'],
        'user_agent': client_info['user_agent'],
        'ip_address': client_info['ip_address'],
        'country': 'Unknown',  # Could add IP geolocation here
        'city': 'Unknown',
        'time_on_page': 0,
        'scroll_depth': 0
    })

# ====================
# WEBSITE ROUTES
# ====================

@app.route('/')
def home():
    """Home page"""
    track_page_view('Home')
    return render_template('index.html')

@app.route('/services/<service_name>')
def service_page(service_name):
    """Dynamic service pages"""
    track_page_view(f'Service: {service_name}')
    
    # Map service names to HTML files
    service_map = {
        'cloud-computing': 'cloud-computing.html',
        'network-systems': 'network-systems.html',
        'digital-transformation': 'digital-transformation.html',
        'managed-it': 'managed-it.html',
        'software-development': 'software-development.html',
        'cybersecurity': 'cybersecurity.html'
    }
    
    html_file = service_map.get(service_name)
    if html_file and os.path.exists(html_file):
        return render_template(html_file)
    else:
        return render_template('404.html'), 404

@app.route('/login')
def login():
    """Login page"""
    track_page_view('Login')
    return render_template('login.html')

@app.route('/signup')
def signup():
    """Signup page"""
    track_page_view('Signup')
    return render_template('signup.html')

# ====================
# API ENDPOINTS
# ====================

@app.route('/api/contact', methods=['POST'])
def api_contact():
    """Handle contact form submissions"""
    try:
        # Get form data
        form_data = {
            'name': request.form.get('name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'company': request.form.get('company', '').strip(),
            'service': request.form.get('service', 'General Inquiry'),
            'message': request.form.get('message', '').strip(),
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        
        # Process form
        result = contact_handler.process_form(form_data)
        
        # Track conversion in analytics
        session_id = request.cookies.get('session_id', 'unknown')
        analytics.track_conversion(
            session_id=session_id,
            conversion_type='contact_form',
            conversion_value=1,
            form_data=form_data
        )
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Contact API error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/analytics/track', methods=['POST'])
def api_analytics_track():
    """Track page views from JavaScript"""
    try:
        data = request.get_json()
        analytics.track_page_view(data)
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Analytics error: {e}")
        return jsonify({'success': False}), 400

@app.route('/api/analytics/update', methods=['POST'])
def api_analytics_update():
    """Update page view data (time on page, scroll depth)"""
    try:
        data = request.get_json()
        # Here you would update the database record
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Analytics update error: {e}")
        return jsonify({'success': False}), 400

@app.route('/api/analytics/conversion', methods=['POST'])
def api_analytics_conversion():
    """Track conversions from JavaScript"""
    try:
        data = request.get_json()
        analytics.track_conversion(
            session_id=data.get('session_id'),
            conversion_type=data.get('conversion_type'),
            conversion_value=data.get('conversion_value', 0),
            form_data=data.get('form_data')
        )
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Conversion tracking error: {e}")
        return jsonify({'success': False}), 400

@app.route('/api/content/services', methods=['GET'])
def api_get_services():
    """Get all services (for dynamic loading)"""
    try:
        services = content_manager.get_all_services()
        return jsonify({'success': True, 'services': services})
    except Exception as e:
        app.logger.error(f"Services API error: {e}")
        return jsonify({'success': False}), 500

@app.route('/api/content/blog', methods=['GET'])
def api_get_blog_posts():
    """Get recent blog posts"""
    try:
        limit = request.args.get('limit', 5, type=int)
        posts = content_manager.get_recent_blog_posts(limit=limit)
        return jsonify({'success': True, 'posts': posts})
    except Exception as e:
        app.logger.error(f"Blog API error: {e}")
        return jsonify({'success': False}), 500

# ====================
# ADMIN ROUTES
# ====================

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard (basic authentication)"""
    # Add authentication here
    return render_template('admin/dashboard.html')

@app.route('/admin/analytics')
def admin_analytics():
    """View analytics data"""
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    report = analytics.get_daily_report(date)
    return jsonify(report)

@app.route('/admin/submissions')
def admin_submissions():
    """View contact form submissions"""
    submissions_dir = 'contact_submissions'
    submissions = []
    
    if os.path.exists(submissions_dir):
        for filename in sorted(os.listdir(submissions_dir), reverse=True):
            if filename.endswith('.json'):
                filepath = os.path.join(submissions_dir, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    submissions.append(data)
    
    return jsonify({'submissions': submissions[:50]})  # Last 50 submissions

# ====================
# STATIC FILES
# ====================

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# ====================
# ERROR HANDLERS
# ====================

@app.errorhandler(404)
def page_not_found(e):
    """404 error page"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500 error page"""
    return render_template('500.html'), 500

# ====================
# STARTUP
# ====================

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("=" * 50)
    print("Western Heights Inc. - Web Application")
    print("=" * 50)
    print("Server running at: http://localhost:5000")
    print("Available routes:")
    print("  /                     - Home page")
    print("  /services/<name>      - Service pages")
    print("  /login                - Login page")
    print("  /signup               - Signup page")
    print("  /api/contact          - Contact form API")
    print("  /api/analytics/*      - Analytics APIs")
    print("  /api/content/*        - Content APIs")
    print("  /admin/*              - Admin pages")
    print("=" * 50)
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
    
    @app.route('/quote')
def quote_page():
    """Get a Quote page"""
    return render_template('quote.html')

@app.route('/api/quote', methods=['POST'])
def api_quote():
    """Handle quote form submissions"""
    try:
        data = request.get_json()
        
        # Process quote request
        quote_data = {
            'type': 'quote_request',
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'ip': request.remote_addr
        }
        
        # Save to file
        quotes_dir = 'quote_requests'
        os.makedirs(quotes_dir, exist_ok=True)
        
        filename = f"{quotes_dir}/quote_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(quote_data, f, indent=2)
        
        # Send email notification
        # (You can reuse the contact_handler email functions)
        
        return jsonify({
            'success': True,
            'message': 'Quote request submitted successfully',
            'quote_id': filename
        })
        
    except Exception as e:
        app.logger.error(f"Quote API error: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500