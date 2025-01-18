from extraction import research_paper_extraction, extract_text
from tqdm import tqdm
from agent import router_conference
from combined_task import USER_PROMPT_TEMPLATE, get_reviewer_feedback, get_aggregated_decision, reviewer_prompts, aggregator_system_prompt


def task_1_process(pdf_path: str):
    extract_pdf = extract_text(pdf_path=pdf_path)
    user_prompt = USER_PROMPT_TEMPLATE.format(extracted_text=extract_pdf)
    
    review_tasks = [get_reviewer_feedback(sp, user_prompt) for sp in tqdm(reviewer_prompts)]

    final_decision = get_aggregated_decision(
        aggregator_prompt=aggregator_system_prompt,
        paper_details=extract_pdf,
        reviewer_feedbacks=review_tasks
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
            print(f"Error in conference recommendation for {pdf_path}: {e}")
            conference_title = "Error"
            rationale = "Could not generate rationale."
    else:
        conference_title = "NA"
        rationale = "NA"

    return publishable, conference_title, rationale

