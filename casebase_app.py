import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="CaseBase - Pediatric Surgery", layout="wide", page_icon="🧸")

# --- قاعدة بيانات وهمية (Session State) ---
# للحفاظ على البيانات أثناء تصفح التطبيق
if 'patients' not in st.session_state:
    st.session_state.patients = [
        {"id": "PS-2026-0047", "name": "ياسين محمود", "age": "4 months", "gender": "Male", "diagnosis": "Hirschsprung Disease", "history": "Abdominal distension and constipation since birth."}
    ]

if 'events' not in st.session_state:
    st.session_state.events = [
        {"patient_id": "PS-2026-0047", "date": "2026-08-16", "type": "Operation", "title": "Laparoscopic-assisted pull-through", "notes": "Procedure went smoothly.", "files": []},
        {"patient_id": "PS-2026-0047", "date": "2026-08-25", "type": "Complication", "title": "Post-operative constipation", "notes": "Conservative management initiated.", "files": ["xray_abdomen.jpg"]}
    ]

# --- القائمة الجانبية (Sidebar) ---
st.sidebar.title("👨‍⚕️ Welcome, Dr. Mohamed Tariq")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navigation", ["Dashboard & Cases", "Add New Case", "Patient Timeline"])

# --- صفحة عرض الحالات والبحث ---
if menu == "Dashboard & Cases":
    st.title("📁 Cases Dashboard")
    
    # فلتر البحث
    col1, col2 = st.columns(2)
    with col1:
        search_query = st.text_input("Search by Name or ID...")
    with col2:
        filter_diagnosis = st.selectbox("Filter by Diagnosis", ["All", "Hirschsprung Disease", "Anorectal Malformation", "Intussusception", "Other"])

    # تجهيز البيانات للعرض
    df_patients = pd.DataFrame(st.session_state.patients)
    
    if not df_patients.empty:
        # تطبيق الفلاتر
        if search_query:
            df_patients = df_patients[df_patients['name'].str.contains(search_query, case=False) | df_patients['id'].str.contains(search_query, case=False)]
        if filter_diagnosis != "All":
            df_patients = df_patients[df_patients['diagnosis'] == filter_diagnosis]

        st.dataframe(df_patients, use_container_width=True)
    else:
        st.info("No cases found.")

# --- صفحة إضافة حالة جديدة ---
elif menu == "Add New Case":
    st.title("➕ Add New Case")
    
    with st.form("new_case_form"):
        col1, col2 = st.columns(2)
        patient_name = col1.text_input("Patient Name")
        patient_age = col2.text_input("Age (e.g., 4 months)")
        
        col3, col4 = st.columns(2)
        patient_gender = col3.selectbox("Sex", ["Male", "Female"])
        patient_diagnosis = col4.text_input("Provisional / Final Diagnosis")
        
        brief_history = st.text_area("Brief History & Chief Complaint")
        
        submitted = st.form_submit_button("Save Case")
        if submitted:
            # توليد ID جديد
            new_id = f"PS-2026-00{len(st.session_state.patients) + 100}"
            st.session_state.patients.append({
                "id": new_id, "name": patient_name, "age": patient_age, 
                "gender": patient_gender, "diagnosis": patient_diagnosis, "history": brief_history
            })
            st.success(f"Case {new_id} added successfully!")

# --- صفحة التسلسل الزمني (Timeline) ---
elif menu == "Patient Timeline":
    st.title("⏳ Case Timeline")
    
    if len(st.session_state.patients) == 0:
        st.warning("Please add a case first.")
    else:
        # اختيار المريض لعرض تفاصيله
        patient_options = {p['id']: f"{p['id']} - {p['name']} ({p['diagnosis']})" for p in st.session_state.patients}
        selected_patient_id = st.selectbox("Select Patient", options=list(patient_options.keys()), format_func=lambda x: patient_options[x])
        
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        # عرض أحداث المريض (Timeline)
        with col1:
            st.subheader("Chronological Events")
            patient_events = [e for e in st.session_state.events if e['patient_id'] == selected_patient_id]
            
            # ترتيب الأحداث بالوقت
            patient_events = sorted(patient_events, key=lambda x: x['date'])
            
            if not patient_events:
                st.info("No events recorded for this patient yet.")
            
            for event in patient_events:
                with st.expander(f"🔹 {event['date']} | {event['type']}: {event['title']}", expanded=True):
                    st.write(f"**Notes:** {event['notes']}")
                    if event['files']:
                        st.write("📎 **Attachments:**", ", ".join(event['files']))

        # إضافة حدث جديد للمريض
        with col2:
            st.subheader("Add New Event")
            with st.form("new_event_form", clear_on_submit=True):
                event_type = st.selectbox("Event Type", ["Clinic Visit", "Operation", "Complication", "Imaging", "Full Labs"])
                event_date = st.date_input("Date")
                event_title = st.text_input("Title")
                event_notes = st.text_area("Notes")
                uploaded_files = st.file_uploader("Upload Documents/Images", accept_multiple_files=True)
                
                add_event_btn = st.form_submit_button("Save Event")
                if add_event_btn:
                    file_names = [file.name for file in uploaded_files] if uploaded_files else []
                    st.session_state.events.append({
                        "patient_id": selected_patient_id,
                        "date": str(event_date),
                        "type": event_type,
                        "title": event_title,
                        "notes": event_notes,
                        "files": file_names
                    })
                    st.success("Event added to timeline!")
                    st.rerun()
