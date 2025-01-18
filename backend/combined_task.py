import os
import glob
import asyncio
import csv
import re
import openai
from openai import OpenAI
from extraction import research_paper_extraction
from tqdm.asyncio import tqdm
from pydantic import BaseModel
from constants import (
    RECOMMENDER_PROMPT,
    MODEL_NAME
)

# score_pattern = re.compile(r'(\d+(?:\.\d+)?)')

# ## helper function to extract scores from a string
# def extract_numeric_score(line: str) -> float:
#     match = score_pattern.search(line)
#     if match:
#         return float(match.group(1))
#     else:
#         return 0.0

###############################################################################
# Initialize your OpenAI async client once, globally.
###############################################################################
client = openai.AsyncOpenAI()

###############################################################################
# 1. System prompts for each reviewer
###############################################################################
reviewer_prompts = [
    """
    You are Dr. Strict, a seasoned AI researcher with 20+ years of experience, 
    focusing on the novelty of the research. 
    Please analyze the paper based on the following criteria: 
    1. Originality (0-10) 
    2. Technical Soundness (0-10) 
    3. Clarity (0-10) 
    4. Relevance (0-10)

    Return your ratings for each criterion in the format:
    Originality: X
    Technical Soundness: X
    Clarity: X
    Relevance: X

    Then provide:
    - A short textual review (2-3 sentences).
    - A final label: either "Publishable" or "Not Publishable".
    
    Make sure your response is clearly structured.
    """,
    """
    You are Dr. Method, an AI professor who emphasizes methodological rigor. 
    Analyze the paper based on: 
    1. Originality (0-10) 
    2. Technical Soundness (0-10) 
    3. Clarity (0-10) 
    4. Relevance (0-10)

    Return your ratings in the format:
    Originality: X
    Technical Soundness: X
    Clarity: X
    Relevance: X

    Then provide:
    - A short textual review (2-3 sentences).
    - A final label: either "Publishable" or "Not Publishable".
    
    Make sure your response is clearly structured.
    """,
    """
    You are Dr. Clarity, a reviewer particularly concerned with the readability 
    and presentation aspects of the paper. 
    Rate the paper on: 
    1. Originality (0-10) 
    2. Technical Soundness (0-10) 
    3. Clarity (0-10) 
    4. Relevance (0-10)

    Return your ratings in the format:
    Originality: X
    Technical Soundness: X
    Clarity: X
    Relevance: X
    Don't provide anything except numeric scores in the above format.
    
    Then provide:
    - A short textual review (2-3 sentences).
    - A final label: either "Publishable" or "Not Publishable".
    
    Make sure your response is clearly structured.
    """
]

