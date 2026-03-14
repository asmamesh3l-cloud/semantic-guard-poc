import streamlit as st
import json
import os
import pandas as pd
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="الحارس الدلالي - Semantic Guard", 
    layout="wide", 
    page_icon="🛡️"
)
load_dotenv()

# 2. تحسين الواجهة ودعم اللغة العربية عبر CSS
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
        font-size: 1.1rem;
        margin-bottom: 30px;
    }

    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    .stMetricValue {
        font-size: 1.8rem !important;
        color: #1E3A8A !important;
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #3B82F6;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# 3. محرك التدقيق الدلالي (المنطق البرمجي)
def semantic_validation_engine(data, mode, api_key):
    """
    يقوم بمطابقة المؤهل، المهنة، العمر، والخبرة.
    """
    age = data.get("age", 0)
    job = data.get("job", "").strip()
    edu = data.get("education", "")
    exp = data.get("experience", 0)

    # وضع الدخول المباشر (المحاكي الذكي)
    if mode == "دخول مباشر (محاكي ذكي)" or not api_key:
        # أ) مطابقة العمر مع المهنة
        if age < 22 and job in ["طبيب جراح", "قاضي", "مهندس استشاري", "محامي"]:
            return {"score": 0.1, "reasoning": f"تنبيه: المهنة '{job}' تتطلب تأهيلاً جامعياً وسناً قانونياً يتجاوز {age} عاماً."}
        
        # ب) مطابقة المؤهل مع المهنة
        high_skill_jobs = ["طبيب جراح", "مهندس", "محامي", "أستاذ جامعي", "طيار"]
        if edu in ["ابتدائي", "متوسط", "ثانوي"] and job in high_skill_jobs:
            return {"score": 0.15, "reasoning": f"تناقض دلالي: مؤهل '{edu}' لا يتناسب مع المتطلبات الأكاديمية لمهنة '{job}'."}
        
        # ج) مطابقة الخبرة مع العمر
        # منطقياً: العمل يبدأ بعد التخرج (مثلاً سن 20)
        if exp > (age - 16):
            return {"score": 0.2, "reasoning": f"خطأ منطقي: سنوات الخبرة ({exp}) غير معقولة مقارنة بعمر الشخص ({age})."}
            
        # د) مطابقة المؤهل مع الخبرة والعمر
        if edu == "دكتوراه" and age < 26:
            return {"score": 0.3, "reasoning": "تنبيه: من غير المنطقي الحصول على درجة الدكتوراه في سن أقل من 26 عاماً وفقاً للمسارات الأكاديمية القياسية."}

        # هـ) مطابقة المهنة مع الخبرة
        if job == "خبير استشاري" and exp < 10:
            return {"score": 0.5, "reasoning": "ملاحظة: المسمى 'خبير استشاري' يتطلب عادة خبرة ميدانية تزيد عن 10 سنوات."}

        return {"score": 0.98, "reasoning": "البيانات متسقة تماماً. تم التحقق من مطابقة (المؤهل + المهنة + العمر + الخبرة) بنجاح."}

    # وضع الذكاء الاصطناعي الحقيقي
    else:
        client = OpenAI(api_key=api_key)
        prompt = f"""
        حلل منطقية السجل الإحصائي التالي وأعطِ نتيجة بـ JSON:
        بيانات الشخص: {json.dumps(data, ensure_ascii=False)}
        القواعد: 
        1. هل المؤهل العلمي يسمح بهذه المهنة؟
        2. هل سنوات الخبرة منطقية بالنسبة للعمر؟ (العمر - الخبرة يجب أن يكون > 16 غالباً)
        3. هل المسمى الوظيفي يتناسب مع السن؟
        الرد يجب أن يكون بالعربية في حقل reasoning ودرجة ثقة في score من 0 إلى 1.
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"score": 0, "reasoning": f"خطأ في الاتصال: {str(e)}"}

# 4. بناء الهيكل الجانبي
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=70)
    st.title("🛡️ الحارس الدلالي")
    st.markdown("---")
    app_page = st.radio("القائمة الرئيسية:", ["🔍 فحص السجلات الميدانية", "📊 لوحة التحكم والتحليلات"])
    
    st.markdown("---")
    st.subheader("⚙️ إعدادات المحرك")
    mode = st.radio("وضع المعالجة:", ["دخول مباشر (محاكي ذكي)", "OpenAI GPT-4o API"])
    api_key = ""
    if mode == "OpenAI GPT-4o API":
        api_key = st.text_input("OpenAI Key:", type="password")

# 5. الصفحة الأولى: فحص السجلات
if app_page == "🔍 فحص السجلات الميدانية":
    st.markdown('<h1 class="main-title">فحص مطابقة البيانات اللحظي</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">يقوم النظام بمطابقة (المؤهل، المهنة، العمر، والخبرة) لضمان جودة السجل</p>', unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("العمر (السنة)", 1, 100, 25)
            job = st.text_input("المسمى الوظيفي الحالي", "طبيب جراح")
        with col2:
            edu = st.selectbox("المؤهل العلمي", ["ابتدائي", "متوسط", "ثانوي", "دبلوم", "بكالوريوس", "ماجستير", "دكتوراه"], index=4)
            exp = st.number_input("سنوات الخبرة", 0, 60, 5)

    data_to_check = {"age": age, "job": job, "education": edu, "experience": exp}

    if st.button("بدء التدقيق الدلالي الذكي"):
        with st.spinner('جاري تحليل الترابط السياقي...'):
            res = semantic_validation_engine(data_to_check, mode, api_key)
            score = res.get("score", 0)
            
            st.markdown("---")
            if score > 0.7:
                st.success(f"✅ تم قبول السجل - درجة الثقة الدلالية: {int(score*100)}%")
                st.info(f"📝 ملاحظة النظام: {res.get('reasoning')}")
            else:
                st.error(f"⚠️ تنبيه: تم رصد تناقض منطقي! (درجة الموثوقية: {int(score*100)}%)")
                st.warning(f"🧐 السبب: {res.get('reasoning')}")
                st.button("إرسال طلب تصحيح للباحث")

# 6. الصفحة الثانية: لوحة التحكم
else:
    st.markdown('<h1 class="main-title">📊 مركز حوكمة جودة البيانات</h1>', unsafe_allow_html=True)
    
    # مقاييس سريعة
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي الفحوصات", "3,450", "+120 اليوم")
    c2.metric("تناقضات مكتشفة", "184", "-8% تحسن")
    c3.metric("دقة الميدان", "94.6%", "1.2% ⬆️")
    c4.metric("وفر تكاليف (SAR)", "24,500", "إلغاء إعادة الزيارة")

    st.markdown("---")
    
    # تحليل التناقضات
    g1, g2 = st.columns([2, 1])
    with g1:
        st.subheader("📈 اتجاه جودة البيانات (أسبوعي)")
        chart_data = pd.DataFrame(np.random.randn(7, 2), columns=['دقة الإدخال', 'منطقية البيانات'])
        st.line_chart(chart_data)
    
    with g2:
        st.subheader("📍 توزيع الأخطاء")
        dist = pd.DataFrame({'الفئة': ['عمر/مهنة', 'مؤهل/وظيفة', 'خبرة زائدة'], 'العدد': [40, 35, 25]}).set_index('الفئة')
        st.bar_chart(dist)

    st.subheader("📑 آخر عمليات التدقيق التي تم اعتراضها")
    logs = pd.DataFrame([
        {"الوقت": "09:12 AM", "الباحث": "صالح أحمد", "الخطأ": "عمر 10 سنوات / مهنة مهندس", "الحالة": "تم التصحيح"},
        {"الوقت": "10:05 AM", "الباحث": "هند خالد", "الخطأ": "دكتوراه / عمر 20 سنة", "الحالة": "تم التصحيح"},
        {"الوقت": "10:45 AM", "الباحث": "محمد فهد", "الخطأ": "متوسط / مهنة جراح", "الحالة": "قيد المراجعة"},
    ])
    st.table(logs)
