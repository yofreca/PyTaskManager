"""
Modelos de datos para Task Manager Simulator.
"""

from .process import (
    Process,
    ProcessStatus,
    ProcessPriority,
    ProcessMemoryInfo,
    ProcessCPUInfo,
    ProcessIOInfo,
    ProcessNetworkInfo,
)

from .performance import (
    SystemPerformance,
    CPUMetrics,
    MemoryMetrics,
    DiskMetrics,
    NetworkMetrics,
)

from .service import (
    Service,
    ServiceStatus,
    ServiceStartType,
)

from .startup_item import (
    StartupItem,
    StartupLocation,
    StartupImpact,
)

__all__ = [
    # Process
    "Process",
    "ProcessStatus",
    "ProcessPriority",
    "ProcessMemoryInfo",
    "ProcessCPUInfo",
    "ProcessIOInfo",
    "ProcessNetworkInfo",
    # Performance
    "SystemPerformance",
    "CPUMetrics",
    "MemoryMetrics",
    "DiskMetrics",
    "NetworkMetrics",
    # Service
    "Service",
    "ServiceStatus",
    "ServiceStartType",
    # Startup
    "StartupItem",
    "StartupLocation",
    "StartupImpact",
]
