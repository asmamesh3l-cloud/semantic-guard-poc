# main.py - واجهة برمجة التطبيقات (FastAPI Backend) لنظام الحارس الدلالي
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from engine import SemanticGuardEngine
import uvicorn

# إنشاء تطبيق FastAPI ليكون حلقة الوصل بين الاستمارة ومحرك الذكاء الاصطناعي
app = FastAPI(
    title="الحارس الدلالي - API",
    description="واجهة برمجية للتحقق اللحظي من جودة البيانات الإحصائية"
)

# تهيئة محرك الاستدلال المنطقي
engine = SemanticGuardEngine()

# تعريف هيكل البيانات المتوقع استقباله في الطلبات (Payload)
class RecordRequest(BaseModel):
    data: Dict[str, Any]

@app.get("/")
def health_check():
    """نقطة نهاية للتحقق من أن النظام يعمل بنجاح"""
    return {
        "status": "online",
        "service": "Semantic Guard API",
        "ready": True
    }

@app.post("/validate")
def validate_record(request: RecordRequest):
    """
    استقبال سجل بيانات واحد، إرساله للمحرك الذكي، وإعادة النتيجة.
    هذه الوظيفة تمثل الربط (Orchestration) الفعلي المطلوب في التحدي.
    """
    # التأكد من أن البيانات ليست فارغة
    if not request.data:
        raise HTTPException(status_code=400, detail="السجل المرسل فارغ أو غير مكتمل")

    # استدعاء المحرك الذكي المحدث لتحليل السجل
    try:
        analysis_result = engine.analyze_record(request.data)

        # إرجاع النتيجة بتنسيق موحد
        return {
            "success": True,
            "analysis": analysis_result
        }
    except Exception as e:
        # التعامل مع أخطاء الاتصال أو المعالجة
        raise HTTPException(
            status_code=500,
            detail=f"فشل المحرك في تحليل البيانات: {str(e)}"
        )

# نقطة الانطلاق لتشغيل الخادم المحلي
if __name__ == "__main__":
    # تشغيل الخادم على المنفذ 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
