import io

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

import torch
from transformers import AutoProcessor
from PIL import Image
import numpy as np
from transformers import PaliGemmaForConditionalGeneration
import os

os.environ['HF_TOKEN'] = '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'
FINETUNED_MODEL_ID = "qhfmshal/TRPaliGemma"
MAX_LENGTH = 512

processor = AutoProcessor.from_pretrained(FINETUNED_MODEL_ID)
model = PaliGemmaForConditionalGeneration.from_pretrained(FINETUNED_MODEL_ID)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

PROMPT = "extract HTML."

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vue 프론트엔드 주소
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=[""],
)

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        # 파일 이름 및 파일 크기 가져오기
        file_name = file.filename
        content_size = str(len(contents)) + "B"  # 파일 크기 (바이트)
        print(file_name, content_size)
        print(type(file))

        print("1")
        # 이미지를 PIL 이미지로 변환
        print(contents)
        print("2")
        img = Image.open(io.BytesIO(contents))
        print("3")

        # input의 device 설정
        inputs = processor(text=PROMPT, images=img, return_tensors="pt")
        inputs = {key: value.to(device) for key, value in inputs.items()}

        print("4")

        # 모델 추론
        generated_ids = model.generate(**inputs, max_new_tokens=MAX_LENGTH)
        image_token_index = model.config.image_token_index
        num_image_tokens = len(generated_ids[generated_ids==image_token_index])
        num_text_tokens = len(processor.tokenizer.encode(PROMPT))
        num_prompt_tokens = num_image_tokens + num_text_tokens + 2
        generated_html = processor.batch_decode(generated_ids[:, num_prompt_tokens:], skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

        print("5")

        return JSONResponse(content={
            "filename": file_name,
            "size": content_size,
            "inference_result": generated_html
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})