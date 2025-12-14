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


DEFAULT_CHAT_TEMPLATE_PARAMS = {
    "tokenize": False,
    "add_generation_prompt": True,
    "enable_thinking": True,
}

DEFAULT_GENERATION_PARAMS = {
    "max_new_tokens": 512,
    "temperature": 0.2,  # slightly stochastic for stability
    "do_sample": True,
}

DEFAULT_TOKENIZER_INPUTS = {
    "return_tensors": "pt",
}


def evaluate_prompt(
    messages,
    userid: str = "anonymous",
    chat_template_params=None,
    tokenizer_input_params=None,
    generation_params=None,
) -> str:
    """
    Run the model for a single request with user-provided parameters and persist the result.
    """
    if not messages:
        raise ValueError("messages are required for generation")

    chat_params = {**DEFAULT_CHAT_TEMPLATE_PARAMS, **(chat_template_params or {})}
    tokenizer_params = {**DEFAULT_TOKENIZER_INPUTS, **(tokenizer_input_params or {})}
    generation_kwargs = {**DEFAULT_GENERATION_PARAMS, **(generation_params or {})}

    text = tokenizer.apply_chat_template(messages, **chat_params)
    inputs = tokenizer([text], **tokenizer_params).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            **generation_kwargs,
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    EvaluationLog(
        userid=userid,
        parameters={
            "messages": messages,
            "chat_template": chat_params,
            "tokenizer_inputs": tokenizer_params,
            "generation": generation_kwargs,
        },
        response=response,
    ).save()

    return response
