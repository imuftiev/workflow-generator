from pathlib import Path
from jinja2 import Template


def create_file(template: Template, path: Path, mode = 'w', encoding='utf-8', **kwargs) -> None:
    with open(path, mode=mode, encoding=encoding) as file:
        file.write(
            template.render(
                controlflow=kwargs.get('controlflow'),
                workflow=kwargs.get('workflow'),
                table=kwargs.get('table'),
                schema=kwargs.get('schema')
            )
        )