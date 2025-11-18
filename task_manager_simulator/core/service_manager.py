"""
Gestor de servicios del sistema (Windows).
"""
import logging
from typing import List, Optional
import sys

from ..models.service import ServiceInfo, ServiceStatus, ServiceStartType


logger = logging.getLogger(__name__)

# Intentar importar módulos de Windows
try:
    if sys.platform == 'win32':
        import win32service
        import win32serviceutil
        import pywintypes
        WIN32_AVAILABLE = True
    else:
        WIN32_AVAILABLE = False
except ImportError:
    WIN32_AVAILABLE = False
    logger.warning("pywin32 no disponible - Funcionalidad de servicios limitada")


class ServiceManager:
    """
    Gestor de servicios del sistema Windows.

    Proporciona funcionalidades para:
    - Listar servicios del sistema
    - Obtener información detallada de servicios
    - Iniciar/Detener servicios
    - Cambiar tipo de inicio de servicios
    """

    def __init__(self):
        """Inicializa el gestor de servicios."""
        self.is_windows = sys.platform == 'win32'
        self.is_available = WIN32_AVAILABLE

        if not self.is_windows:
            logger.info("ServiceManager: No es sistema Windows - funcionalidad no disponible")
        elif not WIN32_AVAILABLE:
            logger.warning("ServiceManager: pywin32 no disponible - instalar con: pip install pywin32")

        logger.info(f"ServiceManager inicializado (disponible: {self.is_available})")

    def get_all_services(self) -> List[ServiceInfo]:
        """
        Obtiene la lista de todos los servicios del sistema.

        Returns:
            Lista de objetos ServiceInfo
        """
        if not self.is_available:
            logger.warning("Servicios no disponibles en este sistema")
            return self._get_mock_services()

        services = []

        try:
            # Conectar al Service Control Manager
            scm_handle = win32service.OpenSCManager(
                None,
                None,
                win32service.SC_MANAGER_ENUMERATE_SERVICE
            )

            try:
                # Enumerar todos los servicios
                service_type = win32service.SERVICE_WIN32
                service_state = win32service.SERVICE_STATE_ALL

                service_list = win32service.EnumServicesStatus(
                    scm_handle,
                    service_type,
                    service_state
                )

                for service in service_list:
                    try:
                        service_info = self._create_service_info(service)
                        if service_info:
                            services.append(service_info)
                    except Exception as e:
                        logger.debug(f"Error procesando servicio: {e}")
                        continue

            finally:
                win32service.CloseServiceHandle(scm_handle)

        except Exception as e:
            logger.error(f"Error obteniendo servicios: {e}")

        logger.debug(f"Obtenidos {len(services)} servicios")
        return services

    def _create_service_info(self, service_tuple) -> Optional[ServiceInfo]:
        """
        Crea un objeto ServiceInfo desde los datos de win32service.

        Args:
            service_tuple: Tupla con información del servicio

        Returns:
            Objeto ServiceInfo o None
        """
        if not WIN32_AVAILABLE:
            return None

        try:
            service_name, display_name, service_status = service_tuple

            # Mapear estado
            state = service_status[1]
            status = self._map_service_state(state)

            # Obtener información adicional
            try:
                scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
                try:
                    hs = win32service.OpenService(scm, service_name, win32service.SERVICE_ALL_ACCESS)
                    try:
                        config = win32service.QueryServiceConfig(hs)
                        start_type = self._map_start_type(config[1])

                        service_info = ServiceInfo(
                            name=service_name,
                            display_name=display_name,
                            status=status,
                            start_type=start_type,
                        )

                        # PID si está en ejecución
                        if state == win32service.SERVICE_RUNNING:
                            status_info = win32service.QueryServiceStatusEx(hs)
                            service_info.pid = status_info['ProcessId']

                        return service_info

                    finally:
                        win32service.CloseServiceHandle(hs)
                finally:
                    win32service.CloseServiceHandle(scm)

            except Exception as e:
                # Si no se puede obtener config, retornar info básica
                return ServiceInfo(
                    name=service_name,
                    display_name=display_name,
                    status=status,
                )

        except Exception as e:
            logger.debug(f"Error creando ServiceInfo: {e}")
            return None

    def _map_service_state(self, state: int) -> ServiceStatus:
        """Mapea el estado de win32service a ServiceStatus."""
        if not WIN32_AVAILABLE:
            return ServiceStatus.UNKNOWN

        state_map = {
            win32service.SERVICE_STOPPED: ServiceStatus.STOPPED,
            win32service.SERVICE_START_PENDING: ServiceStatus.START_PENDING,
            win32service.SERVICE_STOP_PENDING: ServiceStatus.STOP_PENDING,
            win32service.SERVICE_RUNNING: ServiceStatus.RUNNING,
            win32service.SERVICE_CONTINUE_PENDING: ServiceStatus.CONTINUE_PENDING,
            win32service.SERVICE_PAUSE_PENDING: ServiceStatus.PAUSE_PENDING,
            win32service.SERVICE_PAUSED: ServiceStatus.PAUSED,
        }

        return state_map.get(state, ServiceStatus.UNKNOWN)

    def _map_start_type(self, start_type: int) -> ServiceStartType:
        """Mapea el tipo de inicio de win32service a ServiceStartType."""
        if not WIN32_AVAILABLE:
            return ServiceStartType.UNKNOWN

        start_type_map = {
            win32service.SERVICE_AUTO_START: ServiceStartType.AUTO,
            win32service.SERVICE_BOOT_START: ServiceStartType.AUTO,
            win32service.SERVICE_SYSTEM_START: ServiceStartType.AUTO,
            win32service.SERVICE_DEMAND_START: ServiceStartType.MANUAL,
            win32service.SERVICE_DISABLED: ServiceStartType.DISABLED,
        }

        return start_type_map.get(start_type, ServiceStartType.UNKNOWN)

    def start_service(self, service_name: str) -> bool:
        """
        Inicia un servicio.

        Args:
            service_name: Nombre del servicio

        Returns:
            True si se inició exitosamente
        """
        if not self.is_available:
            logger.error("Servicios no disponibles")
            return False

        try:
            win32serviceutil.StartService(service_name)
            logger.info(f"Servicio '{service_name}' iniciado")
            return True
        except Exception as e:
            logger.error(f"Error iniciando servicio '{service_name}': {e}")
            return False

    def stop_service(self, service_name: str) -> bool:
        """
        Detiene un servicio.

        Args:
            service_name: Nombre del servicio

        Returns:
            True si se detuvo exitosamente
        """
        if not self.is_available:
            logger.error("Servicios no disponibles")
            return False

        try:
            win32serviceutil.StopService(service_name)
            logger.info(f"Servicio '{service_name}' detenido")
            return True
        except Exception as e:
            logger.error(f"Error deteniendo servicio '{service_name}': {e}")
            return False

    def restart_service(self, service_name: str) -> bool:
        """
        Reinicia un servicio.

        Args:
            service_name: Nombre del servicio

        Returns:
            True si se reinició exitosamente
        """
        if not self.is_available:
            logger.error("Servicios no disponibles")
            return False

        try:
            win32serviceutil.RestartService(service_name)
            logger.info(f"Servicio '{service_name}' reiniciado")
            return True
        except Exception as e:
            logger.error(f"Error reiniciando servicio '{service_name}': {e}")
            return False

    def pause_service(self, service_name: str) -> bool:
        """
        Pausa un servicio.

        Args:
            service_name: Nombre del servicio

        Returns:
            True si se pausó exitosamente
        """
        if not self.is_available:
            logger.error("Servicios no disponibles")
            return False

        try:
            scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            try:
                hs = win32service.OpenService(scm, service_name, win32service.SERVICE_ALL_ACCESS)
                try:
                    win32service.ControlService(hs, win32service.SERVICE_CONTROL_PAUSE)
                    logger.info(f"Servicio '{service_name}' pausado")
                    return True
                finally:
                    win32service.CloseServiceHandle(hs)
            finally:
                win32service.CloseServiceHandle(scm)
        except Exception as e:
            logger.error(f"Error pausando servicio '{service_name}': {e}")
            return False

    def resume_service(self, service_name: str) -> bool:
        """
        Reanuda un servicio pausado.

        Args:
            service_name: Nombre del servicio

        Returns:
            True si se reanudó exitosamente
        """
        if not self.is_available:
            logger.error("Servicios no disponibles")
            return False

        try:
            scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            try:
                hs = win32service.OpenService(scm, service_name, win32service.SERVICE_ALL_ACCESS)
                try:
                    win32service.ControlService(hs, win32service.SERVICE_CONTROL_CONTINUE)
                    logger.info(f"Servicio '{service_name}' reanudado")
                    return True
                finally:
                    win32service.CloseServiceHandle(hs)
            finally:
                win32service.CloseServiceHandle(scm)
        except Exception as e:
            logger.error(f"Error reanudando servicio '{service_name}': {e}")
            return False

    def _get_mock_services(self) -> List[ServiceInfo]:
        """Retorna servicios de ejemplo para testing en sistemas no-Windows."""
        return [
            ServiceInfo(
                name="MockService1",
                display_name="Mock Service 1",
                description="Servicio de ejemplo para testing",
                status=ServiceStatus.RUNNING,
                start_type=ServiceStartType.AUTO,
                pid=1234
            ),
            ServiceInfo(
                name="MockService2",
                display_name="Mock Service 2",
                description="Otro servicio de ejemplo",
                status=ServiceStatus.STOPPED,
                start_type=ServiceStartType.MANUAL
            ),
        ]
