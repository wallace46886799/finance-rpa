import base64
import urllib
import requests
import json
import os
import sys
from configparser import ConfigParser
from loguru import logger
import pandas as pd
import glob

logger.remove()
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
logger.add("logs/vat_invoice_{time}.log", level="DEBUG")


def main():
    logger.info("Start vat invoice...")
    config_parser = ConfigParser()
    config_parser.read("config.cfg")
    config = config_parser["default"]
    API_KEY = config["API_KEY"]
    SECRET_KEY = config["SECRET_KEY"]
    BASE_PATH = config["BASE_PATH"]


    config_part = config_parser["vat_invoice"]
    vat_invoice_url = config_part["vat_invoice_url"]
    vat_invoice_surfix = config_part["vat_invoice_surfix"]
    vat_invoice_sheet = config_part["vat_invoice_sheet"]
    OUT_FILE_NAME = config_part["vat_invoice_out_file_name"]

    url = vat_invoice_url + get_access_token(API_KEY, SECRET_KEY)

    sub_dirs = os.listdir(BASE_PATH)

    vat_invoice_kvs = []

    for sub_dir in sub_dirs:

        for file_name in glob.glob(BASE_PATH + os.sep + sub_dir + os.sep + vat_invoice_surfix):
            payload = get_file_content_as_base64(file_name, True)

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data="pdf_file=" + payload)

            response_text = response.text
            logger.debug(response_text)

            # parse x:
            response_json = json.loads(response_text)

            # {
            #     "log_id": "5425496231209218858",
            #     "words_result_num": 35,
            #     "words_result": {
            #         "ServiceType": "其他",
            #         "InvoiceNum": "14641426",
            #         "InvoiceNumConfirm": "14641426",
            #         "SellerName": "上海易火广告传媒有限公司",
            #         "CommodityTaxRate": [
            #             {
            #                 "word": "6%",
            #                 "row": "1"
            #             }
            #         ],
            #         "SellerBank": "中国银行南翔支行446863841354",
            #         "Checker": ":沈园园",
            #         "TotalAmount": "94339.62",
            #         "CommodityAmount": [
            #             {
            #                 "word": "94339.62",
            #                 "row": "1"
            #             }
            #         ],
            #         "InvoiceDate": "2016年06月02日",
            #         "CommodityTax": [
            #             {
            #                 "word": "5660.38",
            #                 "row": "1"
            #             }
            #         ],
            #         "PurchaserName": "百度时代网络技术(北京)有限公司",
            #         "CommodityNum": [
            #             {
            #                 "word": "",
            #                 "row": "1"
            #             }
            #         ],
            #         "Province": "上海",
            #         "City": "",
            #         "SheetNum": "第三联",
            #         "Agent": "否",
            #         "PurchaserBank": "招商银行北京分行大屯路支行8661820285100030",
            #         "Remarks": "告传",
            #         "Password": "074/45781873408>/6>8>65*887676033/51+<5415>9/32--852>1+29<65>641-5>66<500>87/*-34<943359034>716905113*4242>",
            #         "SellerAddress": ":嘉定区胜辛南路500号15幢1161室55033753",
            #         "PurchaserAddress": "北京市海淀区东北旺西路8号中关村软件园17号楼二属A2010-59108001",
            #         "InvoiceCode": "3100153130",
            #         "InvoiceCodeConfirm": "3100153130",
            #         "CommodityUnit": [
            #             {
            #                 "word": "",
            #                 "row": "1"
            #             }
            #         ],
            #         "Payee": ":徐蓉",
            #         "PurchaserRegisterNum": "110108787751579",
            #         "CommodityPrice": [
            #             {
            #                 "word": "",
            #                 "row": "1"
            #             }
            #         ],
            #         "NoteDrawer": "沈园园",
            #         "AmountInWords": "壹拾万圆整",
            #         "AmountInFiguers": "100000.00",
            #         "TotalTax": "5660.38",
            #         "InvoiceType": "专用发票",
            #         "SellerRegisterNum": "913101140659591751",
            #         "CommodityName": [
            #             {
            #                 "word": "信息服务费",
            #                 "row": "1"
            #             }
            #         ],
            #         "CommodityType": [
            #             {
            #                 "word": "",
            #                 "row": "1"
            #             }
            #         ],
            #         "CommodityPlateNum": [],
            #         "CommodityVehicleType": [],
            #         "CommodityStartDate": [],
            #         "CommodityEndDate": [],
            #         "OnlinePay": "",
            #     }
            # }
            logger.debug(response_json)

            vat_invoice_kv = {}
            logger.debug("TotalAmount：{}", response_json["words_result"]["TotalAmount"])
            vat_invoice_kv["TotalAmount"] = response_json["words_result"]["TotalAmount"]

            logger.debug("InvoiceDate：{}", response_json["words_result"]["InvoiceDate"])
            vat_invoice_kv["InvoiceDate"] = response_json["words_result"]["InvoiceDate"]

            logger.debug("InvoiceCode：{}", response_json["words_result"]["InvoiceCode"])
            vat_invoice_kv["InvoiceCode"] = response_json["words_result"]["InvoiceCode"]

            logger.debug("PurchaserName：{}", response_json["words_result"]["PurchaserName"])
            vat_invoice_kv["PurchaserName"] = response_json["words_result"]["PurchaserName"]

            logger.debug("PurchaserRegisterNum：{}", response_json["words_result"]["PurchaserRegisterNum"])
            vat_invoice_kv["PurchaserRegisterNum"] = response_json["words_result"]["PurchaserRegisterNum"]

            logger.debug("AmountInFiguers：{}", response_json["words_result"]["AmountInFiguers"])
            vat_invoice_kv["AmountInFiguers"] = response_json["words_result"]["AmountInFiguers"]

            logger.debug("SellerName：{}", response_json["words_result"]["SellerName"])
            vat_invoice_kv["SellerName"] = response_json["words_result"]["SellerName"]

            logger.debug("ServiceType：{}", response_json["words_result"]["ServiceType"])
            vat_invoice_kv["ServiceType"] = response_json["words_result"]["ServiceType"]

            logger.debug("InvoiceTypeOrg：{}", response_json["words_result"]["InvoiceTypeOrg"])
            vat_invoice_kv["InvoiceTypeOrg"] = response_json["words_result"]["InvoiceTypeOrg"]

            vat_invoice_kvs.append(vat_invoice_kv)

    vat_invoice_df = pd.DataFrame(vat_invoice_kvs)

    vat_invoice_df = vat_invoice_df.rename(columns={
            'InvoiceDate': '开票日期',
            'TotalAmount': '总金额',
            'AmountInFiguers': '价税合计',
            'InvoiceCode': '发票代码',
            'PurchaserName': '购方名称',
            'PurchaserRegisterNum': '购方纳税人识别号',
            'SellerName': '销售方名称',
            'ServiceType': '发票消费类型',
            'InvoiceTypeOrg': '发票名称'
        }
    )

    # writer = pd.ExcelWriter(BASE_PATH + os.sep + OUT_FILE_NAME, engine='openpyxl')  # 可以向不同的sheet写入数据
    # book = load_workbook(BASE_PATH + os.sep + OUT_FILE_NAME)
    # writer.book = book
    # vat_invoice_df.to_excel(writer, sheet_name=vat_invoice_sheet, index=True)  # 将数据写入excel中的sheet2表,sheet_name改变后即是新增一个sheet
    # writer.save()  # 保存
    #
    vat_invoice_df.to_excel(BASE_PATH + os.sep + OUT_FILE_NAME, sheet_name=vat_invoice_sheet, index=True)
    logger.info("End vat invoice...")


def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content


def get_access_token(API_KEY, SECRET_KEY):
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


if __name__ == '__main__':
    main()
