r"""Повторяемая локальная проверка: .venv\Scripts\python.exe run_notebooks.py."""
import os
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

os.environ["LAB_MODE"] = "local"
os.environ["MLFLOW_ENABLE_TELEMETRY"] = "false"
root = Path(__file__).resolve().parent
(root / "lab_artifacts").mkdir(exist_ok=True)
# Все служебные файлы остаются в проекте.
os.environ["JUPYTER_RUNTIME_DIR"] = str(root / "lab_artifacts" / "jupyter_runtime")
os.environ["IPYTHONDIR"] = str(root / "lab_artifacts" / "ipython")
os.environ["MPLCONFIGDIR"] = str(root / "lab_artifacts" / "matplotlib")

for name in ("01_s3.ipynb", "02_mlflow.ipynb"):
    path = root / name
    nb = nbformat.read(path, as_version=4)
    km = KernelManager(kernel_name="python3")
    km.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    print(f"Executing {name}", flush=True)
    client = NotebookClient(nb, km=km, timeout=600, resources={"metadata": {"path": str(root)}})
    try:
        client.execute()
    finally:
        nbformat.write(nb, path)
    count = sum(cell.cell_type == "code" for cell in nb.cells)
    assert not any(output.output_type == "error" for cell in nb.cells if cell.cell_type == "code"
                   for output in cell.outputs)
    print(f"OK: {name}, {count} code cells", flush=True)
