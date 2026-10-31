import os, shutil
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import logging

# Название excel-файла, список потоков
excel_file = "cf_list"

input_data = f"src/pxf/input_data/{excel_file}.xlsx"
cf_output = "src/pxf/output_data/cf/"
db_output = "src/pxf/output_data/db_table/"
wf_init_output = "src/pxf/output_data/wf_init/"

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s - %(message)s')

log_stream = logging.StreamHandler()
log_stream.setFormatter(formatter)

log.addHandler(log_stream)

file_template = FileSystemLoader("src/pxf/template")
env = Environment(loader=file_template)

cf_template = env.get_template("cf_mrod_flow_template.yaml")
db_template = env.get_template("db_table_template.yaml")
wf_template = env.get_template("wf_init_template.yaml")


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
    log.info(f"Директории созданы: {cf_output}, {db_output}, {wf_init_output}")


def parse_excel(filepath: str, sheet_name='Sheet1') -> dict[str, str]:
    """
        Парсит excel файл и возвращает список наименований потоков.
        Args:
            filepath: Путь к файлу excel.
            sheet_name: Страница из файла excel которую нужно обработать

        Returns:
            list[str].
    """
    rows = pd.read_excel(filepath, sheet_name)
    log.info("Список потоков для перевода на шаблон yaml:")
    [log.info(x) for x in rows["Flows"]]
    flows = {}
    for row in range(len(rows)):
        flows.setdefault(rows["Flows"][row], rows["Schema"][row])
    return flows


def generate_control_flows(flows: dict[str, str]) -> None:
    """
            Создает управляющие потоки из словаря потоков.
            Args:
                flows: Список наименований потоков, которые будут созданы

            Returns:
                None.
    """
    for flow, schema in flows.items():
        work_flow_id = "wf_" + flow[3:]
        index = flow.find("mrod")
        if index != -1:
            algos_map, algos_map_uni, algos_map_ceh = (flow[index:],
                                                       str(flow)[index:],
                                                       schema + "." + "mart_" + str(flow)[index:])
        with open(f"{cf_output}{flow}.yaml", "w+", encoding="utf-8") as f:
            f.write(str(cf_template.render(
                dag_id=flow,
                work_flow_id=work_flow_id,
                algos_map=algos_map,
                algos_map_uni=algos_map_uni,
                algos_map_ceh=algos_map_ceh
            )))
            log.info(f"Создан файл: {f.name}")


def generate_work_flows(flows: dict[str, str]) -> None:
    """
            Создает рабочие потоки из списка потоков.
            Returns:
                None.
    """
    for flow, schema in flows.items():
        index = flow.find("mrod")  # 12
        table_name = str(flow)[index:]
        with open(f"{wf_init_output}wf_raw_data_{table_name}_init.yaml", "w+") as f:
            f.write(
                wf_template.render(
                    table_name=table_name,
                    table_schema=schema,
                    table_name_upper=str(table_name).upper()
                )
            )
            log.info(f"Создан файл: {f.name}")


def generate_db_table(flows: dict[str, str]) -> None:
    """
            Создает маппинги таблицы приемника.
            Returns:
                None.
    """
    for flow in flows.items():
        name = flow[0][12:]
        with open(f"{db_output}{name}_get_raw_data_init_yaml.yaml", "w+") as f:
            f.write(
                db_template.render(
                    db_table_name=name,
                    mrod_table_name=str.upper(name[5:])
                )
            )
            log.info(f"Создан файл: {f.name}")


def main():
    """
        Запускает функции генерации
    """
    clear([cf_output, wf_init_output, db_output])
    flows = parse_excel(input_data)
    generate_control_flows(flows)
    generate_work_flows(flows)
    generate_db_table(flows)


if __name__ == "__main__":
    main()
