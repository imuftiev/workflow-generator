import os, shutil
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import logging

# Название excel-файла, список потоков
excel_file = "cf_list"

input_data = f"pxf/input_data/{excel_file}.xlsx"
cf_output = "pxf/output_data/cf/"
db_output = "pxf/output_data/db_table/"
wf_init_output = "pxf/output_data/wf_init/"

output = [cf_output, db_output, wf_init_output]

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s - %(message)s')

log_stream = logging.StreamHandler()
log_stream.setFormatter(formatter)

log.addHandler(log_stream)

flows = []

file_template = FileSystemLoader("pxf/template")
env = Environment(loader=file_template)

cf_template = env.get_template("cf_mrod_flow_template.yaml")
db_template = env.get_template("db_table_template.yaml")
wf_template = env.get_template("wf_init_template.yaml")


def clear() -> None:
    try:
        log.info(f"Очистка файлов в директориях: {cf_output}, {db_output}, {wf_init_output} ...")
        for f in output:
            shutil.rmtree(f)
            os.mkdir(f)

    except FileNotFoundError:
        log.error(f"Директорий {cf_output}, {db_output}, {wf_init_output} не существует, создаем")
        for f in output:
            os.mkdir(f)


def parse_excel(filepath: str, sheet_name='Sheet1') -> None:
    df = pd.read_excel(filepath, sheet_name)
    [flows.append(x) for x in df["Flows"]]
    log.info("Список потоков для перевода на шаблон yaml:")
    [log.info(x) for x in flows]


def generate_control_flows() -> None:
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
    rows = pd.read_excel("pxf/input_data/cf_list.xlsx")
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
    rows = pd.read_excel("pxf/input_data/cf_list.xlsx")
    for file in range(len(rows)):
        for row in rows.itertuples(index=False):
            name = row[0][12:]
            with open(f"{db_output}{name}_get_raw_data_init_yaml.yaml", "w+") as f:
                f.write(
                    db_template.render(
                        db_table_name=name,
                        mrod_table_name=str.upper(name[5:])
                    )
                )


clear()
parse_excel(input_data)
generate_control_flows()
generate_work_flows()
generate_db_table()
