#!/usr/bin/env python3
"""
Database optimization script for Engineering Log Intelligence System.
Optimizes PostgreSQL and OpenSearch queries for better performance.
"""

import os
import psycopg2
import requests
import json
import time
from typing import Dict, List, Any, Tuple
from urllib.parse import urlparse
from requests.auth import HTTPBasicAuth

class DatabaseOptimizer:
    """Database optimization class for PostgreSQL and OpenSearch."""
    
    def __init__(self, database_url: str, elasticsearch_url: str, es_auth: Tuple[str, str] = None):
        self.database_url = database_url
        self.elasticsearch_url = elasticsearch_url
        self.es_auth = es_auth
        self.optimization_results = {}
    
    def optimize_postgresql(self) -> Dict[str, Any]:
        """Optimize PostgreSQL database with indexes and query improvements."""
        print("🔧 Optimizing PostgreSQL database...")
        
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            optimizations = []
            
            # 1. Create optimized indexes
            indexes = [
                {
                    "name": "idx_log_entries_timestamp",
                    "query": "CREATE INDEX IF NOT EXISTS idx_log_entries_timestamp ON log_entries (timestamp DESC)",
                    "description": "Optimize timestamp-based queries"
                },
                {
                    "name": "idx_log_entries_level",
                    "query": "CREATE INDEX IF NOT EXISTS idx_log_entries_level ON log_entries (level)",
                    "description": "Optimize level-based filtering"
                },
                {
                    "name": "idx_log_entries_source",
                    "query": "CREATE INDEX IF NOT EXISTS idx_log_entries_source ON log_entries (source)",
                    "description": "Optimize source-based filtering"
                },
                {
                    "name": "idx_log_entries_service",
                    "query": "CREATE INDEX IF NOT EXISTS idx_log_entries_service ON log_entries (service)",
                    "description": "Optimize service-based filtering"
                },
                {
                    "name": "idx_log_entries_composite",
                    "query": "CREATE INDEX IF NOT EXISTS idx_log_entries_composite ON log_entries (level, source, timestamp DESC)",
                    "description": "Composite index for complex queries"
                },
                {
                    "name": "idx_log_entries_text_search",
                    "query": "CREATE INDEX IF NOT EXISTS idx_log_entries_text_search ON log_entries USING gin (to_tsvector('english', message))",
                    "description": "Full-text search optimization"
                }
            ]
            
            for index in indexes:
                start_time = time.time()
                try:
                    cursor.execute(index["query"])
                    conn.commit()
                    end_time = time.time()
                    
                    optimizations.append({
                        "type": "index",
                        "name": index["name"],
                        "description": index["description"],
                        "status": "created",
                        "execution_time": end_time - start_time
                    })
                    print(f"   ✅ Created index: {index['name']}")
                    
                except Exception as e:
                    optimizations.append({
                        "type": "index",
                        "name": index["name"],
                        "description": index["description"],
                        "status": "failed",
                        "error": str(e)
                    })
                    print(f"   ❌ Failed to create index {index['name']}: {e}")
            
            # 2. Analyze table statistics
            cursor.execute("ANALYZE log_entries")
            conn.commit()
            print("   ✅ Updated table statistics")
            
            # 3. Create optimized views
            views = [
                {
                    "name": "recent_errors",
                    "query": """
                        CREATE OR REPLACE VIEW recent_errors AS
                        SELECT id, timestamp, level, message, source, service, hostname
                        FROM log_entries
                        WHERE level = 'ERROR' AND timestamp > NOW() - INTERVAL '24 hours'
                        ORDER BY timestamp DESC
                    """,
                    "description": "View for recent error logs"
                },
                {
                    "name": "log_summary",
                    "query": """
                        CREATE OR REPLACE VIEW log_summary AS
                        SELECT 
                            DATE(timestamp) as log_date,
                            level,
                            source,
                            COUNT(*) as log_count,
                            COUNT(DISTINCT service) as unique_services,
                            COUNT(DISTINCT hostname) as unique_hosts
                        FROM log_entries
                        GROUP BY DATE(timestamp), level, source
                        ORDER BY log_date DESC, log_count DESC
                    """,
                    "description": "Summary view for log analytics"
                }
            ]
            
            for view in views:
                start_time = time.time()
                try:
                    cursor.execute(view["query"])
                    conn.commit()
                    end_time = time.time()
                    
                    optimizations.append({
                        "type": "view",
                        "name": view["name"],
                        "description": view["description"],
                        "status": "created",
                        "execution_time": end_time - start_time
                    })
                    print(f"   ✅ Created view: {view['name']}")
                    
                except Exception as e:
                    optimizations.append({
                        "type": "view",
                        "name": view["name"],
                        "description": view["description"],
                        "status": "failed",
                        "error": str(e)
                    })
                    print(f"   ❌ Failed to create view {view['name']}: {e}")
            
            # 4. Optimize database settings
            settings = [
                "SET work_mem = '256MB'",
                "SET shared_buffers = '256MB'",
                "SET effective_cache_size = '1GB'",
                "SET random_page_cost = 1.1",
                "SET seq_page_cost = 1.0"
            ]
            
            for setting in settings:
                try:
                    cursor.execute(setting)
                    conn.commit()
                    print(f"   ✅ Applied setting: {setting}")
                except Exception as e:
                    print(f"   ⚠️  Could not apply setting {setting}: {e}")
            
            cursor.close()
            conn.close()
            
            self.optimization_results["postgresql"] = {
                "status": "completed",
                "optimizations": optimizations,
                "total_optimizations": len(optimizations),
                "successful_optimizations": len([o for o in optimizations if o["status"] == "created"])
            }
            
            print(f"   📊 PostgreSQL optimization completed: {len([o for o in optimizations if o['status'] == 'created'])}/{len(optimizations)} successful")
            
        except Exception as e:
            print(f"   ❌ PostgreSQL optimization failed: {e}")
            self.optimization_results["postgresql"] = {
                "status": "failed",
                "error": str(e)
            }
    
    def optimize_elasticsearch(self) -> Dict[str, Any]:
        """Optimize Elasticsearch/OpenSearch configuration."""
        print("🔧 Optimizing Elasticsearch/OpenSearch...")
        
        try:
            optimizations = []
            
            # 1. Create optimized index mapping
            mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "timestamp": {
                            "type": "date",
                            "format": "strict_date_optional_time||epoch_millis"
                        },
                        "level": {
                            "type": "keyword",
                            "fields": {
                                "text": {"type": "text"}
                            }
                        },
                        "message": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            }
                        },
                        "source": {
                            "type": "keyword",
                            "fields": {
                                "text": {"type": "text"}
                            }
                        },
                        "service": {
                            "type": "keyword",
                            "fields": {
                                "text": {"type": "text"}
                            }
                        },
                        "hostname": {
                            "type": "keyword",
                            "fields": {
                                "text": {"type": "text"}
                            }
                        },
                        "user_id": {"type": "keyword"},
                        "session_id": {"type": "keyword"},
                        "request_id": {"type": "keyword"},
                        "correlation_id": {"type": "keyword"}
                    }
                },
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "refresh_interval": "30s",
                    "max_result_window": 10000,
                    "analysis": {
                        "analyzer": {
                            "log_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": ["lowercase", "stop"]
                            }
                        }
                    }
                }
            }
            
            # Update index mapping
            start_time = time.time()
            try:
                response = requests.put(
                    f"{self.elasticsearch_url}/engineering_logs",
                    json=mapping,
                    auth=self.es_auth,
                    timeout=30
                )
                end_time = time.time()
                
                if response.status_code in [200, 201]:
                    optimizations.append({
                        "type": "mapping",
                        "name": "engineering_logs",
                        "description": "Optimized index mapping with proper field types",
                        "status": "created",
                        "execution_time": end_time - start_time
                    })
                    print("   ✅ Updated index mapping")
                else:
                    optimizations.append({
                        "type": "mapping",
                        "name": "engineering_logs",
                        "description": "Optimized index mapping",
                        "status": "failed",
                        "error": f"HTTP {response.status_code}: {response.text}"
                    })
                    print(f"   ❌ Failed to update mapping: {response.status_code}")
                    
            except Exception as e:
                optimizations.append({
                    "type": "mapping",
                    "name": "engineering_logs",
                    "description": "Optimized index mapping",
                    "status": "failed",
                    "error": str(e)
                })
                print(f"   ❌ Failed to update mapping: {e}")
            
            # 2. Create index templates
            template = {
                "index_patterns": ["engineering_logs*"],
                "template": {
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0,
                        "refresh_interval": "30s"
                    },
                    "mappings": mapping["mappings"]
                }
            }
            
            start_time = time.time()
            try:
                response = requests.put(
                    f"{self.elasticsearch_url}/_index_template/engineering_logs_template",
                    json=template,
                    auth=self.es_auth,
                    timeout=30
                )
                end_time = time.time()
                
                if response.status_code in [200, 201]:
                    optimizations.append({
                        "type": "template",
                        "name": "engineering_logs_template",
                        "description": "Index template for consistent mapping",
                        "status": "created",
                        "execution_time": end_time - start_time
                    })
                    print("   ✅ Created index template")
                else:
                    optimizations.append({
                        "type": "template",
                        "name": "engineering_logs_template",
                        "description": "Index template",
                        "status": "failed",
                        "error": f"HTTP {response.status_code}: {response.text}"
                    })
                    print(f"   ❌ Failed to create template: {response.status_code}")
                    
            except Exception as e:
                optimizations.append({
                    "type": "template",
                    "name": "engineering_logs_template",
                    "description": "Index template",
                    "status": "failed",
                    "error": str(e)
                })
                print(f"   ❌ Failed to create template: {e}")
            
            # 3. Optimize index settings
            settings = {
                "index": {
                    "refresh_interval": "30s",
                    "number_of_replicas": 0,
                    "max_result_window": 10000
                }
            }
            
            start_time = time.time()
            try:
                response = requests.put(
                    f"{self.elasticsearch_url}/engineering_logs/_settings",
                    json=settings,
                    auth=self.es_auth,
                    timeout=30
                )
                end_time = time.time()
                
                if response.status_code in [200, 201]:
                    optimizations.append({
                        "type": "settings",
                        "name": "index_settings",
                        "description": "Optimized index settings",
                        "status": "created",
                        "execution_time": end_time - start_time
                    })
                    print("   ✅ Updated index settings")
                else:
                    optimizations.append({
                        "type": "settings",
                        "name": "index_settings",
                        "description": "Index settings",
                        "status": "failed",
                        "error": f"HTTP {response.status_code}: {response.text}"
                    })
                    print(f"   ❌ Failed to update settings: {response.status_code}")
                    
            except Exception as e:
                optimizations.append({
                    "type": "settings",
                    "name": "index_settings",
                    "description": "Index settings",
                    "status": "failed",
                    "error": str(e)
                })
                print(f"   ❌ Failed to update settings: {e}")
            
            self.optimization_results["elasticsearch"] = {
                "status": "completed",
                "optimizations": optimizations,
                "total_optimizations": len(optimizations),
                "successful_optimizations": len([o for o in optimizations if o["status"] == "created"])
            }
            
            print(f"   📊 Elasticsearch optimization completed: {len([o for o in optimizations if o['status'] == 'created'])}/{len(optimizations)} successful")
            
        except Exception as e:
            print(f"   ❌ Elasticsearch optimization failed: {e}")
            self.optimization_results["elasticsearch"] = {
                "status": "failed",
                "error": str(e)
            }
    
    def test_query_performance(self) -> Dict[str, Any]:
        """Test query performance after optimization."""
        print("🧪 Testing query performance...")
        
        performance_results = {
            "postgresql": {},
            "elasticsearch": {}
        }
        
        # Test PostgreSQL queries
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            test_queries = [
                {
                    "name": "count_all_logs",
                    "query": "SELECT COUNT(*) FROM log_entries",
                    "description": "Count all log entries"
                },
                {
                    "name": "recent_logs",
                    "query": "SELECT * FROM log_entries ORDER BY timestamp DESC LIMIT 10",
                    "description": "Get recent logs"
                },
                {
                    "name": "error_logs",
                    "query": "SELECT * FROM log_entries WHERE level = 'ERROR' ORDER BY timestamp DESC LIMIT 10",
                    "description": "Get recent error logs"
                },
                {
                    "name": "log_summary",
                    "query": "SELECT level, COUNT(*) FROM log_entries GROUP BY level",
                    "description": "Log level summary"
                },
                {
                    "name": "text_search",
                    "query": "SELECT * FROM log_entries WHERE to_tsvector('english', message) @@ plainto_tsquery('english', 'error') LIMIT 10",
                    "description": "Full-text search"
                }
            ]
            
            for test in test_queries:
                start_time = time.time()
                try:
                    cursor.execute(test["query"])
                    results = cursor.fetchall()
                    end_time = time.time()
                    
                    performance_results["postgresql"][test["name"]] = {
                        "execution_time": end_time - start_time,
                        "result_count": len(results),
                        "status": "success"
                    }
                    print(f"   ✅ PostgreSQL {test['name']}: {end_time - start_time:.3f}s")
                    
                except Exception as e:
                    performance_results["postgresql"][test["name"]] = {
                        "execution_time": 0,
                        "result_count": 0,
                        "status": "failed",
                        "error": str(e)
                    }
                    print(f"   ❌ PostgreSQL {test['name']}: {e}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"   ❌ PostgreSQL performance test failed: {e}")
            performance_results["postgresql"] = {"error": str(e)}
        
        # Test Elasticsearch queries
        try:
            test_queries = [
                {
                    "name": "match_all",
                    "query": {"match_all": {}},
                    "description": "Match all documents"
                },
                {
                    "name": "level_filter",
                    "query": {"term": {"level": "ERROR"}},
                    "description": "Filter by level"
                },
                {
                    "name": "text_search",
                    "query": {"match": {"message": "error"}},
                    "description": "Text search in message"
                },
                {
                    "name": "range_query",
                    "query": {"range": {"timestamp": {"gte": "now-1d"}}},
                    "description": "Recent logs"
                },
                {
                    "name": "aggregation",
                    "query": {
                        "aggs": {
                            "level_counts": {"terms": {"field": "level"}}
                        }
                    },
                    "description": "Level aggregation"
                }
            ]
            
            for test in test_queries:
                start_time = time.time()
                try:
                    response = requests.post(
                        f"{self.elasticsearch_url}/engineering_logs/_search",
                        json={"query": test["query"], "size": 10},
                        auth=self.es_auth,
                        timeout=10
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        data = response.json()
                        performance_results["elasticsearch"][test["name"]] = {
                            "execution_time": end_time - start_time,
                            "result_count": data.get("hits", {}).get("total", {}).get("value", 0),
                            "status": "success"
                        }
                        print(f"   ✅ Elasticsearch {test['name']}: {end_time - start_time:.3f}s")
                    else:
                        performance_results["elasticsearch"][test["name"]] = {
                            "execution_time": 0,
                            "result_count": 0,
                            "status": "failed",
                            "error": f"HTTP {response.status_code}"
                        }
                        print(f"   ❌ Elasticsearch {test['name']}: HTTP {response.status_code}")
                        
                except Exception as e:
                    performance_results["elasticsearch"][test["name"]] = {
                        "execution_time": 0,
                        "result_count": 0,
                        "status": "failed",
                        "error": str(e)
                    }
                    print(f"   ❌ Elasticsearch {test['name']}: {e}")
            
        except Exception as e:
            print(f"   ❌ Elasticsearch performance test failed: {e}")
            performance_results["elasticsearch"] = {"error": str(e)}
        
        self.optimization_results["performance_test"] = performance_results
        return performance_results
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report."""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "optimization_results": self.optimization_results,
            "summary": {
                "postgresql_optimizations": len(self.optimization_results.get("postgresql", {}).get("optimizations", [])),
                "elasticsearch_optimizations": len(self.optimization_results.get("elasticsearch", {}).get("optimizations", [])),
                "total_optimizations": 0,
                "successful_optimizations": 0
            }
        }
        
        # Calculate summary statistics
        for db_type in ["postgresql", "elasticsearch"]:
            if db_type in self.optimization_results:
                optimizations = self.optimization_results[db_type].get("optimizations", [])
                report["summary"]["total_optimizations"] += len(optimizations)
                report["summary"]["successful_optimizations"] += len([o for o in optimizations if o.get("status") == "created"])
        
        return report


def main():
    """Main function for running database optimization."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database optimization for Engineering Log Intelligence System")
    parser.add_argument("--database-url", required=True, help="PostgreSQL database URL")
    parser.add_argument("--elasticsearch-url", required=True, help="Elasticsearch/OpenSearch URL")
    parser.add_argument("--es-username", help="Elasticsearch username")
    parser.add_argument("--es-password", help="Elasticsearch password")
    parser.add_argument("--output", help="Output file for report")
    
    args = parser.parse_args()
    
    print("🔧 Engineering Log Intelligence System - Database Optimization")
    print("=" * 70)
    print(f"PostgreSQL URL: {args.database_url}")
    print(f"Elasticsearch URL: {args.elasticsearch_url}")
    print()
    
    # Prepare authentication
    es_auth = None
    if args.es_username and args.es_password:
        es_auth = (args.es_username, args.es_password)
    
    # Initialize optimizer
    optimizer = DatabaseOptimizer(args.database_url, args.elasticsearch_url, es_auth)
    
    # Run optimizations
    start_time = time.time()
    
    optimizer.optimize_postgresql()
    print()
    
    optimizer.optimize_elasticsearch()
    print()
    
    optimizer.test_query_performance()
    print()
    
    # Generate report
    report = optimizer.generate_optimization_report()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📊 Optimization report saved to: {args.output}")
    else:
        print("📊 Optimization Report:")
        print(json.dumps(report, indent=2))
    
    total_time = time.time() - start_time
    print(f"⏱️  Total optimization time: {total_time:.2f} seconds")
    print("✅ Database optimization completed!")


if __name__ == "__main__":
    main()
