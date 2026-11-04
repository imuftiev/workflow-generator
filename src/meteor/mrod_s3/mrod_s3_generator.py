import os.path
from logging import StreamHandler
import logging
import pandas as pd
import shutil
from jinja2 import Environment, FileSystemLoader

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s - %(message)s')

sh = StreamHandler()
sh.setFormatter(formatter)

log.addHandler(sh)

input_data = 'input_data/input_data.xlsx'
dir_template = FileSystemLoader('template/')
env = Environment(loader=dir_template)
wf_template = env.get_template('wf_fm_template.yaml')
ceh_resource_template = env.get_template('ceh_resource_template.json')
uni_resource_template = env.get_template('uni_resource_template.json')
wf_output = 'output_data/wf/'
ceh_output = 'output_data/ceh_resource/'
uni_output = 'output_data/uni_resource/'


def clear(output: list[str]) -> None:
    """
        Функция очистки директорий вывода сгенерированных потоков
        Returns:
            None.
    """
    for directory in output:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory, exist_ok=True)
        log.info(f'Директория создана: {directory}')


def parse_excel(path: str) -> dict:
    """
        Создает рабочие потоки из списка потоков.
        Returns:
            dict.
    """
    flows = {}
    rows = pd.read_excel(path, sheet_name='Sheet1')
    log.info("Список потоков для перевода на шаблон yaml:")
    [log.info(row) for row in rows["workflow"]]
    for row in range(len(rows)):
        flows.setdefault(rows["workflow"][row], rows["table"][row])
    return flows


def generate_objects(flows: dict) -> None:
    """
        Функция генерации объектов
        Returns:
            None
    """
    for flow, table in flows.items():
        with open(wf_output + flow + '.yaml', 'w+', encoding='utf-8') as wf:
            wf.write(
                wf_template.render(
                    wf_name=flow,
                    wf_tag=flow,
                    table_name=table,
                    table_name_upper=table.upper()
                )
            )
            log.info(f'Создан файл: {wf.name}')
        with open(ceh_output + 'ceh_resource.rd_rawd.mrod_' + table + '.json', 'w+', encoding='utf-8') as ceh:
            ceh.write(
                ceh_resource_template.render(
                    table_name=table
                )
            )
            log.info(f'Создан файл: {ceh.name}')
        with open(uni_output + 'tseh.public.mrod_' + table + '.json', 'w+', encoding='utf-8') as uni:
            uni.write(
                uni_resource_template.render(
                    table_name=table,
                    table_name_uppercase=table.upper()
                )
            )
            log.info(f'Создан файл: {uni.name}')


def main() -> None:
    """
        Запускает функции генерации
        Returns:
            None
    """
    clear([wf_output, ceh_output, uni_output])
    generate_objects(parse_excel(input_data))


if __name__ == "__main__":
    main()
