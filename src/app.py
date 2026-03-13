# app.py - واجهة العرض التفاعلية (Streamlit Frontend) لنظام الحارس الدلالي
import streamlit as st
import requests
import json

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="الحارس الدلالي - عرض حي",
    page_icon="🛡️",
    layout="centered"
)

# تحسين المظهر باستخدام CSS لدعم القراءة من اليمين لليسان (RTL)
st.markdown("""
    <style>
    .reportview-container .main .block-container {
        direction: rtl;
    }
    div.stButton > button:first-child {
        background-color: #007bff;
        color: white;
        width: 100%;
    }
    .stAlert {
        direction: rtl;
        text-align: right;
    }
    </style>
    """, unsafe_allow_api_usage=True)

# العنوان الرئيسي
st.title("🛡️ نظام الحارس الدلالي (Semantic Guard)")
st.subheader("التحقق الذكي من الأخطاء المنطقية لحظياً")

st.info("""
هذا النموذج الأولي يثبت قدرة الذكاء الاصطناعي على تجاوز قواعد التحقق التقليدية
من خلال فهم "السياق" و "المنطق" خلف الإجابات المتقاطعة.
""")

# واجهة إدخال البيانات داخل حاوية منظمة
with st.container():
    st.write("### إدخال بيانات الاستمارة التجريبية")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("العمر", min_value=1, max_value=120, value=12)
        education = st.selectbox(
            "المؤهل العلمي",
            ["ابتدائي", "متوسط", "ثانوي", "بكالوريوس", "ماجستير", "دكتوراه"]
        )

    with col2:
        job = st.text_input("المسمى الوظيفي", value="جراح أعصاب")
        marital_status = st.selectbox(
            "الحالة الاجتماعية",
            ["أعزب", "متزوج", "مطلق", "أرمل"]
        )

# تجهيز البيانات للإرسال
record_data = {
    "العمر": age,
    "المؤهل_العلمي": education,
    "المسمى_الوظيفي": job,
    "الحالة_الاجتماعية": marital_status
}

# زر التفعيل وفحص البيانات
if st.button("التحقق من المنطق السياقي"):
    with st.spinner('جاري التواصل مع المحرك الذكي وتحليل البيانات...'):
        try:
            # إرسال الطلب إلى Backend (FastAPI)
            # ملاحظة: يجب أن يكون main.py قيد التشغيل على المنفذ 8000
            url = "http://127.0.0.1:8000/validate"
            payload = {"data": record_data}

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                analysis = result.get("analysis", {})
                score = analysis.get("score", 0)
                reason = analysis.get("reasoning") or analysis.get("reason") # حسب مفتاح المحرك

                st.divider()
                st.write("### نتيجة التدقيق:")

                # عرض النتيجة بناءً على درجة الثقة
                if score >= 0.7:
                    st.success(f"✅ البيانات منطقية وسليمة (درجة الثقة: {score*100:.1f}%)")
                    if reason:
                        st.info(f"**ملاحظة المحرك:** {reason}")
                else:
                    st.error(f"⚠️ تم رصد تعارض منطقي! (درجة الثقة: {score*100:.1f}%)")
                    st.warning(f"**سبب التنبيه:** {reason}")

                # عرض البيانات التقنية للمحكمين
                with st.expander("معاينة مخرجات الـ JSON التقنية"):
                    st.json(result)
            else:
                st.error(f"فشل الاتصال بالخلفية. كود الخطأ: {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("خطأ: لم يتم العثور على المحرك الخلفي (Backend). يرجى تشغيل ملف main.py أولاً.")
        except Exception as e:
            st.error(f"حدث خطأ غير متوقع: {str(e)}")

# تذييل الصفحة
st.sidebar.markdown("""
---
**فريق رواد الدلالة**
*هكاثون الابتكار في البيانات 2026*
""")
