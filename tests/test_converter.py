from xml.etree import ElementTree
from converter import Converter


class TestConverter:

    def setup(self):
        self.converter = Converter(["--USD", "10"])

    def test_get_currency_xml(self):
        xml = self.converter.get_currency_xml()
        assert xml and isinstance(xml, bytes)
        root = ElementTree.fromstring(xml)
        rates = {rate.attrib["currency"]: rate.attrib["rate"] for rate in root[2][0]
                 if rate.attrib["currency"] in ("USD", "RUB")}
        assert rates.get("USD") and rates.get("RUB")

    def test_parse_xml(self):
        xml = b"""
        <gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01" xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">
            <gesmes:subject>Reference rates</gesmes:subject>
            <gesmes:Sender>
                <gesmes:name>European Central Bank</gesmes:name>
            </gesmes:Sender>
            <Cube>
                <Cube time="2019-03-01">
                    <Cube currency="USD" rate="1.1383"/>
                    <Cube currency="RUB" rate="74.9928"/>
                </Cube>
            </Cube>
        </gesmes:Envelope>
        """

        rate = self.converter.parse_xml(xml)
        assert float(rate) == 65.8814
