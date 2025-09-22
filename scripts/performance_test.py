#!/usr/bin/env python3
"""
Performance testing script for Engineering Log Intelligence System.
Tests Vercel Functions performance, database queries, and system scalability.
"""

import asyncio
import time
import json
import statistics
import requests
import psycopg2
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
import argparse
import sys

class PerformanceTester:
    """Performance testing class for the Engineering Log Intelligence System."""
    
    def __init__(self, base_url: str, database_url: str = None):
        self.base_url = base_url.rstrip('/')
        self.database_url = database_url
        self.results = {
            "health_check": [],
            "logs_search": [],
            "logs_ingestion": [],
            "database_queries": []
        }
    
    def test_health_check(self, num_requests: int = 100) -> List[float]:
        """Test health check endpoint performance."""
        print(f"🔍 Testing health check endpoint ({num_requests} requests)...")
        
        response_times = []
        success_count = 0
        
        for i in range(num_requests):
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}/api/health", timeout=10)
                end_time = time.time()
                
                response_time = end_time - start_time
                response_times.append(response_time)
                
                if response.status_code == 200:
                    success_count += 1
                
                if (i + 1) % 20 == 0:
                    print(f"   Completed {i + 1}/{num_requests} requests")
                    
            except Exception as e:
                print(f"   Request {i + 1} failed: {e}")
                response_times.append(10.0)  # Penalty for failed requests
        
        self.results["health_check"] = response_times
        
        print(f"   ✅ Health check: {success_count}/{num_requests} successful")
        print(f"   📊 Average response time: {statistics.mean(response_times):.3f}s")
        print(f"   📊 95th percentile: {self._percentile(response_times, 95):.3f}s")
        
        return response_times
    
    def test_logs_search(self, num_requests: int = 50) -> List[float]:
        """Test logs search endpoint performance."""
        print(f"🔍 Testing logs search endpoint ({num_requests} requests)...")
        
        response_times = []
        success_count = 0
        
        # Test different search parameters
        search_params = [
            {"level": "INFO"},
            {"source": "application"},
            {"level": "ERROR", "source": "system"},
            {}  # No filters
        ]
        
        for i in range(num_requests):
            params = search_params[i % len(search_params)]
            
            start_time = time.time()
            try:
                response = requests.get(
                    f"{self.base_url}/api/logs",
                    params=params,
                    timeout=10
                )
                end_time = time.time()
                
                response_time = end_time - start_time
                response_times.append(response_time)
                
                if response.status_code == 200:
                    success_count += 1
                
                if (i + 1) % 10 == 0:
                    print(f"   Completed {i + 1}/{num_requests} requests")
                    
            except Exception as e:
                print(f"   Request {i + 1} failed: {e}")
                response_times.append(10.0)
        
        self.results["logs_search"] = response_times
        
        print(f"   ✅ Logs search: {success_count}/{num_requests} successful")
        print(f"   📊 Average response time: {statistics.mean(response_times):.3f}s")
        print(f"   📊 95th percentile: {self._percentile(response_times, 95):.3f}s")
        
        return response_times
    
    def test_logs_ingestion(self, num_requests: int = 50) -> List[float]:
        """Test logs ingestion endpoint performance."""
        print(f"🔍 Testing logs ingestion endpoint ({num_requests} requests)...")
        
        response_times = []
        success_count = 0
        
        # Generate test log data
        test_logs = [
            {
                "level": "INFO",
                "message": f"Test log message {i}",
                "source": "performance_test",
                "service": "test_service",
                "hostname": "test-host"
            }
            for i in range(num_requests)
        ]
        
        for i, log_data in enumerate(test_logs):
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/api/logs",
                    json=log_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                end_time = time.time()
                
                response_time = end_time - start_time
                response_times.append(response_time)
                
                if response.status_code in [200, 201]:
                    success_count += 1
                
                if (i + 1) % 10 == 0:
                    print(f"   Completed {i + 1}/{num_requests} requests")
                    
            except Exception as e:
                print(f"   Request {i + 1} failed: {e}")
                response_times.append(10.0)
        
        self.results["logs_ingestion"] = response_times
        
        print(f"   ✅ Logs ingestion: {success_count}/{num_requests} successful")
        print(f"   📊 Average response time: {statistics.mean(response_times):.3f}s")
        print(f"   📊 95th percentile: {self._percentile(response_times, 95):.3f}s")
        
        return response_times
    
    def test_database_queries(self, num_queries: int = 100) -> List[float]:
        """Test database query performance."""
        if not self.database_url:
            print("   ⚠️  No database URL provided, skipping database tests")
            return []
        
        print(f"🔍 Testing database queries ({num_queries} queries)...")
        
        response_times = []
        success_count = 0
        
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Test different query types
            queries = [
                "SELECT COUNT(*) FROM log_entries",
                "SELECT * FROM log_entries ORDER BY timestamp DESC LIMIT 10",
                "SELECT level, COUNT(*) FROM log_entries GROUP BY level",
                "SELECT source, COUNT(*) FROM log_entries GROUP BY source",
                "SELECT * FROM log_entries WHERE level = 'ERROR' LIMIT 5"
            ]
            
            for i in range(num_queries):
                query = queries[i % len(queries)]
                
                start_time = time.time()
                try:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    response_times.append(response_time)
                    success_count += 1
                    
                    if (i + 1) % 20 == 0:
                        print(f"   Completed {i + 1}/{num_queries} queries")
                        
                except Exception as e:
                    print(f"   Query {i + 1} failed: {e}")
                    response_times.append(1.0)  # Penalty for failed queries
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"   Database connection failed: {e}")
            return []
        
        self.results["database_queries"] = response_times
        
        print(f"   ✅ Database queries: {success_count}/{num_queries} successful")
        print(f"   📊 Average response time: {statistics.mean(response_times):.3f}s")
        print(f"   📊 95th percentile: {self._percentile(response_times, 95):.3f}s")
        
        return response_times
    
    def test_concurrent_load(self, num_requests: int = 100, max_workers: int = 10) -> Dict[str, Any]:
        """Test concurrent load handling."""
        print(f"🚀 Testing concurrent load ({num_requests} requests, {max_workers} workers)...")
        
        def make_request(request_type: str, request_id: int) -> Tuple[str, float, bool]:
            """Make a single request and return results."""
            start_time = time.time()
            success = False
            
            try:
                if request_type == "health":
                    response = requests.get(f"{self.base_url}/api/health", timeout=10)
                elif request_type == "logs":
                    response = requests.get(f"{self.base_url}/api/logs", timeout=10)
                else:
                    response = requests.post(
                        f"{self.base_url}/api/logs",
                        json={"level": "INFO", "message": f"Concurrent test {request_id}", "source": "load_test"},
                        timeout=10
                    )
                
                success = response.status_code in [200, 201]
                
            except Exception as e:
                print(f"   Concurrent request {request_id} failed: {e}")
            
            end_time = time.time()
            return request_type, end_time - start_time, success
        
        # Create requests
        requests_list = []
        for i in range(num_requests):
            request_type = ["health", "logs", "ingestion"][i % 3]
            requests_list.append((request_type, i))
        
        # Execute concurrent requests
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_request = {
                executor.submit(make_request, req_type, req_id): (req_type, req_id)
                for req_type, req_id in requests_list
            }
            
            for future in as_completed(future_to_request):
                req_type, req_id = future_to_request[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"   Future failed for request {req_id}: {e}")
        
        # Analyze results
        response_times = [result[1] for result in results]
        success_count = sum(1 for result in results if result[2])
        
        print(f"   ✅ Concurrent load: {success_count}/{num_requests} successful")
        print(f"   📊 Average response time: {statistics.mean(response_times):.3f}s")
        print(f"   📊 95th percentile: {self._percentile(response_times, 95):.3f}s")
        print(f"   📊 Max response time: {max(response_times):.3f}s")
        
        return {
            "total_requests": num_requests,
            "successful_requests": success_count,
            "success_rate": success_count / num_requests,
            "average_response_time": statistics.mean(response_times),
            "p95_response_time": self._percentile(response_times, 95),
            "max_response_time": max(response_times)
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "summary": {},
            "detailed_results": {}
        }
        
        # Calculate summary statistics
        for test_name, results in self.results.items():
            if results:
                report["summary"][test_name] = {
                    "count": len(results),
                    "average": statistics.mean(results),
                    "median": statistics.median(results),
                    "p95": self._percentile(results, 95),
                    "p99": self._percentile(results, 99),
                    "min": min(results),
                    "max": max(results)
                }
                report["detailed_results"][test_name] = results
        
        return report
    
    def save_report(self, filename: str = None):
        """Save performance report to file."""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Performance report saved to: {filename}")
        return filename


