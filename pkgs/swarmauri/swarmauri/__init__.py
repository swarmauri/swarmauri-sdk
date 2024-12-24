# Namespace package setup
from .importer import SwarmauriImporter

# Ensure the SwarmauriImporter is registered in sys.meta_path
import sys
if not any(isinstance(importer, SwarmauriImporter) for importer in sys.meta_path):
    sys.meta_path.insert(0, SwarmauriImporter())
