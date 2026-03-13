import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. إعدادات الصفحة الأساسية وتنسيق المتصفح
st.set_page_config(
    page_title="الحارس الدلالي - Demo", 
    layout="wide", 
    page_icon="🛡️"
)
load_dotenv()

# 2. إضافة CSS مخصص لتحسين الواجهة ودعم اللغة العربية (RTL) مع الخلفيات الملونة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .main-title {
        color: #1E3A8A;
        text-align: center;
        font-weight: 700;
        margin-top: 10px;
    }
    
    .sub-title {
        color: #4B5563;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }

    .overview-box {
        background-color: #F0F9FF;
        padding: 25px;
        border-radius: 15px;
        border-right: 10px solid #3B82F6;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        color: #1E3A8A;
    }
    
    .quickstart-box {
        background-color: #FEF3C7;
        padding: 20px;
        border-radius: 15px;
        border-right: 10px solid #F59E0B;
        color: #92400E;
        margin-bottom: 10px;
    }

    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #3B82F6;
        color: white;
    }
    
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        text-align: right;
    }

    /* تحسين شكل الـ Expander */
    .stExpander {
        border: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. إعدادات الشريط الجانبي (Sidebar) لإدارة المفتاح
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=80)
    st.header("⚙️ إعدادات النظام")
    st.markdown("---")
    
    # محاولة جلب المفتاح الافتراضي من البيئة أو Secrets
    default_key = st.secrets.get("API_KEY") or os.getenv("API_KEY", "")
    if default_key in ["1111", "DEMO"]: default_key = ""
    
    user_api_key = st.text_input(
        "أدخل مفتاح OpenAI API (اختياري):", 
        value=default_key, 
        type="password",
        help="عند ترك الحقل فارغاً، سيفعّل النظام المحاكي المنطقي الداخلي لضمان استمرار العرض."
    )
    
    st.markdown("---")
    st.info("💡 **تلميح:** تفعيل الذكاء الاصطناعي الحقيقي يتطلب مفتاحاً حقيقياً يبدأ بـ 'sk-'.")

# 4. وظيفة المحرك الذكي (دمج المنطق: محاكاة + ذكاء اصطناعي)
def get_ai_validation(record_data, api_key_input):
    api_key = api_key_input or st.secrets.get("API_KEY") or os.getenv("API_KEY")
    # إذا لم يوجد مفتاح أو كان "DEMO"، نستخدم المحاكي المنطقي البرمجي
    is_demo_mode = not api_key or api_key in ["1111", "DEMO", ""]

    if is_demo_mode:
        # منطق المحاكاة للحالات الشائعة (تغطية سيناريوهات الاختبار)
        age = record_data.get("العمر", 0)
        job = record_data.get("المهنة", "")
        exp = record_data.get("سنوات_الخبرة", 0)
        edu = record_data.get("المؤهل", "")

        if age < 18 and job in ["طيار مدني", "جراح", "مدير تنفيذي", "قاضي", "مهندس"]:
            return {"score": 0.15, "reasoning": "محاكاة: هناك تعارض منطقي صارخ بين السن (قاصر) وهذه المهنة التخصصية التي تتطلب تأهيلاً جامعياً وترخيصاً."}
        if exp > (age - 16): 
            return {"score": 0.2, "reasoning": "محاكاة: سنوات الخبرة المدخلة مستحيلة رياضياً مقارنة بالعمر الفعلي."}
        if edu == "ابتدائي" and job in ["جراح", "مهندس", "محامي", "طيار"]:
            return {"score": 0.1, "reasoning": "محاكاة: المؤهل التعليمي الحالي (ابتدائي) لا يخول ممارسة مهنة تخصصية معقدة."}
        
        return {"score": 0.98, "reasoning": "محاكاة: البيانات تبدو متسقة ومنطقية بناءً على القواعد المرجعية الأساسية."}

    # منطق الاتصال بـ OpenAI الحقيقي (GPT-4o)
    client = OpenAI(api_key=api_key)
    record_json = json.dumps(record_data, ensure_ascii=False)
    
    prompt = f"""
    أنت خبير تدقيق بيانات. حلل السجل التالي وأجب بـ JSON فقط:
    السجل: {record_json}
    المطلوب:
    {{
        "score": (رقم من 0 لـ 1 يمثل درجة المنطقية),
        "reasoning": (شرح موجز بالعربي للخطأ أو null إذا كان السجل سليماً)
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower(): 
            return {"score": 0, "reasoning": "خطأ: انتهى رصيد الـ API الخاص بك (Insufficient Quota)."}
        if "401" in error_msg:
            return {"score": 0, "reasoning": "خطأ: مفتاح الـ API غير صالح (Unauthorized)."}
        return {"score": 0, "reasoning": f"حدث خطأ في الاتصال: {error_msg}"}

# 5. بناء واجهة المستخدم الرسومية (UI Layout)

# العنوان الرئيسي
st.markdown('<h1 class="main-title">🛡️ الحارس الدلالي (Semantic Guard)</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">نظام الذكاء الاصطناعي للتدقيق المنطقي والارتقاء بجودة البيانات اللحظية</p>', unsafe_allow_html=True)

# قسم نظرة عامة (Overview) بخلفية زرقاء
st.markdown("""
<div class="overview-box">
    <h3 style="margin-top: 0;">🌟 نظرة عامة (Overview)</h3>
    <p style="font-size: 1.1rem; line-height: 1.6;">
        الحارس الدلالي هو نموذج أولي (POC) لمساعد ذكي لجودة البيانات. 
        يتميز بقدرته على الانتقال من <b>'التحقق الرقمي'</b> إلى <b>'الإدراك المنطقي'</b>، 
        حيث يستخدم الذكاء الاصطناعي لرصد التناقضات السياقية (مثل تعارض المهنة مع السن) 
        لحظياً أثناء جمع البيانات الميدانية.
    </p>
