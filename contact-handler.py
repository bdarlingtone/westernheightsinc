#!/usr/bin/env python3
"""
Western Heights Inc. - Website Analytics Tracker
Tracks website visits, page views, and user interactions
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlparse
import hashlib

class WebsiteAnalytics:
    """Tracks and analyzes website traffic"""
    
    def __init__(self, db_file: str = 'website_analytics.db'):
        self.db_file = db_file
        self.setup_database()
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create page views table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS page_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                page_url TEXT,
                page_title TEXT,
                referrer TEXT,
                user_agent TEXT,
                ip_address TEXT,
                country TEXT,
                city TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                time_on_page INTEGER,
                scroll_depth INTEGER
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                device_type TEXT,
                browser TEXT,
                os TEXT,
                screen_resolution TEXT,
                first_visit TIMESTAMP,
                last_visit TIMESTAMP,
                total_views INTEGER DEFAULT 1,
                duration INTEGER
            )
        ''')
        
        # Create conversions table (form submissions, etc.)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                conversion_type TEXT,
                conversion_value REAL,
                page_url TEXT,
                form_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create daily stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                total_visits INTEGER DEFAULT 0,
                unique_visitors INTEGER DEFAULT 0,
                page_views INTEGER DEFAULT 0,
                bounce_rate REAL DEFAULT 0,
                avg_session_duration INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_session_id(self, ip: str, user_agent: str) -> str:
        """Generate unique session ID"""
        data = f"{ip}{user_agent}{datetime.now().strftime('%Y%m%d')}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def track_page_view(self, data: Dict):
        """Track a page view"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            # Parse URL to get page information
            url = data.get('page_url', '')
            parsed_url = urlparse(url)
            page_path = parsed_url.path
            
            # Insert page view
            cursor.execute('''
                INSERT INTO page_views 
                (session_id, page_url, page_title, referrer, user_agent, ip_address, 
                 country, city, time_on_page, scroll_depth)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('session_id'),
                url,
                data.get('page_title', ''),
                data.get('referrer', ''),
                data.get('user_agent', ''),
                data.get('ip_address', ''),
                data.get('country', 'Unknown'),
                data.get('city', 'Unknown'),
                data.get('time_on_page', 0),
                data.get('scroll_depth', 0)
            ))
            
            # Update or create session
            cursor.execute('''
                INSERT INTO sessions 
                (session_id, user_id, device_type, browser, os, screen_resolution, first_visit, last_visit, total_views)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(session_id) DO UPDATE SET
                last_visit = ?,
                total_views = total_views + 1
            ''', (
                data.get('session_id'),
                data.get('user_id', ''),
                data.get('device_type', ''),
                data.get('browser', ''),
                data.get('os', ''),
                data.get('screen_resolution', ''),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            self.logger.info(f"Page view tracked: {page_path}")
            
        except Exception as e:
            self.logger.error(f"Error tracking page view: {e}")
            conn.rollback()
        
        finally:
            conn.close()
    
    def track_conversion(self, session_id: str, conversion_type: str, 
                        conversion_value: float = 0, form_data: Dict = None):
        """Track a conversion (form submission, etc.)"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO conversions 
                (session_id, conversion_type, conversion_value, form_data)
                VALUES (?, ?, ?, ?)
            ''', (
                session_id,
                conversion_type,
                conversion_value,
                json.dumps(form_data) if form_data else None
            ))
            
            conn.commit()
            self.logger.info(f"Conversion tracked: {conversion_type}")
            
        except Exception as e:
            self.logger.error(f"Error tracking conversion: {e}")
            conn.rollback()
        
        finally:
            conn.close()
    
    def get_daily_report(self, date: Optional[str] = None) -> Dict:
        """Generate daily analytics report"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        report = {
            'date': date,
            'total_visits': 0,
            'unique_visitors': 0,
            'page_views': 0,
            'top_pages': [],
            'referrers': [],
            'conversions': 0
        }
        
        try:
            # Get total visits and unique visitors for the day
            cursor.execute('''
                SELECT COUNT(DISTINCT session_id) as unique_visitors,
                       COUNT(*) as total_visits
                FROM page_views
                WHERE DATE(timestamp) = ?
            ''', (date,))
            
            result = cursor.fetchone()
            if result:
                report['unique_visitors'] = result[0]
                report['total_visits'] = result[1]
            
            # Get total page views
            cursor.execute('''
                SELECT COUNT(*) as page_views
                FROM page_views
                WHERE DATE(timestamp) = ?
            ''', (date,))
            
            result = cursor.fetchone()
            if result:
                report['page_views'] = result[0]
            
            # Get top pages
            cursor.execute('''
                SELECT page_url, COUNT(*) as views
                FROM page_views
                WHERE DATE(timestamp) = ?
                GROUP BY page_url
                ORDER BY views DESC
                LIMIT 10
            ''', (date,))
            
            report['top_pages'] = [{'page': row[0], 'views': row[1]} 
                                  for row in cursor.fetchall()]
            
            # Get top referrers
            cursor.execute('''
                SELECT referrer, COUNT(*) as visits
                FROM page_views
                WHERE DATE(timestamp) = ? AND referrer != ''
                GROUP BY referrer
                ORDER BY visits DESC
                LIMIT 10
            ''', (date,))
            
            report['referrers'] = [{'referrer': row[0], 'visits': row[1]} 
                                  for row in cursor.fetchall()]
            
            # Get conversions
            cursor.execute('''
                SELECT COUNT(*) as conversions
                FROM conversions
                WHERE DATE(timestamp) = ?
            ''', (date,))
            
            result = cursor.fetchone()
            if result:
                report['conversions'] = result[0]
            
        except Exception as e:
            self.logger.error(f"Error generating daily report: {e}")
        
        finally:
            conn.close()
        
        return report
    
    def get_popular_pages(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get most popular pages over specified days"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT page_url, COUNT(*) as views,
                       COUNT(DISTINCT session_id) as unique_visitors
                FROM page_views
                WHERE DATE(timestamp) >= ?
                GROUP BY page_url
                ORDER BY views DESC
                LIMIT ?
            ''', (cutoff_date, limit))
            
            pages = []
            for row in cursor.fetchall():
                pages.append({
                    'page_url': row[0],
                    'total_views': row[1],
                    'unique_visitors': row[2]
                })
            
            return pages
            
        except Exception as e:
            self.logger.error(f"Error getting popular pages: {e}")
            return []
        
        finally:
            conn.close()
    
    def export_data(self, format: str = 'json') -> str:
        """Export analytics data in specified format"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        data = {
            'export_date': datetime.now().isoformat(),
            'summary': self.get_daily_report(),
            'popular_pages': self.get_popular_pages(days=30, limit=20)
        }
        
        if format.lower() == 'json':
            return json.dumps(data, indent=2)
        elif format.lower() == 'csv':
            # Convert to CSV format
            csv_lines = []
            csv_lines.append("Metric,Value")
            csv_lines.append(f"Export Date,{data['export_date']}")
            csv_lines.append(f"Total Visits,{data['summary']['total_visits']}")
            csv_lines.append(f"Unique Visitors,{data['summary']['unique_visitors']}")
            csv_lines.append(f"Page Views,{data['summary']['page_views']}")
            csv_lines.append(f"Conversions,{data['summary']['conversions']}")
            csv_lines.append("")
            csv_lines.append("Popular Pages,Views,Unique Visitors")
            for page in data['popular_pages']:
                csv_lines.append(f"{page['page_url']},{page['total_views']},{page['unique_visitors']}")
            
            return '\n'.join(csv_lines)
        else:
            return str(data)

