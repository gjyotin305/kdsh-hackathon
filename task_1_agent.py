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
#### **Examples**
**Example 1:**  
**Title:** "A Novel Algorithm for Optimizing Neural Networks"  
**Abstract:** This paper introduces a groundbreaking optimization method that improves both accuracy and efficiency in neural network training.  
**Methodology:** We use stochastic gradient descent with adaptive momentum and test on the CIFAR-10 and ImageNet datasets.  
**Conclusion:** The proposed method achieves 15% improvement in training time with comparable accuracy.  
**Analysis:**  
- **Originality:** The paper introduces a new optimization method for neural networks, which is a significant contribution.  
- **Technical Soundness:** The methods are well-defined, tested on standard datasets (CIFAR-10 and ImageNet), and results are validated.  
- **Clarity:** The abstract and conclusion are clear and concise, explaining the problem and proposed solution effectively.  
- **Relevance:** The topic is highly relevant to the AI field, particularly for deep learning researchers.  
**Label:** Publishable  

**Example 2:**  
**Title:** "Survey of Neural Networks"  
**Abstract:** This paper provides a general overview of neural network techniques without introducing new insights or experimental results.  
**Methodology:** No specific methods were tested or evaluated.  
**Conclusion:** General survey papers without experiments are less impactful.  
**Analysis:**  
- **Originality:** The paper does not contribute new ideas or methods; it is a general overview.  
- **Technical Soundness:** No experiments or validation are provided.  
- **Clarity:** While the writing may be clear, the lack of technical contribution makes it insufficient.  
- **Relevance:** Neural networks are relevant to AI, but this paper doesn't offer new insights.  
**Label:** Not Publishable  

[Add more examples as needed for few-shot performance...]

---
#### **Classify the Following Paper:**  
**Title:** "Improving GPT Models with Fine-Tuning Techniques"  
**Abstract:** This paper explores the fine-tuning of GPT models on domain-specific datasets.  
**Methodology:** Experimental results show improved performance in text generation tasks using a new loss function.  
**Conclusion:** The new fine-tuning approach outperforms existing baselines by 12%.
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

