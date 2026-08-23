

# # the method is no longer used.
# def cross_model_persona_comparisons(LLM_response_list, cross_LLM_prompts, model = "openrouter/deepseek/deepseek-v4-flash"):
#     #model = "openrouter/deepseek/deepseek-v4-flash"  # rated as #1 in health and academia. As such I will be using to compare outputs 
#     cross_model_person_comparions = []
#     max_retries = 50

#     for persona in PERSONA_TITLES:
#         cross_model_persona_outputs = [row for row in LLM_response_list if row["persona"] == persona]
#         across_model_persona_text = f" This is the following outputs for persona {persona}"
#         for output in cross_model_persona_outputs:
#             across_model_persona_text += f"\n\nThis is the output from the model {output['model']}\n\n{output['raw_output']}"

#         for attempt in range(1, max_retries +1):
#             try: 
#                 persona_ouputs_to_be_compared_across_models = completion(
#                     model = model,
#                     messages = [
#                         {"role": "user", "content": cross_LLM_prompts},
#                         {"role": "user", "content": f'{across_model_persona_text.strip()}'}],
#                     timeout=360
#                 )
#                 break 
    
#             except litellm.Timeout:
#                 print(f"Timeout on attempt {attempt}/{max_retries} for {model}. Retrying...")
#                 continue
#             except litellm.AuthenticationError:
#                 print(f'Authentication failed. Check your {model}_API_KEY environment variable.')
#                 return None, None
#             except litellm.RateLimitError as e:
#                 print(f"Rate limited. System says: {e}.")
#                 return None, None
#             except litellm.ContextWindowExceededError:
#                 print("Prompt is too large.")
#                 return None, None
#             except litellm.BadRequestError as e:
#                 print(f"Invalid payload shape or parameters: {e}")
#                 return None, None
#             except litellm.APIConnectionError:
#                 print(f"Network failure or {model} servers are currently unresponsive.")
#                 continue
#             except Exception as e:
#                 print(f"An unexpected error occurred: {e}")
#                 continue
#         else:
#             print(f"Giving up on {model} after {max_retries} timeouts.")
#             return None, None

#         content = persona_ouputs_to_be_compared_across_models.choices[0].message.content
#         if not content:
#             print(f"Empty/error response from {model} (finish_reason={persona_ouputs_to_be_compared_across_models.choices[0].finish_reason}). Raw response: {persona_ouputs_to_be_compared_across_models}")
#             continue

#         path_for_persona_comparisons_across_models = write_to_file(f'{run_id}-Cross_Model-{persona}-analysis-', content)

#         cross_model_person_comparions.append(
#             {
#                 "persona": persona,
#                 "model" : model,
#                 "raw_output" : content,
#                 "file_path" : path_for_persona_comparisons_across_models
#             }
#         )

#     return cross_model_person_comparions



# def final_analysis_model(between_model_output, analysis_prompt):
#     model = "openrouter/deepseek/deepseek-v4-flash"
#     max_retries = 50
#     for attempt in range (1, max_retries +1 ):
#         try: 
#             final_analysis_extraction = completion(
#                 model = model,
#                 messages = [
#                     {"role": "user", "content": analysis_prompt},
#                     {"role": "user", "content": f'This is the output \n {between_model_output}'}],
#                 timeout=180
#             )
#             break

#         except litellm.Timeout:
#             print(f"Timeout on attempt {attempt}/{max_retries} for {model}. Retrying...")
#             continue
#         except litellm.AuthenticationError:
#             print(f'Authentication failed. Check your {model}_API_KEY environment variable.')
#             return
#         except litellm.RateLimitError as e:
#             print(f"Rate limited. System says: {e}.")
#             return
#         except litellm.ContextWindowExceededError:
#             print("Prompt is too large.")
#             return
#         except litellm.BadRequestError as e:
#             print(f"Invalid payload shape or parameters: {e}")
#             return
#         except litellm.APIConnectionError:
#             print(f"Network failure or {model} servers are currently unresponsive.")
#             continue
#         except Exception as e:
#             print(f"An unexpected error occurred: {e}")
#             continue
#     else:
#         print(f"Giving up on {model} after {max_retries} timeouts.")
#         return None

#     content = final_analysis_extraction.choices[0].message.content
#     if not content:
#         print(f"Empty/error response from {model} (finish_reason={final_analysis_extraction.choices[0].finish_reason}). Raw response: {final_analysis_extraction}")
#         return None
#     file_path = write_to_file("Deep_seek_v4_flash_final_analysis", content)
#     return {"File_name":file_path, "raw_output":content}

