import os 
import litellm
import requests
from litellm import completion
from pathlib import Path
import time
from numpy import random as rand


# Comments -- for this to work, you must have a Custom_prompt folder in you path with these prompt text files in there.
persona_files = Path("Custom_prompts") / "New_personas.txt"
task_files = Path("Custom_prompts") / "New_task_prompt.txt"
evidence_files = Path("Custom_prompts") / "New_evidence_prompt.txt"
cross_LLM_prompts_file = Path("Custom_prompts") / "New_cross_model_prompt.txt"
inter_model_cross_persona_comparisons_prompt = Path("Custom_prompts") / "New_inter_model_cross_persona_prompt.txt"



DEFAULT_MODELS = [
    "openrouter/deepseek/deepseek-v4-flash",      # as of 27/07/2026 this was rated as #1 in health and academia
    "openrouter/openai/gpt-5.6-luna",           
    "openrouter/anthropic/claude-sonnet-4.6",     # as of 24/07/26 this was rates as #3 on open-router in health realted topics 
    "openrouter/google/gemini-3.6-flash",
    "openrouter/tencent/hy3"   
    ]

PERSONA_TITLES = ["British_Public", 
                "Patient/Caregiver",
                "General_Practitioner",
                "A&E_consultants",
                "General_medicine_consultant",
                "Local_national-policy_maker",
                "BioTech_Pharma_CEO",
                 ]



# Helper functions:
#  - load_keys reads in the API Keys stored in a text file that should be in your WD
#  - read_file_LLM_response takes in a text file and reads the output. There is not cleaning as it is supposed to be a raw output from an LLM
#  - write_to_file is as described by the name. 
#  - load_prompts reads in the files containing the task prompts and the persona information. Note there is cleaning for the persona that's done before.
#  - sanitise_for_filename is for when model names and or persona titles are incompatible with file directory formating for the output files
#  - get_key_info is self explanitory     

def load_keys(key_txt):
    with open(key_txt, "r", encoding="utf-8") as f:
        output = f.read().splitlines()
        key = str(output[0])
    return key

def read_file_LLM_response(file):
    with open(file, "r", encoding = "utf-8") as f:
        llm_response = f.read()
    return llm_response

def write_to_file(file_name, content):
    output_dir = Path(__file__).parent / "LLM_project_outputs" / f"run-{run_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / sanitise_for_filename(file_name)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content) 
    return output_path


def load_prompts(persona_file, task_file, evidence_file, cross_LLM_prompts_file, inter_model_cross_persona_file):
    with open(persona_file, "r", encoding="utf-8") as a,\
        open(task_file, "r", encoding="utf-8") as b,\
        open(evidence_file, "r", encoding="utf-8") as c, \
        open(cross_LLM_prompts_file, "r", encoding="utf-8") as d, \
        open(inter_model_cross_persona_file, "r", encoding="utf-8") as e:
        content = a.read()
        persona_items = content.split("####")
        task_prompt = b.read()
        evidence_prompt = c.read()
        cross_LLM_prompts = d.read()
        inter_model_cross_persona = e.read()
    return persona_items, task_prompt, evidence_prompt, cross_LLM_prompts, inter_model_cross_persona


def sanitise_for_filename(text):
    return text.replace("/", "_")


