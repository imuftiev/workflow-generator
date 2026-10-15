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
db_table_template = env.get_template("db_table_template.yaml.yaml")

db_tables_list: list[str] = []
mart_list: list[dict] = []
mart_dict = {}

def parse_excel(filename: str, sheets: list[str]) -> None:
    for sheet in sheets:
        if sheet == "Sheet2":
            df = pd.read_excel(filename, sheet_name=sheet)
            for row in df.itertuples(index=False):
                mart = next((item for item in mart_list if row.__getattribute__("mart_name") == item.get("mart_name")),
                            None)

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
            print("Всего маппингов к генерации: " + str(len(mart_list)))

        else:
            df = pd.read_excel(filename, sheet_name=sheet)
            for row in df.itertuples(index=False):
                db_tables_list.append(str(row.table))

def generate_flows():
    try:
        print("Очищаем директорию с маппингами...")
        shutil.rmtree("meteor/ceh/")
        shutil.rmtree("meteor/db_table/")
        print("Создаём директорию для выгрузки маппингов...")
        os.mkdir("meteor/ceh/")
        os.mkdir("meteor/db_table/")

    except FileNotFoundError as e:
        print("Ошибка! Директория отсутствует:" + str(e) + "\nСоздаем директорию...")
        os.mkdir("meteor/db_table/")

    for mart in range(len(mart_list)):
        with open(str("meteor/db_table/2204_sfobo_export_rmb_tech_" + db_tables_list[mart] + ".yaml"), "w+", encoding="utf-8") as db_f:
            db_f.write(
                str(
                    db_table_template.render(
                        db_table_source = db_tables_list[mart],
                        columns = mart_list[mart].get("attributes")
                    )
                )
            )

        with open(str("meteor/ceh/" + mart_list[mart].get("mart_name") + ".yaml"), "w+", encoding="utf-8") as ceh_f:
            ceh_f.write(
                str(ceh_template.render(
                    ceh_mart_naming = mart_list[mart].get("mart_name"),
                    mart_content = mart_list[mart].get("attributes"),
                    hash_fields = [
                        attr["attribute_name"]
                        for attr in mart_list[mart]["attributes"]
                    ]
                ))
            )

parse_excel (
    input_data,
    ["Sheet2","Sheet1"]
)

generate_flows()
