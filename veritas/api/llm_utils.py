# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch

# model_name = "Qwen/Qwen3-0.6B"

# # Load the tokenizer and the model once (global)
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(
#     model_name,
#     torch_dtype="auto",
#     device_map="auto"
# )

# def ask_evaluator(info: str, question: str) -> str:
#     """
#     Ask Qwen3 a YES/NO/NOT SURE question based only on provided info.
#     """
#     system_prompt = (
#         "You are an evaluator.\n"
#         "You must ONLY answer with one of the following:\n"
#         "- YES\n"
#         "- NO\n"
#         "- NOT SURE\n\n"
#         "Rules:\n"
#         "- Base your answer only on the information I provide.\n"
#         "- Do not use any outside knowledge.\n"
#         "- Do not explain your reasoning.\n"
#         "- Do not output anything other than YES, NO, or NOT SURE.\n"
#         "If your answer is not one of these, it will be considered invalid."
#     )

#     user_prompt = f"""
# Here is the information:
# {info}

# Question:
# {question}
#     """

#     messages = [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": user_prompt}
#     ]

#     # Apply chat template
#     text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
#     inputs = tokenizer([text], return_tensors="pt").to(model.device)

#     # Generate response
#     outputs = model.generate(**inputs, max_new_tokens=200)
#     response = tokenizer.decode(outputs[0], skip_special_tokens=True)

#     answer = response.split("Question:")[-1].strip().upper()
#     if "YES" in answer:
#         return "YES"
#     elif "NO" in answer:
#         return "NO"
#     elif "NOT SURE" in answer or "NOTSURE" in answer:
#         return "NOT SURE"
#     else:
#         return "NOT SURE"  # fallback safeguard
