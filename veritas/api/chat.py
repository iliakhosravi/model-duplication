import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from .models import EvaluationLog

MODEL_NAME = "Qwen/Qwen3-0.6B"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",  # Use auto for stability
    device_map="auto"
)

SYSTEM_PROMPT = """You are an evaluator.
You must ONLY answer with one of the following:
- YES
- NO
- NOT SURE

Rules:
- Base your answer only on the information I provide.
- Do not use any outside knowledge.
- Do not explain your reasoning.
- Do not output anything other than YES, NO, or NOT SURE.
"""

def extract_final_answer(text: str) -> str:
            """
            Extract only YES / NO / NOT SURE from a raw model output.
            """
            text = text.upper().strip()

            # First, look for explicit YES, NO, NOT SURE at the end
            for ans in ["YES", "NO", "NOT SURE"]:
                if text.endswith(ans):
                    return ans

            # If not at the end, search anywhere
            for ans in ["YES", "NO", "NOT SURE"]:
                if ans in text:
                    return ans

            # Fallback
            return "NOT SURE"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        info = data.get("info", "")
        question = data.get("question", "")
        userid = data.get("userid", "anonymous")

        # Build messages for Qwen chat template
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is the information:\n{info}\n\nQuestion:\n{question}"}
        ]

        # Apply chat template
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True
        )

        inputs = tokenizer([text], return_tensors="pt").to(model.device)

        # Generate model output
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.2,  # slightly stochastic for stability
            do_sample=True
        )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True).upper()
        # Extract the final answer
        final_answer = response.split("QUESTION:")[-1].strip()
        final_answer = extract_final_answer(response)


        # Ensure answer is one of YES / NO / NOT SURE
        # if final_answer not in ["YES", "NO", "NOT SURE"]:
        #     final_answer = "NOT SURE"

        # Save to MongoDB
        EvaluationLog(
            userid=userid,
            info=info,
            question=question,
            response=final_answer
        ).save()

        # Send the final answer to WebSocket
        await self.send(json.dumps({
            "type": "final",
            "answer": final_answer,
            "info": info,
            "question": question
        }))

    












# MODEL_NAME = "Qwen/Qwen3-0.6B"
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# model = AutoModelForCausalLM.from_pretrained(
#     MODEL_NAME,
#     torch_dtype=torch.float16,
#     device_map="auto"
# )

# SYSTEM_PROMPT = """You are an evaluator.
# You must ONLY answer with one of the following:
# - YES
# - NO
# - NOT SURE

# Rules:
# - Base your answer only on the information I provide.
# - Do not use any outside knowledge.
# - Do not explain your reasoning.
# - Do not output anything other than YES, NO, or NOT SURE.
# - if the answer is correct write YES
# - if the answer is incorrect write NO
# - if there is not enough information write NOT SURE
# """

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()

#     async def disconnect(self, close_code):
#         pass

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         info = data.get("info", "")
#         question = data.get("question", "")
#         userid = data.get("userid", "anonymous")

#         prompt = f"{SYSTEM_PROMPT}\nHere is the information:\n{info}\n\nQuestion:\n{question}"
#         inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

#         # Create TextIteratorStreamer
#         streamer = TextIteratorStreamer(tokenizer, skip_special_tokens=True)

#         # Run generation in a background thread
#         thread = threading.Thread(
#             target=model.generate,
#             kwargs={
#                 "inputs": inputs.input_ids,
#                 "max_new_tokens": 128,
#                 "temperature": 1e-10,
#                 "streamer": streamer
#             }
#         )
#         thread.start()

#         # Stream tokens to WebSocket
#         answer_tokens = []
#         async for token in self.stream_streamer(streamer):
#             answer_tokens.append(token)

#         answer_text = "".join(answer_tokens).strip().upper()

#         # Ensure final answer is YES / NO / NOT SURE
#         # if answer_text.startswith("YES"):
#         #     final_answer = "YES"
#         # elif answer_text.startswith("NO"):
#         #     final_answer = "NO"
#         # elif "NOT SURE" in answer_text:
#         #     final_answer = "NOT SURE"
#         # else:
#         #     final_answer = "NOT SURE"
#         final_answer = answer_text

#         # Save to MongoDB
#         EvaluationLog(userid=userid, info=info, question=question, response=final_answer).save()

#         # Send final answer
#         await self.send(json.dumps({
#             "type": "final",
#             "answer": final_answer,
#             "info": info,
#             "question": question
#         }))

#     async def stream_streamer(self, streamer):
#         loop = asyncio.get_event_loop()
#         for token in streamer:
#             yield token
