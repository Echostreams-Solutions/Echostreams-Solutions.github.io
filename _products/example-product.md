---
# Template for a hand-written product. Most products are generated from the CSVs in _source-data/
# by `python scripts/import_products.py` (which leaves this file alone).
# Copy this file, rename it (the file name is the URL: /products/<file-name>/) and remove `published: false`.
published: false
title: Example DSS-448
full_title: Example DSS-448 4U 48 bays (optional long name)
family: durastreams        # durastreams | flachestreams | gridstreams | omnistreams | scalestreams
cpu: amd                   # amd | intel | jbod  (family pages filter on family + cpu; JBODs show on /jbods.html)
order: 10                  # optional: lower numbers first
image: /assets/img/no-image.svg
spec_sections:
  - title: System
    rows:
      - ["Storage", "48x 3.5\" SAS/SATA"]
  - title: Physical
    rows:
      - ["Weights", "80 lbs"]
resources:
  - { label: "Data Sheet", name: "DS_Example" }
link: https://example.com/buy            # optional "Where to buy" link
link_text: Where to buy
---
Longer description in Markdown goes here.
