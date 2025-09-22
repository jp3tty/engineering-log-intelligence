#!/usr/bin/env python3
"""
Simple performance test for Engineering Log Intelligence System.
Tests basic connectivity and response times without authentication.
"""

import requests
import time
import statistics
from typing import List, Dict, Any

def test_endpoint_connectivity(url: str, endpoint: str, expected_status: int = 401) -> Dict[str, Any]:
    """Test endpoint connectivity and response time."""
    full_url = f"{url}{endpoint}"
    
    response_times = []
    success_count = 0
    
    print(f"🔍 Testing {endpoint} connectivity...")
    
    for i in range(10):
        start_time = time.time()
        try:
            response = requests.get(full_url, timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            # Count as success if we get the expected status (401 for protected endpoints)
            if response.status_code == expected_status:
                success_count += 1
            
            print(f"   Request {i+1}: {response.status_code} ({response_time:.3f}s)")
            
        except Exception as e:
            print(f"   Request {i+1} failed: {e}")
            response_times.append(10.0)  # Penalty for failed requests
    
    return {
        "endpoint": endpoint,
        "url": full_url,
        "total_requests": 10,
        "successful_requests": success_count,
        "success_rate": success_count / 10,
        "average_response_time": statistics.mean(response_times),
        "median_response_time": statistics.median(response_times),
        "min_response_time": min(response_times),
        "max_response_time": max(response_times),
        "response_times": response_times
    }

def test_concurrent_requests(url: str, endpoint: str, num_requests: int = 20) -> Dict[str, Any]:
    """Test concurrent request handling."""
    import concurrent.futures
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    print(f"🚀 Testing concurrent requests to {endpoint} ({num_requests} requests)...")
    
    def make_request(request_id: int) -> Dict[str, Any]:
        start_time = time.time()
        try:
            response = requests.get(f"{url}{endpoint}", timeout=10)
            end_time = time.time()
            
            return {
                "request_id": request_id,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 401  # Expected for protected endpoints
            }
        except Exception as e:
            return {
                "request_id": request_id,
                "status_code": 0,
                "response_time": 10.0,
                "success": False,
                "error": str(e)
            }
    
    # Execute concurrent requests
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_request = {
            executor.submit(make_request, i): i 
            for i in range(num_requests)
        }
        
        for future in as_completed(future_to_request):
            result = future.result()
            results.append(result)
    
    # Analyze results
    response_times = [r["response_time"] for r in results]
    success_count = sum(1 for r in results if r["success"])
    
    return {
        "endpoint": endpoint,
        "total_requests": num_requests,
        "successful_requests": success_count,
        "success_rate": success_count / num_requests,
        "average_response_time": statistics.mean(response_times),
        "median_response_time": statistics.median(response_times),
        "p95_response_time": sorted(response_times)[int(0.95 * len(response_times))],
        "min_response_time": min(response_times),
        "max_response_time": max(response_times),
        "results": results
    }

def test_database_connections() -> Dict[str, Any]:
    """Test database connection performance."""
    print("🔍 Testing database connections...")
    
    results = {
        "postgresql": {"status": "not_tested", "reason": "No credentials provided"},
        "elasticsearch": {"status": "not_tested", "reason": "No credentials provided"},
        "kafka": {"status": "not_tested", "reason": "No credentials provided"}
    }
    
    print("   ⚠️  Database connection tests require credentials")
    print("   💡 Run with --database-url, --elasticsearch-url, --kafka-url for full testing")
    
    return results

def generate_performance_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate performance report."""
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_type": "connectivity_and_response_time",
        "summary": {},
        "detailed_results": results
    }
    
    # Calculate summary statistics
    all_response_times = []
    total_requests = 0
    total_successful = 0
    
    for result in results:
        if "response_times" in result:
            all_response_times.extend(result["response_times"])
        if "total_requests" in result:
            total_requests += result["total_requests"]
        if "successful_requests" in result:
            total_successful += result["successful_requests"]
    
    if all_response_times:
        report["summary"] = {
            "total_requests": total_requests,
            "successful_requests": total_successful,
            "success_rate": f"{(total_successful / total_requests * 100):.2f}%" if total_requests > 0 else "0%",
            "average_response_time": f"{statistics.mean(all_response_times):.3f}s",
            "median_response_time": f"{statistics.median(all_response_times):.3f}s",
            "min_response_time": f"{min(all_response_times):.3f}s",
            "max_response_time": f"{max(all_response_times):.3f}s"
        }
    
    return report

def main():
    """Main function for running simple performance tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple performance test for Engineering Log Intelligence System")
    parser.add_argument("--url", required=True, help="Base URL of the application")
    parser.add_argument("--requests", type=int, default=10, help="Number of requests per endpoint")
    parser.add_argument("--concurrent", type=int, default=20, help="Number of concurrent requests")
    parser.add_argument("--output", help="Output file for report")
    
    args = parser.parse_args()
    
    print("🚀 Engineering Log Intelligence System - Simple Performance Test")
    print("=" * 70)
    print(f"Base URL: {args.url}")
    print(f"Requests per endpoint: {args.requests}")
    print(f"Concurrent requests: {args.concurrent}")
    print()
    
    # Test endpoints
    endpoints = [
        "/api/health",
        "/api/logs", 
        "/api/auth",
        "/api/test"
    ]
    
    results = []
    
    # Test individual endpoint connectivity
    for endpoint in endpoints:
        result = test_endpoint_connectivity(args.url, endpoint)
        results.append(result)
        print()
    
    # Test concurrent requests
    concurrent_result = test_concurrent_requests(args.url, "/api/health", args.concurrent)
    results.append(concurrent_result)
    print()
    
    # Test database connections
    db_results = test_database_connections()
    results.append(db_results)
    print()
    
    # Generate report
    report = generate_performance_report(results)
    
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📊 Performance report saved to: {args.output}")
    else:
        print("📊 Performance Report Summary:")
        print(f"   Total Requests: {report['summary'].get('total_requests', 0)}")
        print(f"   Success Rate: {report['summary'].get('success_rate', '0%')}")
        print(f"   Average Response Time: {report['summary'].get('average_response_time', '0.000s')}")
        print(f"   Max Response Time: {report['summary'].get('max_response_time', '0.000s')}")
    
    print("✅ Simple performance testing completed!")

if __name__ == "__main__":
    main()
