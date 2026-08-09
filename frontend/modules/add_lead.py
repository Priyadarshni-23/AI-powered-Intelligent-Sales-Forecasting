import streamlit as st
from database import add_lead, update_lead, find_duplicate_lead

def show():
    st.subheader("Add New Lead")

    st.markdown("""
        <style>
        .duplicate-alert {
            background-color: #fff3cd;
            border-left: 6px solid #ff9800;
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-family: 'Segoe UI', sans-serif;
            animation: shake 0.4s ease-in-out;
        }
        .duplicate-alert h4 {
            margin: 0 0 8px 0;
            color: #7a4a00;
        }
        .duplicate-alert p {
            margin: 2px 0;
            color: #333;
        }
        @keyframes shake {
            0% { transform: translateX(0); }
            25% { transform: translateX(-6px); }
            50% { transform: translateX(6px); }
            75% { transform: translateX(-4px); }
            100% { transform: translateX(0); }
        }
        </style>
    """, unsafe_allow_html=True)

    if "pending_lead" not in st.session_state:
        st.session_state.pending_lead = None
    if "duplicate_row" not in st.session_state:
        st.session_state.duplicate_row = None

    # ---- Confirmation flow if a duplicate email/phone was found ----
    if st.session_state.pending_lead is not None:
        new = st.session_state.pending_lead
        old = st.session_state.duplicate_row

        matched_on = []
        if old[4].lower() == new["email"].lower():
            matched_on.append("Email")
        if old[5] == new["phone"]:
            matched_on.append("Phone")

        st.markdown(f"""
            <div class="duplicate-alert">
                <h4>Duplicate {' & '.join(matched_on)} Detected</h4>
                <p><b>Existing record:</b> {old[1]} | {old[3]} | {old[4]} | {old[5]}</p>
                <p><b>New details entered:</b> {new['company_name']} | {new['contact_name']} | {new['email']} | {new['phone']}</p>
                <p>Do you want to replace the existing lead's details with the new ones?</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Replace Details", use_container_width=True):
                update_lead(
                    old[0], new["company_name"], new["industry"],
                    new["contact_name"], new["email"], new["phone"]
                )
                st.success(f"Lead '{new['company_name']}' updated successfully!")
                st.session_state.pending_lead = None
                st.session_state.duplicate_row = None
                st.rerun()
        with col2:
            if st.button("No, Cancel", use_container_width=True):
                st.info("Cancelled. Existing lead was not changed.")
                st.session_state.pending_lead = None
                st.session_state.duplicate_row = None
                st.rerun()

        return

    # ---- Normal Add Lead form ----
    with st.form("add_lead_form", clear_on_submit=False):
        company_name = st.text_input("Company Name")
        industry = st.text_input("Industry")
        contact_name = st.text_input("Contact Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")

        submitted = st.form_submit_button("Add Lead")

        if submitted:
            fields = {
                "Company Name": company_name,
                "Industry": industry,
                "Contact Name": contact_name,
                "Email": email,
                "Phone": phone,
            }
            missing = [name for name, val in fields.items() if not val.strip()]

            if missing:
                st.error(f"All fields are required. Missing: {', '.join(missing)}")
            else:
                duplicate = find_duplicate_lead(email, phone)
                if duplicate:
                    st.session_state.pending_lead = {
                        "company_name": company_name.strip(),
                        "industry": industry.strip(),
                        "contact_name": contact_name.strip(),
                        "email": email.strip(),
                        "phone": phone.strip(),
                    }
                    st.session_state.duplicate_row = duplicate
                    st.rerun()
                else:
                    add_lead(company_name.strip(), industry.strip(),
                              contact_name.strip(), email.strip(), phone.strip())
                    st.success(f"Lead '{company_name}' added successfully!")