###############################################################################
# 2. Core user prompt (template). We'll fill the {extracted_text} for each PDF.
###############################################################################
USER_PROMPT_TEMPLATE = """
You are an expert reviewer for AI research papers. Your task is to classify 
whether a paper is "Publishable" or "Not Publishable" based on these criteria:  
1. **Originality**: Does the paper contribute new ideas or methods?  
2. **Technical Soundness**: Are the methods well-defined and validated with experiments?  
3. **Clarity**: Is the paper well-written and easy to understand?  
4. **Relevance**: Is the topic relevant to the field of AI?  

After analyzing the **Title**, **Abstract**, **Methodology**, and **Conclusion**, 
provide a step-by-step explanation of your decision-making process, considering 
all four criteria, and label the paper accordingly.

---
Example 1

Title: Analyzing Real-Time Group Coordination in Augmented Dance Performances: An LSTM-Based Gesture Modeling Approach
Abstract (Excerpt):

    The paper explores the intersection of augmented reality (AR) and flamenco dance to enhance group cohesion through gesture forecasting with LSTM networks. It proposes an innovative "virtual flamenco guru" to provide real-time feedback, improving synchronization and creativity among dancers. The research also examines cultural implications, therapeutic applications, and the use of AR and LSTM to push the boundaries of art, technology, and collective behavior.
Decision: Not Publishable
Reasoning (Step-by-Step):

    Originality: While integrating AR and LSTM in flamenco dance is interesting, the paper includes tangential ideas (e.g., tea leaf predictions) that lack scientific foundation.
    Technical Soundness: Insufficient experimental detail; novelty of “temporally-compressed gesture forecasting” is unsubstantiated.
    Clarity: Speculative elements (chaos theory, quantum flamenco) obscure the main contribution.
    Relevance: Potentially interesting for AR and AI in performing arts, but the paper is too unfocused and lacks rigorous backing.

Example 2

Title: AI-Driven Personalization in Online Education Platforms
Abstract (Excerpt):

    This research investigates AI-driven personalization in online education by analyzing learning behaviors and integrating a unique AI-generated dreamscape for immersive learning. The authors claim this approach improves engagement and learning outcomes through tailored pathways and unconventional techniques like "philosophical resonance."
Decision: Not Publishable
Reasoning (Step-by-Step):

    Originality: AI-generated dreamscapes and “philosophical resonance” are creative but ungrounded.
    Technical Soundness: Reliance on unscientific “daydreaming modules” and speculative data.
    Clarity: Overly abstract explanations and lack of reproducible experiments.
    Relevance: While online education is important, the approach is too whimsical for practical or academic impact.

Example 3

Title: Detailed Action Identification in Baseball Game Recordings
Abstract (Excerpt):

    This paper introduces MLB-YouTube, a dataset for nuanced activity recognition in baseball videos. It evaluates methods for both segmented and continuous video analysis, incorporating temporal feature aggregation and focusing on fine-grained activities like pitch speed and type prediction. The study highlights the significance of temporal structures in improving recognition accuracy and proposes advanced models for multi-label classification and regression tasks.

Decision: Publishable
Reasoning (Step-by-Step):

    Originality: Domain-specific baseball dataset (MLB-YouTube) is novel; pitch speed prediction is unique.
    Technical Soundness: Rigorous experiments with advanced temporal modeling approaches.
    Clarity: Detailed methodology, results, and metrics.
    Relevance: Highly relevant to computer vision and sports analytics.

Example 4

Title: Addressing Min-Max Challenges in Nonconvex-Nonconcave Problems with Solutions Exhibiting Weak Minty Properties
Abstract (Excerpt):

    This research addresses structured nonconvex-nonconcave min-max problems with weak Minty solutions, introducing a modified OGDA+ algorithm with convergence guarantees. It establishes improved convergence rates, compares OGDA+ with existing methods, and introduces an adaptive-step-size EG+ variant to handle weak Minty solutions without prior parameter knowledge.
Decision: Publishable
Reasoning (Step-by-Step):

    Originality: Novel exploration of weak Minty solutions in min-max optimization.
    Technical Soundness: Well-defined algorithms (OGDA+, EG+), theoretical proofs, and strong empirical results.
    Clarity: Clear organization, definitions, and numerical experiments.
    Relevance: Significant contribution to optimization, GANs, and adversarial frameworks.

Example 5

Title: Detecting Medication Usage in Parkinson’s Disease Through Multi-modal Indoor Positioning: A Pilot Study in a Naturalistic Environment
Abstract (Excerpt):
   This study explores a transformer-based approach using RSSI and accelerometer data to enhance indoor localization for detecting motor fluctuations in Parkinson's disease (PD) patients. It introduces the MDCSA model to predict medication adherence via in-home gait speed features. Evaluations in smart homes validate its efficacy in differentiating "ON" and "OFF" medication states.
    
Decision: Publishable
Reasoning (Step-by-Step):

    Originality: Multi-modal indoor positioning for medication adherence in PD is novel.
    Technical Soundness: Transformer-based RSSI and accelerometer data approach validated on real-world datasets.
    Clarity: Well-written with clear methodology and quantitative findings.
    Relevance: Addresses critical healthcare challenge, highly relevant to AI in medicine.

Example 6

Title: Safe Predictors for Input-Output Specification Enforcement
Abstract (Excerpt):
   The paper proposes a method for designing neural networks that adhere to input-output specifications by combining constrained predictors with convex combinations. Applications include synthetic datasets and an aircraft collision avoidance problem, demonstrating safety guarantees without sacrificing accuracy. 
Decision: Publishable
Reasoning (Step-by-Step):

    Originality: Introduces correct-by-construction safe predictors for neural networks.
    Technical Soundness: Solid theoretical foundation with proofs and real-world collision avoidance examples.
    Clarity: Thorough explanations, illustrative examples, and proofs.
    Relevance: Highly relevant to AI safety and autonomous systems.

Example 7

Title: Improving Temporal Analysis for Predictive Systems in Dynamic Environments
Abstract (Excerpt):
   This research presents a novel predictive framework designed for dynamic environments, integrating temporal embeddings with self-attention mechanisms. The method enhances predictive accuracy in tasks such as traffic forecasting and resource allocation. Extensive testing on real-world datasets demonstrates its superior performance compared to baseline methods. 
Decision: Publishable
Reasoning (Step-by-Step):

    Originality: Innovative integration of temporal embeddings with self-attention.
    Technical Soundness: Detailed algorithms and validation on real-world datasets.
    Clarity: Well-structured text, visual aids, and thorough experimental results.
    Relevance: Significant for traffic forecasting, resource allocation, and other dynamic AI applications.
---

Now classify the given research paper based on given structured extraction{extracted_text} from the actual research paper based on the reasoning steps in the examples. Output format should be followed strictly, examples above are only for reasoning steps.

"""

###############################################################################
# 3. Asynchronous call to get reviewer feedback
###############################################################################
async def get_reviewer_feedback(system_prompt: str, user_prompt: str):
    """
    Makes an asynchronous call to the OpenAI ChatCompletion endpoint
    for a single reviewer's feedback.
    Expects the reviewer to return:
      - Ratings for each criterion
      - A short textual review
      - A final label: Publishable or Not Publishable
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


###############################################################################
# 4. Define Decision Aggregator prompt for the final decision
###############################################################################
aggregator_system_prompt = """
You are the final aggregator. You will receive:
1. The original paper details (Title, Abstract, Methodology, Conclusion).
2. Three reviewer feedbacks, including numeric scores for (Originality, Technical Soundness, Clarity, Relevance) each out of 10, plus a short textual review and label.

