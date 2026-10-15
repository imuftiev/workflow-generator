import os, shutil
import pandas as pd
from jinja2 import Environment, FileSystemLoader

#Название excel-файла, список потоков
excel_file = "cf_list"

input_data = f"pxf/input_data/{excel_file}.xlsx"
output_dir = "output_data"
flows = []

file_template = FileSystemLoader("pxf/template")
env = Environment(loader=file_template)

template = env.get_template("cf_mrod_flow_template.yaml")

try:
    print(f"Очистка файлов в директории: {output_dir}...")
    shutil.rmtree(output_dir)
    os.mkdir(output_dir)
except FileNotFoundError:
    print(f"Директории {output_dir} не существует, создаем...")
    os.mkdir(output_dir)

def parse_excel(filepath: str, sheet_name='Sheet1') -> None:
    df = pd.read_excel(filepath, sheet_name)
    [flows.append(x) for x in df["Flows"]]
    print("Список потоков для перевода на шаблон yaml:")
    [print(x) for x in flows]

def generate_flows() -> None:
    for flow in flows:
        dag_id = str(flow)
        work_flow_id = "wf_" + flow[3:]
        target = "mrod"
        index = str(flow).find(target)
        if index != -1:
            algos_map, algos_map_uni, algos_map_ceh = (str(flow)[index:],
                                                       "tseh.public." + str(flow)[index:],
                                                       "ceh.rd_rawd." + str(flow)[index:])
        with open(f"{output_dir}/{flow}.yaml", "w+", encoding="utf-8") as f:
            f.write(str(template.render(
                dag_id=dag_id,
                work_flow_id=work_flow_id,
                algos_map=algos_map,
                algos_map_uni=algos_map_uni,
                algos_map_ceh=algos_map_ceh
            )))


parse_excel(input_data)
generate_flows()