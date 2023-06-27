import unittest
from unittest.mock import mock_open, patch, call
from client.client import VariantAnnotationClient
from tests import util

TEST_FILENAME = "variants.txt"
TEST_FILE = '''variant1
variant2
variant3'''

TEST_URL = "https://test.com/{variant}"

class TestVariantAnnotationClient(unittest.TestCase):
    def test_parse_variants(self):
        m = mock_open(read_data=TEST_FILE)
        client = VariantAnnotationClient(TEST_URL)
        with patch('builtins.open', m, create=True):
            variants = client.parse_variants(TEST_FILENAME)
            self.assertEqual(TEST_FILE.split("\n"), variants)
        m.assert_called_once_with("variants.txt", "r")

    def test_annotate_variant(self):
        mock_request_dict = {
            "https://test.com/variant1": {
                "json": [
                    {
                        "assembly_name": "assembly_name",
                        "seq_region_name": "seq_region_name",
                        "start": "start",
                        "end": "end",
                        "most_severe_consequence": "most_severe_consequence",
                        "strand": "strand",
                        "transcript_consequences": [
                            {
                                "gene_symbol": "gene_symbol"
                            }
                        ]
                    }
                ],
                "status_code": 200,
            }
        }
        with patch('requests.get') as mock_get:
            mock_get.side_effect = util.mocked_requests_get_wrapper(mock_request_dict)
            client = VariantAnnotationClient(TEST_URL)
            annotated_row = client.annotate_variant("variant1")
            self.assertEqual('''variant1\tassembly_name\tseq_region_name\tstart\tend\tmost_severe_consequence\tstrand\tgene_symbol''', annotated_row)
            mock_get.assert_called_once_with("https://test.com/variant1", headers={'Content-type': 'application/json'})

    def test_annotate_file(self):
        with patch.object(VariantAnnotationClient, 'parse_variants') as mock_parse_variants:
            with patch.object(VariantAnnotationClient, 'annotate_variant') as mock_annotate_variant:
                mock_parse_variants.return_value = [
                    "variant1",
                    "variant2",
                    "variant3",
                ]
                mock_annotate_variant.side_effect = [
                    "variant1\tattr1\tattr2\tattr3",
                    "variant2\tattr1\tattr2\tattr3",
                    "variant3\tattr1\tattr2\tattr3",
                ]
                client = VariantAnnotationClient(TEST_URL)
                with patch('builtins.print') as mock_print:
                    tsv = client.annotate_file(TEST_FILENAME)
                mock_print.assert_not_called()
                self.assertEqual('''variant\tassembly_name\tseq_region_name\tstart\tend\tmost_severe_consequence\tstrand\tgenes
variant1\tattr1\r2\tattr3
variant2\tattr1\r2\tattr3
variant3\tattr1\r2\tattr3''', tsv)
                self.assertEqual(mock_annotate_variant.call_args_list[0], call("variant1"))
                self.assertEqual(mock_annotate_variant.call_args_list[1], call("variant2"))
                self.assertEqual(mock_annotate_variant.call_args_list[2], call("variant3"))
                self.assertEqual(mock_annotate_variant.call_count, 3)
                mock_parse_variants.assert_called_once_with(TEST_FILENAME)
                    

    def test_annotate_file_with_error(self):
        with patch.object(VariantAnnotationClient, 'parse_variants') as mock_parse_variants:
            with patch.object(VariantAnnotationClient, 'annotate_variant') as mock_annotate_variant:
                mock_parse_variants.return_value = [
                    "variant1",
                    "variant2",
                    "variant3",
                ]
                mock_annotate_variant.side_effect = [
                    "variant1\tattr1\tattr2\tattr3",
                    Exception("TEST EXCEPTION"),
                    "variant3\tattr1\tattr2\tattr3",
                ]
                client = VariantAnnotationClient(TEST_URL)
                with patch('builtins.print') as mock_print:
                    tsv = client.annotate_file(TEST_FILENAME)
                    mock_print.assert_called_once_with("Variant variant2 Encountered Annotation Exception\nException:TEST EXCEPTION")
                self.assertEqual('''variant\tassembly_name\tseq_region_name\tstart\tend\tmost_severe_consequence\tstrand\tgenes
variant1\tattr1\tattr2\tattr3
variant3\tattr1\tattr2\tattr3''', tsv)
                self.assertEqual(mock_annotate_variant.call_args_list[0], call("variant1"))
                self.assertEqual(mock_annotate_variant.call_args_list[1], call("variant2"))
                self.assertEqual(mock_annotate_variant.call_args_list[2], call("variant3"))
                self.assertEqual(mock_annotate_variant.call_count, 3)
                mock_parse_variants.assert_called_once_with(TEST_FILENAME)

if __name__ == '__main__':
        unittest.main()

