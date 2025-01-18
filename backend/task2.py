import os
import csv
from openai import OpenAI
from extraction import research_paper_extraction
from pydantic import BaseModel
from constants import (
    RECOMMENDER_PROMPT,
    MODEL_NAME
)

client = OpenAI()

class ConferenceRecommender(BaseModel):
    conference_title: str
    rationale: str

def router_conference(pdf_path: str) -> ConferenceRecommender:
    extracted_object = research_paper_extraction(pdf_path=pdf_path)

    completion = client.beta.chat.completions.parse(
        model=f"{MODEL_NAME}",
        messages=[
            {
                "role": "system", 
                "content": f"{RECOMMENDER_PROMPT}"
            },
            {
                "role": "user", 
                "content": f"ABSTRACT:\n{extracted_object.abstract}"
            }
        ],
        response_format=ConferenceRecommender,
    )

    event = completion.choices[0].message.parsed
    return event

# if __name__ == "__main__":
#     paper_folder = "Papers" # Folder containing the test set 
#     output_csv_path = "task2.csv"

#     results = []

#     if not os.path.exists(paper_folder):
#         print(f"The folder {paper_folder} does not exist.")
#     else:
#         for pdf_file in os.listdir(paper_folder):
#             if pdf_file.endswith(".pdf"):
#                 pdf_path = os.path.join(paper_folder, pdf_file)
#                 print(f"Processing: {pdf_path}")

#                 try:
#                     conf_details = router_conference(pdf_path=pdf_path)
#                     paper_id = os.path.splitext(pdf_file)[0]  
#                     results.append({
#                         "Paper ID": paper_id,
#                         "Conference": conf_details.conference_title,
#                         "Rationale": conf_details.rationale
#                     })
#                 except Exception as e:
#                     print(f"Error processing {pdf_file}: {e}\n")

#     with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
#         fieldnames = ["Paper ID", "Conference", "Rationale"]
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#         writer.writeheader()
#         writer.writerows(results)

#     print(f"Results have been saved to {output_csv_path}")
