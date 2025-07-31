# JSON Outputs for Specification PDFs

This folder contains the structured JSON outputs for all specification PDFs as required by the coding challenge.

## Files Status:

### ✅ Completed:
- `22_08_00_commissioning_plumbing_short.json` - From "22 08 00 - COMMISSIONING OF PLUMBING (Short).pdf"
- `23_82_43_electric_heaters.json` - From "23 82 43 Electric Heaters.pdf" (already provided in documents/)
- `271500_medium.json` - From "271500 (Medium).pdf" - "27 15 00 HORIZONTAL CABLING REQUIREMENTS"
- `233000_hvac_air_distribution_long.json` -  "233000 HVAC Air Distribution (Long).pdf"

## JSON Schema:

All JSON files follow the same structure:
```json
{
  "section": "XX XX XX",
  "name": "SPECIFICATION NAME",
  "part1": {
    "partItems": [
      {
        "index": "1.1",
        "text": "SECTION TITLE",
        "children": [
          {
            "index": "A.",
            "text": "Content text",
            "children": null | [nested children]
          }
        ]
      }
    ]
  },
  "part2": { /* same structure */ },
  "part3": { /* same structure */ }
}
```

## Notes:
- All content is parsed verbatim from the PDF
- Hierarchical structure is preserved with nested children
- Tables are included where present in the original documents
