import json
import os, shutil
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import logging

# Название excel-файла, список потоков
excel_file = 'input_data'

input_data = f'input_data/{excel_file}.xlsx'
cf_output = 'output_data/cf/'
ceh_resource_output = 'output_data/ceh_resource/'
uni_resource_output = 'output_data/uni_resource/'
db_output = 'output_data/db_table/'
wf_init_output = 'output_data/wf_init/'
wf_output = 'output_data/wf/'

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s - %(message)s')

log_stream = logging.StreamHandler()
log_stream.setFormatter(formatter)

log.addHandler(log_stream)

file_template = FileSystemLoader("template")
env = Environment(loader=file_template)

cf_template = env.get_template("cf_mrod_flow_template.yaml")
db_template = env.get_template("db_table_template.yaml")
wf_template_py = env.get_template("wf_template.txt")
wf_template_yaml = env.get_template("wf_template.yaml")
wf_init_template = env.get_template("wf_init_template.yaml")
ceh_resource_template = env.get_template("ceh_resource_template.json")
uni_resource_template = env.get_template("uni_resource_template.json")


def clear(output: list[str]) -> None:
    """
        Очищает выходные директории генератора.

        Для каждой директории удаляет существующее содержимое
        и создаёт пустую директорию для новых YAML-файлов.

        Args:
            output: Список путей к выходным директориям.

        Returns:
            None.
    """
    for directory in output:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory, exist_ok=True)
        log.info(f'Директория создана: {directory}')


def parse_excel(filepath: str, sheet_name='Sheet1') -> dict[str, str]:
    """
        Парсит excel файл и возвращает список наименований потоков.
        Args:
            filepath: Путь к файлу excel.
            sheet_name: Страница из файла excel которую нужно обработать

        Returns:
            list[str].
    """
    flows_df = pd.read_excel(filepath, sheet_name)
    log.info("Список потоков для перевода на шаблон yaml:")
    [log.info(x) for x in flows_df['workflow']]
    flows = {}
    for row in range(len(flows_df)):
        workflow = flows.setdefault(flows_df['table'][row], {})
        workflow.setdefault('controlflow', flows_df['controlflow'][row])
        workflow.setdefault('workflow', flows_df['workflow'][row])
        workflow.setdefault('schema', flows_df['schema'][row])
        flows.setdefault(flows_df['table'][row], workflow)
    return flows


def generate_objects(flows: dict) -> None:
    for flow in flows:
        controlflow = flows[flow]['controlflow']
        workflow = flows[flow]['workflow']
        schema = flows[flow]['schema']
        table = flow

        with open(cf_output + controlflow + '.yaml', 'w+', encoding='utf-8') as cf:
            cf.write(
                cf_template.render(
                    controlflow=controlflow,
                    workflow=workflow,
                    schema=schema,
                    table=table
                )
            )

        with open(wf_output + workflow + '.yaml', 'w+', encoding='utf-8') as wf:
            wf.write(
                wf_template_yaml.render(
                    workflow=workflow,
                    schema=schema,
                    table=table
                )
            )

        with open(ceh_resource_output + 'ceh.' + schema + ".mart_mrod_" + table + '.json', 'w+',
                  encoding='utf-8') as ceh_resource:
            ceh_resource.write(
                ceh_resource_template.render(
                    schema=schema,
                    table=table
                )
            )
        with open(uni_resource_output + 'tseh.public.mrod_' + table + '.json', 'w+', encoding='utf-8') as uni_resource:
            uni_resource.write(
                uni_resource_template.render(
                    schema=schema,
                    table=table
                )
            )

        with open(db_output + table + '_get_raw_data_init_yaml.yaml', 'w+', encoding='utf-8') as db_table:
            db_table.write(
                db_template.render(
                    table=table
                )
            )

        with open(wf_init_output + workflow + '_init.yaml', 'w+', encoding='utf-8') as wf_init_yml:
            wf_init_yml.write(
                wf_init_template.render(
                    workflow=workflow,
                    schema=schema,
                    table=table
                )
            )

        with open(wf_output + workflow + '.py', 'w+', encoding='utf-8') as wf_py:
            wf_py.write(
                wf_template_py.render()
            )
        with open(wf_output + workflow + '_init.py', 'w+', encoding='utf-8') as wf_init_py:
            wf_init_py.write(
                wf_template_py.render()
            )


def main() -> None:
    """
        Запускает функции генерации
    """
    clear([cf_output, wf_init_output, db_output, wf_output, ceh_resource_output, uni_resource_output])
    generate_objects(parse_excel(input_data))


if __name__ == "__main__":
    main()
