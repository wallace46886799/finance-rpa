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
logger.add("logs/online_taxi_itinerary_{time}.log", level="DEBUG")


def main():
    logger.info("Start online taxi itinerary...")
    config_parser = ConfigParser()
    config_parser.read("config.cfg")
    config = config_parser["default"]
    API_KEY = config["API_KEY"]
    SECRET_KEY = config["SECRET_KEY"]
    BASE_PATH = config["BASE_PATH"]

    config_part = config_parser["online_taxi_itinerary"]
    online_taxi_itinerary_url = config_part["online_taxi_itinerary_url"]
    online_taxi_itinerary_surfix = config_part["online_taxi_itinerary_surfix"]
    online_taxi_itinerary_sheet = config_part["online_taxi_itinerary_sheet"]
    OUT_FILE_NAME = config_part["online_taxi_itinerary_out_file_name"]

    url = online_taxi_itinerary_url + get_access_token(API_KEY, SECRET_KEY)

    sub_dirs = os.listdir(BASE_PATH)

    online_taxi_itinerary_kvs = []

    for sub_dir in sub_dirs:

        for file_name in glob.glob(BASE_PATH + os.sep + sub_dir + os.sep + online_taxi_itinerary_surfix):
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
            online_taxi_itinerary_kv = {}
            logger.debug("TotalFare", response_json["words_result"]["TotalFare"])
            online_taxi_itinerary_kv["TotalFare"] = response_json["words_result"]["TotalFare"]

            logger.debug("ServiceProvider", response_json["words_result"]["ServiceProvider"])
            online_taxi_itinerary_kv["ServiceProvider"] = response_json["words_result"]["ServiceProvider"]

            logger.debug("StartPlace", response_json["words_result"]["items"][0]["StartPlace"])
            online_taxi_itinerary_kv["StartPlace"] = response_json["words_result"]["items"][0]["StartPlace"]

            logger.debug("PickupTime", response_json["words_result"]["items"][0]["PickupTime"])
            online_taxi_itinerary_kv["PickupTime"] = response_json["words_result"]["items"][0]["PickupTime"]

            # logger.debug("CarType", response_json["words_result"]["items"][0]["CarType"])
            # online_taxi_itinerary_kv["CarType"] = response_json["words_result"]["items"][0]["CarType"]

            logger.debug("City", response_json["words_result"]["items"][0]["City"])
            online_taxi_itinerary_kv["City"] = response_json["words_result"]["items"][0]["City"]

            # logger.debug("Distance", response_json["words_result"]["items"][0]["Distance"])
            # online_taxi_itinerary_kv["Distance"] = response_json["words_result"]["items"][0]["Distance"]

            logger.debug("PickupDate", response_json["words_result"]["items"][0]["PickupDate"])
            online_taxi_itinerary_kv["PickupDate"] = response_json["words_result"]["items"][0]["PickupDate"]

            logger.debug("DestinationPlace", response_json["words_result"]["items"][0]["DestinationPlace"])
            online_taxi_itinerary_kv["DestinationPlace"] = response_json["words_result"]["items"][0]["DestinationPlace"]

            logger.debug("Fare:{}", response_json["words_result"]["items"][0]["Fare"])
            online_taxi_itinerary_kv["Fare"] = response_json["words_result"]["items"][0]["Fare"]

            online_taxi_itinerary_kvs.append(online_taxi_itinerary_kv)

    online_taxi_itinerary_df = pd.DataFrame(online_taxi_itinerary_kvs)

    online_taxi_itinerary_df = online_taxi_itinerary_df.rename(columns={
        'PickupTime': '上车时间',
        'PickupDate': '上车日期',
        'TotalFare': '总金额',
        'Fare': '金额',
        'ServiceProvider': '服务商',
        'StartPlace': '起点',
        'DestinationPlace': '终点',
        # 'CarType': '车型',
        'City': '城市'
        # 'Distance': '里程'
        }
    )

    online_taxi_itinerary_df.to_excel(BASE_PATH + os.sep + OUT_FILE_NAME, sheet_name=online_taxi_itinerary_sheet,
                                      index=True)

    logger.info("End online taxi itinerary...")


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
