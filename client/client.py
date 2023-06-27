import requests

VARIANT_ENDPOINT = "http://rest.ensembl.org/vep/human/hgvs/{variant}" 

class VariantAnnotationClient:
    def __init__(self, variant_endpoint=VARIANT_ENDPOINT):
        self.variant_endpoint = variant_endpoint

    def parse_variants(self, filename):
        file_object = open(filename, "r")
        variants = file_object.readlines()
        file_object.close()
        # remove all empty lines
        return [variant.strip() for variant in variants if variant.strip() != ""]

    def annotate_variant(self, variant):
        response = requests.get(self.variant_endpoint.format(variant=variant), headers={
            'Content-type':'application/json'
        })
        if response.status_code != 200:
            raise Exception(f"Annotation website returned bad response\nstatus_code:{response.status_code}\nerror:{response.text}")
        data = response.json()
        assembly_name = data[0]["assembly_name"]
        seq_region_name = data[0]["seq_region_name"]
        start = data[0]["start"]
        end = data[0]["end"]
        most_severe_consequence = data[0]["most_severe_consequence"]
        strand = data[0]["strand"]
        genes = data[0]["transcript_consequences"][0]["gene_symbol"]
        return "\t".join([variant, assembly_name, seq_region_name, str(start), str(end), most_severe_consequence, str(strand), genes])

    def annotate_file(self, filename):
        variants = self.parse_variants(filename)
        annotations = ["\t".join([
            "variant",
            "assembly_name",
            "seq_region_name",
            "start",
            "end",
            "most_severe_consequence",
            "strand",
            "genes",
        ])]
        for variant in variants:
            variant = variant.strip()
            try:
                annotation = self.annotate_variant(variant)
                annotations.append(annotation)
            except Exception as e:
                print(f"Variant {variant} Encountered Annotation Exception\nException:{str(e)}")
        return "\n".join(annotations)
