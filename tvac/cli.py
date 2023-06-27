from client import VariantAnnotationClient
def main():
    parser = argparse.ArgumentParser(prog="tvac")
    parser.add_argument('filename')
    args = parser.parse_args()
    c = VariantAnnotationClient()
    annotations = c.annotate_file(args.filename)
    print(annotations)
