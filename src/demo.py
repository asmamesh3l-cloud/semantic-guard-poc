import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. إعدادات الصفحة والتحميل
st.set_page_config(
    page_title="الحارس الدلالي - Demo", 
    layout="wide", 
    page_icon="🛡️"
)
load_dotenv()

# 2. شريط جانبي لإعدادات المفتاح (Sidebar)
with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    st.markdown("---")
    
    # محاولة جلب المفتاح من الملفات أولاً
    default_key = st.secrets.get("API_KEY") or os.getenv("API_KEY", "")
    if default_key == "1111": default_key = "" 
    
    user_api_key = st.text_input(
        "أدخل مفتاح OpenAI API (اختياري):", 
        value=default_key, 
        type="password",
        help="إذا تركت الحقل فارغاً سيعمل النظام في وضع المحاكاة التجريبي."
    )
    
    target_model = st.selectbox(
        "اختر نموذج الذكاء الاصطناعي:",
        ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0
    )
    
    st.markdown("---")
    st.info("💡 ملاحظة: عند إدخال مفتاح يبدأ بـ 'sk-' سيتم تفعيل الاستدلال المنطقي الحقيقي.")

# 3. وظيفة المحرك الذكي (دعم وضع العرض بدون مفتاح)
def get_ai_validation(record_data, api_key_input):
    """تحليل البيانات مع دعم وضع المحاكاة أو الاتصال الفعلي"""
    api_key = api_key_input or st.secrets.get("API_KEY") or os.getenv("API_KEY")
    is_demo_mode = not api_key or api_key in ["1111", "DEMO", ""]

    if is_demo_mode:
        # منطق محاكاة للأخطاء المشهورة
        age = record_data.get("العمر", 0)
        job = record_data.get("المهنة", "")
        exp = record_data.get("سنوات_الخبرة", 0)
        edu = record_data.get("المؤهل", "")

        if age < 18 and job in ["طيار مدني", "جراح", "مدير تنفيذي"]:
            return {"score": 0.2, "reasoning": "محاكاة: هناك تعارض بين العمر الصغير والمهنة التي تتطلب سنوات دراسة وترخيصاً رسمياً."}
        if exp > age - 15: 
            return {"score": 0.3, "reasoning": "محاكاة: سنوات الخبرة المدخلة غير منطقية مقارنة بعمر المستجيب."}
        if edu == "ابتدائي" and job in ["جراح", "مهندس"]:
            return {"score": 0.1, "reasoning": "محاكاة: المؤهل التعليمي لا يتناسب مع المتطلبات العلمية للمهنة المدخلة."}
        
        return {"score": 0.95, "reasoning": "محاكاة: البيانات تبدو منطقية وسليمة بناءً على الفحص الأولي."}

    # استدعاء OpenAI الحقيقي
    client = OpenAI(api_key=api_key)
    record_json = json.dumps(record_data)
    prompt = f"أنت خبير في تدقيق جودة البيانات. حلل السجل التالي وأجب بـ JSON (score, reasoning): {record_json}"

    try:
        response = client.chat.completions.create(
            model=target_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"score": 0, "reasoning": f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {str(e)}"}

# 4. الواجهة الرسومية (UI Design)
# العنوان الرئيسي
st.title("🛡️ الحارس الدلالي (Semantic Guard)")
st.subheader("نظام الذكاء الاصطناعي للتدقيق المنطقي والارتقاء بجودة البيانات اللحظية")

# قسم نظرة عامة (Overview)
with st.container():
    st.markdown("### 🌟 نظرة عامة (Overview)")
    st.write(
        "الحارس الدلالي هو نموذج أولي (POC) لمساعد ذكي لجودة البيانات. "
        "يتميز بقدرته على الانتقال من **'التحقق الرقمي'** إلى **'الإدراك المنطقي'**، "
        "حيث يستخدم الذكاء الاصطناعي لرصد التناقضات السياقية (مثل تعارض المهنة مع السن) "
        "لحظياً أثناء جمع البيانات الميدانية."
    )

# قسم التشغيل السريع (Quick Start)
with st.expander("🚀 التشغيل السريع (Quick Start) - اضغط هنا"):
    st.markdown("""
    1. **تعبئة البيانات:** أدخل القيم في الحقول أدناه (العمر، المهنة، المؤهل).
    2. **تفعيل الذكاء الاصطناعي و في حال لم تدخل المفتاح سيعمل المحاكي المنطقي بدل من الذكاء الاصطناعي :** أدخل مفتاح OpenAI الخاص بك في الشريط الجانبي (يسار الصفحة).
    3. **التحقق:** اضغط على زر 'تحقق من المنطق الدلالي' لمشاهدة تحليل النظام.
    """)

st.markdown("---")

# تنبيه وضع التشغيل
if not user_api_key or user_api_key in ["1111", "DEMO"]:
    st.warning("⚠️ يعمل النظام الآن في **وضع العرض التجريبي** (Simulation).")
else:
    st.success("✨ النظام متصل الآن بمحرك الذكاء الاصطناعي الفعلي.")

# مدخلات البيانات
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

# زر التحقق
if st.button("تحقق من المنطق الدلالي فوراً"):
    with st.spinner('جاري الاستدلال المنطقي...'):
        result = get_ai_validation(record_to_test, user_api_key)
        
        st.write("---")
        score = result.get("score", 0)
        if score > 0.7:
            st.success(f"✅ درجة الثقة: {int(score*100)}%")
            st.info(f"**النتيجة:** {result.get('reasoning') or 'البيانات منطقية وسليمة.'}")
        else:
            st.error(f"⚠️ تنبيه منطقي! (درجة الثقة: {int(score*100)}%)")
            st.warning(f"**السبب:** {result.get('reasoning')}")

with st.expander("🔍 معاينة البيانات المرسلة (JSON)"):
    st.json(record_to_test)
