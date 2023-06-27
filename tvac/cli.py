import argparse
from .client import VariantAnnotationClient

def cli_annotate_variants():
    parser = argparse.ArgumentParser(prog="tvac-annotate-variants", description="Command line tool for annotating variants provided in a filename")
    parser.add_argument('filename', help="Name of file with variants seperated by newlines")
    args = parser.parse_args()
    c = VariantAnnotationClient()
    annotations = c.annotate_file(args.filename)
    print(annotations)
