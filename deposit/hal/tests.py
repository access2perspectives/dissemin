# -*- encoding: utf-8 -*-

# Dissemin: open access policy enforcement tool
# Copyright (C) 2014 Antonin Delpeuch
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#



import os
import responses
from unittest import expectedFailure, skip
from django.test import TestCase

from deposit.hal.metadata import AOFRFormatter
from deposit.hal.protocol import HALProtocol
from deposit.tests.test_protocol import ProtocolTest
from deposit.models import DepositRecord
from deposit.models import Repository
from papers.models import Paper
from papers.models import OaiRecord
from upload.models import UploadedPDF
from backend.oai import OaiPaperSource
from backend.translators import BASEDCTranslator


class AOFRTest(TestCase):

    def setUp(self):
        super(AOFRTest, self).setUp()

        # This currently fails and is unused

        #xsd_fname = path.join(path.dirname(__file__), 'aofr-sword.xsd')
        # with open(xsd_fname, 'r') as f:
        #   elem = etree.parse(f)
        #   cls.xsd = etree.XMLSchema(elem)

    def test_generate_metadata_doi(self):
        # f =
        AOFRFormatter()
        dois = ['10.1175/jas-d-15-0240.1']
        for doi in dois:
            Paper.create_by_doi(doi)
            #form = TODO
            #rendered = f.render(p, 'article.pdf', form)
            # with open('/tmp/xml_validation.xml', 'w') as f:
            #    f.write(etree.tostring(rendered, pretty_print=True))
            # XSD validation currently fails
            # self.xsd.assertValid(rendered)

class TopicPredictionTest(TestCase):
    def setUp(self):
        self.protocol = HALProtocol(repository=Repository())

    @responses.activate
    def test_predict_topic(self):
        text = 'A complete model for faceted dataflow programs'
        expected_response = {
            "results": [
                {
                "label": "Computer science",
                "score": 0.8055065870285034,
                "uri": "https://aurehal.archives-ouvertes.fr/domain/INFO"
                },
                {
                "label": "Cognitive science",
                "score": 0.09652446210384369,
                "uri": "https://aurehal.archives-ouvertes.fr/domain/SCCO"
                },
                {
                "label": "Statistics",
                "score": 0.02962828427553177,
                "uri": "https://aurehal.archives-ouvertes.fr/domain/STAT"
                }
            ]
        }
        responses.add(responses.POST, 'https://annif.dissem.in/v1/projects/hal-fasttext/suggest', json=expected_response)

        self.assertEqual(self.protocol.predict_topic(text), 'INFO')

    @responses.activate
    def test_predict_empty_text(self):
        self.assertEqual(self.protocol.predict_topic(''), None)


