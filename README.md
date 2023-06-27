#Description
This package provides both functions and a command line tool to assist in annotating variants

#Features
- Can be used as a package or command line tool
- Provides intermediate functions for more flexibility
- Remove duplicate variants
- Skips variant names that cause errors

#Installation
`pip install git+ssh://git@github.com/fizzy123/tc-variant-annotation-client.git@822a93f66b0cdc636436e7114361bd48fa9a286d`

#Usage
As a package:
```
from tvac.client import VariantAnnotationClient
c = VariantAnnotationClient() # a custom url can be provided as an argument here
tsv = c.annotate_file("variants.txt")
print(tsv)
```

As a command line tool:
```
> tvac-annotate-variants variants.txt
```

For either of these, the expected output for the provided `variants.txt` file should be:
```
Variant NC_000001.11:g.40819893T>A Encountered Annotation Exception
Exception:Annotation website returned bad response
status_code:400
error:{"error":"Unable to parse HGVS notation 'NC_000001.11:g.40819893T>A': Reference allele extracted from NC_000001.11:40819893-40819893 (G) does not match reference allele given by HGVS notation NC_000001.11:g.40819893T>A (T)"}

variant assembly_name   seq_region_name start   end     most_severe_consequence strand  genes
NC_000001.11:g.215674515G>A     GRCh38  1       215674515       215674515       missense_variant        1       USH2A
NC_000001.11:g.40819893G>A      GRCh38  1       40819893        40819893        missense_variant        1       KCNQ4
NC_000002.12:g.39006443C>T      GRCh38  2       39006443        39006443        synonymous_variant      1       SOS1
NC_000006.12:g.152387156G>A     GRCh38  6       152387156       152387156       synonymous_variant      1       SYNE1
NC_000001.11:g.215674515G>A     GRCh38  1       215674515       215674515       missense_variant        1       USH2A
```

#Weaknesses
- If an invalid Ensembl response is provided without an accompanying 400 or 500 status code, the tsv will not be formatted correctly 

#Next Steps
- More tooltips/error handlers in CLI tool
- Expose other functions in CLI tool
- Add CI/CD scripts
- Add linting

I consider CLI tool UI/UX improvement to be the top priority just cause that has the most impact on how easy it is for people to use it.

My next priority is CI/CD since that's very valuable for further development, which linting specifications also tie into

#Questions
##Suppose we now want to create a web microservice that accepts a GET (or POST) request with the variant in HGVS format and returns the annotation as JSON. What tools or standards would you implement this? How does your code structure change?
We could implement a web microservice with Flask or Django and simply import this package in order to annotate these variants.

##Start-ups and start-up employees must balance quick and satisfactory (i.e., good enough) results with more deliberate and reliable results. The same is true for code. You do not have enough time to write the ultimate answer to variant annotation. What is important to get "right" now and what can be deferred?
Here is a list of things that could potentially be deferred, with the best things to defer at the beginning and the worst things to defer at the end:
- Features that are not strictly necessary to solve the problem at hand
- Functionality that provides wider support, but will not necessarily be used for the current application
- Documentation (since people can often read the code to figure out what's going on)
- Code Hygiene (DRY-ness, simplicity, cleanliness)
- Tests
- Input validation
- Bugs that can currently occur, but will not occur in the current use case
- Security Bugs

It's also meaningful to note that doing new things takes more time than doing things that the engineer is used to, or things that have already been done. This might affect the design of the overall application to be different, especially if we're developing for speed. In this case, we might focus on solutions where the engineer in question is particularly familiar, or on solutions where similar functionality has already been implemented elsewhere in the codebase and can easily be copy/pasted into the new code.

##What's the simplest method you can think of to handle cases of duplicated variants in the input?
Variants should be put into a hash, so they won't be duplicated.

##What optimizations would you pursue in your code if you had time? How would you prioritize your effort?
The answer to this is provided in [Next Steps](#next-steps) in order of priority
