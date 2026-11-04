import os
import shutil
import pandas as pd
import logging
from jinja2 import Environment, FileSystemLoader

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s - %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
log.addHandler(sh)

input_data = 'input_data/input_data.xlsx'
wf_output = 'output_data/wf/'
ceh_output = 'output_data/ceh/'
uni_output = 'output_data/db_table/'
ceh_resource_output = 'output_data/ceh_resource/'
uni_resource_output = 'output_data/uni_resource/'
ddl_output = 'output_data/ddl/'

dir_template = FileSystemLoader('template')
env = Environment(loader=dir_template)

wf_template = env.get_template('wf_init_template.yaml')
mart_template = env.get_template('mart_ceh_template.yaml')
uni_template = env.get_template('db_table_template.yaml')
ceh_resource_template = env.get_template('ceh_resource_template.json')
uni_resource_template = env.get_template('uni_resource_template.json')
ddl_template = env.get_template('ddl_template.sql')


def clear(output: list[str]) -> None:
    """
        Функция очистки директорий вывода сгенерированных потоков
        Returns:
            None
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
    flows_df = pd.read_excel(path, sheet_name='Sheet2')
    for row in range(len(flows_df)):
        workflow = flows.setdefault(flows_df['workflow'][row], {})
        workflow.setdefault('mart', flows_df['mart'][row].strip())
        workflow.setdefault('table', flows_df['table'][row].strip())

        data = workflow.setdefault('data', {})
        data.setdefault(flows_df['attribute'][row], flows_df['type'][row])

        flows.setdefault(flows_df['workflow'][row], workflow)
    log.info(f'Всего объектов к генерации: {len(flows)}')
    [log.info(flow) for flow in flows.keys()]
    return flows


def generate_objects(flows: dict) -> None:
    """
        Функция генерации файлов потоков и маппингов
        Returns:
            None
    """
    for workflow in flows:
        mart = flows[workflow]['mart']
        uni_source = flows[workflow]['table']
        with open(ceh_output + mart + '.yaml', 'w+', encoding='utf-8') as file:
            file.write(
                mart_template.render(
                    mart=mart,
                    data=flows[workflow]['data'].items()
                )
            )
        with open(uni_output + '2204_sfobo_export_rmb_tech_' + uni_source + '.yaml', 'w+', encoding='utf-8') as file:
            file.write(
                uni_template.render(
                    uni_source=uni_source,
                    data=flows[workflow]['data'].items(),
                )
            )
        with open(ceh_resource_output + 'ceh.rd_rawd.' + mart + '.json', 'w+', encoding='utf-8') as file:
            file.write(
                ceh_resource_template.render(
                    mart=mart
                )
            )
        with open(uni_resource_output + '2204.sfobo_export_rmb_tech.' + uni_source + '.rawd.json', 'w+',
                  encoding='utf-8') as file:
            file.write(
                uni_resource_template.render(
                    uni=uni_source
                )
            )
        with open(ddl_output + mart + '.sql', 'w+',
                  encoding='utf-8') as file:
            file.write(
                ddl_template.render(
                    mart=mart,
                    data=flows[workflow]['data'].items()
                )
            )
        with open(wf_output + workflow + '.yaml', 'w+', encoding='utf-8') as file:
            file.write(
                wf_template.render(
                    workflow=workflow,
                    tag=flows[workflow]['table'],
                    uni_source=uni_source,
                    mart=mart,
                    attributes=flows[workflow]['data']
                )
            )


def main() -> None:
    """
        Главная функция
        Returns:
            None
    """
    clear([wf_output, ceh_output, uni_output, ddl_output, ceh_resource_output, uni_resource_output, ddl_output])
    generate_objects(parse_excel(input_data))


if __name__ == "__main__":
    """
        Точка входа
        Returns:
            None
    """
    main()
