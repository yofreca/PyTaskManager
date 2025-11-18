"""
Gestor de procesos del sistema usando psutil.
"""
import psutil
import logging
from typing import List, Optional, Dict
from datetime import datetime

from ..models.process import (
    Process,
    ProcessStatus,
    ProcessPriority,
    ProcessCPUInfo,
    ProcessMemoryInfo,
    ProcessIOInfo,
    ProcessNetworkInfo,
)


logger = logging.getLogger(__name__)


class ProcessManager:
    """
    Gestor de procesos del sistema.

    Proporciona funcionalidades para:
    - Obtener lista de procesos activos
    - Obtener información detallada de procesos
    - Gestionar procesos (terminar, suspender, reanudar)
    - Cambiar prioridad de procesos
    """

    def __init__(self):
        """Inicializa el gestor de procesos."""
        self._process_cache: Dict[int, Process] = {}
        logger.info("ProcessManager inicializado")

    def get_all_processes(self, include_system: bool = True) -> List[Process]:
        """
        Obtiene la lista de todos los procesos activos.

        Args:
            include_system: Si True, incluye procesos del sistema

        Returns:
            Lista de objetos Process
        """
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'status', 'username']):
            try:
                process = self._create_process_from_psutil(proc)

                # Filtrar procesos del sistema si se solicita
                if not include_system and self._is_system_process(process):
                    continue

                processes.append(process)
                self._process_cache[process.pid] = process

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                logger.debug(f"Error obteniendo proceso {proc.pid}: {e}")
                continue

        logger.debug(f"Obtenidos {len(processes)} procesos")
        return processes

    def get_process_by_pid(self, pid: int, detailed: bool = False) -> Optional[Process]:
        """
        Obtiene un proceso específico por su PID.

        Args:
            pid: Process ID
            detailed: Si True, obtiene información detallada

        Returns:
            Objeto Process o None si no existe
        """
        try:
            proc = psutil.Process(pid)
            process = self._create_process_from_psutil(proc, detailed=detailed)
            self._process_cache[pid] = process
            return process

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error obteniendo proceso {pid}: {e}")
            return None

    def kill_process(self, pid: int, force: bool = False) -> bool:
        """
        Termina un proceso.

        Args:
            pid: Process ID a terminar
            force: Si True, usa SIGKILL, sino SIGTERM

        Returns:
            True si se terminó exitosamente, False en caso contrario
        """
        try:
            proc = psutil.Process(pid)

            if force:
                proc.kill()  # SIGKILL
            else:
                proc.terminate()  # SIGTERM

            logger.info(f"Proceso {pid} terminado {'(force)' if force else ''}")
            return True

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error terminando proceso {pid}: {e}")
            return False

    def suspend_process(self, pid: int) -> bool:
        """
        Suspende un proceso.

        Args:
            pid: Process ID a suspender

        Returns:
            True si se suspendió exitosamente
        """
        try:
            proc = psutil.Process(pid)
            proc.suspend()
            logger.info(f"Proceso {pid} suspendido")
            return True

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error suspendiendo proceso {pid}: {e}")
            return False

    def resume_process(self, pid: int) -> bool:
        """
        Reanuda un proceso suspendido.

        Args:
            pid: Process ID a reanudar

        Returns:
            True si se reanudó exitosamente
        """
        try:
            proc = psutil.Process(pid)
            proc.resume()
            logger.info(f"Proceso {pid} reanudado")
            return True

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error reanudando proceso {pid}: {e}")
            return False

    def set_process_priority(self, pid: int, priority: ProcessPriority) -> bool:
        """
        Establece la prioridad de un proceso.

        Args:
            pid: Process ID
            priority: Nueva prioridad

        Returns:
            True si se cambió exitosamente
        """
        try:
            proc = psutil.Process(pid)
            proc.nice(priority.value)
            logger.info(f"Prioridad de proceso {pid} cambiada a {priority.name}")
            return True

        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError) as e:
            logger.error(f"Error cambiando prioridad de proceso {pid}: {e}")
            return False

    def _create_process_from_psutil(self, proc: psutil.Process, detailed: bool = False) -> Process:
        """
        Crea un objeto Process a partir de un proceso de psutil.

        Args:
            proc: Objeto psutil.Process
            detailed: Si True, obtiene información detallada (más costoso)

        Returns:
            Objeto Process
        """
        try:
            # Información básica
            info = proc.as_dict(attrs=[
                'pid', 'name', 'status', 'username', 'create_time',
                'cpu_percent', 'memory_info', 'memory_percent',
                'num_threads'
            ])

            # Crear objeto Process
            process = Process(
                pid=info['pid'],
                name=info['name'],
                status=self._map_status(info['status']),
                username=info.get('username'),
                create_time=datetime.fromtimestamp(info['create_time']) if info.get('create_time') else None
            )

            # CPU info
            process.cpu_info = ProcessCPUInfo(
                percent=info.get('cpu_percent', 0.0) or 0.0,
                num_threads=info.get('num_threads', 0)
            )

            # Memory info
            mem_info = info.get('memory_info')
            if mem_info:
                process.memory_info = ProcessMemoryInfo(
                    rss=mem_info.rss,
                    vms=mem_info.vms,
                    percent=info.get('memory_percent', 0.0) or 0.0
                )

            # Información detallada (opcional)
            if detailed:
                try:
                    # CPU times
                    cpu_times = proc.cpu_times()
                    process.cpu_info.user_time = cpu_times.user
                    process.cpu_info.system_time = cpu_times.system

                    # I/O counters
                    io_counters = proc.io_counters()
                    process.io_info = ProcessIOInfo(
                        read_count=io_counters.read_count,
                        write_count=io_counters.write_count,
                        read_bytes=io_counters.read_bytes,
                        write_bytes=io_counters.write_bytes
                    )

                    # Detalles del proceso
                    process.exe = proc.exe()
                    process.cmdline = proc.cmdline()
                    process.cwd = proc.cwd()
                    process.parent_pid = proc.ppid()

                    # Número de handles (Windows)
                    if hasattr(proc, 'num_handles'):
                        process.num_handles = proc.num_handles()

                    # Conexiones de red
                    connections = proc.connections()
                    process.network_info = ProcessNetworkInfo(
                        connections=len(connections)
                    )

                except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
                    pass  # Información no disponible

            return process

        except Exception as e:
            logger.error(f"Error creando Process desde psutil: {e}")
            # Retornar objeto básico
            return Process(
                pid=proc.pid,
                name=proc.name() if hasattr(proc, 'name') else "Unknown"
            )

    def _map_status(self, status_str: str) -> ProcessStatus:
        """
        Mapea el estado de psutil a ProcessStatus.

        Args:
            status_str: String de estado de psutil

        Returns:
            ProcessStatus correspondiente
        """
        status_map = {
            psutil.STATUS_RUNNING: ProcessStatus.RUNNING,
            psutil.STATUS_SLEEPING: ProcessStatus.SLEEPING,
            psutil.STATUS_DISK_SLEEP: ProcessStatus.DISK_SLEEP,
            psutil.STATUS_STOPPED: ProcessStatus.STOPPED,
            psutil.STATUS_ZOMBIE: ProcessStatus.ZOMBIE,
            psutil.STATUS_DEAD: ProcessStatus.DEAD,
            psutil.STATUS_WAKING: ProcessStatus.WAKING,
            psutil.STATUS_IDLE: ProcessStatus.IDLE,
            psutil.STATUS_LOCKED: ProcessStatus.LOCKED,
            psutil.STATUS_WAITING: ProcessStatus.WAITING,
        }

        return status_map.get(status_str, ProcessStatus.RUNNING)

    def _is_system_process(self, process: Process) -> bool:
        """
        Determina si un proceso es del sistema.

        Args:
            process: Objeto Process

        Returns:
            True si es un proceso del sistema
        """
        # Criterios simples para identificar procesos del sistema
        if process.pid < 10:
            return True

        if process.username in ['SYSTEM', 'NT AUTHORITY\\SYSTEM', 'root']:
            return True

        return False

    def get_process_tree(self, pid: int) -> List[Process]:
        """
        Obtiene un proceso y todos sus hijos (árbol de procesos).

        Args:
            pid: Process ID raíz

        Returns:
            Lista de procesos en el árbol
        """
        try:
            proc = psutil.Process(pid)
            children = proc.children(recursive=True)

            tree = [self._create_process_from_psutil(proc)]
            for child in children:
                try:
                    tree.append(self._create_process_from_psutil(child))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return tree

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error obteniendo árbol de proceso {pid}: {e}")
            return []

    def kill_process_tree(self, pid: int) -> bool:
        """
        Termina un proceso y todos sus hijos.

        Args:
            pid: Process ID raíz

        Returns:
            True si se terminó exitosamente
        """
        try:
            proc = psutil.Process(pid)
            children = proc.children(recursive=True)

            # Terminar hijos primero
            for child in children:
                try:
                    child.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Terminar proceso principal
            proc.kill()

            logger.info(f"Árbol de proceso {pid} terminado")
            return True

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error terminando árbol de proceso {pid}: {e}")
            return False

    def clear_cache(self):
        """Limpia la caché de procesos."""
        self._process_cache.clear()
        logger.debug("Caché de procesos limpiada")
