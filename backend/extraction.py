from pydantic import BaseModel
from openai import OpenAI
import os
from constants import MODEL_NAME
from pypdf import PdfReader

client = OpenAI()

class ResearchPaperExtraction(BaseModel):
    title: str
    authors: list[str]
    abstract: str
    keywords: list[str]
    methodology: str
    experiments: list[str]
    impact: str


def clean_text(context: str):
    response = client.chat.completions.create(
        model=f"{MODEL_NAME}",
        messages=[
            {
                "role": "system",
                "content": "You are to clean the given text below do not remove the content and only format it properly in markdown format."
            },
            {
                "role": "user",
                "content": f"{context}"
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


def research_paper_extraction(
    pdf_path: str
) -> ResearchPaperExtraction:
    pdf_read = PdfReader(pdf_path)
    context = ""

    for x in pdf_read.pages:
        context += x.extract_text()

    #print(context)

    completion = client.beta.chat.completions.parse(
        model=f"{MODEL_NAME}",
        messages=[
            {"role": "system", "content": "You are an expert at structured data extraction. You will be given unstructured text from a research paper and should convert it into the given structure."},
            {"role": "user", "content": f"CONTENT:\n{context}"}
        ],
        response_format=ResearchPaperExtraction,
    )

    research_paper = completion.choices[0].message.parsed

    return research_paper


# Example Usage
# obj_ = research_paper_extraction(
#     "/home/gjyotin305/Desktop/kdsh-hackathon/data/data/Publishable/CVPR/R007.pdf"
# )

# print(obj_.impact)