def get_key_info(api_key):
    response = requests.get(
        "https://openrouter.ai/api/v1/credits",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    return response.json()
    # {'data': {'total_credits': 100, 'total_usage': 12.34}}





#################
# Code above relates to reading in the prompt files and setting variables
# Code bellow here is API calls and wrangling.
#################


def Bias_Assessment(cross_persona_comparisons, cross_LLM_prompts):
    Random__models = rand.choice(DEFAULT_MODELS, size=3, replace=False)
    selected_For_comparison = [row for row in cross_persona_comparisons if row["model"] in Random__models]
    remaining_models = [m for m in DEFAULT_MODELS if m not in Random__models]
    final_random_assessor = rand.choice(remaining_models)

    Bias_assessment_results = []
    for assessor in Random__models:
        file_path, content = Between_Model_comparions(selected_For_comparison, cross_LLM_prompts, model=assessor, tag="-bias-check")
        Bias_assessment_results.append(
            {
                "assessor": assessor,
                "models_compared": list(Random__models),
                "file_path": file_path,
                "raw_output": content
            }
        )
    raw_output = "\n\n".join([f"Assessor: {row['assessor']}\nModels Compared: {', '.join(row['models_compared'])}\nOutput:\n{row['raw_output']}" for row in Bias_assessment_results])
    bias_check_instructions = (
    "Based on the following outputs, I'd like you to identify if the models are biased,"
    "toward their own outputs. This means if the assessor recognises an output made by "
    "itself from a different chat and, when asked to compare, favours its own model's output."
    )
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            response = completion(
                        model= final_random_assessor,
                        messages=[
                            {"role": "system", "content": f"{bias_check_instructions}\n\n{raw_output}"}
                        ],     
                timeout=180,
            )
            break

        except litellm.Timeout:
            print(f"Timeout on attempt {attempt}/{max_retries} for {final_random_assessor}. Retrying...")
            continue
        except litellm.AuthenticationError:
            print(f'Authentication failed. Check your {final_random_assessor}_API_KEY environment variable.')
            return
        except litellm.RateLimitError as e:
            print(f"Rate limited. System says: {e}.")
            return
        except litellm.ContextWindowExceededError:
            print("Prompt is too large.")
            return
        except litellm.BadRequestError as e:
            print(f"Invalid payload shape or parameters: {e}")
            return
        except litellm.APIConnectionError:
            print(f"Network failure or {final_random_assessor} servers are currently unresponsive.")
            return
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return
    else:
        print(f"Giving up on {final_random_assessor} after {max_retries} timeouts.")
        return

    content = response.choices[0].message.content
    if not content:
        print(f"Empty/error response from {final_random_assessor} (finish_reason={response.choices[0].finish_reason}). Raw response: {response}")
        return

    output_path = write_to_file('Bias_assessment',content)





def prompting_data_collection_function(persona, task, evidence, model, file_name, max_retries=50):
    for attempt in range(1, max_retries + 1):
        try:
            response = completion(
                model=model,
                messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": task},
                    {"role": "user", "content": evidence}
                ],
                extra_body={
                    "tools": [{"type": "openrouter:web_search"}]
                }, 
                timeout=180
            )
            break 
        
        except litellm.Timeout:
            print(f"Timeout on attempt {attempt}/{max_retries} for {model}. Retrying...")
            continue
        except litellm.AuthenticationError:
            print(f'Authentication failed. Check your {model}_API_KEY environment variable.')
            return None, None
        except litellm.RateLimitError as e:
            print(f"Rate limited. System says: {e}.")
            return None, None
        except litellm.ContextWindowExceededError:
            print("Prompt is too large.")
            return None, None
        except litellm.BadRequestError as e:
            print(f"Invalid payload shape or parameters: {e}")
            return None, None
        except litellm.APIConnectionError:
            print(f"Network failure or {model} servers are currently unresponsive.")
            continue
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            continue
    else:
        print(f"Giving up on {model} after {max_retries} timeouts.")
        return None, None

    content = response.choices[0].message.content
    if not content:
        print(f"Empty/error response from {model} (finish_reason={response.choices[0].finish_reason}). Raw response: {response}")
        return None, None

    LLM_text_extraction = write_to_file(file_name, content)
    return LLM_text_extraction, content.strip()


## -Comment-:
#   This method now takes the list of dictionaries in the form - {"model": model, "persona": persona_title, "output": file_path}. This allows use to add the persona title for each outputs to prevent the LLM being confused at what output belongs to who 
#   path_for_extracted_cross_persona_analysis will call a fuction that will return a path to the file with the a within model and between personal analysis of winter pressures. For more information read the inter_model_persona_comparisons_prompt.txt

def inter_model_comparison(LLM_response_list, model, cross_persona_comparisons_prompt):
    max_retries = 50
    for attempt in range( 1, max_retries+1):
        persona_ouputs_to_be_compared = ""
        for row in LLM_response_list:
            if row["model"] == model:
                title = row["persona"]
                text = row["raw_output"]
                persona_ouputs_to_be_compared += f"\n{title} response:\n{text}\n\n"

        try: 
            within_model_comparison_extraction = completion(
                model = model,
                messages = [
                    {"role": "user", "content": cross_persona_comparisons_prompt},
                    {"role": "user", "content": f'These are the following outputs {persona_ouputs_to_be_compared.strip()}'}],
                timeout=180
            )
            break 
        
        except litellm.Timeout:
            print(f"Timeout on attempt {attempt}/{max_retries} for {model}. Retrying...")
            continue
        except litellm.AuthenticationError:
            print(f'Authentication failed. Check your {model}_API_KEY environment variable.')
            return None, None
        except litellm.RateLimitError as e:
            print(f"Rate limited. System says: {e}.")
            return None, None
        except litellm.ContextWindowExceededError:
            print("Prompt is too large.")
            return None, None
        except litellm.BadRequestError as e:
            print(f"Invalid payload shape or parameters: {e}")
            return None, None
        except litellm.APIConnectionError:
            print(f"Network failure or {model} servers are currently unresponsive.")
            continue
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            continue
    else:
        print(f"Giving up on {model} after {max_retries} timeouts.")
        return None, None

    content = within_model_comparison_extraction.choices[0].message.content
    if not content:
        print(f"Empty/error response from {model} (finish_reason={within_model_comparison_extraction.choices[0].finish_reason}). Raw response: {within_model_comparison_extraction}")
        return None, None

    path_for_extracted_cross_persona_analysis = write_to_file(f'-comparison-of-personas-data-{run_id}-{sanitise_for_filename(model)}', content)

    return path_for_extracted_cross_persona_analysis, content



