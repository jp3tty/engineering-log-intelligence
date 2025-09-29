#!/usr/bin/env python3
"""
Performance Analytics API
========================

This module provides performance analytics and optimization capabilities including:
- Real-time performance monitoring and metrics
- Performance optimization recommendations
- Capacity planning and forecasting
- Bottleneck analysis and identification
- Performance baseline comparison

Author: Engineering Log Intelligence Team
Date: September 29, 2025
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Represents a performance metric."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    percentile: Optional[float] = None
    baseline: Optional[float] = None
    threshold: Optional[float] = None
    status: str = "normal"  # normal, warning, critical

@dataclass
class PerformanceInsight:
    """Represents a performance insight."""
    id: str
    type: str  # bottleneck, optimization, capacity, trend
    title: str
    description: str
    severity: str  # low, medium, high, critical
    confidence: float  # 0.0 to 1.0
    metrics_affected: List[str]
    recommendations: List[str]
    impact_score: float  # 0.0 to 10.0
    implementation_effort: str  # low, medium, high
    timestamp: datetime

@dataclass
class CapacityForecast:
    """Represents a capacity forecast."""
    resource: str
    current_utilization: float
    forecast_periods: List[str]  # 1w, 1m, 3m, 6m, 1y
    forecast_values: List[float]
    confidence_intervals: List[Tuple[float, float]]
    recommendations: List[str]
    risk_level: str  # low, medium, high, critical

@dataclass
class BottleneckAnalysis:
    """Represents a bottleneck analysis result."""
    bottleneck_type: str  # cpu, memory, disk, network, database
    location: str
    severity: str  # low, medium, high, critical
    impact: float  # 0.0 to 10.0
    current_value: float
    threshold_value: float
    utilization_percentage: float
    recommendations: List[str]
    affected_services: List[str]

class PerformanceAnalytics:
    """Performance analytics and optimization system."""
    
    def __init__(self):
        self.metrics_history = {}
        self.baselines = {}
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time_p95': 1000.0,  # ms
            'response_time_p99': 2000.0,  # ms
            'error_rate': 1.0,  # %
            'throughput': 1000.0  # requests/sec
        }
    
    def analyze_performance_metrics(self, metrics_data: List[Dict]) -> List[PerformanceInsight]:
        """Analyze performance metrics and generate insights."""
        insights = []
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(metrics_data)
            
            if len(df) == 0:
                return insights
            
            # Ensure timestamp column is datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Analyze different metric types
            cpu_insights = self._analyze_cpu_metrics(df)
            memory_insights = self._analyze_memory_metrics(df)
            response_time_insights = self._analyze_response_time_metrics(df)
            throughput_insights = self._analyze_throughput_metrics(df)
            error_rate_insights = self._analyze_error_rate_metrics(df)
            
            # Combine all insights
            insights.extend(cpu_insights)
            insights.extend(memory_insights)
            insights.extend(response_time_insights)
            insights.extend(throughput_insights)
            insights.extend(error_rate_insights)
            
            # Analyze correlations and bottlenecks
            correlation_insights = self._analyze_metric_correlations(df)
            insights.extend(correlation_insights)
            
            logger.info(f"Generated {len(insights)} performance insights")
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing performance metrics: {e}")
            return []
    
    def _analyze_cpu_metrics(self, df: pd.DataFrame) -> List[PerformanceInsight]:
        """Analyze CPU performance metrics."""
        insights = []
        
        try:
            cpu_columns = [col for col in df.columns if 'cpu' in col.lower()]
            
            for cpu_col in cpu_columns:
                if cpu_col in df.columns and df[cpu_col].dtype in ['int64', 'float64']:
                    cpu_data = df[cpu_col].dropna()
                    
                    if len(cpu_data) > 0:
                        avg_cpu = cpu_data.mean()
                        max_cpu = cpu_data.max()
                        p95_cpu = cpu_data.quantile(0.95)
                        
                        # Check for high CPU usage
                        if avg_cpu > self.thresholds['cpu_usage']:
                            insights.append(PerformanceInsight(
                                id=f"cpu_high_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                type="bottleneck",
                                title="High CPU Usage Detected",
                                description=f"Average CPU usage is {avg_cpu:.1f}%, above threshold of {self.thresholds['cpu_usage']}%",
                                severity="high" if avg_cpu > 90 else "medium",
                                confidence=0.9,
                                metrics_affected=[cpu_col],
                                recommendations=[
                                    "Monitor CPU-intensive processes",
                                    "Consider scaling up or adding more CPU cores",
                                    "Optimize application code for better CPU efficiency",
                                    "Review and optimize database queries",
                                    "Consider implementing caching strategies"
                                ],
                                impact_score=8.0,
                                implementation_effort="medium",
                                timestamp=datetime.now()
                            ))
                        
                        # Check for CPU spikes
                        if max_cpu > 95:
                            insights.append(PerformanceInsight(
                                id=f"cpu_spikes_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                type="optimization",
                                title="CPU Spikes Detected",
                                description=f"CPU usage spikes to {max_cpu:.1f}%, indicating potential bottlenecks",
                                severity="critical" if max_cpu > 98 else "high",
                                confidence=0.8,
                                metrics_affected=[cpu_col],
                                recommendations=[
                                    "Investigate what causes CPU spikes",
                                    "Implement CPU usage monitoring and alerting",
                                    "Consider load balancing to distribute CPU load",
                                    "Review application architecture for scalability"
                                ],
                                impact_score=9.0,
                                implementation_effort="high",
                                timestamp=datetime.now()
                            ))
                        
                        # Check for CPU trend
                        if len(cpu_data) > 10:
                            # Calculate trend
                            x = np.arange(len(cpu_data))
                            y = cpu_data.values
                            slope, _, r_value, _, _ = stats.linregress(x, y)
                            
                            if slope > 0.1 and r_value > 0.5:  # Increasing trend
                                insights.append(PerformanceInsight(
                                    id=f"cpu_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                    type="capacity",
                                    title="Increasing CPU Usage Trend",
                                    description=f"CPU usage is trending upward with R² = {r_value**2:.3f}",
                                    severity="medium",
                                    confidence=0.7,
                                    metrics_affected=[cpu_col],
                                    recommendations=[
                                        "Plan for capacity scaling",
                                        "Monitor CPU usage trends closely",
                                        "Consider proactive scaling strategies",
                                        "Review application optimization opportunities"
                                    ],
                                    impact_score=6.0,
                                    implementation_effort="medium",
                                    timestamp=datetime.now()
                                ))
            
        except Exception as e:
            logger.error(f"Error analyzing CPU metrics: {e}")
        
        return insights
    
    def _analyze_memory_metrics(self, df: pd.DataFrame) -> List[PerformanceInsight]:
        """Analyze memory performance metrics."""
        insights = []
        
        try:
            memory_columns = [col for col in df.columns if 'memory' in col.lower() or 'mem' in col.lower()]
            
            for mem_col in memory_columns:
                if mem_col in df.columns and df[mem_col].dtype in ['int64', 'float64']:
                    mem_data = df[mem_col].dropna()
                    
                    if len(mem_data) > 0:
                        avg_memory = mem_data.mean()
                        max_memory = mem_data.max()
                        p95_memory = mem_data.quantile(0.95)
                        
                        # Check for high memory usage
                        if avg_memory > self.thresholds['memory_usage']:
                            insights.append(PerformanceInsight(
                                id=f"memory_high_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                type="bottleneck",
                                title="High Memory Usage Detected",
                                description=f"Average memory usage is {avg_memory:.1f}%, above threshold of {self.thresholds['memory_usage']}%",
                                severity="high" if avg_memory > 90 else "medium",
                                confidence=0.9,
                                metrics_affected=[mem_col],
                                recommendations=[
                                    "Investigate memory leaks in application code",
                                    "Consider increasing available memory",
                                    "Review memory allocation patterns",
                                    "Implement memory usage monitoring",
                                    "Optimize data structures and algorithms"
                                ],
                                impact_score=8.0,
                                implementation_effort="high",
                                timestamp=datetime.now()
                            ))
                        
                        # Check for memory spikes
                        if max_memory > 95:
                            insights.append(PerformanceInsight(
                                id=f"memory_spikes_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                type="optimization",
                                title="Memory Spikes Detected",
                                description=f"Memory usage spikes to {max_memory:.1f}%, indicating potential memory issues",
                                severity="critical" if max_memory > 98 else "high",
                                confidence=0.8,
                                metrics_affected=[mem_col],
                                recommendations=[
                                    "Investigate memory-intensive operations",
                                    "Implement memory profiling and monitoring",
                                    "Consider garbage collection optimization",
                                    "Review memory allocation strategies"
                                ],
                                impact_score=9.0,
                                implementation_effort="high",
                                timestamp=datetime.now()
                            ))
            
        except Exception as e:
            logger.error(f"Error analyzing memory metrics: {e}")
        
        return insights
    
    def _analyze_response_time_metrics(self, df: pd.DataFrame) -> List[PerformanceInsight]:
        """Analyze response time performance metrics."""
        insights = []
        
        try:
            response_columns = [col for col in df.columns if 'response' in col.lower() or 'latency' in col.lower()]
            
            for resp_col in response_columns:
                if resp_col in df.columns and df[resp_col].dtype in ['int64', 'float64']:
                    resp_data = df[resp_col].dropna()
                    
                    if len(resp_data) > 0:
                        avg_resp = resp_data.mean()
                        p95_resp = resp_data.quantile(0.95)
                        p99_resp = resp_data.quantile(0.99)
                        
                        # Check for high response times
                        if p95_resp > self.thresholds['response_time_p95']:
                            insights.append(PerformanceInsight(
                                id=f"response_time_high_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                type="bottleneck",
                                title="High Response Times Detected",
                                description=f"95th percentile response time is {p95_resp:.0f}ms, above threshold of {self.thresholds['response_time_p95']}ms",
                                severity="high" if p95_resp > 2000 else "medium",
                                confidence=0.9,
                                metrics_affected=[resp_col],
                                recommendations=[
                                    "Optimize database queries and indexes",
                                    "Implement caching strategies",
                                    "Review application performance bottlenecks",
                                    "Consider CDN for static content",
                                    "Optimize API endpoints and data serialization"
                                ],
                                impact_score=8.0,
                                implementation_effort="medium",
                                timestamp=datetime.now()
                            ))
                        
                        # Check for response time variance
                        cv = resp_data.std() / resp_data.mean() if resp_data.mean() > 0 else 0
                        if cv > 0.5:  # High coefficient of variation
                            insights.append(PerformanceInsight(
                                id=f"response_time_variance_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                type="optimization",
                                title="High Response Time Variance",
                                description=f"Response time coefficient of variation is {cv:.3f}, indicating inconsistent performance",
                                severity="medium",
                                confidence=0.7,
                                metrics_affected=[resp_col],
                                recommendations=[
                                    "Investigate sources of response time variance",
                                    "Implement consistent caching strategies",
                                    "Review load balancing configuration",
                                    "Optimize slow queries and operations"
                                ],
                                impact_score=6.0,
                                implementation_effort="medium",
                                timestamp=datetime.now()
                            ))
            
        except Exception as e:
            logger.error(f"Error analyzing response time metrics: {e}")
        
        return insights
    
    def _analyze_throughput_metrics(self, df: pd.DataFrame) -> List[PerformanceInsight]:
        """Analyze throughput performance metrics."""
        insights = []
        
        try:
            throughput_columns = [col for col in df.columns if 'throughput' in col.lower() or 'tps' in col.lower()]
            
            for tps_col in throughput_columns:
                if tps_col in df.columns and df[tps_col].dtype in ['int64', 'float64']:
                    tps_data = df[tps_col].dropna()
                    
                    if len(tps_data) > 0:
                        avg_tps = tps_data.mean()
                        min_tps = tps_data.min()
                        
                        # Check for low throughput
                        if avg_tps < self.thresholds['throughput'] * 0.5:  # Below 50% of threshold
                            insights.append(PerformanceInsight(
                                id=f"throughput_low_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                type="bottleneck",
                                title="Low Throughput Detected",
                                description=f"Average throughput is {avg_tps:.0f} requests/sec, below expected performance",
                                severity="medium",
                                confidence=0.8,
                                metrics_affected=[tps_col],
                                recommendations=[
                                    "Investigate application bottlenecks",
                                    "Review database performance and indexing",
                                    "Optimize application code and algorithms",
                                    "Consider horizontal scaling",
                                    "Implement connection pooling"
                                ],
                                impact_score=7.0,
                                implementation_effort="high",
                                timestamp=datetime.now()
                            ))
            
        except Exception as e:
            logger.error(f"Error analyzing throughput metrics: {e}")
        
        return insights
    
    def _analyze_error_rate_metrics(self, df: pd.DataFrame) -> List[PerformanceInsight]:
        """Analyze error rate performance metrics."""
        insights = []
        
        try:
            error_columns = [col for col in df.columns if 'error' in col.lower() or 'failure' in col.lower()]
            
            for error_col in error_columns:
                if error_col in df.columns and df[error_col].dtype in ['int64', 'float64']:
                    error_data = df[error_col].dropna()
                    
                    if len(error_data) > 0:
                        avg_error_rate = error_data.mean()
                        max_error_rate = error_data.max()
                        
                        # Check for high error rates
                        if avg_error_rate > self.thresholds['error_rate']:
                            insights.append(PerformanceInsight(
                                id=f"error_rate_high_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                type="bottleneck",
                                title="High Error Rate Detected",
                                description=f"Average error rate is {avg_error_rate:.2f}%, above threshold of {self.thresholds['error_rate']}%",
                                severity="critical" if avg_error_rate > 5 else "high",
                                confidence=0.9,
                                metrics_affected=[error_col],
                                recommendations=[
                                    "Investigate root causes of errors",
                                    "Implement better error handling and logging",
                                    "Review application stability and reliability",
                                    "Consider implementing circuit breakers",
                                    "Add monitoring and alerting for error rates"
                                ],
                                impact_score=9.0,
                                implementation_effort="medium",
                                timestamp=datetime.now()
                            ))
            
        except Exception as e:
            logger.error(f"Error analyzing error rate metrics: {e}")
        
        return insights
    
    def _analyze_metric_correlations(self, df: pd.DataFrame) -> List[PerformanceInsight]:
        """Analyze correlations between performance metrics."""
        insights = []
        
        try:
            # Select numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) > 1:
                # Calculate correlation matrix
                corr_matrix = df[numeric_cols].corr()
                
                # Find strong correlations
                for i in range(len(numeric_cols)):
                    for j in range(i+1, len(numeric_cols)):
                        col1, col2 = numeric_cols[i], numeric_cols[j]
                        correlation = corr_matrix.loc[col1, col2]
                        
                        if abs(correlation) > 0.8:  # Strong correlation
                            correlation_type = "positive" if correlation > 0 else "negative"
                            
                            insights.append(PerformanceInsight(
                                id=f"correlation_{col1}_{col2}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                type="optimization",
                                title=f"Strong {correlation_type.capitalize()} Correlation Detected",
                                description=f"{col1} and {col2} have a {correlation_type} correlation of {correlation:.3f}",
                                severity="low",
                                confidence=0.8,
                                metrics_affected=[col1, col2],
                                recommendations=[
                                    f"Monitor both {col1} and {col2} together",
                                    f"Optimize {col1} may also improve {col2}",
                                    "Consider joint optimization strategies",
                                    "Review system architecture for coupled metrics"
                                ],
                                impact_score=4.0,
                                implementation_effort="low",
                                timestamp=datetime.now()
                            ))
            
        except Exception as e:
            logger.error(f"Error analyzing metric correlations: {e}")
        
        return insights
    
    def generate_capacity_forecast(self, metrics_data: List[Dict], 
                                 forecast_periods: List[str] = None) -> List[CapacityForecast]:
        """Generate capacity forecasts for different resources."""
        forecasts = []
        
        if forecast_periods is None:
            forecast_periods = ['1w', '1m', '3m', '6m', '1y']
        
        try:
            df = pd.DataFrame(metrics_data)
            
            if len(df) == 0:
                return forecasts
            
            # Ensure timestamp column
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('timestamp')
            
            # Analyze different resource types
            resource_columns = {
                'cpu': [col for col in df.columns if 'cpu' in col.lower()],
                'memory': [col for col in df.columns if 'memory' in col.lower() or 'mem' in col.lower()],
                'disk': [col for col in df.columns if 'disk' in col.lower() or 'storage' in col.lower()],
                'network': [col for col in df.columns if 'network' in col.lower() or 'bandwidth' in col.lower()]
            }
            
            for resource_type, columns in resource_columns.items():
                if columns:
                    # Use first available column for this resource type
                    resource_col = columns[0]
                    
                    if resource_col in df.columns and df[resource_col].dtype in ['int64', 'float64']:
                        resource_data = df[resource_col].dropna()
                        
                        if len(resource_data) > 10:  # Need sufficient data for forecasting
                            forecast = self._generate_single_resource_forecast(
                                resource_type, resource_data, forecast_periods
                            )
                            if forecast:
                                forecasts.append(forecast)
            
            logger.info(f"Generated {len(forecasts)} capacity forecasts")
            return forecasts
            
        except Exception as e:
            logger.error(f"Error generating capacity forecasts: {e}")
            return []
    
    def _generate_single_resource_forecast(self, resource: str, data: pd.Series, 
                                         periods: List[str]) -> Optional[CapacityForecast]:
        """Generate forecast for a single resource."""
        try:
            # Calculate current utilization
            current_utilization = data.iloc[-1] if len(data) > 0 else 0
            
            # Simple linear trend forecasting
            x = np.arange(len(data))
            y = data.values
            
            # Linear regression
            slope, intercept, r_value, _, _ = stats.linregress(x, y)
            
            # Generate forecasts
            forecast_values = []
            confidence_intervals = []
            
            # Map periods to data points
            period_mapping = {
                '1w': len(data) + 7,   # 7 days
                '1m': len(data) + 30,  # 30 days
                '3m': len(data) + 90,  # 90 days
                '6m': len(data) + 180, # 180 days
                '1y': len(data) + 365  # 365 days
            }
            
            for period in periods:
                if period in period_mapping:
                    future_x = period_mapping[period]
                    forecast_value = slope * future_x + intercept
                    forecast_values.append(max(0, min(100, forecast_value)))  # Clamp between 0-100%
                    
                    # Simple confidence interval (assuming normal distribution)
                    std_err = np.sqrt(np.sum((y - (slope * x + intercept))**2) / (len(data) - 2))
                    margin = 1.96 * std_err  # 95% confidence
                    confidence_intervals.append((
                        max(0, forecast_value - margin),
                        min(100, forecast_value + margin)
                    ))
            
            # Generate recommendations
            recommendations = []
            if current_utilization > 80:
                recommendations.append("Current utilization is high, consider immediate scaling")
            
            max_forecast = max(forecast_values) if forecast_values else current_utilization
            if max_forecast > 90:
                recommendations.append("Forecast indicates critical capacity levels")
            elif max_forecast > 80:
                recommendations.append("Plan for capacity expansion in the near term")
            
            if slope > 0.1:
                recommendations.append("Strong upward trend detected, plan proactive scaling")
            
            # Determine risk level
            if max_forecast > 95:
                risk_level = "critical"
            elif max_forecast > 85:
                risk_level = "high"
            elif max_forecast > 75:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return CapacityForecast(
                resource=resource,
                current_utilization=float(current_utilization),
                forecast_periods=periods,
                forecast_values=forecast_values,
                confidence_intervals=confidence_intervals,
                recommendations=recommendations,
                risk_level=risk_level
            )
            
        except Exception as e:
            logger.error(f"Error generating forecast for {resource}: {e}")
            return None
    
    def identify_bottlenecks(self, metrics_data: List[Dict]) -> List[BottleneckAnalysis]:
        """Identify system bottlenecks based on performance metrics."""
        bottlenecks = []
        
        try:
            df = pd.DataFrame(metrics_data)
            
            if len(df) == 0:
                return bottlenecks
            
            # Analyze different bottleneck types
            cpu_bottlenecks = self._identify_cpu_bottlenecks(df)
            memory_bottlenecks = self._identify_memory_bottlenecks(df)
            disk_bottlenecks = self._identify_disk_bottlenecks(df)
            network_bottlenecks = self._identify_network_bottlenecks(df)
            database_bottlenecks = self._identify_database_bottlenecks(df)
            
            bottlenecks.extend(cpu_bottlenecks)
            bottlenecks.extend(memory_bottlenecks)
            bottlenecks.extend(disk_bottlenecks)
            bottlenecks.extend(network_bottlenecks)
            bottlenecks.extend(database_bottlenecks)
            
            logger.info(f"Identified {len(bottlenecks)} bottlenecks")
            return bottlenecks
            
        except Exception as e:
            logger.error(f"Error identifying bottlenecks: {e}")
            return []
    
    def _identify_cpu_bottlenecks(self, df: pd.DataFrame) -> List[BottleneckAnalysis]:
        """Identify CPU bottlenecks."""
        bottlenecks = []
        
        cpu_columns = [col for col in df.columns if 'cpu' in col.lower()]
        
        for cpu_col in cpu_columns:
            if cpu_col in df.columns and df[cpu_col].dtype in ['int64', 'float64']:
                cpu_data = df[cpu_col].dropna()
                
                if len(cpu_data) > 0:
                    avg_cpu = cpu_data.mean()
                    max_cpu = cpu_data.max()
                    utilization_pct = max(avg_cpu, max_cpu)
                    
                    if utilization_pct > 80:
                        severity = "critical" if utilization_pct > 95 else "high" if utilization_pct > 90 else "medium"
                        
                        bottlenecks.append(BottleneckAnalysis(
                            bottleneck_type="cpu",
                            location=cpu_col,
                            severity=severity,
                            impact=utilization_pct / 10.0,  # Scale to 0-10
                            current_value=float(utilization_pct),
                            threshold_value=80.0,
                            utilization_percentage=utilization_pct,
                            recommendations=[
                                "Scale up CPU resources",
                                "Optimize CPU-intensive processes",
                                "Implement load balancing",
                                "Review application code efficiency"
                            ],
                            affected_services=["application", "system"]
                        ))
        
        return bottlenecks
    
    def _identify_memory_bottlenecks(self, df: pd.DataFrame) -> List[BottleneckAnalysis]:
        """Identify memory bottlenecks."""
        bottlenecks = []
        
        memory_columns = [col for col in df.columns if 'memory' in col.lower() or 'mem' in col.lower()]
        
        for mem_col in memory_columns:
            if mem_col in df.columns and df[mem_col].dtype in ['int64', 'float64']:
                mem_data = df[mem_col].dropna()
                
                if len(mem_data) > 0:
                    avg_mem = mem_data.mean()
                    max_mem = mem_data.max()
                    utilization_pct = max(avg_mem, max_mem)
                    
                    if utilization_pct > 85:
                        severity = "critical" if utilization_pct > 95 else "high" if utilization_pct > 90 else "medium"
                        
                        bottlenecks.append(BottleneckAnalysis(
                            bottleneck_type="memory",
                            location=mem_col,
                            severity=severity,
                            impact=utilization_pct / 10.0,
                            current_value=float(utilization_pct),
                            threshold_value=85.0,
                            utilization_percentage=utilization_pct,
                            recommendations=[
                                "Increase available memory",
                                "Investigate memory leaks",
                                "Optimize memory allocation",
                                "Implement memory monitoring"
                            ],
                            affected_services=["application", "database"]
                        ))
        
        return bottlenecks
    
    def _identify_disk_bottlenecks(self, df: pd.DataFrame) -> List[BottleneckAnalysis]:
        """Identify disk bottlenecks."""
        bottlenecks = []
        
        disk_columns = [col for col in df.columns if 'disk' in col.lower() or 'storage' in col.lower()]
        
        for disk_col in disk_columns:
            if disk_col in df.columns and df[disk_col].dtype in ['int64', 'float64']:
                disk_data = df[disk_col].dropna()
                
                if len(disk_data) > 0:
                    avg_disk = disk_data.mean()
                    max_disk = disk_data.max()
                    utilization_pct = max(avg_disk, max_disk)
                    
                    if utilization_pct > 90:
                        severity = "critical" if utilization_pct > 95 else "high"
                        
                        bottlenecks.append(BottleneckAnalysis(
                            bottleneck_type="disk",
                            location=disk_col,
                            severity=severity,
                            impact=utilization_pct / 10.0,
                            current_value=float(utilization_pct),
                            threshold_value=90.0,
                            utilization_percentage=utilization_pct,
                            recommendations=[
                                "Increase disk storage capacity",
                                "Implement disk cleanup procedures",
                                "Move data to external storage",
                                "Optimize data retention policies"
                            ],
                            affected_services=["database", "logs", "storage"]
                        ))
        
        return bottlenecks
    
    def _identify_network_bottlenecks(self, df: pd.DataFrame) -> List[BottleneckAnalysis]:
        """Identify network bottlenecks."""
        bottlenecks = []
        
        network_columns = [col for col in df.columns if 'network' in col.lower() or 'bandwidth' in col.lower()]
        
        for net_col in network_columns:
            if net_col in df.columns and df[net_col].dtype in ['int64', 'float64']:
                net_data = df[net_col].dropna()
                
                if len(net_data) > 0:
                    avg_net = net_data.mean()
                    max_net = net_data.max()
                    utilization_pct = max(avg_net, max_net)
                    
                    if utilization_pct > 80:
                        severity = "critical" if utilization_pct > 95 else "high" if utilization_pct > 90 else "medium"
                        
                        bottlenecks.append(BottleneckAnalysis(
                            bottleneck_type="network",
                            location=net_col,
                            severity=severity,
                            impact=utilization_pct / 10.0,
                            current_value=float(utilization_pct),
                            threshold_value=80.0,
                            utilization_percentage=utilization_pct,
                            recommendations=[
                                "Increase network bandwidth",
                                "Optimize data transfer protocols",
                                "Implement network monitoring",
                                "Consider CDN for content delivery"
                            ],
                            affected_services=["application", "api", "cdn"]
                        ))
        
        return bottlenecks
    
    def _identify_database_bottlenecks(self, df: pd.DataFrame) -> List[BottleneckAnalysis]:
        """Identify database bottlenecks."""
        bottlenecks = []
        
        # Look for database-related metrics
        db_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['db', 'database', 'query', 'connection'])]
        
        for db_col in db_columns:
            if db_col in df.columns and df[db_col].dtype in ['int64', 'float64']:
                db_data = df[db_col].dropna()
                
                if len(db_data) > 0:
                    avg_db = db_data.mean()
                    max_db = db_data.max()
                    
                    # Check for high database usage (assuming percentage or connection count)
                    if 'connection' in db_col.lower():
                        if max_db > 80:  # High connection count
                            bottlenecks.append(BottleneckAnalysis(
                                bottleneck_type="database",
                                location=db_col,
                                severity="high" if max_db > 90 else "medium",
                                impact=min(max_db / 10.0, 10.0),
                                current_value=float(max_db),
                                threshold_value=80.0,
                                utilization_percentage=max_db,
                                recommendations=[
                                    "Implement connection pooling",
                                    "Optimize database queries",
                                    "Review connection management",
                                    "Consider database scaling"
                                ],
                                affected_services=["database", "application"]
                            ))
                    else:
                        # Assume it's a performance metric
                        if avg_db > 1000:  # High query time or similar
                            bottlenecks.append(BottleneckAnalysis(
                                bottleneck_type="database",
                                location=db_col,
                                severity="high" if avg_db > 5000 else "medium",
                                impact=min(avg_db / 1000.0, 10.0),
                                current_value=float(avg_db),
                                threshold_value=1000.0,
                                utilization_percentage=min(avg_db / 10.0, 100.0),
                                recommendations=[
                                    "Optimize database indexes",
                                    "Review query performance",
                                    "Consider database tuning",
                                    "Implement query caching"
                                ],
                                affected_services=["database"]
                            ))
        
        return bottlenecks

def handler(request):
    """Vercel function handler for performance analytics."""
    try:
        if request.method == 'GET':
            # Return performance analytics capabilities
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                },
                'body': json.dumps({
                    'capabilities': [
                        'performance_analysis',
                        'capacity_forecasting',
                        'bottleneck_identification',
                        'optimization_recommendations'
                    ],
                    'supported_metrics': [
                        'cpu_usage',
                        'memory_usage',
                        'disk_usage',
                        'network_usage',
                        'response_time',
                        'throughput',
                        'error_rate'
                    ]
                })
            }
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            
            analytics = PerformanceAnalytics()
            
            # Extract parameters
            metrics_data = data.get('metrics_data', [])
            analysis_type = data.get('analysis_type', 'insights')
            forecast_periods = data.get('forecast_periods', ['1w', '1m', '3m'])
            
            results = {}
            
            if analysis_type == 'insights':
                insights = analytics.analyze_performance_metrics(metrics_data)
                results['insights'] = [asdict(insight) for insight in insights]
            
            elif analysis_type == 'forecast':
                forecasts = analytics.generate_capacity_forecast(metrics_data, forecast_periods)
                results['forecasts'] = [asdict(forecast) for forecast in forecasts]
            
            elif analysis_type == 'bottlenecks':
                bottlenecks = analytics.identify_bottlenecks(metrics_data)
                results['bottlenecks'] = [asdict(bottleneck) for bottleneck in bottlenecks]
            
            elif analysis_type == 'all':
                insights = analytics.analyze_performance_metrics(metrics_data)
                forecasts = analytics.generate_capacity_forecast(metrics_data, forecast_periods)
                bottlenecks = analytics.identify_bottlenecks(metrics_data)
                
                results = {
                    'insights': [asdict(insight) for insight in insights],
                    'forecasts': [asdict(forecast) for forecast in forecasts],
                    'bottlenecks': [asdict(bottleneck) for bottleneck in bottlenecks]
                }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                },
                'body': json.dumps({
                    'success': True,
                    'analysis_type': analysis_type,
                    'results': results,
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        elif request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            }
        
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except Exception as e:
        logger.error(f"Error in performance analytics handler: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