Your task:
- Read the paper details carefully.
- Read each reviewer feedback and the average scores.
- Decide if the paper should be labeled "Publishable" or "Not Publishable".
- Provide a short explanation of your reasoning (2-3 sentences).
- Provide a confidence measure on a scale of 1 to 10 (where 1 = very uncertain, 10 = extremely confident).

You should consider the reviewers' feedback as well as use your own judgment.
Format your response in a clear, structured and strict manner, for example:
"
Final Decision: <Publishable or Not Publishable>
Reasoning: <2-3 sentences summarizing the key points>
Confidence: <number from 1 to 10>
"
Another important fact is that you should strictly adhere to this template. Specially for the 'Final Decision' part, you are allowed to use only the words 'Publishable' or 'Not Publishable'. No other variations (like “Potentially Publishable”, “Might be Publishable”, "publishable under no circumstances", etc.) should be used.
"""

###############################################################################
# 5. Aggregator function: combine reviewer feedback & final verdict
###############################################################################
async def get_aggregated_decision(
    aggregator_prompt: str,
    paper_details: str,
    reviewer_feedbacks: list
):
    """
    Makes a call to the OpenAI ChatCompletion endpoint for the final aggregator.
    The aggregator has access to:
      - paper_details
      - all reviewer feedback
    Returns a structured final decision.
    """
    aggregator_user_content = f"""
Paper Details:
{paper_details}

Reviewer Feedbacks:
1) {reviewer_feedbacks[0]}
2) {reviewer_feedbacks[1]}
3) {reviewer_feedbacks[2]}
"""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": aggregator_prompt},
            {"role": "user", "content": aggregator_user_content}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


###############################################################################
# Define a Pydantic model for the conference recommendation
###############################################################################
class ConferenceRecommender(BaseModel):
    conference_title: str
    rationale: str

###############################################################################
# Create a synchronous OpenAI client for the conference recommendation
###############################################################################
client_sync = OpenAI()  

def router_conference(pdf_path: str, final_decision: str) -> ConferenceRecommender:
    """
    Takes in the PDF path and the aggregator final decision,
    returns a recommended conference and rationale.
    """
    extracted_object = research_paper_extraction(pdf_path=pdf_path)
    
    formatted_prompt = RECOMMENDER_PROMPT.format(decision_text=final_decision)

    
    completion = client_sync.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system", 
                "content": formatted_prompt
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


###############################################################################
# 8. Process a single PDF: 
#    - Extract text, get feedback from 3 reviewers, aggregate, 
#    - Then get recommended conference & rationale
###############################################################################
async def process_paper(pdf_path: str, paper_id: str):
    paper_extracted_text = research_paper_extraction(pdf_path)
    user_prompt = USER_PROMPT_TEMPLATE.format(extracted_text=paper_extracted_text)
    review_tasks = [get_reviewer_feedback(sp, user_prompt) for sp in reviewer_prompts]
    reviewer_responses = await asyncio.gather(*review_tasks)

    final_decision = await get_aggregated_decision(
        aggregator_prompt=aggregator_system_prompt,
        paper_details=paper_extracted_text,
        reviewer_feedbacks=reviewer_responses
    )


    if "final decision: publishable" in final_decision.lower():
        publishable = 1
    elif "final decision: not publishable" in final_decision.lower():
        publishable = 0
    else:
        raise ValueError("Unable to determine publishability from final decision.")

    if publishable == 1:
        try:
            conference_info = router_conference(pdf_path, final_decision)
            conference_title = conference_info.conference_title
            rationale = conference_info.rationale
        except Exception as e:
            print(f"Error in conference recommendation for {paper_id}: {e}")
            conference_title = "Error"
            rationale = "Could not generate rationale."
    else:
        conference_title = "NA"
        rationale = "NA"

    return publishable, conference_title, rationale



###############################################################################
# 9. Main entry point: 
#    - Loop over PDFs, gather results, write a single CSV
###############################################################################
async def main():
    papers_folder = "Papers"
    pdf_files = glob.glob(os.path.join(papers_folder, "*.pdf"))

    output_csv = "paper_publishability_conference_2.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["Paper ID", "Publishable", "Conference", "Rationale"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for pdf_path in tqdm(pdf_files, desc="Processing papers", unit="paper"):
            paper_id = os.path.splitext(os.path.basename(pdf_path))[0]
            try:
                publishable_label, conference_title, rationale = await process_paper(pdf_path, paper_id)

                writer.writerow({
                    "Paper ID": paper_id,
                    "Publishable": publishable_label,
                    "Conference": conference_title,
                    "Rationale": rationale
                })
            except Exception as e:
                print(f"Error processing {paper_id}: {e}")

    print(f"\nResults have been saved to {output_csv}")


if __name__ == "__main__":
    asyncio.run(main())
