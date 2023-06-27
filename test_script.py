# WARNING: THIS TEST IS MEANT TO DO A LIVE TEST OF THE CLIENT AND TESTS AGAINST A REAL FILE AND AGAINST A REAL WEBSITE
from client.client import VariantAnnotationClient
c = VariantAnnotationClient()
print(c.annotate_file("variants.txt"))
