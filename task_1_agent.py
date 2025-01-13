import openai
import asyncio


###############################################################################
# 1. system prompts for each reviewer
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

    Then provide:
    - A short textual review (2-3 sentences).
    - A final label: either "Publishable" or "Not Publishable".
    
    Make sure your response is clearly structured.
    """
]

###############################################################################
# context
###############################################################################
context= ""

###############################################################################
    # 2. User prompt: Define the task and provide an example for the reviewers
###############################################################################
user_prompt = """
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

Now classify the given research paper based on given structured extraction{context} from the actual research paper based on the reasoning steps in the examples. 
"""


###############################################################################
# 3. Parallel function to get reviewer feedback asynchronously
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
    response = await openai.ChatCompletion.acreate(
        model="gpt-4", 
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
3. The average of each criterion (Originality, Technical Soundness, Clarity, Relevance) computed across the three reviewers.

Your task:
- Read the paper details carefully.
- Read each reviewer feedback and the average scores.
- Decide if the paper should be labeled "Publishable" or "Not Publishable".
- Provide a short explanation of your reasoning (2-3 sentences).
- Provide a confidence measure on a scale of 1 to 10 (where 1 = very uncertain, 10 = extremely confident).

You may consider the reviewers' feedback, but use your own judgment as well.
Format your response in a clear and structured manner, for example:

Final Decision: <Publishable or Not Publishable>
Reasoning: <2-3 sentences summarizing the key points>
Confidence: <number from 1 to 10>
"""


###############################################################################
# 5. Aggregator function: call the LLM to combine reviewer feedback & final verdict
###############################################################################
async def get_aggregated_decision(
    aggregator_prompt: str,
    paper_details: str,
    reviewer_feedbacks: list,
    avg_scores: dict
):
    """
    Makes a call to the OpenAI ChatCompletion endpoint for the final aggregator.
    The aggregator has access to:
      - paper_details
      - all reviewer feedback
      - average scores
    Returns a structured final decision.
    """
    
    aggregator_user_content = f"""
Paper Details:
{paper_details}

Reviewer Feedbacks:
1) {reviewer_feedbacks[0]}
2) {reviewer_feedbacks[1]}
3) {reviewer_feedbacks[2]}

Average Scores:
Originality: {avg_scores['Originality']:.2f}
Technical Soundness: {avg_scores['Technical Soundness']:.2f}
Clarity: {avg_scores['Clarity']:.2f}
Relevance: {avg_scores['Relevance']:.2f}
"""

    response = await openai.ChatCompletion.acreate(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": aggregator_prompt},
            {"role": "user", "content": aggregator_user_content}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


###############################################################################
# 6. Main function: orchestrate the entire workflow
###############################################################################
async def main():
    
    review_tasks = [
        get_reviewer_feedback(sp, user_prompt) for sp in reviewer_prompts
    ]
    reviewer_responses = await asyncio.gather(*review_tasks)

    scores_list = []
    for resp in reviewer_responses:
        lines = resp.splitlines()
        score_dict = {"Originality": 0, "Technical Soundness": 0, "Clarity": 0, "Relevance": 0}

        for line in lines:
            line_lower = line.lower()
            if "originality:" in line_lower:
                score_dict["Originality"] = float(line.split(":")[-1].strip())
            elif "technical soundness:" in line_lower:
                score_dict["Technical Soundness"] = float(line.split(":")[-1].strip())
            elif "clarity:" in line_lower:
                score_dict["Clarity"] = float(line.split(":")[-1].strip())
            elif "relevance:" in line_lower:
                score_dict["Relevance"] = float(line.split(":")[-1].strip())

        scores_list.append(score_dict)

    
    avg_scores = {
        "Originality": sum(d["Originality"] for d in scores_list) / len(scores_list),
        "Technical Soundness": sum(d["Technical Soundness"] for d in scores_list) / len(scores_list),
        "Clarity": sum(d["Clarity"] for d in scores_list) / len(scores_list),
        "Relevance": sum(d["Relevance"] for d in scores_list) / len(scores_list),
    }

    final_decision = await get_aggregated_decision(
        aggregator_prompt=aggregator_system_prompt,
        paper_details=user_prompt,
        reviewer_feedbacks=reviewer_responses,
        avg_scores=avg_scores
    )

   
    # print("----------- REVIEWER RESPONSES -----------")
    # for i, resp in enumerate(reviewer_responses):
    #     print(f"Reviewer {i+1} Response:\n{resp}\n")

    # print("----------- AVERAGE SCORES -----------")
    # for criterion, value in avg_scores.items():
    #     print(f"{criterion}: {value:.2f}")

    print("\n----------- FINAL AGGREGATED DECISION -----------")
    print(final_decision)


###############################################################################
# 7. Run main
###############################################################################
if __name__ == "__main__":
    asyncio.run(main())

