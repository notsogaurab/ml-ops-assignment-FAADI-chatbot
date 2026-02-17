import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .. import config
from .prompts import FEW_SHOT_EXAMPLES, SYSTEM_PROMPT, build_user_prompt


class LLMService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.settings.LLM_MODEL, trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            config.settings.LLM_MODEL,
            device_map="auto" if self.device == "cuda" else None,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            trust_remote_code=True,
        )
        if self.device == "cpu":
            self.model.to(self.device)

    def generate(self, context_chunks, query, chat_history=None):
        if not context_chunks:
            return "I don't have any documents indexed to answer this question."

        user_content = build_user_prompt(context_chunks, query, chat_history)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(FEW_SHOT_EXAMPLES)
        messages.append({"role": "user", "content": user_content})

        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(
            model_inputs.input_ids, max_new_tokens=512, do_sample=True, temperature=0.3
        )

        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[
            0
        ]
        return response


llm_service = LLMService()
