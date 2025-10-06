import streamlit as st
import pandas as pd
import os
import openai
st.sidebar.title("القائمة")
page = st.sidebar.radio("اختر الصفحة:", ["الرئيسية", "من نحن", "الاختبار", "الدروس"])

if page == "من نحن":
    st.title("منصة تعليمية ذكية")
    st.write("""
    هذه المنصة تهدف إلى تقديم محتوى تعليمي مخصص حسب مستوى الطالب باستخدام الذكاء الاصطناعي.
    تم تطويرها من قبل إيمان، طالبة علم البيانات والذكاء الاصطناعي في الأردن.
    """)
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("⚠️ لم يتم العثور على مفتاح OpenAI. يرجى إضافته في ملف secrets.toml.")
# 🔐 إعداد مفتاح OpenAI
# openai.api_key = "YOUR_API_KEY"  # ← استبدليه بمفتاحك الحقيقي

# 🧠 توليد أسئلة ذكية حسب المستوى
from openai import OpenAI

def generate_questions(level, num_questions=5):
    prompt = f"""
    أنشئ {num_questions} سؤالًا لتحديد مستوى اللغة الإنجليزية لطالب {level}.
    نوع الأسئلة: ترجمة، قواعد، اختيار من متعدد.
    صيغة الإخراج: قائمة من القواميس، كل سؤال يحتوي على 'q' للسؤال و 'a' للإجابة.
    مثال: [{{"q": "ما ترجمة كلمة 'apple'؟", "a": "تفاحة"}}, ...]
    """

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    content = response.choices[0].message.content
    try:
        questions = eval(content)
        return questions
    except:
        st.error("فشل في توليد الأسئلة. يرجى المحاولة لاحقًا.")
        return []
# try:
#      questions = eval(content)
#     return questions
# except:
#         st.error("فشل في توليد الأسئلة. يرجى المحاولة لاحقًا.")
#         return []

# 🧼 تهيئة الجلسة
if "page" not in st.session_state:
    st.session_state.page = "login"
if "name" not in st.session_state:
    st.session_state.name = ""
if "score" not in st.session_state:
    st.session_state.score = 0
if "generated_questions" not in st.session_state:
    st.session_state.generated_questions = []

# 🔐 تسجيل الدخول
def login():
    st.title("🔐 تسجيل الدخول")

    # 📷 عرض الصورة في الأعلى
    # st.image("text", width=300)# ← استبدلي بالاسم الفعلي للصورة

    name = st.text_input("أدخل اسمك:")
    if st.button("دخول"):
        if name.strip() != "":
            st.session_state.name = name
            st.session_state.page = "home"
        else:
            st.warning("يرجى إدخال الاسم أولًا.")
    st.markdown("### 👋 أهلاً بك في منصتنا التعليمية الذكية")

# 🏠 الصفحة الرئيسية
def home():
    st.title(f"📚 أهلاً {st.session_state.name}!")
    st.write("مرحبًا بك في منصتنا التعليمية الذكية.")
    if st.button("ابدأ الاختبار"):
        st.session_state.page = "test"

# 📝 اختبار تحديد المستوى
def test():
    st.title("📝 اختبار تحديد المستوى")
    questions = [
        {"q": "ما ترجمة كلمة 'apple'؟", "a": "تفاحة"},
        {"q": "ما جمع كلمة 'child'؟", "a": "children"},
        {"q": "اختر الكلمة الصحيحة: He ___ to school every day. (go/goes)", "a": "goes"},
        {"q": "ما معنى كلمة 'beautiful'؟", "a": "جميلة"},
        {"q": "اختر الترتيب الصحيح: I ___ playing football. (am/is)", "a": "am"}
    ]
    score = 0
    for i, item in enumerate(questions):
        ans = st.text_input(item["q"], key=f"q{i}")
        if ans.strip().lower() == item["a"].lower():
            score += 1
    if st.button("عرض النتيجة"):
        st.session_state.score = score
        save_result(st.session_state.name, score)
        st.session_state.page = "result"

# 💾 حفظ النتيجة
def save_result(name, score):
    filename = "results.csv"
    new_entry = {"الاسم": name, "النتيجة": score}
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    else:
        df = pd.DataFrame([new_entry])
    df.to_csv(filename, index=False)

# 📊 عرض النتيجة
def result():
    score = st.session_state.score
    name = st.session_state.name
    st.title(f"📊 نتيجتك يا {name}: {score}/5")
    if score <= 2:
        level = "مبتدئ"
        exercises = ["الألوان", "تحية صباحية"]
    elif score <= 4:
        level = "متوسط"
        exercises = ["جمل يومية", "قواعد المضارع"]
    else:
        level = "متقدم"
        exercises = ["مقال قصير", "محادثة متقدمة"]

    st.success(f"حصلت على المستوى: {level}")
    st.write("أكمل هذه الدروس المقترحة فقط:")
    for ex in exercises:
        st.write("- " + ex)

    if st.button("🔁 اختبار جديد حسب مستواي"):
        st.session_state.generated_questions = generate_questions(level)
        st.session_state.page = "smart_test"

    if st.button("📚 عرض دروسي"):
        st.session_state.page = "lessons"

