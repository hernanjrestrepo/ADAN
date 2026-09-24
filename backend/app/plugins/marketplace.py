"""
Plugin Marketplace — Sistema para instalar módulos nuevos.

Registra plugins dinámicamente mediante TEF.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class PluginManifest:
    """Manifiesto de un plugin."""
    id: str
    name: str
    description: str
    version: str
    author: str
    category: str                        # crm, erp, analytics, communication
    tools: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    config_schema: dict = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class InstalledPlugin:
    """Plugin instalado."""
    manifest: PluginManifest
    status: str = "active"               # active, disabled, error
    installed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    config: dict = field(default_factory=dict)


class PluginMarketplace:
    """
    Marketplace de plugins.
    
    Permite:
    - Registrar plugins disponibles
    - Instalar plugins
    - Desinstalar plugins
    - Listar plugins instalados
    """

    def __init__(self):
        self._available: dict[str, PluginManifest] = {}
        self._installed: dict[str, InstalledPlugin] = {}

    def register_plugin(self, manifest: PluginManifest):
        """Registra un plugin disponible."""
        self._available[manifest.id] = manifest

    def install(self, plugin_id: str, config: dict | None = None) -> InstalledPlugin:
        """Instala un plugin."""
        manifest = self._available.get(plugin_id)
        if not manifest:
            raise ValueError(f"Plugin '{plugin_id}' not found in marketplace")

        plugin = InstalledPlugin(
            manifest=manifest,
            config=config or {},
        )
        self._installed[plugin_id] = plugin
        return plugin

    def uninstall(self, plugin_id: str) -> bool:
        """Desinstala un plugin."""
        if plugin_id in self._installed:
            del self._installed[plugin_id]
            return True
        return False

    def get_installed(self, plugin_id: str) -> InstalledPlugin | None:
        """Obtiene un plugin instalado."""
        return self._installed.get(plugin_id)

    def list_available(self) -> list[dict]:
        """Lista plugins disponibles."""
        return [
            {
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "version": m.version,
                "category": m.category,
                "installed": m.id in self._installed,
            }
            for m in self._available.values()
        ]

    def list_installed(self) -> list[dict]:
        """Lista plugins instalados."""
        return [
            {
                "id": p.manifest.id,
                "name": p.manifest.name,
                "version": p.manifest.version,
                "status": p.status,
                "installed_at": p.installed_at.isoformat(),
            }
            for p in self._installed.values()
        ]

    def count(self) -> dict:
        return {"available": len(self._available), "installed": len(self._installed)}
