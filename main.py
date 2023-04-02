import os
import sys

import pandas as pd
from loguru import logger
from ocr_vat_invoice import main as vat_invoice_main
from orc_online_taxi_itinerary import main as online_taxi_itinerary_main
from configparser import ConfigParser

logger.remove()
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
logger.add("logs/main_{time}.log", level="DEBUG")

def merge_vat_invoice_online_taxi_itinerary():
    config_parser = ConfigParser()
    config_parser.read("config.cfg")
    config = config_parser["default"]
    BASE_PATH = config["BASE_PATH"]
    OUT_FILE_NAME = config["OUT_FILE_NAME"]
    SHEET_NAME = config["SHEET_NAME"]

    config_part1 = config_parser["vat_invoice"]
    vat_invoice_out_file_name = config_part1["vat_invoice_out_file_name"]
    vat_invoice_df = pd.read_excel(BASE_PATH + os.sep + vat_invoice_out_file_name)

    config_part2 = config_parser["online_taxi_itinerary"]
    online_taxi_itinerary_out_file_name = config_part2["online_taxi_itinerary_out_file_name"]
    online_taxi_itinerary_df = pd.read_excel(BASE_PATH + os.sep + online_taxi_itinerary_out_file_name)

    merge_df = pd.merge(vat_invoice_df,online_taxi_itinerary_df, left_on='总金额', right_on='总金额')
    merge_df = merge_df.loc[:, ~merge_df.columns.str.contains('Unnamed')] # 删除Unnamed
    merge_df

    merge_df.to_excel(BASE_PATH + os.sep + OUT_FILE_NAME, sheet_name=SHEET_NAME)


def main():
    logger.info("Start...")

    vat_invoice_main()

    online_taxi_itinerary_main()

    merge_vat_invoice_online_taxi_itinerary()

    logger.info("End...")


if __name__ == '__main__':
    main()
