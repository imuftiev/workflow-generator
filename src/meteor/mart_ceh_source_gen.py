import os

from jinja2 import Environment, FileSystemLoader
import pandas as pd
import shutil

ceh_output = "meteor/ceh/"
db_table_output = "/meteor/db_table"
input_data = "meteor/input_data/input_data.xlsx"
file_template = FileSystemLoader("meteor/template")
env = Environment(loader=file_template)

ceh_template = env.get_template("mart_ceh_template.yaml")
db_table_template = env.get_template("db_table_template.yaml")

db_tables_list: list[str] = []
mart_list: list[dict] = []
mart_dict = {}

def parse_mart_props(filename: str, sheet_name: str) -> None:
    df = pd.read_excel(filename, sheet_name=sheet_name)
    for row in df.itertuples(index=False):
        mart = next((item for item in mart_list if row.__getattribute__("mart_name") == item.get("mart_name")), None)
        if mart is None:
            mart = {
                "mart_name": row.mart_name,
                "attributes": []
            }
            mart_list.append(mart)

        mart["attributes"].append({
            "attribute_name": row.attribute_name,
            "data_type": row.data_type.upper()
        })

def parse_db_table_props(filename: str, sheet_name: str) -> None:
    df = pd.read_excel(filename, sheet_name=sheet_name)
    for row in df.itertuples(index=False):
        db_tables_list.append(row.table)


def generate_flows():

    try:
        print("Очищаем директорию с таблицами...")
        shutil.rmtree("meteor/ceh/")
        print("Создаём директорию для выгрузки таблиц...")
        os.mkdir("meteor/ceh/")

    except FileNotFoundError as e:
        print("Ошибка! Директория отсутствует:" + str(e) + "\nСоздаем директорию...")
        os.mkdir("meteor/ceh/")

    for mart in range(len(mart_list)):
        with open(str("meteor/ceh/" + mart_list[mart].get("mart_name") + ".yaml"), "w+", encoding="utf-8") as f:
            f.write(
                str(ceh_template.render(
                    ceh_mart_naming = mart_list[mart].get("mart_name"),
                    mart_content = mart_list[mart].get("attributes"),
                    hash_fields = [
                        attr["attribute_name"]
                        for attr in mart_list[mart]["attributes"]
                    ]
                ))
            )

parse_mart_props (
    input_data,
    "Sheet2"
)

parse_db_table_props (
    input_data,
    "Sheet1"
)

generate_flows()
