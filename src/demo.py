import streamlit as st
import json
import os
import pandas as pd
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="الحارس الدلالي - Demo", 
    layout="wide", 
    page_icon="🛡️"
)
load_dotenv()

# 2. إضافة CSS مخصص (تم تحديثه ليدعم لوحة التحكم)
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

    /* تنسيق الكروت الإحصائية */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #1E3A8A !important;
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
    </style>
""", unsafe_allow_html=True)

# 3. إعدادات الشريط الجانبي للتنقل
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=80)
    st.header("🛡️ نظام الحارس الدلالي")
    st.markdown("---")
    
    # التنقل الأساسي
    app_mode = st.radio("اختر الشاشة:", ["🔍 المدقق الذكي (الميدان)", "📊 لوحة تحكم الجودة (الإدارة)"])
    
    st.markdown("---")
    st.subheader("⚙️ الإعدادات التقنية")
    access_mode = st.radio("وضع الوصول:", ["دخول مباشر (محاكي ذكي)", "ربط مفتاح API حقيقي"])
    
    user_api_key = ""
    if access_mode == "ربط مفتاح API حقيقي":
        user_api_key = st.text_input("أدخل مفتاح OpenAI API:", type="password")
    else:
        st.info("🔓 وضع المحاكي مفعل")

# 4. وظيفة المحرك (الدخول المباشر / الذكاء الاصطناعي)
def get_validation_result(record_data, api_key_input, mode):
    if mode == "دخول مباشر (محاكي ذكي)" or not api_key_input:
        age = record_data.get("العمر", 0)
        job = record_data.get("المهنة", "")
        exp = record_data.get("سنوات_الخبرة", 0)
        edu = record_data.get("المؤهل", "")

        if age < 18 and job in ["طيار مدني", "جراح", "مدير تنفيذي", "قاضي", "مهندس"]:
            return {"score": 0.15, "reasoning": "تم رصد تناقض بين السن والمهنة. لا يمكن ممارسة هذه المهنة في هذا السن قانونياً."}
        if exp > (age - 16): 
            return {"score": 0.2, "reasoning": "سنوات الخبرة غير منطقية مقارنة بالعمر الفعلي."}
        if edu == "ابتدائي" and job in ["جراح", "مهندس", "محامي"]:
            return {"score": 0.1, "reasoning": "المؤهل العلمي الحالي لا يتناسب مع المتطلبات التخصصية لهذه المهنة."}
        
        return {"score": 0.98, "reasoning": "البيانات تبدو متسقة ومنطقية بناءً على القواعد المرجعية."}

    # منطق الذكاء الاصطناعي الحقيقي
    client = OpenAI(api_key=api_key_input)
    record_json = json.dumps(record_data, ensure_ascii=False)
    prompt = f"حلل منطقية هذا السجل وأجب بـ JSON (score, reasoning بالعربية): {record_json}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"score": 0, "reasoning": f"خطأ في الاتصال: {str(e)}"}

# 5. عرض الشاشات
if app_mode == "🔍 المدقق الذكي (الميدان)":
    st.markdown('<h1 class="main-title">🛡️ الحارس الدلالي (Semantic Guard)</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">واجهة جمع البيانات المدعومة بالذكاء الاصطناعي</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="overview-box">
        <h3 style="margin-top: 0;">🌟 تجربة الباحث الميداني</h3>
        <p>جرب إدخال بيانات متناقضة (مثلاً: عمر 10 سنوات ووظيفة جراح) لترى كيف يعترض الحارس الدلالي البيانات فوراً.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        age_in = st.number_input("العمر", 1, 120, 10)
        job_in = st.text_input("المسمى الوظيفي", "طيار مدني")
    with c2:
        edu_in = st.selectbox("المؤهل العلمي", ["ابتدائي", "متوسط", "ثانوي", "بكالوريوس", "دكتوراه"])
        exp_in = st.number_input("سنوات الخبرة", 0, 60, 20)

    input_data = {"العمر": age_in, "المهنة": job_in, "المؤهل": edu_in, "سنوات_الخبرة": exp_in}

    if st.button("تحقق من المنطق الدلالي فوراً"):
        with st.spinner('جاري الفحص اللحظي...'):
            result = get_validation_result(input_data, user_api_key, access_mode)
            st.write("---")
            final_score = result.get("score", 0)
            if final_score > 0.7:
                st.success(f"✅ درجة الثقة: {int(final_score*100)}%")
                st.info(f"💡 النتيجة: {result.get('reasoning') or 'البيانات سليمة.'}")
            else:
                st.error(f"⚠️ تنبيه منطقي! (الثقة: {int(final_score*100)}%)")
                st.warning(f"🧐 السبب: {result.get('reasoning')}")

    with st.expander("🔍 معاينة بيانات JSON الصادرة للهيئة"):
        st.json(input_data)

else:
    # شاشة لوحة التحكم (Dashboard)
    st.markdown('<h1 class="main-title">📊 لوحة تحكم مراقبة الجودة المركزية</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">إحصائيات مباشرة لجودة البيانات الوطنية المجمعة ميدانياً</p>', unsafe_allow_html=True)

    # المؤشرات الرئيسية
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("إجمالي السجلات", "1,284", "+155 اليوم")
    m2.metric("أخطاء تم تلافيها", "142", "-5% تحسن", delta_color="normal")
    m3.metric("دقة البيانات", "96.4%", "2% ⬆️")
    m4.metric("توفير تقديري (SAR)", "12,400", "وفر تشغيلي")

    st.markdown("---")

    # الرسوم البيانية
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("⚠️ توزيع الأخطاء الدلالية")
        error_stats = pd.DataFrame({
            'النوع': ['عمر/مهنة', 'مؤهل/وظيفة', 'خبرة غير منطقية', 'أخرى'],
            'الحالات': [45, 30, 20, 10]
        }).set_index('النوع')
        st.bar_chart(error_stats)

    with g2:
        st.subheader("📈 استقرار الجودة (آخر 7 أيام)")
        trend_data = pd.DataFrame(np.random.randn(7, 2), columns=['دقة المصدر', 'كفاءة الباحثين'])
        st.line_chart(trend_data)

    # سجل العمليات الأخير
    st.markdown("---")
    st.subheader("🕵️ سجل الاعتراضات اللحظي (Logs)")
    logs = pd.DataFrame([
        {"الباحث": "أحمد علي", "المنطقة": "الرياض", "الحالة": "تم التصحيح", "الخطأ": "عمر 12 سنة / مهنة طبيب"},
        {"الباحث": "نورة فهد", "المنطقة": "جدة", "الحالة": "تم التصحيح", "الخطأ": "ابتدائي / مهنة مهندس"},
        {"الباحث": "سعد محمد", "المنطقة": "الدمام", "الحالة": "مقبول يدوياً", "الخطأ": "سنوات خبرة > العمر"},
    ])
    st.table(logs)
