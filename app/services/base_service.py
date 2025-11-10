"""
Servicio Base - Multi-Usuario (FASE 3)

Este módulo contiene la lógica base para los servicios que requieren
autenticación y acceso al usuario actual.
"""

from ..utils.auth import StreamlitAuth


class BaseService:
    """Servicio base con funcionalidades de autenticación compartidas"""

    @staticmethod
    def _get_current_user_id() -> int:
        """
        Obtiene el ID del usuario actual autenticado

        Returns:
            int: ID del usuario actual

        Raises:
            Exception: Si no hay usuario autenticado
        """
        if not StreamlitAuth.is_authenticated():
            raise Exception("Usuario no autenticado")

        user = StreamlitAuth.get_current_user()
        if not user:
            raise Exception("No se pudo obtener información del usuario")

        return user['id']
