import pytest

from lxml import etree
from deposit.sword.protocol import SWORDMETSProtocol

@pytest.mark.usefixtures('sword_mets_protocol')
class TestSWORDMETSProtocol(object):
    """
    A test class for named protocol
    """
    @pytest.mark.skip(reason="I don't need that?!")
    def  test_repr(self):
        """
        Tests the representation of class and object
        """
        pass

    @pytest.mark.skip(reason="I don't need that?!")
    def test_str(self):
        """
        Tests the string output of class and object
        """
        pass

    def test_get_mets(self, mets_xsd, metadata_xml_dc):
        """
        A test for creating mets from metadata
        """
        mets_xml = SWORDMETSProtocol._get_mets(metadata_xml_dc)
        # Because of the xml declaration we have to convert to a bytes object
        mets_xsd.assertValid(etree.fromstring(bytes(mets_xml, encoding='utf-8')))


    @pytest.mark.skip(reason="Tests not fully implemented. Fixtures missing. Mocking missing.")
    def test_get_mets_container(self):
        """
        A test for creating a mets container
        """
        pass

    @pytest.mark.skip(reason="Tests not fully implemented. Fixtures missing. Mocking missing.")
    def test_submit_deposit(self):
        """
        A test for submit deposit. This test is called multiple times with a lot of fixtures
        """
        pass


