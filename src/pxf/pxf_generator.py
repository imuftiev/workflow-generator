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


def parse_excel(filepath: str, sheet_name='Sheet1') -> list[str]:
    """
        Парсит excel файл и возвращает список наименований потоков.
        Args:
            filepath: Путь к файлу excel.
            sheet_name: Страница из файла excel которую нужно обработать

        Returns:
            list[str].
    """
    df = pd.read_excel(filepath, sheet_name)
    log.info("Список потоков для перевода на шаблон yaml:")
    [log.info(x) for x in df["Flows"]]
    return df["Flows"].tolist()


def generate_control_flows(flows: list[str]) -> None:
    """
            Создает управляющие потоки из списка потоков.
            Args:
                flows: Список наименований потоков, которые будут созданы

            Returns:
                None.
    """
    for flow in flows:
        dag_id = str(flow)
        work_flow_id = "wf_" + flow[3:]
        target = "mrod"
        index = str(flow).find(target)
        if index != -1:
            algos_map, algos_map_uni, algos_map_ceh = (str(flow)[index:],
                                                       "tseh.public." + str(flow)[index:],
                                                       "ceh.rd_rawd." + str(flow)[index:])
        with open(f"{cf_output}/{flow}.yaml", "w+", encoding="utf-8") as f:
            f.write(str(cf_template.render(
                dag_id=dag_id,
                work_flow_id=work_flow_id,
                algos_map=algos_map,
                algos_map_uni=algos_map_uni,
                algos_map_ceh=algos_map_ceh
            )))


def generate_work_flows() -> None:
    """
            Создает рабочие потоки из списка потоков.
            Returns:
                None.
    """
    rows = pd.read_excel("src/pxf/input_data/cf_list.xlsx")
    for row in range(len(rows)):
        flow = rows["Flows"][row]
        index = str(rows["Flows"][row]).find("mrod_")  # 12
        table_name = str(flow)[index:]
        table_schema = rows["Schema"][row]
        with open(f"{wf_init_output}wf_raw_data_{table_name}_init.yaml", "w+") as f:
            f.write(
                wf_template.render(
                    table_name=table_name,
                    table_schema=table_schema,
                    table_name_upper=str(table_name).upper()
                )
            )


def generate_db_table() -> None:
    """
            Создает маппинги таблицы приемника.
            Returns:
                None.
    """
    rows = pd.read_excel("src/pxf/input_data/cf_list.xlsx")
    for row in rows.itertuples(index=False):
        name = row[0][12:]
        with open(f"{db_output}{name}_get_raw_data_init_yaml.yaml", "w+") as f:
            f.write(
                db_template.render(
                    db_table_name=name,
                    mrod_table_name=str.upper(name[5:])
                )
            )


def main():
    """
        Запускает функции генерации
    """
    clear([cf_output, wf_init_output, db_output])
    flows = parse_excel(input_data)
    generate_control_flows(flows)
    generate_work_flows()
    generate_db_table()


if __name__ == "__main__":
    main()
