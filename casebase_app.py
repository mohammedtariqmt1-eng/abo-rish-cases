import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="CaseBase - Pediatric Surgery", layout="wide", page_icon="🧸")

# --- قائمة تشخيصات جراحة الأطفال الشاملة ---
PEDIATRIC_DIAGNOSES = [
    "Anorectal Malformation (ARM)", "Appendicitis", "Biliary Atresia", "Branchial Cleft Cyst", 
    "Bronchopulmonary Sequestration (BPS)", "Choledochal Cyst", "Circumcision / Phimosis", 
    "Congenital Diaphragmatic Hernia (CDH)", "Congenital Pulmonary Airway Malformation (CPAM)", 
    "Cystic Hygroma", "Esophageal Atresia (EA)", "Foreign Body Ingestion", "Gastroschisis", 
    "Hepatoblastoma", "Hirschsprung Disease", "Hydrocele", "Hypospadias", "Inguinal Hernia", 
    "Intussusception", "Malrotation and Volvulus", "Meckel's Diverticulum", 
    "Necrotizing Enterocolitis (NEC)", "Neuroblastoma", "Omphalocele", "Pectus Carinatum", 
    "Pectus Excavatum", "Pyloric Stenosis", "Sacrococcygeal Teratoma", "Thyroglossal Duct Cyst", 
    "Tracheoesophageal Fistula (TEF)", "Trauma", "Umbilical Hernia", 
    "Undescended Testis (Cryptorchidism)", "Wilms Tumor", "Other"
]

# --- قاعدة بيانات وهمية (Session State) ---
if 'patients' not in st.session_state:
    st.session_state.patients = [
        {"id": "PS-2026-0047", "name": "ياسين محمود", "age": "4 months", "gender": "Male", "diagnosis": "Hirschsprung Disease", "history": "Abdominal distension and constipation since birth."}
    ]

if 'events' not in st.session_state:
    st.session_state.events = [
        {"patient_id": "PS-2026-0047", "date": "2026-08-16", "type": "Operation", "title": "Laparoscopic-assisted pull-through", "notes": "Procedure went smoothly.", "files": []},
        {"patient_id": "PS-2026-0047", "date": "2026-08-25", "type": "Complication", "title": "Post-operative constipation", "notes": "Conservative management initiated.", "files": []}
    ]

# متغير للتحكم في القائمة النشطة برمجياً
if 'menu_selection' not in st.session_state:
    st.session_state.menu_selection = "Dashboard & Cases"

# متغير لحفظ المريض المختار عند الانتقال للـ Timeline
if 'selected_patient_id' not in st.session_state:
    st.session_state.selected_patient_id = None

# --- دوال الأزرار (Callbacks) لحل مشكلة التنقل ---
def go_to_timeline(patient_id):
    st.session_state.menu_selection = "Patient Timeline"
    st.session_state.selected_patient_id = patient_id

def delete_patient(patient_id):
    st.session_state.patients = [p for p in st.session_state.patients if p['id'] != patient_id]
    st.session_state.events = [e for e in st.session_state.events if e['patient_id'] != patient_id]
    if st.session_state.selected_patient_id == patient_id:
        st.session_state.selected_patient_id = None

# --- القائمة الجانبية (Sidebar) ---
st.sidebar.title("👨‍⚕️ Welcome Surgeon")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navigation", ["Dashboard & Cases", "Add New Case", "Patient Timeline"], key="menu_selection")

# --- صفحة عرض الحالات والبحث ---
if menu == "Dashboard & Cases":
    st.title("🏥 Abu El Reesh Specialized Children Hospital")
    
    col1, col2 = st.columns(2)
    with col1:
        search_query = st.text_input("Search by Name, ID, or Diagnosis...")
    with col2:
        filter_diagnosis = st.selectbox("Filter by Diagnosis", ["All"] + PEDIATRIC_DIAGNOSES)

    df_patients = pd.DataFrame(st.session_state.patients)
    
    if not df_patients.empty:
        if search_query:
            df_patients = df_patients[
                df_patients['name'].str.contains(search_query, case=False) | 
                df_patients['id'].str.contains(search_query, case=False) |
                df_patients['diagnosis'].str.contains(search_query, case=False)
            ]
        if filter_diagnosis != "All":
            df_patients = df_patients[df_patients['diagnosis'] == filter_diagnosis]

        st.markdown("### 📋 Patients List")
        
        if not df_patients.empty:
            header_cols = st.columns([1.5, 2, 1, 2.5, 2])
            header_cols[0].markdown("**Patient ID**")
            header_cols[1].markdown("**Name**")
            header_cols[2].markdown("**Age**")
            header_cols[3].markdown("**Diagnosis**")
            header_cols[4].markdown("**Actions**")
            st.markdown("---")
            
            for index, row in df_patients.iterrows():
                cols = st.columns([1.5, 2, 1, 2.5, 2])
                cols[0].write(row['id'])
                cols[1].write(row['name'])
                cols[2].write(row['age'])
                cols[3].write(row['diagnosis'])
                
                action_col1, action_col2 = cols[4].columns(2)
                
                action_col1.button("👁️ View", key=f"view_{row['id']}", on_click=go_to_timeline, args=(row['id'],))
                action_col2.button("🗑️ Del", key=f"del_{row['id']}", on_click=delete_patient, args=(row['id'],))
        else:
            st.info("No cases match your search.")
    else:
        st.info("No cases found in the system.")

