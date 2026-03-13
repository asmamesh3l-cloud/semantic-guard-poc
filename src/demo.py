import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. إعدادات الصفحة والتحميل
st.set_page_config(page_title="الحارس الدلالي - Demo", layout="wide")
load_dotenv()

# 2. وظيفة المحرك الذكي (دمج منطق engine.py هنا)
def get_ai_validation(record_data):
    """تحليل البيانات مباشرة باستخدام OpenAI دون الحاجة لـ API خارجي"""
    
    # جلب المفتاح من Secrets (للسحابة) أو من .env (للمحلي)
    api_key = st.secrets.get("API_KEY") or os.getenv("API_KEY")
    model_name = st.secrets.get("LLM_MODEL") or os.getenv("LLM_MODEL", "gpt-4o")

    if not api_key or api_key == "1111":
        return {"score": 0, "reasoning": "خطأ: مفتاح API غير صالح أو لم يتم ضبطه في Secrets."}

    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    أنت خبير في تدقيق جودة البيانات الإحصائية. حلل السجل التالي بناءً على المنطق البشري والترابط السياقي.
    السجل المطلوب فحصه: {json.dumps(record_data, ensure_ascii=False)}

    يجب أن يكون الرد بصيغة JSON فقط:
    {{
        "score": (رقم بين 0 و 1 يمثل درجة الثقة)،
        "reasoning": (شرح موجز باللغة العربية للخطأ أو null إذا كان سليماً)
    }}
    """

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"score": 0, "reasoning": f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {str(e)}"}

# 3. واجهة المستخدم (Streamlit UI)
st.title("🛡️ الحارس الدلالي (Semantic Guard)")
st.subheader("نظام التدقيق المنطقي اللحظي المدعوم بالذكاء الاصطناعي")

st.info("💡 ملاحظة: هذا الإصدار المحدث يعمل بشكل مستقل تماماً على السحابة.")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input("العمر", min_value=1, max_value=120, value=10)
    job = st.text_input("المسمى الوظيفي", value="طيار مدني")
    
with col2:
    education = st.selectbox("المؤهل العلمي", ["ابتدائي", "متوسط", "ثانوي", "بكالوريوس", "دكتوراه"])
    exp_years = st.number_input("سنوات الخبرة", min_value=0, max_value=50, value=20)

record_to_test = {
    "العمر": age,
    "المهنة": job,
    "المؤهل": education,
    "سنوات_الخبرة": exp_years
}

if st.button("تحقق من المنطق الدلالي فوراً"):
    with st.spinner('جاري الاستدلال المنطقي...'):
        result = get_ai_validation(record_to_test)
        
        st.write("---")
        if result.get("score", 0) > 0.7:
            st.success(f"✅ درجة الثقة: {result['score']*100}%")
            st.info(f"**النتيجة:** {result.get('reasoning') or 'البيانات منطقية وسليمة.'}")
        else:
            st.error(f"⚠️ تنبيه منطقي! (درجة الثقة: {result.get('score', 0)*100}%)")
            st.warning(f"**السبب:** {result.get('reasoning')}")

with st.expander("معاينة البيانات المرسلة"):
    st.json(record_to_test)
