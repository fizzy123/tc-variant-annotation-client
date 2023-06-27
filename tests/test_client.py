import unittest
from unittest.mock import mock_open, patch, call
from client.client import VariantAnnotationClient, EnsemblError
from tests import util

TEST_FILENAME = "variants.txt"

TEST_URL = "https://test.com/{variant}"

class TestVariantAnnotationClient(unittest.TestCase):
    def test_parse_variants(self):
        # This test string includes whitespace
        TEST_FILE = '''variant1
variant2    
variant3'''
        m = mock_open(read_data=TEST_FILE)
        client = VariantAnnotationClient(TEST_URL)
        with patch('builtins.open', m, create=True):
            variants = client.parse_variants(TEST_FILENAME)
            self.assertEqual(variants, [
                "variant1",
                "variant2",
                "variant3",
            ])
        m.assert_called_once_with("variants.txt", "r")

    def test_parse_variants_with_duplicates(self):
        TEST_FILE = '''variant1
variant1
variant3'''
        m = mock_open(read_data=TEST_FILE)
        client = VariantAnnotationClient(TEST_URL)
        with patch('builtins.open', m, create=True):
            variants = client.parse_variants(TEST_FILENAME)
            self.assertEqual(variants, [
                "variant1",
                "variant3"
            ])
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
        client = VariantAnnotationClient(TEST_URL)
        with patch('requests.get') as mock_get:
            mock_get.side_effect = util.mocked_requests_get_wrapper(mock_request_dict)
            annotated_row = client.annotate_variant("variant1")
            mock_get.assert_called_once_with("https://test.com/variant1", headers={'Content-type': 'application/json'})
        self.assertEqual(annotated_row, '''variant1\tassembly_name\tseq_region_name\tstart\tend\tmost_severe_consequence\tstrand\tgene_symbol''')

    def test_annotate_variant_with_error(self):
        error_text = "error blah error"
        mock_request_dict = {
            "https://test.com/variant1": {
                "text": error_text,
                "status_code": 400,
            }
        }
        client = VariantAnnotationClient(TEST_URL)
        with patch('requests.get') as mock_get:
            mock_get.side_effect = util.mocked_requests_get_wrapper(mock_request_dict)
            with self.assertRaises(EnsemblError) as context:
                annotated_row = client.annotate_variant("variant1")
                self.assertEqual(context.exception.status_code, 400)
                self.assertEqual(context.exception.error_text, error_text)
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
                self.assertEqual(mock_annotate_variant.call_args_list[0], call("variant1"))
                self.assertEqual(mock_annotate_variant.call_args_list[1], call("variant2"))
                self.assertEqual(mock_annotate_variant.call_args_list[2], call("variant3"))
                self.assertEqual(mock_annotate_variant.call_count, 3)
                mock_parse_variants.assert_called_once_with(TEST_FILENAME)
            self.assertEqual(tsv, '''variant\tassembly_name\tseq_region_name\tstart\tend\tmost_severe_consequence\tstrand\tgenes
variant1\tattr1\tattr2\tattr3
variant2\tattr1\tattr2\tattr3
variant3\tattr1\tattr2\tattr3''')
                    

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
                    EnsemblError(500, "TEST EXCEPTION"),
                    "variant3\tattr1\tattr2\tattr3",
                ]
                client = VariantAnnotationClient(TEST_URL)
                with patch('builtins.print') as mock_print:
                    tsv = client.annotate_file(TEST_FILENAME)
                    mock_print.assert_called_once_with("Variant variant2 Encountered Annotation Exception\nException:Annotation website returned bad response\nstatus_code:500\nerror:TEST EXCEPTION\n")

                self.assertEqual(mock_annotate_variant.call_args_list[0], call("variant1"))
                self.assertEqual(mock_annotate_variant.call_args_list[1], call("variant2"))
                self.assertEqual(mock_annotate_variant.call_args_list[2], call("variant3"))
                self.assertEqual(mock_annotate_variant.call_count, 3)
                mock_parse_variants.assert_called_once_with(TEST_FILENAME)
            self.assertEqual(tsv, '''variant\tassembly_name\tseq_region_name\tstart\tend\tmost_severe_consequence\tstrand\tgenes
variant1\tattr1\tattr2\tattr3
variant3\tattr1\tattr2\tattr3''')

if __name__ == '__main__':
        unittest.main()

