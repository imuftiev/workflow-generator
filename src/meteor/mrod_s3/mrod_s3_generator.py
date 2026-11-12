import json
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

input_data = 'input/input.xlsx'
dir_template = FileSystemLoader('template/')
env = Environment(loader=dir_template)
wf_template = env.get_template('wf_init_template.yaml')
ceh_resource_template = env.get_template('ceh_resource_template.json')
uni_resource_template = env.get_template('uni_resource_template.json')
ddl_template = env.get_template('ddl_template.sql')
wf_output = 'output/wf/'
ceh_output = 'output/ceh_resource/'
uni_output = 'output/uni_resource/'
ddl_output = 'output/ddl/'


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
        Функция парсинга excel файла с наименованиями и атрибутами потоков
        Returns:
            dict
    """
    flows = {}
    flows_df = pd.read_excel(path, sheet_name='Sheet1')
    for row in range(len(flows_df)):
        workflow = flows.setdefault(flows_df['workflow'][row], {})
        workflow.setdefault('schema', flows_df['schema'][row].strip())
        workflow.setdefault('table', flows_df['table'][row].strip())

        data = workflow.setdefault('data', {})
        data.setdefault(flows_df['attribute'][row], flows_df['type'][row])

        flows.setdefault(flows_df['workflow'][row], workflow)
    log.info(f'Всего объектов к генерации: {len(flows)}')
    [log.info(flow) for flow in flows.keys()]
    log.info('Структура потока(-ов):')
    log.info(json.dumps(flows, indent=4))
    return flows


def generate_objects(flows: dict) -> None:
    """
        Функция генерации объектов
        Returns:
            None
    """
    for flow in flows:
        table = flows[flow]['table']
        schema = flows[flow]['schema']
        data = flows[flow]['data']
        with open(wf_output + flow + '.yaml', 'w+', encoding='utf-8') as wf:
            wf.write(
                wf_template.render(
                    workflow=flow,
                    tag=flow,
                    schema=schema,
                    table=table,
                    table_uppercase=table.upper()
                )
            )
            log.info(f'Создан файл: {wf.name}')
        with open(ceh_output + 'ceh.' + schema + '.mrod_' + table + '.json', 'w+', encoding='utf-8') as ceh:
            ceh.write(
                ceh_resource_template.render(
                    table=table,
                    schema=schema
                )
            )
            log.info(f'Создан файл: {ceh.name}')
        with open(uni_output + 'tseh.public.mrod_' + table + '.json', 'w+', encoding='utf-8') as uni:
            uni.write(
                uni_resource_template.render(
                    table=table,
                    table_uppercase=table.upper()
                )
            )
            log.info(f'Создан файл: {uni.name}')
        with open(ddl_output + table + '.sql', 'w+', encoding='utf-8') as ddl:
            ddl.write(
                ddl_template.render(
                    table=table,
                    schema=schema,
                    data=data.items()
                )
            )
            log.info(f'Создан файл: {ddl.name}')


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
