import logging
import argparse
import urllib.request
from typing import Optional
from xml.etree import ElementTree
from decimal import Decimal, ROUND_DOWN


class Converter:

    def __init__(self):

        logging.basicConfig(filename="converter.log", level=logging.INFO)
        self.parser = argparse.ArgumentParser(description="Convert USD to RUB.")
        self.parser.add_argument("--USD", required=True, help='amount of USD')

    def get_currency_xml(self) -> bytes:

        url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        response = urllib.request.urlopen(url)
        xml = response.read()
        return xml

    def parse_xml(self, xml: bytes) -> Decimal:

        root = ElementTree.fromstring(xml)
        rates = {rate.attrib["currency"]: rate.attrib["rate"] for rate in root[2][0]
                 if rate.attrib["currency"] in ("USD", "RUB")}
        usd_rub_rate = Decimal(1) / Decimal(rates["USD"]) * Decimal(rates["RUB"])
        usd_rub_rate = usd_rub_rate.quantize(Decimal('.0001'), rounding=ROUND_DOWN)
        return usd_rub_rate

    def get_usd_amount(self, list_args: Optional[list] = None) -> float:

        args = self.parser.parse_args(list_args)
        try:
            usd = float(args.USD)
            assert usd > 0
        except:
            raise Exception("USD value must be positive number!!!")
        return usd

    def run(self) -> None:

        usd = self.get_usd_amount()
        xml = self.get_currency_xml()
        usd_rub_rate = self.parse_xml(xml)
        rub = Decimal(usd) * usd_rub_rate
        rub = rub.quantize(Decimal('.01'), rounding=ROUND_DOWN)
        logging.info("USD input: {0}; RUB output: {1}".format(usd, rub))
        print(rub)


if __name__ == "__main__":
    converter = Converter()
    try:
        converter.run()
    except Exception as exp:
        output = "{0}. {1}".format(type(exp).__name__, exp)
        logging.error(output)
        print(output)
