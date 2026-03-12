import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SemanticGuardEngine:
    def __init__(self):
        # Initialize OpenAI client (API key from .env)
        self.client = OpenAI(api_key=os.getenv("API_KEY", ""))
        self.model = os.getenv("LLM_MODEL", "gpt-4o")

    def _build_prompt(self, record_data):
        """Construct prompt with Few-Shot examples for logical reasoning"""
        
        examples = """
        أمثلة سابقة للمنطق السليم والتنبيهات:
        1. السجل: {"العمر": 10, "الحالة_الاجتماعية": "متزوج"} -> النتيجة: {"score": 0.1, "error": "لا يمكن لسن 10 سنوات أن يكون متزوجاً منطقياً."}
        2. السجل: {"المؤهل": "ابتدائي", "المهنة": "جراح"} -> النتيجة: {"score": 0.05, "error": "مهنة الجراح تتطلب مؤهلاً جامعيًا تخصصيًا، ولا يكفي المؤهل الابتدائي."}
        3. السجل: {"المؤهل": "بكالوريوس هندسة", "المهنة": "مهندس مدني"} -> النتيجة: {"score": 1.0, "error": null}
        """

        prompt = f"""
        أنت خبير في تدقيق جودة البيانات الإحصائية. حلل السجل التالي بناءً على المنطق البشري والترابط السياقي.
        
        {examples}

        السجل المطلوب فحصه حالياً:
        {json.dumps(record_data, ensure_ascii=False)}

        يجب أن يكون الرد بصيغة JSON فقط:
        {{
            "score": (رقم بين 0 و 1 يمثل درجة الثقة)،
            "reasoning": (شرح موجز باللغة العربية للخطأ أو null إذا كان سليماً)
        }}
        """
        return prompt

    def validate_record(self, record_data):
        """Send request to LLM and return logical analysis"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت مدقق بيانات ذكي."},
                    {"role": "user", "content": self._build_prompt(record_data)}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"score": 0, "reasoning": f"خطأ في الاتصال بالمحرك: {str(e)}"}
