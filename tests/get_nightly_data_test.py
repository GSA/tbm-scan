import json
import os
import sys
import unittest
from unittest.mock import patch, Mock

from bs4 import BeautifulSoup
import responses
import requests
import requests_mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__) ) ) )
from utils.get_nightly_data import clean_line_text, get_email_from_url, extract_emails, \
    merge_dicts, id_and_count_notice_tags, pseudo_xml_to_json, get_nightly_data
from fixtures.nightly_file import nightly_file
from fixtures import pseudo_xml_to_json_expected


class GetNightlyDataTestCase(unittest.TestCase):
    '''
    Test cases for functions in utils/get_nightly_data.py
    '''
    
    def setUp(self):
        self.file_lines = nightly_file
        self.maxDiff = None

    def tearDown(self):
        self.file_lines = None

    def test_clean_line_text_garbage(self):
        '''
        See that it strips out garbage
        '''
        result = clean_line_text('&nbsp;\n')
        expected = ''
        self.assertEqual(result, expected)

    def test_clean_line_text_some_garbage(self):
        '''
        See that it strips out garbage
        '''
        text_to_clean = '<p style="MARGIN-BOTTOM: 0pt; LINE-HEIGHT: normal"><a name="OLE_LINK2"></a><a name="OLE_LINK1"><span style="mso-bookmark: OLE_LINK2"><span style="FONT-FAMILY: ">SOLICITATION FOR NSN:</span> </span></a><span style="mso-bookmark: OLE_LINK1"><span style="mso-bookmark: OLE_LINK2"><span style="FONT-FAMILY: ">2915009189013, 0076482892, GUIDE, SPRING, ONTIC (45934) P/N: 557568, FOB ORIGIN, INSPECTION/ACCEPTANCE AT DESTINATION. <span style="mso-spacerun: yes">&nbsp;</span>ONTIC IS THE ONLY APPROVED SOURCES FOR THIS ITEM.<span style="mso-spacerun: yes">&nbsp; </span>DLA DOES NOT CURRENTLY HAVE AN APPROVED TECHNICAL DATA PACKAGE AVAILABLE FOR THIS NSN.<span style="mso-spacerun: yes">&nbsp; </span>ANY MANUFACTURER, OTHER THAN THE APPROVED SOURCE, WISHING TO SUBMIT A PROPOSAL ON THIS ITEM MUST SUBMIT A COMPLETE SOURCE APPROVAL REQUEST (SAR) PACKAGE.<span style="mso-spacerun: yes">&nbsp; </span>SOLICITATION WILL BE FOR A FIRM FIXED PRICE QUANTITY OF 418 EACH.<span style="mso-spacerun: yes">&nbsp; </span>SOLICITATION WILL PUBLISH ON OR ABOUT DECEMBER 12, 2018 WITH A CLOSING DATE OF JANUARY 11, 2019.<span style="mso-spacerun: yes">&nbsp; </span>DELIVERY REQUESTED WILL BE 365 DAYS ARO.<span style="mso-spacerun: yes">&nbsp;&nbsp; </span>SAMPLING FOR INSPECTION &amp; TESTING SHALL BE IAW ANSI/ASQ Z1.4-2003. <span style="mso-spacerun: yes">&nbsp;</span>PPIRS APPLIES.<span style="mso-spacerun: yes">&nbsp; </span>THE FINAL CONTRACT AWARD DECISION MAY BE BASED UPON A COMBINATION OF PRICE, PAST PERFORMANCE, AND OTHER EVALUATION FACTORS AS DESCRIBED IN THE SOLICITATION.<span style="mso-spacerun: yes">&nbsp; </span>THE SOLICITATION WILL BE AVAILABLE VIA THE DLA-BSM INTERNET BID BOARD SYSTEM (DIBBS) AT </span></span></span><a href="https://www.dibbs.bsm.dla.mil"><span style="mso-bookmark: OLE_LINK1"><span style="mso-bookmark: OLE_LINK2"><span style="FONT-FAMILY: ">https://www.dibbs.bsm.dla.mil</span></span></span></a><span style="mso-bookmark: OLE_LINK1"><span style="mso-bookmark: OLE_LINK2"><span style="FONT-FAMILY: "> ON THE ISSUE DATE CITED IN THE RFP.<span style="mso-spacerun: yes">&nbsp; </span>FROM THE DIBBS HOMEPAGE, SELECT SOLICITATIONS, SELECT REQUEST FOR PROPOSAL (RFP)/INVITATION FOR BID (IFB) TAB, THEN SELECT SEARCH THE RFP/IFB DATABASE, THEN CHOOSE THE RFP YOU ARE SEARCHING FOR.<span style="mso-spacerun: yes">&nbsp; </span>RFP\'S ARE IN PORTABLE DOCUMENT FORMAT (PDF).<span style="mso-spacerun: yes">&nbsp; </span>TO DOWNLOAD AND VIEW THESE DOCUMENTS YOU WILL NEED THE LATEST VERSION OF ADOBE ACROBAT READER.<span style="mso-spacerun: yes">&nbsp; </span>THIS SOFTWARE IS AVAILABLE FREE AT </span></span></span><a href="http://www.adobe.com"><span style="mso-bookmark: OLE_LINK1"><span style="mso-bookmark: OLE_LINK2"><span style="FONT-FAMILY: ">http://www.adobe.com</span></span></span></a><span style="mso-bookmark: OLE_LINK1"><span style="mso-bookmark: OLE_LINK2"><span style="FONT-FAMILY: ">.<span style="mso-spacerun: yes">&nbsp; </span>A PAPER COPY OF THE SOLICIATION WILL NOT BE AVAILABLE TO REQUESTORS. EMAIL QUOTE TO DESIREE.MCCORMICK@DLA.MIL.</span></span></span></p>\n'
        result = clean_line_text(text_to_clean)
        expected = "https://www.dibbs.bsm.dla.mil SOLICITATION FOR NSN: 2915009189013, 0076482892, GUIDE, SPRING, ONTIC (45934) P/N: 557568, FOB ORIGIN, INSPECTION/ACCEPTANCE AT DESTINATION. ONTIC IS THE ONLY APPROVED SOURCES FOR THIS ITEM. DLA DOES NOT CURRENTLY HAVE AN APPROVED TECHNICAL DATA PACKAGE AVAILABLE FOR THIS NSN. ANY MANUFACTURER, OTHER THAN THE APPROVED SOURCE, WISHING TO SUBMIT A PROPOSAL ON THIS ITEM MUST SUBMIT A COMPLETE SOURCE APPROVAL REQUEST (SAR) PACKAGE. SOLICITATION WILL BE FOR A FIRM FIXED PRICE QUANTITY OF 418 EACH. SOLICITATION WILL PUBLISH ON OR ABOUT DECEMBER 12, 2018 WITH A CLOSING DATE OF JANUARY 11, 2019. DELIVERY REQUESTED WILL BE 365 DAYS ARO. SAMPLING FOR INSPECTION & TESTING SHALL BE IAW ANSI/ASQ Z1.4-2003. PPIRS APPLIES. THE FINAL CONTRACT AWARD DECISION MAY BE BASED UPON A COMBINATION OF PRICE, PAST PERFORMANCE, AND OTHER EVALUATION FACTORS AS DESCRIBED IN THE SOLICITATION. THE SOLICITATION WILL BE AVAILABLE VIA THE DLA-BSM INTERNET BID BOARD SYSTEM (DIBBS) AT https://www.dibbs.bsm.dla.mil ON THE ISSUE DATE CITED IN THE RFP. FROM THE DIBBS HOMEPAGE, SELECT SOLICITATIONS, SELECT REQUEST FOR PROPOSAL (RFP)/INVITATION FOR BID (IFB) TAB, THEN SELECT SEARCH THE RFP/IFB DATABASE, THEN CHOOSE THE RFP YOU ARE SEARCHING FOR. RFP'S ARE IN PORTABLE DOCUMENT FORMAT (PDF). TO DOWNLOAD AND VIEW THESE DOCUMENTS YOU WILL NEED THE LATEST VERSION OF ADOBE ACROBAT READER. THIS SOFTWARE IS AVAILABLE FREE AT http://www.adobe.com. A PAPER COPY OF THE SOLICIATION WILL NOT BE AVAILABLE TO REQUESTORS. EMAIL QUOTE TO DESIREE.MCCORMICK@DLA.MIL."
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_email_from_url(self, mock_request):
        url = 'https://www.fbo.gov/index.php?s=opportunity&mode=form&id=e3368a7dee3966e14d574f2f0591f2d1&tab=core&_cview=1'
        mock_request.register_uri('GET',
                                  url = url ,
                                  text = '''<div><a href="mailto:foo.bar.bax.civ@mail.mil" onmousedown="_sendEvent('Outbound MailTo','foo.bar.bax.civ@mail.mil','',0);">foo.bar.bax.civ@mail.mil</a></div>''',
                                  status_code = 200)
        result = get_email_from_url(url)
        expected = ['mailto:foo.bar.bax.civ@mail.mil']
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_email_from_url_404(self, mock_request):
        url = 'https://www.fbo.gov/index.php?s=opportunity&mode=form&id=e3368a7dee3966e14d574f2f0591f2d1&tab=core&_cview=1'
        mock_request.register_uri('GET',
                                  url = url,
                                  text = 'foo',
                                  status_code = 404)
        result = get_email_from_url(url)
        expected = []
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_get_email_from_url_exception(self, mock_request):
        url = 'https://www.fbo.gov/index.php?s=opportunity&mode=form&id=e3368a7dee3966e14d574f2f0591f2d1&tab=core&_cview=1'
        mock_request.register_uri('GET',
                               url = url,
                               exc = requests.exceptions.ConnectionError)
        result = get_email_from_url(url)
        expected = None
        self.assertEqual(result, expected)

    def test_extract_emails_contact_w_email(self):
        notice = {'CONTACT':'foo.bar@gsa.gov'}
        result = extract_emails(notice)
        expected = ['foo.bar@gsa.gov']
        self.assertEqual(result, expected)

    def test_extract_emails_email_w_email(self):
        notice = {'CONTACT':'no email here :(',
                  'EMAIL':'foo.bar@gsa.gov'}
        result = extract_emails(notice)
        expected = ['foo.bar@gsa.gov']
        self.assertEqual(result, expected)

    def test_extract_emails_desc_w_email(self):
        notice = {'CONTACT':'no email here :(',
                  'DESC':'foo.bar@gsa.gov'}
        result = extract_emails(notice)
        expected = ['foo.bar@gsa.gov']
        self.assertEqual(result, expected)

    @requests_mock.Mocker()
    def test_extract_emails_scrape_needed(self, mock_request):
        url = 'https://www.fbo.gov/index.php?s=opportunity&mode=form&id=e3368a7dee3966e14d574f2f0591f2d1&tab=core&_cview=1'
        mock_request.register_uri('GET',
                                  url = url ,
                                  text = '''<div><a href="mailto:foo.bar.civ@mail.mil" onmousedown="_sendEvent('Outbound MailTo','foo.bar.bax.civ@mail.mil','',0);">foo.bar.bax.civ@mail.mil</a></div>''',
                                  status_code = 200)
        notice = {'CONTACT':'no email here :(',
                  'DESC':'and no email here',
                  'URL':url}
        result = extract_emails(notice)
        expected = ['foo.bar.civ@mail.mil']
        self.assertEqual(result, expected)

    def test_id_and_count_notice_tags(self):
        result = id_and_count_notice_tags(self.file_lines)
        expected = {'PRESOL': 1, 'COMBINE': 1, 'ARCHIVE': 1,
                    'AWARD': 1, 'MOD': 1, 'AMDCSS': 1, 'SRCSGT': 1, 'UNARCHIVE': 1}
        self.assertEqual(result, expected)

    def test_merge_dicts(self):
        notice = [{'a': '123'}, {'b': '345'}, {'c': '678'}, {'c': '9'}]
        result = merge_dicts(notice)
        expected = {'a': '123', 'b': '345', 'c': '678 9'}
        self.assertEqual(result, expected)
    
    def test_pseudo_xml_to_json(self):
        result = pseudo_xml_to_json(self.file_lines)
        expected = pseudo_xml_to_json_expected.merge_notices_dict
        self.assertEqual(result, expected)

    def test_get_nightly_data(self):
        #use it on real data for an end-to-end test
        date = '20190203'
        try:
            get_nightly_data(date = date)
        except Exception as e:
            self.fail('get_nightly_data() raised an Exceptio:  {e}')
        #cleanup here
        os.remove(os.path.join(os.getcwd(), 'data', f'{date}-result.json'))
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()