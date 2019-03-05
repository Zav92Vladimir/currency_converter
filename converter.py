import sys
import logging
import argparse
import urllib.request
from typing import Optional
from xml.etree import ElementTree
from decimal import Decimal, ROUND_DOWN


class Converter:

    def __init__(self, list_args: Optional[list] = None):

        self.init_args(list_args)
        self.file_logger = self.get_logger("file_logger", self.args.LOGS, "file")
        self.output_logger = self.get_logger("output_logger", self.args.LOGS, "stream")

    def init_args(self, list_args: Optional[list] = None) -> None:

        if not sys.stdin.isatty():  # determining if was launched not via the console
            sys.argv.extend(["--USD", "2"])

        parser = argparse.ArgumentParser(description="Convert USD to RUB.")
        parser.add_argument("--USD", required=True, help='amount of USD')
        parser.add_argument("--LOGS", default="info", help='set logging level',
                            choices=["debug", "info", "warning", "error", "critical"])
        self.args = parser.parse_args(list_args)
        try:
            self.args.USD = float(self.args.USD)
            assert self.args.USD > 0
        except:
            raise Exception("USD value must be positive number!!!")

    def get_logger(self, name: str, log_level: str, handler_type: str) -> logging.Logger:

        handlers = {
            "file": logging.FileHandler("converter.log"),
            "stream": logging.StreamHandler()
        }

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(name)
        handler = handlers[handler_type]
        if handler_type == "file":
            handler.setFormatter(formatter)
        logger.setLevel(getattr(logging, log_level.upper()))
        logger.addHandler(handler)

        return logger

    def get_currency_xml(self) -> bytes:

        url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        self.file_logger.info("sending request to {0}".format(url))
        response = urllib.request.urlopen(url)
        assert response.status == 200, "bad response status code!!!"
        xml = response.read()
        assert xml, "response content is empty!!!"
        self.file_logger.info("received not empty response content with status code 200")
        return xml

    def parse_xml(self, xml: bytes) -> Decimal:

        root = ElementTree.fromstring(xml)
        try:
            rates = {rate.attrib["currency"]: rate.attrib["rate"] for rate in root[2][0]
                     if rate.attrib["currency"] in ("USD", "RUB")}
            assert rates.get("USD") and rates.get("RUB")
        except:
            raise Exception("got an unexpected response content!!!")
        usd_rub_rate = Decimal(1) / Decimal(rates["USD"]) * Decimal(rates["RUB"])
        usd_rub_rate = usd_rub_rate.quantize(Decimal('.0001'), rounding=ROUND_DOWN)
        return usd_rub_rate

    def run(self) -> None:

        usd = self.args.USD
        xml = self.get_currency_xml()
        usd_rub_rate = self.parse_xml(xml)
        rub = Decimal(usd) * usd_rub_rate
        rub = rub.quantize(Decimal('.01'), rounding=ROUND_DOWN)
        self.file_logger.info("USD input: {0}; RUB output: {1}".format(usd, rub))
        self.output_logger.info(rub)


if __name__ == "__main__":
    converter = Converter()
    try:
        converter.run()
    except Exception as exp:
        output = "{0}. {1}".format(type(exp).__name__, exp)
        converter.file_logger.error(output)
        converter.output_logger.error(output)
