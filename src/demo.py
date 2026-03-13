import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. إعدادات الصفحة والتحميل
st.set_page_config(page_title="الحارس الدلالي - Demo", layout="wide")
load_dotenv()

# 2. شريط جانبي لإعدادات المفتاح (Sidebar)
with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    st.markdown("---")
    
    # محاولة جلب المفتاح من الملفات أولاً
    default_key = st.secrets.get("API_KEY") or os.getenv("API_KEY", "")
    if default_key == "1111": default_key = "" # تصفير الكود التجريبي للبدء بمفتاح جديد
    
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
    
    # الأولوية للمفتاح المدخل في الواجهة، ثم الملفات
    api_key = api_key_input or st.secrets.get("API_KEY") or os.getenv("API_KEY")

    # التحقق مما إذا كان المستخدم يرغب في "وضع العرض التجريبي"
    is_demo_mode = not api_key or api_key in ["1111", "DEMO", ""]

    if is_demo_mode:
        # منطق محاكاة للأخطاء المشهورة لتوضيح الفكرة بدون API
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

    # إذا كان هناك مفتاح حقيقي، يتم استدعاء OpenAI
    client = OpenAI(api_key=api_key)
    record_json = json.dumps(record_data)

    prompt = f"""
    أنت خبير في تدقيق جودة البيانات الإحصائية. حلل السجل التالي بناءً على المنطق البشري والترابط السياقي.
    السجل المطلوب فحصه: {record_json}
    يجب أن يكون الرد بصيغة JSON فقط يحتوي على score و reasoning بالعربية.
    """

    try:
        response = client.chat.completions.create(
            model=target_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"score": 0, "reasoning": f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {str(e)}"}

# 4. واجهة المستخدم (Streamlit UI)
st.title("🛡️ الحارس الدلالي (Semantic Guard)")
st.subheader("نظام التدقيق المنطقي اللحظي المدعوم بالذكاء الاصطناعي")

# تنبيه للمستخدم حول وضع التشغيل
if not user_api_key or user_api_key in ["1111", "DEMO"]:
    st.warning("⚠️ يعمل النظام الآن في 'وضع العرض التجريبي' (بدون مفتاح API حقيقي). أدخلي مفتاحك في الشريط الجانبي لتفعيل الذكاء الاصطناعي.")
else:
    st.success("✨ النظام متصل الآن بمحرك الذكاء الاصطناعي (OpenAI) بنجاح.")

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
        result = get_ai_validation(record_to_test, user_api_key)
        
        st.write("---")
        score = result.get("score", 0)
        if score > 0.7:
            st.success(f"✅ درجة الثقة: {int(score*100)}%")
            st.info(f"**النتيجة:** {result.get('reasoning') or 'البيانات منطقية وسليمة.'}")
        else:
            st.error(f"⚠️ تنبيه منطقي! (درجة الثقة: {int(score*100)}%)")
            st.warning(f"**السبب:** {result.get('reasoning')}")

with st.expander("معاينة البيانات المرسلة (JSON)"):
    st.json(record_to_test)