# 🤖 اختبار ذكي حسب المستوى
def smart_test():
    st.title("🧠 اختبار ذكي حسب مستواك")
    questions = st.session_state.get("generated_questions", [])
    score = 0
    for i, item in enumerate(questions):
        ans = st.text_input(item["q"], key=f"smart_q{i}")
        if ans.strip().lower() == item["a"].lower():
            score += 1
    if st.button("عرض النتيجة الذكية"):
        st.session_state.score = score
        save_result(st.session_state.name, score)
        st.session_state.page = "result"

# 📚 دروس تعليمية حسب المستوى
def lessons():
    st.title("📚 دروس تعليمية حسب مستواك")
    score = st.session_state.score
    if score <= 2:
        level = "مبتدئ"
        content = {
            "الألوان": {
                "شرح": "تعلم أسماء الألوان بالإنجليزية مع صور توضيحية.",
                "سؤال": "ما ترجمة كلمة 'blue'؟",
                "إجابة": "أزرق"
            },
            "الضمائر": {
                "شرح": "شرح مبسط للضمائر مثل I, You, He, She.",
                "سؤال": "ما الضمير المناسب لـ فتاة؟",
                "إجابة": "She"
            }
        }
    elif score <= 4:
        level = "متوسط"
        content = {
            "جمل يومية": {
                "شرح": "جمل تستخدمها في حياتك اليومية مثل: I’m hungry.",
                "سؤال": "ما ترجمة 'I’m tired'؟",
                "إجابة": "أنا متعب"
            }
        }
    else:
        level = "متقدم"
        content = {
            "مقال قصير": {
                "شرح": "تدريب على كتابة فقرة قصيرة عن موضوع معين.",
                "سؤال": "اكتب جملة تعبر عن رأيك في التعلم الذاتي",
                "إجابة": ""
            }
        }

    st.subheader(f"🧠 مستواك: {level}")
    for title, data in content.items():
        with st.expander(f"📘 {title}"):
            st.write(data["شرح"])
            ans = st.text_input(f"📝 تمرين: {data['سؤال']}", key=title)
            if data["إجابة"]:
                if ans.strip().lower() == data["إجابة"].lower():
                    st.success("إجابة صحيحة ✅")
                elif ans:
                    st.error("إجابة غير صحيحة ❌") 
# 📖 سجل الطالب
def my_history():
    st.title("📖 سجلك الشخصي")
    filename = "results.csv"
    name = st.session_state.name
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        my_data = df[df["الاسم"] == name]
        if not my_data.empty:
            st.dataframe(my_data)
        else:
            st.info("لا يوجد نتائج محفوظة لك بعد.")
    else:
        st.info("لا يوجد نتائج محفوظة بعد.")

# 📊 تحليل النتائج
def analysis():
    st.title("📊 تحليل نتائج الطلاب")
    filename = "results.csv"
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        st.write(f"عدد الطلاب: {len(df)}")
        st.write(f"متوسط الدرجات: {df['النتيجة'].mean():.2f}")
        def classify(score):
            if score <= 2:
                return "مبتدئ"
            elif score <= 4:
                return "متوسط"
            else:
                return "متقدم"
        df["المستوى"] = df["النتيجة"].apply(classify)
        level_counts = df["المستوى"].value_counts()
        st.write("🔢 توزيع المستويات:")
        st.bar_chart(level_counts)
        st.dataframe(df)
    else:
        st.info("لا يوجد نتائج لتحليلها بعد.")

# 🎛️ الشريط الجانبي
st.sidebar.title("📂 قائمة التنقل")
if st.sidebar.button("🔄 إعادة البدء"):
    st.session_state.page = "login"
    st.session_state.name = ""
    st.session_state.score = 0
    st.session_state.generated_questions = []
if st.sidebar.button("📖 سجلي"):
    st.session_state.page = "my_history"
if st.sidebar.button("📊 تحليل النتائج"):
    st.session_state.page = "analysis"
if st.sidebar.button("📚 دروسي"):
    st.session_state.page = "lessons"

# 🚦 تشغيل الصفحة المناسبة
if st.session_state.page == "login":
    login()
elif st.session_state.page == "home":
    home()
elif st.session_state.page == "test":
    test()
elif st.session_state.page == "result":
    result()
elif st.session_state.page == "smart_test":
    smart_test()
elif st.session_state.page == "lessons":
    lessons()
elif st.session_state.page == "my_history":
    my_history()
elif st.session_state.page == "analysis":
    analysis()