</div>
""", unsafe_allow_html=True)

# قسم التشغيل السريع (Quick Start) بخلفية ذهبية داخل Expander
with st.expander("🚀 التشغيل السريع (Quick Start) - اضغط هنا"):
    st.markdown("""
    <div class="quickstart-box">
        <ol>
            <li><b>تعبئة البيانات:</b> أدخل القيم في الحقول أدناه (العمر، المهنة، المؤهل، الخبرة).</li>
            <li><b>تفعيل الذكاء الاصطناعي:</b> أدخل المفتاح الخاص بك في الشريط الجانبي . وفي حال لم تدخل المفتاح سيعمل <b>المحاكي المنطقي</b> بدلاً من الذكاء الاصطناعي لضمان استمرار العرض.</li>
            <li><b>التحقق:</b> اضغط على زر 'تحقق من المنطق الدلالي' لمشاهدة تحليل النظام الفوري.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# تنبيه حالة التشغيل الحالية
if not user_api_key or user_api_key in ["1111", "DEMO"]:
    st.warning("🔄 **وضع المحاكاة المنطقية نشط:** النظام يعمل الآن بالقواعد البرمجية الداخلية (بدون استهلاك رصيد).")
else:
    st.success("🤖 **وضع الذكاء الاصطناعي نشط:** النظام متصل الآن بمحرك GPT-4o الفعلي.")

# منطقة المدخلات (Data Entry)
st.markdown("### 📝 إدخال سجل البيانات للاختبار")
c1, c2 = st.columns(2)
with c1:
    age_in = st.number_input("العمر المدخل", 1, 120, 10)
    job_in = st.text_input("المسمى الوظيفي", "طيار مدني")
with c2:
    edu_in = st.selectbox("أعلى مؤهل تعليمي", ["ابتدائي", "متوسط", "ثانوي", "بكالوريوس", "دكتوراه"])
    exp_in = st.number_input("سنوات الخبرة العملية", 0, 60, 20)

input_data = {
    "العمر": age_in,
    "المهنة": job_in,
    "المؤهل": edu_in,
    "سنوات_الخبرة": exp_in
}

# زر التشغيل والتحليل
if st.button("تحقق من المنطق الدلالي فوراً"):
    with st.spinner('جاري تحليل الترابط السياقي دلالياً...'):
        result = get_ai_validation(input_data, user_api_key)
        
        st.write("---")
        final_score = result.get("score", 0)
        
        if final_score > 0.7:
            st.balloons()
            st.success(f"✅ **درجة الثقة المنطقية: {int(final_score*100)}%**")
            st.info(f"💡 **النتيجة:** {result.get('reasoning') or 'البيانات سليمة ومتسقة دلالياً ولا يوجد تعارض مرصود.'}")
        else:
            st.error(f"⚠️ **تنبيه منطقي مرصود! (درجة الثقة: {int(final_score*100)}%)**")
            st.warning(f"🧐 **السبب:** {result.get('reasoning')}")

# معاينة البيانات التقنية
with st.expander("🔍 معاينة البيانات المرسلة للمحرك (JSON Viewer)"):
    st.json(input_data)
