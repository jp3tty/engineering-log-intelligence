#!/usr/bin/env python3
"""
Advanced Analytics Engine
========================

This module provides advanced analytics capabilities including:
- Statistical analysis and insights
- Trend analysis and forecasting
- Anomaly detection and pattern recognition
- Performance analytics and optimization recommendations

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
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalyticsInsight:
    """Represents an analytics insight."""
    id: str
    type: str  # trend, anomaly, pattern, performance, optimization
    title: str
    description: str
    severity: str  # low, medium, high, critical
    confidence: float  # 0.0 to 1.0
    data: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class TrendAnalysis:
    """Represents trend analysis results."""
    metric: str
    trend_direction: str  # increasing, decreasing, stable, volatile
    trend_strength: float  # 0.0 to 1.0
    change_percentage: float
    confidence_interval: Tuple[float, float]
    forecast_values: List[float]
    forecast_dates: List[datetime]
    seasonal_pattern: Optional[Dict[str, Any]] = None

@dataclass
class AnomalyDetection:
    """Represents anomaly detection results."""
    anomaly_type: str  # point, contextual, collective
    anomaly_score: float  # 0.0 to 1.0
    severity: str  # low, medium, high, critical
    affected_metrics: List[str]
    time_range: Tuple[datetime, datetime]
    explanation: str
    recommendations: List[str]

class AdvancedAnalyticsEngine:
    """Advanced analytics engine for log intelligence."""
    
    def __init__(self):
        self.insights_cache = {}
        self.trend_cache = {}
        self.anomaly_cache = {}
        
    def analyze_log_patterns(self, log_data: List[Dict]) -> List[AnalyticsInsight]:
        """Analyze log patterns and generate insights."""
        insights = []
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(log_data)
            
            # Time-based analysis
            if 'timestamp' in df.columns:
                time_insights = self._analyze_time_patterns(df)
                insights.extend(time_insights)
            
            # Error pattern analysis
            if 'level' in df.columns:
                error_insights = self._analyze_error_patterns(df)
                insights.extend(error_insights)
            
            # Source-based analysis
            if 'source' in df.columns:
                source_insights = self._analyze_source_patterns(df)
                insights.extend(source_insights)
            
            # Performance pattern analysis
            if 'response_time' in df.columns or 'duration' in df.columns:
                perf_insights = self._analyze_performance_patterns(df)
                insights.extend(perf_insights)
            
            logger.info(f"Generated {len(insights)} insights from log analysis")
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing log patterns: {e}")
            return []
    
    def _analyze_time_patterns(self, df: pd.DataFrame) -> List[AnalyticsInsight]:
        """Analyze time-based patterns in logs."""
        insights = []
        
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            # Peak hours analysis
            hourly_counts = df.groupby('hour').size()
            peak_hours = hourly_counts.nlargest(3).index.tolist()
            
            if peak_hours:
                insights.append(AnalyticsInsight(
                    id=f"peak_hours_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    type="pattern",
                    title="Peak Activity Hours Identified",
                    description=f"Highest log activity occurs during hours: {peak_hours}",
                    severity="medium",
                    confidence=0.8,
                    data={
                        "peak_hours": peak_hours,
                        "hourly_distribution": hourly_counts.to_dict()
                    },
                    recommendations=[
                        "Monitor system resources during peak hours",
                        "Consider load balancing during high-traffic periods",
                        "Plan maintenance windows during low-activity hours"
                    ],
                    timestamp=datetime.now()
                ))
            
            # Day-of-week patterns
            daily_counts = df.groupby('day_of_week').size()
            if daily_counts.std() > daily_counts.mean() * 0.2:  # Significant variation
                insights.append(AnalyticsInsight(
                    id=f"weekly_pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    type="pattern",
                    title="Weekly Activity Pattern Detected",
                    description="Significant variation in log activity across days of the week",
                    severity="low",
                    confidence=0.7,
                    data={
                        "daily_distribution": daily_counts.to_dict(),
                        "variation_coefficient": daily_counts.std() / daily_counts.mean()
                    },
                    recommendations=[
                        "Analyze business processes that drive weekly patterns",
                        "Adjust monitoring thresholds based on day-of-week patterns"
                    ],
                    timestamp=datetime.now()
                ))
            
        except Exception as e:
            logger.error(f"Error analyzing time patterns: {e}")
        
        return insights
    
    def _analyze_error_patterns(self, df: pd.DataFrame) -> List[AnalyticsInsight]:
        """Analyze error patterns in logs."""
        insights = []
        
        try:
            # Error level distribution
            error_counts = df['level'].value_counts()
            error_rate = error_counts.get('ERROR', 0) / len(df) if len(df) > 0 else 0
            
            if error_rate > 0.05:  # More than 5% errors
                insights.append(AnalyticsInsight(
                    id=f"high_error_rate_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    type="performance",
                    title="High Error Rate Detected",
                    description=f"Error rate is {error_rate:.2%}, which is above normal threshold",
                    severity="high",
                    confidence=0.9,
                    data={
                        "error_rate": error_rate,
                        "error_distribution": error_counts.to_dict(),
                        "total_logs": len(df)
                    },
                    recommendations=[
                        "Investigate root causes of high error rate",
                        "Review error handling and logging practices",
                        "Consider implementing circuit breakers"
                    ],
                    timestamp=datetime.now()
                ))
            
            # Error trend analysis
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                error_df = df[df['level'] == 'ERROR'].copy()
                if len(error_df) > 10:
                    error_df = error_df.set_index('timestamp').resample('H').size().fillna(0)
                    
                    # Check for increasing error trend
                    if len(error_df) > 24:  # At least 24 hours of data
                        recent_avg = error_df.tail(6).mean()
                        earlier_avg = error_df.head(6).mean()
                        
                        if recent_avg > earlier_avg * 1.5:  # 50% increase
                            insights.append(AnalyticsInsight(
                                id=f"increasing_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                type="trend",
                                title="Increasing Error Trend",
                                description=f"Error rate has increased by {(recent_avg/earlier_avg - 1)*100:.1f}%",
                                severity="high",
                                confidence=0.8,
                                data={
                                    "recent_average": float(recent_avg),
                                    "earlier_average": float(earlier_avg),
                                    "increase_percentage": float((recent_avg/earlier_avg - 1) * 100)
                                },
                                recommendations=[
                                    "Investigate recent changes that may have caused increased errors",
                                    "Monitor error patterns more closely",
                                    "Consider implementing additional error handling"
                                ],
                                timestamp=datetime.now()
                            ))
            
        except Exception as e:
            logger.error(f"Error analyzing error patterns: {e}")
        
        return insights
    
    def _analyze_source_patterns(self, df: pd.DataFrame) -> List[AnalyticsInsight]:
        """Analyze patterns by log source."""
        insights = []
        
        try:
            source_counts = df['source'].value_counts()
            
            # Identify dominant sources
            total_logs = len(df)
            for source, count in source_counts.items():
                percentage = count / total_logs
                
                if percentage > 0.5:  # More than 50% of logs from one source
                    insights.append(AnalyticsInsight(
                        id=f"dominant_source_{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        type="pattern",
                        title=f"Dominant Log Source: {source}",
                        description=f"{source} generates {percentage:.1%} of all logs",
                        severity="medium",
                        confidence=0.9,
                        data={
                            "source": source,
                            "log_count": int(count),
                            "percentage": float(percentage),
                            "total_sources": len(source_counts)
                        },
                        recommendations=[
                            f"Review logging configuration for {source}",
                            "Consider log volume optimization",
                            "Ensure proper log rotation and cleanup"
                        ],
                        timestamp=datetime.now()
                    ))
            
            # Source diversity analysis
            if len(source_counts) < 3 and total_logs > 100:
                insights.append(AnalyticsInsight(
                    id=f"low_source_diversity_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    type="pattern",
                    title="Low Log Source Diversity",
                    description=f"Only {len(source_counts)} sources generating logs",
                    severity="low",
                    confidence=0.8,
                    data={
                        "source_count": len(source_counts),
                        "sources": source_counts.to_dict()
                    },
                    recommendations=[
                        "Consider adding more comprehensive logging across services",
                        "Review if all expected services are properly logging",
                        "Implement distributed logging for better observability"
                    ],
                    timestamp=datetime.now()
                ))
            
        except Exception as e:
            logger.error(f"Error analyzing source patterns: {e}")
        
        return insights
    
    def _analyze_performance_patterns(self, df: pd.DataFrame) -> List[AnalyticsInsight]:
        """Analyze performance patterns in logs."""
        insights = []
        
        try:
            # Check for response time data
            time_column = None
            if 'response_time' in df.columns:
                time_column = 'response_time'
            elif 'duration' in df.columns:
                time_column = 'duration'
            
            if time_column and df[time_column].dtype in ['int64', 'float64']:
                response_times = df[time_column].dropna()
                
                if len(response_times) > 0:
                    mean_rt = response_times.mean()
                    p95_rt = response_times.quantile(0.95)
                    p99_rt = response_times.quantile(0.99)
                    
                    # Performance threshold analysis
                    if p95_rt > 1000:  # More than 1 second
                        insights.append(AnalyticsInsight(
                            id=f"slow_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            type="performance",
                            title="Slow Response Times Detected",
                            description=f"95th percentile response time is {p95_rt:.0f}ms",
                            severity="high",
                            confidence=0.9,
                            data={
                                "mean_response_time": float(mean_rt),
                                "p95_response_time": float(p95_rt),
                                "p99_response_time": float(p99_rt),
                                "sample_count": len(response_times)
                            },
                            recommendations=[
                                "Investigate performance bottlenecks",
                                "Review database query optimization",
                                "Consider caching strategies",
                                "Monitor resource utilization"
                            ],
                            timestamp=datetime.now()
                        ))
                    
                    # Performance trend analysis
                    if 'timestamp' in df.columns and len(response_times) > 50:
                        df_perf = df[df[time_column].notna()].copy()
                        df_perf['timestamp'] = pd.to_datetime(df_perf['timestamp'])
                        df_perf = df_perf.set_index('timestamp')[time_column]
                        
                        # Calculate hourly averages
                        hourly_avg = df_perf.resample('H').mean()
                        
                        if len(hourly_avg) > 12:  # At least 12 hours
                            recent_avg = hourly_avg.tail(3).mean()
                            earlier_avg = hourly_avg.head(3).mean()
                            
                            if recent_avg > earlier_avg * 1.3:  # 30% increase
                                insights.append(AnalyticsInsight(
                                    id=f"performance_degradation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                    type="trend",
                                    title="Performance Degradation Detected",
                                    description=f"Response times have increased by {(recent_avg/earlier_avg - 1)*100:.1f}%",
                                    severity="high",
                                    confidence=0.8,
                                    data={
                                        "recent_average": float(recent_avg),
                                        "earlier_average": float(earlier_avg),
                                        "degradation_percentage": float((recent_avg/earlier_avg - 1) * 100)
                                    },
                                    recommendations=[
                                        "Investigate recent system changes",
                                        "Monitor resource utilization trends",
                                        "Review application performance metrics",
                                        "Consider scaling resources"
                                    ],
                                    timestamp=datetime.now()
                                ))
            
        except Exception as e:
            logger.error(f"Error analyzing performance patterns: {e}")
        
        return insights
    
    def detect_anomalies(self, log_data: List[Dict], method: str = "isolation_forest") -> List[AnomalyDetection]:
        """Detect anomalies in log data using various methods."""
        anomalies = []
        
        try:
            df = pd.DataFrame(log_data)
            
            if method == "isolation_forest":
                anomalies = self._detect_anomalies_isolation_forest(df)
            elif method == "statistical":
                anomalies = self._detect_anomalies_statistical(df)
            elif method == "time_series":
                anomalies = self._detect_anomalies_time_series(df)
            
            logger.info(f"Detected {len(anomalies)} anomalies using {method} method")
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    def _detect_anomalies_isolation_forest(self, df: pd.DataFrame) -> List[AnomalyDetection]:
        """Detect anomalies using Isolation Forest algorithm."""
        anomalies = []
        
        try:
            # Prepare features for anomaly detection
            features = []
            
            # Time-based features
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                features.extend(['hour', 'day_of_week'])
            
            # Categorical features
            if 'level' in df.columns:
                df['level_encoded'] = df['level'].astype('category').cat.codes
                features.append('level_encoded')
            
            if 'source' in df.columns:
                df['source_encoded'] = df['source'].astype('category').cat.codes
                features.append('source_encoded')
            
            # Numerical features
            if 'response_time' in df.columns:
                df['response_time'] = pd.to_numeric(df['response_time'], errors='coerce')
                features.append('response_time')
            
            if len(features) > 0:
                # Prepare data for anomaly detection
                X = df[features].fillna(0)
                
                if len(X) > 10:  # Minimum data points
                    # Standardize features
                    scaler = StandardScaler()
                    X_scaled = scaler.fit_transform(X)
                    
                    # Apply Isolation Forest
                    iso_forest = IsolationForest(contamination=0.1, random_state=42)
                    anomaly_labels = iso_forest.fit_predict(X_scaled)
                    anomaly_scores = iso_forest.decision_function(X_scaled)
                    
                    # Find anomalies
                    anomaly_indices = np.where(anomaly_labels == -1)[0]
                    
                    if len(anomaly_indices) > 0:
                        for idx in anomaly_indices:
                            anomaly_score = abs(anomaly_scores[idx])
                            
                            # Determine severity based on score
                            if anomaly_score > 0.5:
                                severity = "critical"
                            elif anomaly_score > 0.3:
                                severity = "high"
                            elif anomaly_score > 0.1:
                                severity = "medium"
                            else:
                                severity = "low"
                            
                            anomalies.append(AnomalyDetection(
                                anomaly_type="collective",
                                anomaly_score=float(anomaly_score),
                                severity=severity,
                                affected_metrics=features,
                                time_range=(
                                    df.iloc[idx]['timestamp'] if 'timestamp' in df.columns else datetime.now(),
                                    df.iloc[idx]['timestamp'] if 'timestamp' in df.columns else datetime.now()
                                ),
                                explanation=f"Unusual pattern detected with score {anomaly_score:.3f}",
                                recommendations=[
                                    "Investigate the specific log entry for unusual characteristics",
                                    "Review system behavior around this time period",
                                    "Consider if this represents a legitimate anomaly or false positive"
                                ]
                            ))
            
        except Exception as e:
            logger.error(f"Error in isolation forest anomaly detection: {e}")
        
        return anomalies
    
    def _detect_anomalies_statistical(self, df: pd.DataFrame) -> List[AnomalyDetection]:
        """Detect anomalies using statistical methods."""
        anomalies = []
        
        try:
            # Check for numerical columns
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numerical_cols:
                if col in ['response_time', 'duration', 'size']:  # Performance metrics
                    values = df[col].dropna()
                    
                    if len(values) > 10:
                        # Z-score based anomaly detection
                        z_scores = np.abs(stats.zscore(values))
                        threshold = 3  # 3 standard deviations
                        
                        anomaly_indices = np.where(z_scores > threshold)[0]
                        
                        for idx in anomaly_indices:
                            value = values.iloc[idx]
                            mean_val = values.mean()
                            std_val = values.std()
                            z_score = z_scores[idx]
                            
                            anomalies.append(AnomalyDetection(
                                anomaly_type="point",
                                anomaly_score=min(float(z_score / 3), 1.0),
                                severity="high" if z_score > 5 else "medium",
                                affected_metrics=[col],
                                time_range=(datetime.now(), datetime.now()),
                                explanation=f"{col} value {value:.2f} is {z_score:.1f} standard deviations from mean ({mean_val:.2f} ± {std_val:.2f})",
                                recommendations=[
                                    f"Investigate unusual {col} value",
                                    "Review system performance around this time",
                                    "Check for potential system issues or errors"
                                ]
                            ))
            
        except Exception as e:
            logger.error(f"Error in statistical anomaly detection: {e}")
        
        return anomalies
    
    def _detect_anomalies_time_series(self, df: pd.DataFrame) -> List[AnomalyDetection]:
        """Detect anomalies in time series data."""
        anomalies = []
        
        try:
            if 'timestamp' not in df.columns:
                return anomalies
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            
            # Resample to hourly data
            hourly_counts = df.resample('H').size()
            
            if len(hourly_counts) > 24:  # At least 24 hours of data
                # Calculate rolling statistics
                window = min(24, len(hourly_counts) // 4)
                rolling_mean = hourly_counts.rolling(window=window, center=True).mean()
                rolling_std = hourly_counts.rolling(window=window, center=True).std()
                
                # Find anomalies (values outside 2 standard deviations)
                threshold = 2
                anomalies_mask = np.abs(hourly_counts - rolling_mean) > (threshold * rolling_std)
                
                anomaly_times = hourly_counts[anomalies_mask]
                
                for timestamp, count in anomaly_times.items():
                    expected = rolling_mean.loc[timestamp]
                    deviation = (count - expected) / rolling_std.loc[timestamp] if rolling_std.loc[timestamp] > 0 else 0
                    
                    anomalies.append(AnomalyDetection(
                        anomaly_type="contextual",
                        anomaly_score=min(float(abs(deviation) / threshold), 1.0),
                        severity="high" if abs(deviation) > 4 else "medium",
                        affected_metrics=["log_volume"],
                        time_range=(timestamp, timestamp + timedelta(hours=1)),
                        explanation=f"Log volume anomaly: {count} logs (expected ~{expected:.0f}, {deviation:.1f}σ deviation)",
                        recommendations=[
                            "Investigate what caused unusual log volume",
                            "Check for system events or errors during this period",
                            "Review if this represents a legitimate spike or issue"
                        ]
                    ))
            
        except Exception as e:
            logger.error(f"Error in time series anomaly detection: {e}")
        
        return anomalies
    
    def generate_trend_analysis(self, log_data: List[Dict], metric: str = "count") -> Optional[TrendAnalysis]:
        """Generate trend analysis for log data."""
        try:
            df = pd.DataFrame(log_data)
            
            if 'timestamp' not in df.columns:
                return None
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            
            # Aggregate data by hour
            if metric == "count":
                hourly_data = df.resample('H').size()
            elif metric == "error_rate" and 'level' in df.columns:
                hourly_data = (df['level'] == 'ERROR').resample('H').mean()
            elif metric in df.columns:
                hourly_data = df[metric].resample('H').mean()
            else:
                return None
            
            if len(hourly_data) < 12:  # Need at least 12 hours
                return None
            
            # Calculate trend
            x = np.arange(len(hourly_data))
            y = hourly_data.values
            
            # Linear regression for trend
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Determine trend direction
            if slope > 0 and p_value < 0.05:
                trend_direction = "increasing"
            elif slope < 0 and p_value < 0.05:
                trend_direction = "decreasing"
            elif p_value < 0.05:
                trend_direction = "stable"
            else:
                trend_direction = "volatile"
            
            # Calculate trend strength (R-squared)
            trend_strength = r_value ** 2
            
            # Calculate change percentage
            first_value = y[0]
            last_value = y[-1]
            change_percentage = ((last_value - first_value) / first_value) * 100 if first_value > 0 else 0
            
            # Generate forecast (simple linear extrapolation)
            forecast_hours = 24
            forecast_x = np.arange(len(hourly_data), len(hourly_data) + forecast_hours)
            forecast_y = slope * forecast_x + intercept
            forecast_values = forecast_y.tolist()
            
            # Generate forecast dates
            last_timestamp = hourly_data.index[-1]
            forecast_dates = [last_timestamp + timedelta(hours=i+1) for i in range(forecast_hours)]
            
            # Confidence interval (simplified)
            confidence_interval = (
                forecast_y[-1] - 1.96 * std_err * np.sqrt(forecast_hours),
                forecast_y[-1] + 1.96 * std_err * np.sqrt(forecast_hours)
            )
            
            return TrendAnalysis(
                metric=metric,
                trend_direction=trend_direction,
                trend_strength=float(trend_strength),
                change_percentage=float(change_percentage),
                confidence_interval=confidence_interval,
                forecast_values=forecast_values,
                forecast_dates=forecast_dates
            )
            
        except Exception as e:
            logger.error(f"Error generating trend analysis: {e}")
            return None

def handler(request):
    """Vercel function handler for advanced analytics insights."""
    try:
        # Parse request
        if request.method == 'GET':
            # Return analytics capabilities
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
                        'log_pattern_analysis',
                        'anomaly_detection',
                        'trend_analysis',
                        'performance_analytics'
                    ],
                    'methods': {
                        'isolation_forest': 'Machine learning based anomaly detection',
                        'statistical': 'Statistical outlier detection',
                        'time_series': 'Time series anomaly detection'
                    }
                })
            }
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            
            analytics_engine = AdvancedAnalyticsEngine()
            
            # Extract parameters
            log_data = data.get('log_data', [])
            analysis_type = data.get('analysis_type', 'patterns')
            method = data.get('method', 'isolation_forest')
            metric = data.get('metric', 'count')
            
            results = {}
            
            if analysis_type == 'patterns':
                insights = analytics_engine.analyze_log_patterns(log_data)
                results['insights'] = [asdict(insight) for insight in insights]
            
            elif analysis_type == 'anomalies':
                anomalies = analytics_engine.detect_anomalies(log_data, method)
                results['anomalies'] = [asdict(anomaly) for anomaly in anomalies]
            
            elif analysis_type == 'trends':
                trend = analytics_engine.generate_trend_analysis(log_data, metric)
                results['trend'] = asdict(trend) if trend else None
            
            elif analysis_type == 'all':
                insights = analytics_engine.analyze_log_patterns(log_data)
                anomalies = analytics_engine.detect_anomalies(log_data, method)
                trend = analytics_engine.generate_trend_analysis(log_data, metric)
                
                results = {
                    'insights': [asdict(insight) for insight in insights],
                    'anomalies': [asdict(anomaly) for anomaly in anomalies],
                    'trend': asdict(trend) if trend else None
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
        logger.error(f"Error in analytics insights handler: {e}")
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
