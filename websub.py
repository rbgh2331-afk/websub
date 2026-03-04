import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date, timedelta

st.set_page_config(layout="wide")

st.markdown("""
<style>
.block-container {
    max-width: 1200px;
}
</style>
""", unsafe_allow_html=True)

cred = credentials.Certificate("key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

if "login" not in st.session_state:
    st.session_state["login"] = False

if st.session_state["login"]:
    st.title("규호의 버킷리스트📋")

    if st.button("로그아웃"):
        st.session_state["login"] = False
        st.rerun()

else:
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        st.header("로그인")
        login_id = st.text_input("아이디", key="login_id")
        login_pw = st.text_input("비밀번호", type="password", key="login_pw")

        if st.button("로그인"):
            if not login_id or not login_pw:
                st.warning("아이디와 비밀번호를 모두 입력해주세요.")
            else:
                user_doc = db.collection("users").document(login_id).get()
                if user_doc.exists and user_doc.to_dict()["password"] == login_pw:
                    st.session_state["login"] = True
                    st.session_state["user_id"] = login_id
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 틀렸습니다.")
    
    with tab2:
        st.header("회원가입")
        new_id = st.text_input("사용할 아이디", key="new_id")
        new_pw = st.text_input("사용할 비밀번호", type="password", key="new_pw")
        confirm_pw = st.text_input("비밀번호 확인", type="password", key="confirm_pw")

        if st.button("가입하기"):
            if new_pw != confirm_pw:
                st.error("비밀번호가 일치하지 않습니다.")
            elif not new_id or not new_pw:
                st.error("아이디와 비밀번호를 모두 입력하여 주세요.")
            else:
                user_ni = db.collection("users").document(new_id)
                user_doc = user_ni.get()

                if user_doc.exists:
                    st.error("이미 같은 아이디가 존재 합니다.")
                else:
                    user_ni.set({"password" : new_pw})
                    st.success("회원가입 완료! 로그인 탭에서 접속하세요.")

if st.session_state["login"]:
    
    with st.sidebar:
        st.header("📅오늘의 정보")
        st.info(f"오늘 날짜 : {date.today()}")

        choice = st.selectbox("오늘의 기분", ["좋음!!😀", "평범😐", "슬픔..😢"])

        if st.button("기분 좋아지는 버튼"):
            st.balloons()
            st.success("❤️❤️❤️사랑해❤️❤️❤️")

    with st.form("input_form"):
        title = st.title("버킷 리스트 작성📝")

        ct1 = st.selectbox("카테고리", ["여행 ✈️","데이트 👬","공부 🖋"])

        col1, col2, col3, col8 = st.columns([2, 2, 2, 2])

        with col1:
            task1 = st.text_input("누구랑")
        with col2:
            task2 = st.text_input("어디서")
        with col3:
            task3 = st.text_input("어떻게")
        with col8:
            task4 = st.text_input("언제")

        sub = st.form_submit_button("추가")

    task = task1 + " • " + task2 + " • " + task3 + " • " + task4

    if sub:
        db.collection("bucketlist").add({
            "category1": ct1, 
            "content1" : task,
            "done": False,
            "at" : firestore.SERVER_TIMESTAMP
        })
        st.rerun()

    docs1 = db.collection("bucketlist").stream()
    for doc in docs1:
        todo = doc.to_dict()

        col4, col5, col6, col7, col9 = st.columns([2,10,3,2,2])

        with col4:
            st.info(todo.get("category1", "카테고리 없음"))
        with col5:
            st.info(todo.get("content1", ""))
        with col6:
            at_time = todo.get("at")

            if at_time:
                kr_time = at_time + timedelta(hours=9)
                formatted_time = kr_time.strftime("%Y년%m월%d일")
                st.info(formatted_time)
            else:
                st.info("")
        with col7:
            current_done = todo.get("done", False)
            checked = st.checkbox("완료", value=current_done, key=f"done_{doc.id}")

            if checked != current_done:
                db.collection("bucketlist").document(doc.id).update({"done": checked})
                st.rerun()

        with col9:
            if st.button("삭제", key=f"del_{doc.id}"):
                db.collection("bucketlist").document(doc.id).delete()
                st.success("삭제되었습니다!")
                st.rerun()