# Example JavaScript to use with this analytics tracker
JS_TRACKING_CODE = """
<script>
// Western Heights Inc. Analytics Tracker
(function() {
    // Generate session ID
    function generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }
    
    // Get or create session ID
    let sessionId = localStorage.getItem('wh_session_id');
    if (!sessionId) {
        sessionId = generateSessionId();
        localStorage.setItem('wh_session_id', sessionId);
    }
    
    // Track page view
    function trackPageView() {
        const data = {
            session_id: sessionId,
            page_url: window.location.href,
            page_title: document.title,
            referrer: document.referrer,
            user_agent: navigator.userAgent,
            screen_resolution: window.screen.width + 'x' + window.screen.height,
            timestamp: new Date().toISOString()
        };
        
        // Send to analytics endpoint
        fetch('/api/analytics/track', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        }).catch(console.error);
    }
    
    // Track time on page
    let startTime = new Date();
    window.addEventListener('beforeunload', function() {
        const timeOnPage = Math.round((new Date() - startTime) / 1000);
        const scrollDepth = Math.round((window.scrollY / document.body.scrollHeight) * 100);
        
        fetch('/api/analytics/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                time_on_page: timeOnPage,
                scroll_depth: scrollDepth,
                page_url: window.location.href
            })
        }).catch(console.error);
    });
    
    // Track form submissions
    document.addEventListener('submit', function(e) {
        if (e.target.matches('form[data-track-conversion]')) {
            const formData = new FormData(e.target);
            const formObject = {};
            formData.forEach((value, key) => formObject[key] = value);
            
            fetch('/api/analytics/conversion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    conversion_type: e.target.dataset.conversionType || 'form_submission',
                    form_data: formObject,
                    page_url: window.location.href
                })
            }).catch(console.error);
        }
    });
    
    // Initial page view tracking
    trackPageView();
    
    // Track service page clicks
    document.addEventListener('click', function(e) {
        const serviceLink = e.target.closest('a[href*="services"]');
        if (serviceLink) {
            fetch('/api/analytics/event', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    event_type: 'service_click',
                    event_data: {
                        service: serviceLink.textContent,
                        url: serviceLink.href
                    }
                })
            }).catch(console.error);
        }
    });
})();
</script>
"""

if __name__ == "__main__":
    # Example usage
    analytics = WebsiteAnalytics()
    
    # Example: Track a page view
    analytics.track_page_view({
        'session_id': 'test_session_123',
        'page_url': 'https://westernheights.inc/services/cloud-computing',
        'page_title': 'Cloud Computing Services - Western Heights Inc.',
        'referrer': 'https://google.com',
        'user_agent': 'Mozilla/5.0 (Test Browser)',
        'ip_address': '127.0.0.1',
        'country': 'Malawi',
        'city': 'Lilongwe'
    })
    
    # Get today's report
    report = analytics.get_daily_report()
    print("Today's Analytics Report:")
    print(json.dumps(report, indent=2))
    
    # Get popular pages
    popular_pages = analytics.get_popular_pages(days=7)
    print("\nPopular Pages (Last 7 Days):")
    for page in popular_pages:
        print(f"- {page['page_url']}: {page['total_views']} views")
    
    # Export data
    export = analytics.export_data('json')
    print("\nExport data saved to analytics_export.json")
    with open('analytics_export.json', 'w') as f:
        f.write(export)