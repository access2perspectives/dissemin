import json
import os
import pytest


from deposit.models import License
from deposit.models import LicenseChooser
from deposit.tests.test_protocol import MetaTestProtocol
from dissemin.settings import BASE_DIR
from papers.models import Paper
from papers.models import Researcher


author_one =  [{
    'name': {
        'full': 'herbert quain',
        'first': 'Herbert',
        'last': 'Quain',
    },
    'orcid' : None
}]

author_two = [{
    'name': {
        'full': 'aristoteles',
        'first': 'Aristoteles',
        'last': 'Stageira'
    },
    'orcid': None,
}]


@pytest.mark.usefixtures('dark_archive_protocol')
class TestDarkArchiveProtocol(MetaTestProtocol):
    """
    A test class for named protocol
    """

    @pytest.mark.write_darkarchive_examples
    def test_write_dark_archive_examples(self, db, upload_data, user_leibniz):
        """
        This is not really a test. It just outputs metadata examples that the protocol generates.
        Ususally this test is omitted, you can run it explicetely with "-m write_darkarchive_examples".
        In case of changes of the protocol or repository, you should run this function, but make sure it's up to date
        """
        self.protocol.paper = upload_data['paper']
        self.protocol.user = user_leibniz

        Researcher.create_by_name(
            user=user_leibniz,
            first=user_leibniz.first_name,
            last=user_leibniz.last_name,
            orcid="2543-2454-2345-234X",
        )

        # Set form data
        data = dict()
        if upload_data['oairecord'].description is not None:
            data['abstract'] = upload_data['oairecord'].description
        else:
            data['abstract'] = upload_data['abstract']

        l = License.objects.get(uri="https://creativecommons.org/licenses/by/4.0/")
        lc = LicenseChooser.objects.create(
            license=l,
            repository=self.protocol.repository,
            transmit_id='cc_by-40'
        )
        licenses = LicenseChooser.objects.by_repository(repository=self.protocol.repository)
        data['license'] = lc.pk

        form = self.protocol.form_class(licenses=licenses, data=data)
        form.is_valid()

        md = self.protocol._get_metadata(form)

        f_path = os.path.join(BASE_DIR, 'doc', 'sphinx', 'examples', 'darkarchive')
        f_name = os.path.join(f_path, upload_data['load_name'] + '.json')
        os.makedirs(f_path, exist_ok=True)
        with open(f_name, 'w') as fout:
            json.dump(md, fout, indent=4)


    @pytest.mark.xfail
    def test_protocol_registered(self):
        pass


    @pytest.mark.parametrize('authors_list', [author_one, author_one + author_two])
    def test_get_authors_single_author(self, authors_list):
        """
        Tests if authors are generated accordingly
        """
        self.protocol.paper = Paper.objects.create(authors_list=authors_list, pubdate='2014-01-01')

        authors = self.protocol._get_authors()

        assert isinstance(authors, list)
        assert len(authors) == len(authors_list)
        for idx, author in enumerate(authors):
            assert author['first'] == authors_list[idx]['name']['first']
            assert author['last'] == authors_list[idx]['name']['last']
            assert author['orcid'] == authors_list[idx]['orcid']


    @pytest.mark.parametrize('eissn', [None, '2343-2345'])
    def test_get_eissn(self, dummy_oairecord, dummy_journal, eissn):
        """
        Tests if the correct eissn / essn is returned
        """
        dummy_journal.essn = eissn
        dummy_journal.save()
        dummy_oairecord.journal = dummy_journal
        dummy_oairecord.save()
        self.protocol.publication = dummy_oairecord

        assert self.protocol._get_eissn() == eissn


    def test_get_eissn_no_journal(self, dummy_oairecord):
        """
        If no journal, expect None
        """
        self.protocol.publication = dummy_oairecord

        assert self.protocol._get_eissn() == None


    @pytest.mark.parametrize('issn', [None, '2343-2345'])
    def test_get_issn(self, dummy_oairecord, dummy_journal, issn):
        """
        Tests if the correct eissn / essn is returned
        """
        dummy_journal.issn = issn
        dummy_journal.save()
        dummy_oairecord.journal = dummy_journal
        dummy_oairecord.save()
        self.protocol.publication = dummy_oairecord

        assert self.protocol._get_issn() == issn


    def test_get_issn_no_journal(self, dummy_oairecord):
        """
        If no journal, expect None
        """
        self.protocol.publication = dummy_oairecord

        assert self.protocol._get_issn() == None


    def test_get_license(self, license_standard):
        """
        Function should return a dict with license name, URI and transmit_id for given LicenseChooser object
        """
        transmit_id = 'standard'
        lc = LicenseChooser.objects.create(
            license=license_standard,
            repository=self.protocol.repository,
            transmit_id=transmit_id,
        )

        l = self.protocol._get_license(lc)

        assert isinstance(l, dict) == True
        assert l.get('name') == license_standard.name
        assert l.get('uri') == license_standard.uri
        assert l.get('transmit_id') == transmit_id


    def test_get_metadata(self, upload_data, license_chooser, depositing_user):
        """
        Test if the metadata is correctly generated
        """
        self.protocol.paper = upload_data['paper']
        self.protocol.user = depositing_user

        # Set form data
        data = dict()
        if upload_data['oairecord'].description is not None:
            data['abstract'] = upload_data['oairecord'].description
        else:
            data['abstract'] = upload_data['abstract']

        if license_chooser:
            data['license'] = license_chooser.pk

        form = self.protocol.form_class(data=data)
        form.is_valid()

        md = self.protocol._get_metadata(form)

        md_fields = ['abstract', 'authors', 'date', 'depositor', 'doctype', 'doi', 'eissn', 'issn', 'issue', 'journal', 'page', 'publisher', 'title', 'volume', ]

        assert all(k in md for k in md_fields) == True


    def test_str(self):
        """
        Tests the string output
        """
        s = self.protocol.__str__()
        assert isinstance(s, str) == True