def main():
    """Main function for running performance tests."""
    parser = argparse.ArgumentParser(description="Performance testing for Engineering Log Intelligence System")
    parser.add_argument("--url", required=True, help="Base URL of the application")
    parser.add_argument("--database-url", help="Database URL for testing")
    parser.add_argument("--requests", type=int, default=100, help="Number of requests per test")
    parser.add_argument("--concurrent", type=int, default=50, help="Number of concurrent requests")
    parser.add_argument("--workers", type=int, default=10, help="Number of worker threads")
    parser.add_argument("--output", help="Output file for report")
    
    args = parser.parse_args()
    
    print("🚀 Engineering Log Intelligence System - Performance Testing")
    print("=" * 60)
    print(f"Base URL: {args.url}")
    print(f"Requests per test: {args.requests}")
    print(f"Concurrent requests: {args.concurrent}")
    print()
    
    # Initialize tester
    tester = PerformanceTester(args.url, args.database_url)
    
    # Run tests
    start_time = time.time()
    
    # Individual endpoint tests
    tester.test_health_check(args.requests)
    print()
    
    tester.test_logs_search(args.requests // 2)
    print()
    
    tester.test_logs_ingestion(args.requests // 2)
    print()
    
    tester.test_database_queries(args.requests)
    print()
    
    # Concurrent load test
    concurrent_results = tester.test_concurrent_load(args.concurrent, args.workers)
    print()
    
    # Generate and save report
    report_file = tester.save_report(args.output)
    
    total_time = time.time() - start_time
    print(f"⏱️  Total testing time: {total_time:.2f} seconds")
    print("✅ Performance testing completed!")


if __name__ == "__main__":
    main()