# --- صفحة إضافة حالة جديدة ---
elif menu == "Add New Case":
    st.title("➕ Add New Case")
    
    with st.form("new_case_form"):
        col1, col2 = st.columns(2)
        patient_name = col1.text_input("Patient Name")
        patient_age = col2.text_input("Age (e.g., 4 months)")
        
        col3, col4 = st.columns(2)
        patient_gender = col3.selectbox("Sex", ["Male", "Female"])
        patient_diagnosis = col4.selectbox("Provisional / Final Diagnosis", PEDIATRIC_DIAGNOSES)
        
        brief_history = st.text_area("Brief History & Chief Complaint")
        
        submitted = st.form_submit_button("Save Case")
        if submitted:
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
        patient_options = {p['id']: f"{p['id']} - {p['name']} ({p['diagnosis']})" for p in st.session_state.patients}
        patient_ids = list(patient_options.keys())
        
        default_index = 0
        if st.session_state.selected_patient_id in patient_ids:
            default_index = patient_ids.index(st.session_state.selected_patient_id)
            
        selected_patient_id = st.selectbox(
            "Select Patient", 
            options=patient_ids, 
            format_func=lambda x: patient_options[x],
            index=default_index
        )
        
        st.session_state.selected_patient_id = selected_patient_id
        
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Chronological Events")
            patient_events = [e for e in st.session_state.events if e['patient_id'] == selected_patient_id]
            patient_events = sorted(patient_events, key=lambda x: x['date'])
            
            if not patient_events:
                st.info("No events recorded for this patient yet.")
            
            for event_idx, event in enumerate(patient_events):
                with st.expander(f"🔹 {event['date']} | {event['type']}: {event['title']}", expanded=True):
                    st.write(f"**Notes:** {event['notes']}")
                    
                    # معاينة الملفات المرفقة بأمان تام
                    if event.get('files') and len(event['files']) > 0:
                        st.markdown("---")
                        st.write("📎 **Attachments:**")
                        
                        file_cols = st.columns(3) 
                        for i, file_data in enumerate(event['files']):
                            col = file_cols[i % 3]
                            with col:
                                # التأكد مما إذا كان الملف مخزناً كقاموس (الإصدار الجديد) أو نص قديم
                                if isinstance(file_data, dict):
                                    if file_data.get('type', '').startswith('image/'):
                                        st.image(file_data['data'], caption=file_data['name'], use_container_width=True)
                                    else:
                                        st.download_button(
                                            label=f"📄 Open {file_data['name']}",
                                            data=file_data['data'],
                                            file_name=file_data['name'],
                                            mime=file_data.get('type', 'application/octet-stream'),
                                            key=f"dl_{event_idx}_{i}"
                                        )
                                else:
                                    # توافق عكسي مع أي بيانات نصية قديمة
                                    st.text(f"📄 {file_data}")

        with col2:
            st.subheader("Add New Event")
            with st.form("new_event_form", clear_on_submit=True):
                event_type = st.selectbox("Event Type", ["Clinic Visit", "Operation", "Complication", "Imaging", "Full Labs"])
                event_date = st.date_input("Date")
                event_title = st.text_input("Title")
                event_notes = st.text_area("Notes")
                uploaded_files = st.file_uploader("Upload Documents/Images (PDF, Word, JPG, PNG)", accept_multiple_files=True)
                
                add_event_btn = st.form_submit_button("Save Event")
                if add_event_btn:
                    processed_files = []
                    if uploaded_files:
                        for f in uploaded_files:
                            processed_files.append({
                                "name": f.name,
                                "type": f.type,
                                "data": f.getvalue()
                            })

                    st.session_state.events.append({
                        "patient_id": selected_patient_id,
                        "date": str(event_date),
                        "type": event_type,
                        "title": event_title,
                        "notes": event_notes,
                        "files": processed_files
                    })
                    st.success("Event added to timeline!")
                    st.rerun()