@skip("""
HAL tests are currently disabled because of deletion issues in
hal-preprod. Feel free to reactivate once this has been solved.
(2017-10-23)
""")
class HALProtocolTest(ProtocolTest):
    def setUp(self):
        super(HALProtocolTest, self).setUp()
        self.setUpForProtocol(HALProtocol, Repository(
            username='test_ws',
            password='test',
            endpoint='https://api-preprod.archives-ouvertes.fr/sword/'))

    def test_encode(self):
        self.assertEqual(self.proto.encodeUserData(), b'Basic dGVzdF93czp0ZXN0')

    @expectedFailure
    def test_lncs_many_authors(self):
        """
        Submit a paper from LNCS (type: book-chapter).
        This fails with the default test account because
        it does not have the right to deposit with only one
        affiliation.
        """
        # the DOI below should *not* already exist in HAL
        # so it may need to be changed if the test fails
        p = Paper.create_by_doi('10.1007/978-3-319-63342-8_1')
        r = self.dry_deposit(p,
            abstract='this is an abstract',
            topic='INFO',
            depositing_author=0,
            affiliation=59704) # ENS
        self.assertEqualOrLog(r.status, 'faked')

    def test_lncs(self):
        """
        Same as test_lncs but with only one author
        """
        p = Paper.create_by_doi('10.1007/978-3-319-63342-8_1')
        p.authors_list = [p.authors_list[0]]
        r = self.dry_deposit(p,
            abstract='this is an abstract',
            topic='INFO',
            depositing_author=0,
            affiliation=59704) # ENS
        self.assertEqualOrLog(r.status, 'faked')


    def test_lics(self):
        """
        Submit a paper from LICS (type: conference-proceedings)
        """
        p = Paper.create_by_doi('10.1109/lics.2015.37')
        p.authors_list = [p.authors_list[0]]
        r = self.dry_deposit(p,
             abstract='here is my great result',
             topic='NLIN',
             depositing_author=0,
             affiliation=128940)
        self.assertEqualOrLog(r.status, 'faked')

    def test_journal_article(self):
        """
        Submit a journal article
        """
        p = Paper.create_by_doi('10.1016/j.agee.2004.10.001')
        p.authors_list = [p.authors_list[0]]
        r = self.dry_deposit(p,
             abstract='here is my great result',
             topic='SDV',
             depositing_author=0,
             affiliation=128940)
        self.assertEqualOrLog(r.status, 'faked')

    def test_topic_set_to_other(self):
        """
        Submit a journal article with "OTHER" as topic,
        which is forbidden by HAL
        """
        p = Paper.create_by_doi('10.1016/j.agee.2004.10.001')
        self.proto.init_deposit(p, self.user)

        # the user is presented with initial data
        args = self.proto.get_form_initial_data()
        # they fill the form with an invalid topic
        form_fields = {'abstract':'here is my great result',
             'topic':'OTHER',
             'depositing_author':0,
             'affiliation':128940}
        args.update(form_fields)

        # the form should reject the "OTHER" topic
        form = self.proto.get_bound_form(args)
        self.assertFalse(form.is_valid())

    def test_keywords(self):
        """
        Keywords are mandatory
        """
        p = Paper.create_by_doi('10.1007/s00268-016-3429-x')
        p.authors_list = [p.authors_list[0]]
        r = self.dry_deposit(p,
            abstract='bla ble bli blo blu',
            topic='SDV',
            depositing_author=0,
            affiliation=128940)
        self.assertEqualOrLog(r.status, 'faked')

    def test_preprint(self):
        """
        Submit a preprint
        """
        oai = OaiPaperSource(self.oaisource)
        oai.add_translator(BASEDCTranslator(self.oaisource))
        p = oai.create_paper_by_identifier('ftarxivpreprints:oai:arXiv.org:1207.2079', 'base_dc')
        p.authors_list = [p.authors_list[0]]
        r = self.dry_deposit(p,
             abstract='here is my great result',
             topic='SDV',
             depositing_author=0,
             affiliation=128940)
        self.assertEqualOrLog(r.status, 'faked')

    def test_bad_journal_article(self):
        """
        Submit something that pretends to be a journal article,
        but for which we fail to find publication metadata.
        The interface should fall back on something lighter.
        """
        oai = OaiPaperSource(self.oaisource)
        oai.add_translator(BASEDCTranslator(self.oaisource))
        p = oai.create_paper_by_identifier(
            'ftalborguniv:oai:pure.atira.dk:openaire/30feea10-9c2f-11db-8ed6-000ea68e967b',
            'base_dc')
        p.authors_list = [p.authors_list[0]]
        p.doctype = 'journal-article'
        p.save()
        r = self.dry_deposit(p,
            abstract='hey you, yes you',
            topic='SDV',
            depositing_author=0,
            affiliation=128940)
        self.assertEqualOrLog(r.status, 'faked')

    def test_paper_already_in_hal(self):
        p = Paper.create_by_hal_id(
            'hal-01062241v1')
        enabled = self.proto.init_deposit(p, self.user)
        self.assertFalse(enabled)

    def test_refresh_deposit_status(self):
        # This is the identifier of a paper which should
        # currently be published on HAL preprod
        hal_id = 'hal-01211282'
        # First, fake the deposition of a paper
        p = Paper.create_by_doi('10.1109/lics.2015.37')
        r = OaiRecord.new(source=self.repo.oaisource,
                        identifier='deposition:1:'+hal_id,
                        splash_url='https://hal-preprod.archives-ouvertes.fr/'+hal_id,
                        pdf_url=None,
                        about=p)
        f = UploadedPDF.objects.create(
                user=self.user,
                orig_name='File.pdf',
                file=os.path.join(self.testdir, 'testdata/blank.pdf'),
                thumbnail='my_thumbnail.png')
        d = DepositRecord.objects.create(
                paper=p,
                oairecord=r,
                repository=self.repo,
                user=self.user,
                status='pending',
                identifier=hal_id,
                upload_type='postprint',
                file=f)
        self.proto.refresh_deposit_status(d)
        self.assertEqual(d.status, 'published')
        self.assertTrue(r.pdf_url)

    def test_get_new_status(self):
        cases = {
            'tel-01584471':'published',
            'hal-01038374':'deleted',
            # the document below should have "pending" status on hal-preprod
            # and may need to be updated if the preprod database is reset
            'hal-01587501':'pending',
        }
        for identifier in cases:
            self.assertEqual(self.proto.get_new_status(identifier),
                            cases[identifier])

    def test_paper_already_in_hal_but_not_in_dissemin(self):
        """
        In this case, Dissemin missed the paper on HAL
        (for some reason) and so the deposit interface was
        enabled. But HAL refuses the deposit! We have to
        give a good error message to the user.
        """
        # this paper is currently in HAL-preprod
        p = Paper.create_by_doi('10.1051/jphys:01975003607-8060700')

        # this is just to make sure that we are depositing with
        # a single author (otherwise, the deposit would fail because
        # we are not providing enough affiliations).
        p.authors_list = [p.authors_list[0]]

        r = self.dry_deposit(p,
            abstract='this is an abstract',
            topic='INFO',
            depositing_author=0,
            affiliation=59704) # ENS

        # Deposit fails: a duplicate is found
        self.assertEqualOrLog(r.status, 'failed')

        # The error message should be specific
        self.assertTrue('already in HAL' in r.message)

    def test_on_behalf_of(self):
        # Set on-behalf-of to some user
        # Currently we are using "test_ws" as deposit account
        preferences = self.proto.get_preferences(self.user)
        preferences.on_behalf_of = 'dissemin_test'
        preferences.save()

        # the DOI here should *not* already exist in HAL
        # so it may need to be changed if the test fails
        p = Paper.create_by_doi('10.1007/978-3-319-63342-8_1')
        p.authors_list = [p.authors_list[0]]
        r = self.dry_deposit(p,
            abstract='this is an abstract',
            topic='INFO',
            depositing_author=0,
            affiliation=59704) # ENS
        self.assertEqualOrLog(r.status, 'faked')


