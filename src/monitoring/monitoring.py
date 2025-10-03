"""
Production monitoring and logging configuration for Postopus.
"""
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import structlog
from structlog.stdlib import LoggerFactory

# Configure structured logging
def configure_logging(
    log_level: str = "INFO",
    environment: str = "production",
    enable_json_logs: bool = True
) -> None:
    """Configure structured logging for production."""
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure structlog
    if enable_json_logs:
        # JSON logging for production
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Human-readable logging for development
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.dev.ConsoleRenderer(colors=True)
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    # Configure root logger
    logging.basicConfig(
        format="%(message)s" if enable_json_logs else "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=level,
        stream=sys.stdout,
    )


class PerformanceMonitor:
    """Monitor application performance metrics."""
    
    def __init__(self):
        self.logger = structlog.get_logger("performance")
        self.metrics = {}
    
    def record_request(self, endpoint: str, method: str, duration: float, status_code: int):
        """Record API request metrics."""
        self.logger.info(
            "api_request",
            endpoint=endpoint,
            method=method,
            duration_ms=round(duration * 1000, 2),
            status_code=status_code,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Store metrics for aggregation
        key = f"{method}:{endpoint}"
        if key not in self.metrics:
            self.metrics[key] = {"count": 0, "total_duration": 0, "errors": 0}
        
        self.metrics[key]["count"] += 1
        self.metrics[key]["total_duration"] += duration
        if status_code >= 400:
            self.metrics[key]["errors"] += 1
    
    def record_database_query(self, query_type: str, duration: float, success: bool):
        """Record database query metrics."""
        self.logger.info(
            "database_query",
            query_type=query_type,
            duration_ms=round(duration * 1000, 2),
            success=success,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def record_vk_api_call(self, method: str, duration: float, success: bool, region: str = None):
        """Record VK API call metrics."""
        self.logger.info(
            "vk_api_call",
            method=method,
            duration_ms=round(duration * 1000, 2),
            success=success,
            region=region,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summarized metrics."""
        summary = {}
        for endpoint, data in self.metrics.items():
            avg_duration = data["total_duration"] / data["count"] if data["count"] > 0 else 0
            error_rate = data["errors"] / data["count"] if data["count"] > 0 else 0
            
            summary[endpoint] = {
                "total_requests": data["count"],
                "avg_duration_ms": round(avg_duration * 1000, 2),
                "error_rate": round(error_rate * 100, 2),
                "total_errors": data["errors"]
            }
        
        return summary


class HealthMonitor:
    """Monitor system health and dependencies."""
    
    def __init__(self):
        self.logger = structlog.get_logger("health")
        self.last_check = None
        self.health_status = {"status": "unknown", "components": {}}
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        from ..database.postgres import async_session
        
        start_time = datetime.utcnow()
        try:
            if async_session:
                async with async_session() as session:
                    await session.execute("SELECT 1")
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                status = {
                    "status": "healthy",
                    "response_time_ms": round(duration * 1000, 2),
                    "connection": "postgresql",
                    "last_check": start_time.isoformat()
                }
            else:
                status = {
                    "status": "unavailable",
                    "message": "Database connection not configured",
                    "connection": "none",
                    "last_check": start_time.isoformat()
                }
            
            self.logger.info("database_health_check", **status)
            return status
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            status = {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": round(duration * 1000, 2),
                "last_check": start_time.isoformat()
            }
            
            self.logger.error("database_health_check_failed", **status)
            return status
    
    def check_disk_usage(self) -> Dict[str, Any]:
        """Check disk usage."""
        import shutil
        
        try:
            total, used, free = shutil.disk_usage("/")
            usage_percent = (used / total) * 100
            
            status = "healthy"
            if usage_percent > 90:
                status = "critical"
            elif usage_percent > 80:
                status = "warning"
            
            return {
                "status": status,
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "usage_percent": round(usage_percent, 2)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage."""
        import psutil
        
        try:
            memory = psutil.virtual_memory()
            
            status = "healthy"
            if memory.percent > 90:
                status = "critical"
            elif memory.percent > 80:
                status = "warning"
            
            return {
                "status": status,
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "usage_percent": memory.percent
            }
        except ImportError:
            return {
                "status": "unavailable",
                "message": "psutil not installed"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive system health report."""
        self.last_check = datetime.utcnow()
        
        health_report = {
            "timestamp": self.last_check.isoformat(),
            "overall_status": "healthy",
            "components": {}
        }
        
        # Check database
        db_health = await self.check_database_health()
        health_report["components"]["database"] = db_health
        
        # Check disk
        disk_health = self.check_disk_usage()
        health_report["components"]["disk"] = disk_health
        
        # Check memory
        memory_health = self.check_memory_usage()
        health_report["components"]["memory"] = memory_health
        
        # Determine overall status
        component_statuses = [comp.get("status", "unknown") for comp in health_report["components"].values()]
        
        if "critical" in component_statuses:
            health_report["overall_status"] = "critical"
        elif "unhealthy" in component_statuses or "error" in component_statuses:
            health_report["overall_status"] = "unhealthy"
        elif "warning" in component_statuses:
            health_report["overall_status"] = "warning"
        
        self.health_status = health_report
        self.logger.info("comprehensive_health_check", **health_report)
        
        return health_report


# Global monitoring instances
performance_monitor = PerformanceMonitor()
health_monitor = HealthMonitor()

# Setup logging on import
environment = os.getenv("ENVIRONMENT", "development")
log_level = os.getenv("LOG_LEVEL", "INFO")
configure_logging(log_level, environment, environment == "production")