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

# 3. محرك الحارس الدلالي 
def semantic_validation_engine(data, mode, api_key):
    """
    محرك شامل لتحليل الترابط بين العمر، المؤهل، المهنة، والخبرة.
    """
    age = data.get("age", 0)
    job = data.get("job", "").strip().lower()
    edu = data.get("education", "")
    exp = data.get("experience", 0)

    # وضع الدخول المباشر (المنطق الشامل المبرمج)
    if mode == "دخول مباشر (محاكي ذكي)" or not api_key:
        
        # خريطة الحد الأدنى للعمر لكل مؤهل علمي
        edu_min_age = {
            "ابتدائي": 6, "متوسط": 12, "ثانوي": 15, 
            "دبلوم": 19, "بكالوريوس": 21, "ماجستير": 24, "دكتوراه": 27
        }

        # 1. فحص منطقية العمر مع المؤهل
        if age < edu_min_age.get(edu, 0):
            return {"score": 0.1, "reasoning": f"خطأ منطقي: لا يمكن الحصول على مؤهل '{edu}' في سن {age} عاماً."}

        # 2. فحص منطقية الخبرة مع العمر والمؤهل
        # يفترض أن الخبرة المهنية تبدأ بعد انتهاء المؤهل (أو سن 18 كحد أدنى للعمل)
        career_start_age = max(18, edu_min_age.get(edu, 18))
        if exp > (age - career_start_age):
            return {"score": 0.2, "reasoning": f"تناقض في الخبرة: سنوات الخبرة ({exp}) غير منطقية بالنسبة لعمر الشخص ({age}) وتاريخ حصوله المفترض على المؤهل."}

        # 3. فحص الفئات المهنية التخصصية (تحليل الكلمات المفتاحية الشامل)
        medical_keywords = ['طبيب', 'جراح', 'دكتور', 'صيدلي', 'أخصائي']
        legal_keywords = ['محامي', 'قاضي', 'مستشار قانوني', 'وكيل نيابة']
        teaching_keywords = ['معلم', 'مدرس', 'تعليم', 'محاضر', 'معلمة', 'مدرسة']
        eng_keywords = ['مهندس', 'معماري', 'مخطط']
        academic_keywords = ['أستاذ', 'بروفيسور', 'باحث']
        exec_keywords = ['مدير تنفيذي', 'رئيس مجلس', 'CEO']

        # أ. المهن الطبية والقانونية والتعليمية تتطلب بكالوريوس على الأقل
        if any(kw in job for kw in medical_keywords + legal_keywords + teaching_keywords):
            if edu not in ["بكالوريوس", "ماجستير", "دكتوراه"]:
                return {"score": 0.15, "reasoning": f"فشل المطابقة المهنية: مهنة '{job}' تتطلب حتماً مؤهلاً جامعياً (بكالوريوس فأعلى)."}
            if age < 21:
                return {"score": 0.3, "reasoning": f"تنبيه سن قانوني: مهنة '{job}' تتطلب سناً يتناسب مع التخرج الجامعي (21-22 عاماً على الأقل)."}

        # ب. المهن الهندسية تتطلب دبلوم تقني أو بكالوريوس
        if any(kw in job for kw in eng_keywords):
            if edu not in ["دبلوم", "بكالوريوس", "ماجستير", "دكتوراه"]:
                return {"score": 0.2, "reasoning": f"عدم توافق أكاديمي: المهن الهندسية والتقنية تتطلب حداً أدنى من التأهيل (دبلوم أو بكالوريوس)."}

        # ج. المهن الأكاديمية العليا
        if any(kw in job for kw in academic_keywords) and edu != "دكتوراه":
            if "أستاذ" in job or "بروفيسور" in job:
                return {"score": 0.4, "reasoning": "ملاحظة: المسميات الأكاديمية مثل 'أستاذ' ترتبط عادة بمؤهل الدكتوراه."}

        # د. المهن القيادية والخبرة
        if any(kw in job for kw in exec_keywords) and exp < 7:
            return {"score": 0.5, "reasoning": "تنبيه كفاءة: مسميات الإدارة العليا (C-Level) تتطلب عادة خبرة قيادية تتجاوز 7-10 سنوات."}

        return {"score": 0.98, "reasoning": "تم التحقق الشامل: البيانات متسقة دلالياً بين العمر والمؤهل والمسار المهني المذكور."}

    # وضع الذكاء الاصطناعي الحقيقي (للحالات غير المتوقعة)
    else:
        client = OpenAI(api_key=api_key)
        prompt = f"""
        بصفتك مدقق إحصائي خبير، حلل منطقية السجل التالي وأعطِ النتيجة بـ JSON:
        السجل: {json.dumps(data, ensure_ascii=False)}
        المطلوب:
        1. هل المهنة تتناسب مع المؤهل؟
        2. هل الخبرة منطقية بالنسبة للسن؟
        3. هل المسار الأكاديمي واقعي زمنياً؟
        أجب بحقل 'score' (0-1) وحقل 'reasoning' بالعربية بشكل مفصل.
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"score": 0, "reasoning": f"خطأ فني في محرك الذكاء: {str(e)}"}

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
    st.markdown('<h1 class="main-title">🛡️ الحارس الدلالي </h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">نظام ذكي لمطابقة المهن، الأعمار، المؤهلات، والخبرات لحظياً</p>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("العمر الحالي", 1, 100, 25)
            job = st.text_input("المسمى الوظيفي (أدخل أي مهنة)", "معلم لغة عربية")
        with col2:
            edu = st.selectbox("أعلى مؤهل علمي", ["ابتدائي", "متوسط", "ثانوي", "دبلوم", "بكالوريوس", "ماجستير", "دكتوراه"], index=4)
            exp = st.number_input("إجمالي سنوات الخبرة", 0, 60, 5)
        st.markdown('</div>', unsafe_allow_html=True)

    data_to_check = {"age": age, "job": job, "education": edu, "experience": exp}

    if st.button("بدء الفحص المنطقي"):
        with st.spinner('جاري تحليل السجل عبر محرك القواعد الشاملة...'):
            res = semantic_validation_engine(data_to_check, mode, api_key)
            score = res.get("score", 0)
            
            st.markdown("---")
            if score > 0.7:
                st.success(f"✅ تم قبول السجل - درجة الثقة: {int(score*100)}%")
                st.info(f"📝 تحليل النظام: {res.get('reasoning')}")
            else:
                st.error(f"⚠️ تنبيه جودة: تم رصد تناقض دلالي! (الثقة: {int(score*100)}%)")
                st.warning(f"🧐 السبب المكتشف: {res.get('reasoning')}")
                
    with st.expander("🛠️ كيف يعمل الفحص الشامل؟"):
        st.write("""
        1. **التحليل الزمني:** يحسب النظام الحد الأدنى للسن المطلوب لإنهاء كل مؤهل.
        2. **المطابقة المهنية:** يحلل الكلمات المفتاحية للمهنة ويربطها بالمتطلبات الأكاديمية (طب، قانون، تعليم، هندسة..).
        3. **كاشف الخبرة الوهمية:** يقارن سنوات الخبرة بعمر الشخص بعد حسم سنوات الدراسة.
        """)

# 6. الصفحة الثانية: لوحة التحكم (نفس الكود السابق مع الاحتفاظ بالإحصائيات)
else:
    st.markdown('<h1 class="main-title">📊 مركز حوكمة جودة البيانات</h1>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي السجلات المدققة", "3,450", "+120 اليوم")
    c2.metric("تناقضات تم اعتراضها", "184", "-8% تحسن")
    c3.metric("دقة البيانات الميدانية", "94.6%", "1.2% ⬆️")
    c4.metric("وفر تشغيلي (SAR)", "24,500", "إلغاء إعادة الزيارة")

    st.markdown("---")
    
    g1, g2 = st.columns([2, 1])
    with g1:
        st.subheader("📈 مؤشر دقة البيانات الأسبوعي")
        chart_data = pd.DataFrame(np.random.randn(7, 2), columns=['دقة الإدخال', 'منطقية السياق'])
        st.line_chart(chart_data)
    
    with g2:
        st.subheader("📍 فئات الأخطاء")
        dist = pd.DataFrame({'الفئة': ['عمر/مؤهل', 'مؤهل/مهنة', 'خبرة/عمر'], 'العدد': [30, 45, 25]}).set_index('الفئة')
        st.bar_chart(dist)

    st.subheader("📑 السجلات الأخيرة المعترضة")
    logs = pd.DataFrame([
        {"الوقت": "09:12 AM", "الباحث": "صالح أحمد", "التناقض": "ابتدائي / مهنة جراح", "الإجراء": "تم التصحيح"},
        {"الوقت": "10:05 AM", "الباحث": "هند خالد", "التناقض": "خبير استشاري / خبرة سنة", "الإجراء": "تم الرفض"},
        {"الوقت": "11:20 AM", "الباحث": "سعد منصور", "التناقض": "دكتوراه / عمر 20 سنة", "الإجراء": "تم التصحيح"},
    ])
    st.table(logs)
