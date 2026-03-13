# engine.py - محرك الاستدلال المنطقي باستخدام الذكاء الاصطناعي
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

class SemanticGuardEngine:
    """
    هذا المحرك هو المسؤول عن تحليل التناقضات الدلالية بين حقول الاستمارة
    """
    def __init__(self):
        # يتم جلب المفتاح من ملف .env لضمان الأمان
        self.api_key = os.getenv("API_KEY", "")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o" # يمكن استخدام أي نموذج يدعم JSON mode

    def analyze_record(self, data_dict):
        """
        تحليل سجل واحد وإرجاع درجة ثقة وتبرير منطقي
        """
        # هندسة الأوامر (Prompt Engineering) باستخدام تقنية Few-Shot
        system_prompt = """
        أنت مساعد ذكي متخصص في جودة البيانات الإحصائية (الحارس الدلالي).
        مهمتك: اكتشاف التناقضات المنطقية المعقدة التي تفشل القواعد التقليدية في رصدها.
        يجب أن ترد دائماً بصيغة JSON تحتوي على:
        1. "score": درجة من 0 إلى 1 (حيث 1 تعني بيانات منطقية تماماً).
        2. "is_valid": boolean (True إذا كانت النتيجة > 0.7).
        3. "reason": شرح مختصر باللغة العربية للخطأ المنطقي إن وجد.
        """

        user_content = f"""
        حلل السجل التالي بدقة: {json.dumps(data_dict, ensure_ascii=False)}

        أمثلة للتناقضات المستهدفة:
        - تعارض (العمر) مع (الحالة الاجتماعية) مثل طفل متزوج.
        - تعارض (المسمى الوظيفي) مع (المؤهل) مثل طبيب بمؤهل ابتدائي.
        - تعارض (سنوات الخبرة) مع (العمر) مثل خبرة 30 سنة وعمره 25.
        - تعارض (الدخل) مع (المهنة) في حالات غير منطقية إحصائياً.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"score": 0, "is_valid": False, "reason": f"حدث خطأ في الاتصال: {str(e)}"}
