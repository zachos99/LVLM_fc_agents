import json

from evidence_filtering.evidencePreprocessing import process_evidence, readable_print_for_debugging




xml_path = "web_search/fa1260/fa1260_q2_v1/fa1260_q2_v1_result_1.xml"
images_path = "web_search/fa1260/fa1260_q2_v1/fa1260_q2_v1_result_1_scrapedImageURLs.json"

# Run initial preprocessing
print("Initial evidence preprocessing...")
processed_evidence = process_evidence(xml_path,images_path)

# Save <main> in an a readable format for debugging
readable_print_for_debugging(processed_evidence.get('text'))

# Save output that we will feed as input to the next step
with open("evidence_filtering/output.json", "w", encoding="utf-8") as f:
        json.dump(processed_evidence, f, ensure_ascii=False, indent=2)



