#!/usr/bin/env python3
"""
Custom Helm Prometheus Exporter
Exports Helm release information as Prometheus metrics
"""

import time
import subprocess
import json
import logging
from prometheus_client import start_http_server, Gauge, Info, Counter, Enum
from prometheus_client.core import CollectorRegistry, REGISTRY
import threading
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HelmCollector:
    """Custom Prometheus collector for Helm releases"""
    
    def __init__(self, scrape_interval=60):
        self.scrape_interval = scrape_interval
        self.last_scrape = 0
        self.cached_metrics = []
        
        # Define Prometheus metrics
        self.helm_release_info = Info(
            'helm_release_info',
            'Information about Helm releases',
            ['name', 'namespace', 'chart', 'app_version']
        )
        
        self.helm_release_status = Enum(
            'helm_release_status',
            'Status of Helm releases',
            ['name', 'namespace'],
            states=['failed', 'unknown', 'deployed', 'deleted', 'superseded', 'deleting', 'pending-install', 'pending-upgrade', 'pending-rollback']
        )
        
        self.helm_release_revision = Gauge(
            'helm_release_revision',
            'Current revision number of Helm releases',
            ['name', 'namespace', 'chart']
        )
        
        self.helm_release_age_seconds = Gauge(
            'helm_release_age_seconds',
            'Age of Helm release in seconds since last update',
            ['name', 'namespace']
        )
        
        self.helm_scrape_duration_seconds = Gauge(
            'helm_scrape_duration_seconds',
            'Time spent scraping Helm releases'
        )
        
        self.helm_scrape_errors_total = Counter(
            'helm_scrape_errors_total',
            'Total number of errors during Helm scraping'
        )
        
        self.helm_releases_total = Gauge(
            'helm_releases_total',
            'Total number of Helm releases by status',
            ['status']
        )
    
    def get_helm_releases(self):
        """Execute helm list and return parsed JSON data"""
        try:
            logger.info("Executing helm list command")
            result = subprocess.run(
                ['helm', 'list', '-A', '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            
            releases = json.loads(result.stdout)
            logger.info(f"Found {len(releases)} Helm releases")
            return releases
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Helm command failed: {e.stderr}")
            self.helm_scrape_errors_total.inc()
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse helm output: {e}")
            self.helm_scrape_errors_total.inc()
            raise
        except subprocess.TimeoutExpired:
            logger.error("Helm command timed out")
            self.helm_scrape_errors_total.inc()
            raise
    
    def parse_timestamp(self, timestamp_str):
        """Parse Helm timestamp to Unix timestamp"""
        try:
            # Helm timestamps are in format: "2024-01-15 10:30:45.123456789 +0000 UTC"
            from datetime import datetime
            # Remove the nanoseconds and timezone info for parsing
            clean_time = timestamp_str.split('.')[0]
            dt = datetime.strptime(clean_time, "%Y-%m-%d %H:%M:%S")
            return dt.timestamp()
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse timestamp '{timestamp_str}': {e}")
            return time.time()  # Fallback to current time
    
    def update_metrics(self):
        """Update Prometheus metrics with current Helm data"""
        scrape_start = time.time()
        
        try:
            releases = self.get_helm_releases()
            
            # Clear existing metrics
            self.helm_release_info.clear()
            self.helm_release_status._metrics.clear()
            self.helm_release_revision.clear()
            self.helm_release_age_seconds.clear()
            self.helm_releases_total.clear()
            
            # Count releases by status
            status_counts = {}
            
            current_time = time.time()
            
            for release in releases:
                name = release.get('name', 'unknown')
                namespace = release.get('namespace', 'default')
                chart = release.get('chart', 'unknown')
                app_version = release.get('app_version', 'unknown')
                status = release.get('status', 'unknown').lower()
                revision = int(release.get('revision', 0))
                updated = release.get('updated', '')
                
                # Update info metric
                self.helm_release_info.labels(
                    name=name,
                    namespace=namespace,
                    chart=chart,
                    app_version=app_version
                ).info({
                    'status': status,
                    'revision': str(revision),
                    'updated': updated
                })
                
                # Update status metric
                valid_statuses = ['failed', 'unknown', 'deployed', 'deleted', 'superseded', 'deleting', 'pending-install', 'pending-upgrade', 'pending-rollback']
                if status in valid_statuses:
                    self.helm_release_status.labels(
                        name=name,
                        namespace=namespace
                    ).state(status)
                else:
                    # Handle any unexpected status by mapping to 'unknown'
                    logger.warning(f"Unknown Helm status '{status}' for release {name}, mapping to 'unknown'")
                    self.helm_release_status.labels(
                        name=name,
                        namespace=namespace
                    ).state('unknown')
                
                # Update revision metric
                self.helm_release_revision.labels(
                    name=name,
                    namespace=namespace,
                    chart=chart
                ).set(revision)
                
                # Update age metric
                if updated:
                    updated_timestamp = self.parse_timestamp(updated)
                    age_seconds = current_time - updated_timestamp
                    self.helm_release_age_seconds.labels(
                        name=name,
                        namespace=namespace
                    ).set(max(0, age_seconds))
                
                # Count by status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Update total counts by status
            for status, count in status_counts.items():
                self.helm_releases_total.labels(status=status).set(count)
            
            logger.info(f"Updated metrics for {len(releases)} releases")
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
            self.helm_scrape_errors_total.inc()
        finally:
            # Record scrape duration
            scrape_duration = time.time() - scrape_start
            self.helm_scrape_duration_seconds.set(scrape_duration)
            logger.info(f"Scrape completed in {scrape_duration:.2f} seconds")
    
    def start_scraping(self):
        """Start the background scraping thread"""
        def scrape_loop():
            while True:
                try:
                    self.update_metrics()
                    time.sleep(self.scrape_interval)
                except Exception as e:
                    logger.error(f"Scrape loop error: {e}")
                    time.sleep(min(self.scrape_interval, 30))  # Short retry delay
        
        scrape_thread = threading.Thread(target=scrape_loop, daemon=True)
        scrape_thread.start()
        logger.info(f"Started scraping thread with {self.scrape_interval}s interval")

def main():
    parser = argparse.ArgumentParser(description='Helm Prometheus Exporter')
    parser.add_argument('--port', type=int, default=8080, help='Port to serve metrics on')
    parser.add_argument('--interval', type=int, default=60, help='Scrape interval in seconds')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Initialize collector
    collector = HelmCollector(scrape_interval=args.interval)
    
    # Perform initial metrics collection
    logger.info("Performing initial metrics collection...")
    collector.update_metrics()
    
    # Start background scraping
    collector.start_scraping()
    
    # Start Prometheus HTTP server
    logger.info(f"Starting Prometheus metrics server on port {args.port}")
    start_http_server(args.port)
    
    logger.info("Helm Prometheus Exporter is running. Press Ctrl+C to exit.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == '__main__':
    main()