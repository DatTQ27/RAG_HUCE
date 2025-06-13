# utils.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_prompt(question, contexts):
    prompt = (
        "Bạn là trợ lý ảo AI tư vấn tuyển sinh của Khoa Công nghệ thông tin – Trường Đại học Xây dựng Hà Nội.\n"
        "Chỉ trả lời dựa trên các thông tin được cung cấp bên dưới. "
        "Nếu không tìm thấy thông tin phù hợp, hãy trả lời: \"Tôi không tìm thấy thông tin trong dữ liệu hiện có. Bạn vui lòng liên hệ với Khoa qua số hotline hoặc Fanpage\"\n\n"
    )
    for i, chunk in enumerate(contexts):
        prompt += f"[Đoạn {i+1}]: {chunk}\n\n"

    prompt += (
        f"Câu hỏi: {question}\n\n"
        "Trả lời chi tiết, đầy đủ và rõ ràng. Có thể trình bày theo từng mục hoặc từng ý nếu cần thiết dựa vào nội dung ở trên:\n"
    )
    return prompt


def ask_chatgpt(prompt, model="gpt-4o-mini", temperature=0.5, max_tokens=2500, top_p=0.98):
    """
    Gọi OpenAI API theo định dạng mới (openai>=1.0.0)
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Bạn là trợ lý ảo AI hỗ trợ tuyển sinh của Khoa Công nghệ thông tin, Trường Đại học Xây dựng Hà Nội."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )
    return response.choices[0].message.content
