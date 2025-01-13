from openai import OpenAI
from extraction import research_paper_extraction
from pydantic import BaseModel
from constants import RECOMMENDER_PROMPT

client = OpenAI()

class ConferenceRecommender(BaseModel):
    conference_title: str


def router_conference( 
    pdf_path: str
) -> ConferenceRecommender:
    
    extracted_object = research_paper_extraction(
        pdf_path=pdf_path
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
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

if __name__ == "__main__":
    conf_title = router_conference(
        pdf_path="/home/gjyotin305/Desktop/kdsh-hackathon/data/data/Publishable/CVPR/R006.pdf"
    )
    print(conf_title.conference_title)