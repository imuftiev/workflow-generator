import os
import pandas as pd
from jinja2 import FileSystemLoader, Environment
import shutil

# 'excel'-файл со всеми требованиями и маппингами
input_data = "meteor/input_data/input_data.xlsx"

# Директория с выводом потоков
output_data = "meteor/wf/"

mart_list: list[dict] = []
wf_list = []
table_list = []

file_template = FileSystemLoader("meteor/template/")

env = Environment(loader=file_template)

# Файл-шаблон по которому будет строиться wf
template = env.get_template("wf_fm_template.yaml")

def parse_ceh_excel(filename: str, sheet: str) -> None:
    df = pd.read_excel(filename, sheet_name=sheet, index_col=False)
    for row in df.itertuples(index=False):
        mart = next((
            item
            for item in mart_list
            if item.get("mart_name") == row.__getattribute__("mart_name")
        ), None)

        if mart is None:
            mart = {
                "mart_name": row.mart_name,
                "attributes": []
            }
            mart_list.append(mart)

        mart["attributes"].append({
            "attribute_name": row.attribute_name,
            "data_type": row.data_type,
        })

    print("Всего объектов к генерации: " + str(len(mart_list)))

def parse_db_table_excel(filename1: str, sheet: str) -> None:
    df = pd.read_excel(filename1, sheet_name=sheet, index_col=False)
    for row in df.itertuples(index=False):
        table_list.append(row.table)
        wf_list.append(row.workflow)


def generate_flows() -> None:
    try:
        print("Очищаем директорию с потоками...")
        shutil.rmtree(output_data)
        print("Создаём директорию для выгрузки потоков...")
        os.mkdir(output_data)
    except FileNotFoundError as e:
        print("Ошибка! Директория отсутствует:" + str(e) + "\nСоздаем директорию...")
        os.mkdir(output_data)

    for mart in range(len(mart_list)):
        with open(str(output_data + wf_list[mart] + ".yaml"), "w+", encoding="utf-8") as f:
            f.write(
                template.render(
                    wf_name = wf_list[mart],
                    ceh_source = mart_list[mart]["mart_name"],
                    wf_tag = table_list[mart],
                    fields = [
                        attr["attribute_name"]
                        for attr in mart_list[mart]["attributes"]
                    ],
                    db_table_source = table_list[mart]
                )
            )


parse_ceh_excel(input_data, "Sheet2")
parse_db_table_excel(input_data, "Sheet1")
generate_flows()