import inspect
import os, shutil
import pandas as pd
from jinja2 import Environment, FileSystemLoader

from src.logs.log import get_log
from src.writer.file_writer import create_file

# Название excel-файла, список потоков
excel_file = 'input'

input_data = f'input/{excel_file}.xlsx'
cf_output = 'output/cf/'
ceh_resource_output = 'output/ceh_resource/'
uni_resource_output = 'output/uni_resource/'
db_output = 'output/db_table/'
wf_init_output = 'output/wf_init/'
wf_output = 'output/wf/'
log = get_log(__name__='pxf')

file_template = FileSystemLoader("template")
env = Environment(loader=file_template)

cf_template = env.get_template("cf_mrod_flow_template.yaml")
db_template = env.get_template("db_table_template.yaml")
wf_template_py = env.get_template("wf_template.txt")
wf_template_yaml = env.get_template("wf_template.yaml")
wf_init_template_yaml = env.get_template("wf_init_template.yaml")
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
    for x in flows_df['workflow']:
        log.info(x)
    flows = {}
    for row in range(len(flows_df)):
        workflow = flows.setdefault(flows_df['table'][row], {})
        workflow.setdefault('controlflow', flows_df['controlflow'][row])
        workflow.setdefault('workflow', flows_df['workflow'][row])
        workflow.setdefault('schema', flows_df['schema'][row])
        flows.setdefault(flows_df['table'][row], workflow)
    return flows


def generate_control_flows(flows: dict) -> None:
    try:
        for flow in flows:
            controlflow = flows[flow]['controlflow']
            workflow = flows[flow]['workflow']
            schema = flows[flow]['schema']
            table = flow
            create_file(
                controlflow=controlflow,
                workflow=workflow,
                schema=schema,
                table=table,
                template=cf_template,
                path=cf_output + controlflow + '.yaml'
            )
    except Exception as e:
        method_name = inspect.currentframe().f_code.co_name
        log.error(msg=f'Метод: {method_name} - {e.__str__()}')


def generate_workflow(flows: dict) -> None:
    try:
        for flow in flows:
            workflow = flows[flow]['workflow']
            schema = flows[flow]['schema']
            table = flow
            create_file(
                workflow=workflow,
                schema=schema,
                table=table,
                template=wf_template_yaml,
                path=wf_output + workflow + '.yaml'
            )
    except Exception as e:
        method_name = inspect.currentframe().f_code.co_name
        log.error(msg=f'Метод: {method_name} - {e.__str__()}')


def generate_workflow_py(flows: dict) -> None:
    try:
        for flow in flows:
            workflow = flows[flow]['workflow']
            create_file(wf_template_py, path=wf_output + workflow + '.py')
    except Exception as e:
        method_name = inspect.currentframe().f_code.co_name
        log.error(msg=f'Метод: {method_name} - {e.__str__()}')


def generate_workflow_init_yaml(flows: dict) -> None:
    try:
        for flow in flows:
            workflow = flows[flow]['workflow']
            schema = flows[flow]['schema']
            table = flow
            create_file(
                schema=schema,
                table=table,
                template=wf_init_template_yaml,
                path=wf_init_output + workflow + '_init.yaml'
            )
    except Exception as e:
        method_name = inspect.currentframe().f_code.co_name
        log.error(msg=f'Метод: {method_name} - {e.__str__()}')


def generate_workflow_init_py(flows: dict) -> None:
    try:
        for flow in flows:
            workflow = flows[flow]['workflow']
            create_file(
                template=wf_template_py,
                path=wf_init_output + workflow + '_init.py'
            )
    except Exception as e:
        method_name = inspect.currentframe().f_code.co_name
        log.error(msg=f'Метод: {method_name} - {e.__str__()}')


def generate_db_table(flows: dict) -> None:
    try:
        for flow in flows:
            table = flow
            create_file(
                table=table,
                template=db_template,
                path=db_output + table + '_get_raw_data_init_yaml.yaml'
            )
    except Exception as e:
        method_name = inspect.currentframe().f_code.co_name
        log.error(msg=f'Метод: {method_name} - {e.__str__()}')


def generate_ceh_resource(flows: dict) -> None:
    try:
        for flow in flows:
            schema = flows[flow]['schema']
            table = flow
            create_file(
                template=ceh_resource_template,
                path=ceh_resource_output + 'ceh.' + schema + ".mart_mrod_" + table + '.json'
            )
    except Exception as e:
        method_name = inspect.currentframe().f_code.co_name
        log.error(msg=f'Метод: {method_name} - {e.__str__()}')


def generate_uni_resource(flows: dict) -> None:
    try:
        for flow in flows:
            table = flow
            create_file(
                table=table,
                template=uni_resource_template,
                path=uni_resource_output + 'tseh.public.mrod_' + table + '.json'
            )
    except Exception as e:
        method_name = inspect.currentframe().f_code.co_name
        log.error(msg=f'Метод: {method_name} - {e.__str__()}')


#
def main() -> None:
    """
        Запускает функции генерации
    """
    clear([cf_output, wf_init_output, db_output, wf_output, ceh_resource_output, uni_resource_output])
    flows = parse_excel(input_data)
    generate_control_flows(flows)
    generate_workflow(flows)
    generate_workflow_init_yaml(flows)
    generate_ceh_resource(flows)
    generate_uni_resource(flows)
    generate_db_table(flows)
    generate_workflow_init_py(flows)
    generate_workflow_py(flows)


if __name__ == "__main__":
    main()
