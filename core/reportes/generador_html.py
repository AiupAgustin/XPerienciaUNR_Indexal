
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# La plantilla está en la carpeta templates dentro de core
BASE_DIR = Path(__file__).resolve().parent.parent
env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))

def renderizar_reporte_html(master_json: dict) -> str:
    """Toma el Master JSON e inyecta los datos en la plantilla Jinja2."""
    template = env.get_template("reporte_template.html")
    return template.render(
        metadata=master_json["metadata"],
        bloques=master_json["bloques"]
    )