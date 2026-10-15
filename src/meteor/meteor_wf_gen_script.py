import os
from logging import Formatter

import pandas as pd
from dotenv import load_dotenv
from jinja2 import FileSystemLoader, Environment
import shutil
import logging
import dotenv

env = dotenv.load_dotenv("D:\\PycharmProjects\\flowgen-script\\meteor\\config\\.env")
load_dotenv()

logger = logging.getLogger(__name__)

ch = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


# 'excel'-файл со всеми требованиями и маппингами
input_data = os.getenv("INPUT_DATA")

# Директория с выводом потоков
output_data = os.getenv("OUTPUT_DATA")

mart_list: list[dict] = []
wf_list = []
table_list = []

file_template = FileSystemLoader(os.getenv("TEMPLATE_DIRECTORY"))

jinja_env = Environment(loader=file_template)

# Файл-шаблон по которому будет строиться wf
template = jinja_env.get_template("wf_fm_template.yaml")


def parse_ceh_excel(filename: str, sheet: str) -> None:
    df = pd.read_excel(filename, sheet_name=sheet, index_col=False)
    for row in df.itertuples(index=False):
        mart = next((
            item
            for item in mart_list
            if item.get("table") == row.__getattribute__("table")
        ), None)

        if mart is None:
            mart = {
                "table_name": row.table,
                "table_name_upper": row.table.upper()
            }
            logger.info("Был добавлен объект: " + row.table)
            mart_list.append(mart)
            wf_list.append("wf_raw_data_mrod_" + row.table)

    logger.info("Всего объектов к генерации: " + str(len(mart_list)))


def generate_flows() -> None:
    try:
        logger.info("Очищаем директорию с потоками")
        shutil.rmtree(output_data)
        logger.info("Создаём директорию для выгрузки потоков")
        os.mkdir(output_data)
    except FileNotFoundError as e:
        logger.info("Ошибка! Директория отсутствует:" + str(e) + "\nСоздаем директорию")
        os.mkdir(output_data)

    for mart in range(len(mart_list)):
        logger.info("Создаём файл потока: " + wf_list[mart])
        with open(str(output_data + wf_list[mart] + "_fm_s3.yaml"), "w+", encoding="utf-8") as f:
            f.write(
                template.render(
                    wf_name=wf_list[mart] + "_fm_s3",
                    table_name=mart_list[mart]["table_name"],
                    table_name_upper=mart_list[mart]["table_name_upper"],
                    ceh_source=mart_list[mart],
                    wf_tag=wf_list[mart] + "_fm_s3",
                )
            )


parse_ceh_excel(input_data, "Sheet1")
generate_flows()