def Between_Model_comparions(cross_persona_comparisons, cross_LLM_prompts, model = "openrouter/deepseek/deepseek-v4-flash", tag = ""):
    LLM_model_ouputs_to_be_compared = ""
    max_retries = 50

    for row in cross_persona_comparisons:
        Current_Model = row["model"]
        text = row["raw_output"]
        LLM_model_ouputs_to_be_compared += f"\n{Current_Model} response:\n{text}\n\n"

    for attempt in range(1, max_retries + 1):
        try: 
            between_model_comparison_extraction = completion(
                model = model,
                messages = [
                    {"role": "user", "content": cross_LLM_prompts},
                    {"role": "user", "content": f'These are the following outputs {LLM_model_ouputs_to_be_compared.strip()}'}],
                timeout=180
            )
            break

        except litellm.Timeout:
            print(f"Timeout on attempt {attempt}/{max_retries} for {model}. Retrying...")
            continue
        except litellm.AuthenticationError:
            print(f'Authentication failed. Check your {model}_API_KEY environment variable.')
            return None, None
        except litellm.RateLimitError as e:
            print(f"Rate limited. System says: {e}.")
            return None, None
        except litellm.ContextWindowExceededError:
            print("Prompt is too large.")
            return None, None
        except litellm.BadRequestError as e:
            print(f"Invalid payload shape or parameters: {e}")
            return None, None
        except litellm.APIConnectionError:
            print(f"Network failure or {model} servers are currently unresponsive.")
            continue
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            continue
    else:
        print(f"Giving up on {model} after {max_retries} timeouts.")
        return None, None

    content = between_model_comparison_extraction.choices[0].message.content
    if not content:
        print(f"Empty/error response from {model} (finish_reason={between_model_comparison_extraction.choices[0].finish_reason}). Raw response: {between_model_comparison_extraction}")
        return None, None

    between_model_comparison_extraction_analysis = write_to_file(f'{run_id}-comparison between model-{sanitise_for_filename(model)}{tag}', content)
    print(f'the final analysis between models {between_model_comparison_extraction_analysis}')

    return between_model_comparison_extraction_analysis, content




def main():  
    global run_id
    run_id = time.strftime("%Y-%m-%d_%H-%M-%S")
    os.environ["OPENROUTER_API_key"] = load_keys("open-router-API-key.txt")

    
    personas, task_prompt, evidence, cross_LLM_prompts, inter_model_cross_persona = load_prompts(
        persona_files, 
        task_files, 
        evidence_files, 
        cross_LLM_prompts_file, 
        inter_model_cross_persona_comparisons_prompt
    )


    responses_data_structure = []
    cross_persona_comparisons = []


    for model in DEFAULT_MODELS:
        for persona_title, indexed_persona in zip(PERSONA_TITLES, personas):
            LLM_response_file_path, text_response = prompting_data_collection_function(
                indexed_persona, 
                task_prompt, 
                evidence, 
                model, 
                f"{sanitise_for_filename(model)}-{persona_title}-output-{run_id}"
            )

            responses_data_structure.append(
                {
                    "model": model, 
                    "persona": persona_title, 
                    "output": LLM_response_file_path,
                    "raw_output": text_response
                }
            )

        file_path_within_model_comparison, raw_within_model_comparison_output =  inter_model_comparison(
            responses_data_structure, 
            model,
            inter_model_cross_persona
        )

        cross_persona_comparisons.append(
            {"model": model, 
             "output": file_path_within_model_comparison, 
             "raw_output" :raw_within_model_comparison_output
            }
        )

   
    
    file_path, raw_output =Between_Model_comparions(cross_persona_comparisons, cross_LLM_prompts, tag="-full-trial")
    Bias_Assessment(cross_persona_comparisons, cross_LLM_prompts)

        
    api_key = load_keys("open-router-API-key.txt")
    key_info = get_key_info(api_key)
    print(f"Spent so far: ${key_info['data']['total_usage']:.4f}")
        

if __name__ == "__main__":
    main()


###### NOTE:

# this method is un-used. It could be implemented and was written as a sanity check for the inbetween checks. Future deployment could be used within the bias assessment. 
# If this method were to be implemented the model used to be assessory would need to be reconsidered
# Find the method in the file names "Unused_methods.py"
    # cross_model_persona_Comparison = cross_model_persona_comparisons(responses_data_structure, inter_persona_cross_model)

#--------------------
#This final analysis method seems largly un-useful and so it has been removed from codebase and moved to Unused_methods.py 
     # final_analysis_model(raw_output, final_analysis)

#######
    
