import hashlib
import os
import tempfile
import time
from pathlib import Path
from random import random
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from fpdf import FPDF
from database_utils import *
from datetime import datetime, timedelta
import random
import streamlit as st
from decimal import Decimal

st.set_page_config(
    page_title="Hospital Management System",  # Title of the page
    layout="wide",  # Use the full width of the screen
    page_icon="🏥",  # Icon for the page (hospital emoji)
    initial_sidebar_state="expanded"  # Sidebar is expanded by default
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Application Started")

# ------------------ Custom CSS for Tab Hover Effect and Headers ------------------
st.markdown(
    """
    <style>
    /* Style for the sidebar navigation tabs */
    .sidebar-tabs {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }

    .sidebar-tabs button {
        width: 100%;
        height: 50px; /* Fixed height for all buttons */
        padding: 10px;
        font-size: 16px;
        font-weight: bold;
        color: #FFFFFF;
        background-color: #4B0082; /* Indigo blue background */
        border: none;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: left;
        display: flex;
        align-items: center;
    }

    /* Hover effect for the tabs */
    .sidebar-tabs button:hover {
        background-color: #87CEEB; /* Sky blue on hover */
        transform: scale(1.02);
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
    }

    /* Active tab style */
    .sidebar-tabs button.active {
        background-color: #87CEEB; /* Sky blue for active tab */
        color: #FFFFFF;
    }

    /* Style for headers containing text boxes */
    .header-lightblue {
        background-color: #E6F7FF; /* Light blue background */
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    }

    /* Style for text boxes */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stNumberInput > div > div > input {
        background-color: #FFFFFF; /* White background */
        border: 1px solid #87CEEB; /* Sky blue border */
        border-radius: 5px;
        padding: 8px;
    }

    /* Style for buttons */
    .stButton > button {
        background-color: #4B0082; /* Indigo blue background */
        color: #FFFFFF; /* White text */
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    /* Hover effect for buttons */
    .stButton > button:hover {
        background-color: #87CEEB; /* Sky blue on hover */
        transform: scale(1.05);
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
    }

    /* Active button style */
    .stButton > button:active {
        background-color: #87CEEB; /* Sky blue when clicked */
    }

    /* Text input focus effect */
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus, .stNumberInput > div > div > input:focus {
        border: 2px solid #87CEEB;
        background-color: #E6F7FF;
    }

    /* Passcode screen styles */
    .passcode-screen {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .passcode-box {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
        text-align: center;
    }

    .passcode-box input {
        width: 100%;
        padding: 10px;
        margin: 10px 0;
        border: 1px solid #87CEEB;
        border-radius: 5px;
    }

    .passcode-box button {
        background-color: #4B0082;
        color: #FFFFFF;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
    }

    .passcode-box button:hover {
        background-color: #87CEEB;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ------------------ Animated Startup Screen ------------------
def glowing_text(text, size=100, color="#FFFFFF"):  # Set text color to white
    return f"""
    <p style="font-size:{size}px; font-weight:bold; text-align:center; color:{color}; 
    text-shadow: 0px 0px 10px #FFFFFF, 0px 0px 20px #FFFFFF, 0px 0px 30px #FFFFFF;">
    {text}</p>"""


def startup_animation():
    messages = [
        "🌟 Welcome To 🌟",
        "🏥 The Hospital Management System 🏥",
        "🚀 Project By 🚀",
        "👨‍💻 ACCELERATORS 💻"
    ]

    container = st.empty()
    box_html = """
    <div style='width:100%; height:600px; border: none; border-radius: 50px; 
    background: linear-gradient(45deg, #FF0000, #FF7F00, #FFFF00, #00FF00, #0000FF, #4B0082, #9400D3);
    background-size: 200% 200%; animation: rainbow 5s ease infinite; display:flex; justify-content:center; align-items:center;'>
    {content}
    </div>
    <style>
    @keyframes rainbow {{
        0% {{background-position: 0% 50%;}}
        50% {{background-position: 100% 50%;}}
        100% {{background-position: 0% 50%;}}
    }}
    </style>
    """

    start_time = time.time()
    while time.time() - start_time < 4:
        for msg in messages:
            if time.time() - start_time >= 4:
                break
            container.markdown(
                box_html.format(content=glowing_text(msg, size=48, color="#FFFFFF")),  # Set text color to white
                unsafe_allow_html=True
            )
            time.sleep(1)

    # Clear the animation container
    container.empty()
    st.session_state["startup_done"] = True
    st.rerun()  # Rerun the app to display the login page


# ------------------ Hash Password ------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ------------------ User Authentication ------------------
def register_user(username, password, full_name, user_role):
    """
    Register a new user with the specified role (Admin, Doctor, Receptionist, Nurse, or Patient).
    """
    if not username or not password or not full_name:
        st.error("All fields are required!")
        logging.warning("Registration failed: Missing required fields.")
        return
    try:
        con = connection()
        if con:
            cur = con.cursor()
            hashed_password = hash_password(password)
            cur.execute(
                "INSERT INTO users(username, password_hash, full_name, user_role) VALUES (%s, %s, %s, %s)",
                (username, hashed_password, full_name, user_role)
            )
            con.commit()
            st.success("User Registered Successfully! Please Login.")
            logging.info(f"User {username} registered successfully with role: {user_role}.")
    except sq.Error as er:
        st.error(f"Error: {er}")
        logging.error(f"Error during user registration: {er}")


def login_user(username, password):
    """
    Authenticate a user and set session state based on their role.
    """
    try:
        con = connection()
        if con:
            cur = con.cursor()
            hashed_password = hash_password(password)
            cur.execute(
                "SELECT user_role FROM users WHERE username=%s AND password_hash=%s",
                (username, hashed_password)
            )
            user = cur.fetchone()
            if user:
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = user[0]
                st.session_state['username'] = username
                st.session_state["active_tab"] = "Dashboard"  # Set active tab to Dashboard
                st.success(f"Welcome {username} as a {st.session_state['user_role']}")
                logging.info(f"User {username} logged in successfully with role: {user[0]}.")

                # Log login action and mark attendance
                log_user_action(username, user[0], "login")
                mark_attendance(username, user[0])

                time.sleep(1)
                st.rerun()  # Rerun the app to reflect the changes
                return True
            else:
                st.error("Invalid Credentials!")
                logging.warning(f"Failed login attempt for username: {username}")
                return False
    except sq.Error as er:
        st.error(f"Error: {er}")
        logging.error(f"Error during login: {er}")
        return False


def logout():
    if st.session_state.get('authenticated'):
        # Log logout action
        log_user_action(st.session_state['username'], st.session_state['user_role'], "logout")

    st.session_state.clear()
    st.info("Login Session Terminated")
    st.warning("Please login to the system to access its features.")


# ------------------ Passcode Security ------------------
def check_passcode(passcode):
    """Check if the entered passcode is correct."""
    return passcode == "12345"  # Hardcoded passcode


# ------------------ Passcode Screen ------------------
def show_passcode_screen():
    """Displays the passcode screen with a blurred background."""
    st.markdown(
        """
        <div class="passcode-screen">
            <div class="passcode-box">
                <h3>Enter Passcode</h3>
                <input type="password" id="passcode" placeholder="Enter passcode">
                <button onclick="verifyPasscode()">Submit</button>
            </div>
        </div>
        <script>
        function verifyPasscode() {
            const passcode = document.getElementById('passcode').value;
            if (passcode === '12345') {
                window.location.href = window.location.href + '?passcode_verified=true';
            } else {
                alert('Incorrect Passcode!');
            }
        }
        </script>
        """,
        unsafe_allow_html=True
    )


# -----------------AcessControl-----------------
def access_control():
    """
    Ensure the user is authenticated before accessing any feature.
    """
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if not st.session_state['authenticated']:
        st.warning("Access Denied! Please login to access the Hospital Management System.")
        st.stop()


def check_user_role(required_roles):
    """
    Check if the user has the required role to access a feature.

    Args:
        required_roles (list): List of roles allowed to access the feature.
    """
    if 'user_role' not in st.session_state:
        st.warning("Access Denied! Please login to access this feature.")
        st.stop()

    if st.session_state['user_role'] not in required_roles:
        st.warning(f"Access Denied! This feature is only available to {', '.join(required_roles)}.")
        st.stop()


# ------------------ Feature-Specific Access ------------------
def manage_patients():
    """
    Manage Patients feature.
    Only Admin, Doctor, and Nurse can access this feature.
    """
    check_user_role(["Admin", "Doctor", "Nurse"])
    st.write("Manage Patients Page")


def view_appointments():
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])
    st.write("View Appointments Page")


# ------------------ Role-Specific Access ------------------
def restrict_access_to_admin():
    """
    Restrict access to Admin-only features.
    """
    check_user_role(["Admin"])


def restrict_access_to_doctor():
    """
    Restrict access to Doctor-only features.
    """
    check_user_role(["Doctor"])


def restrict_access_to_receptionist():
    """
    Restrict access to Receptionist-only features.
    """
    check_user_role(["Receptionist"])


def restrict_access_to_nurse():
    """
    Restrict access to Nurse-only features.
    """
    check_user_role(["Nurse"])


def restrict_access_to_patient():
    """
    Restrict access to Patient-only features.
    """
    check_user_role(["Patient"])


# ------------------ View Patients ------------------
def view_patients():
    """
    View Patients: Accessible to Admin, Doctor, and Nurse.
    """
    check_user_role(["Admin", "Doctor", "Nurse"])
    st.subheader("📋 Patient Records")

    # Fetch and display patient data
    patient_data = fetch_data("SELECT * FROM patients", "patients")
    if patient_data.empty:
        st.warning("No patient records found.")
    else:
        st.dataframe(patient_data)


# Chatbot response generation


def generate_response(user_input):
    user_input_lower = user_input.lower()
    user_role = st.session_state.get('user_role')

    # Enhanced greeting responses
    greeting_responses = [
        "Hello there! How can I assist you with hospital services today?",
        "Hi! Welcome to Hospital Management System. What can I do for you?",
        "Greetings! I'm here to help with your hospital needs. What would you like to do?"
    ]

    # Enhanced farewell responses
    farewell_responses = [
        "Goodbye! Wishing you good health!",
        "Have a wonderful day! Don't hesitate to return if you need more assistance.",
        "Take care! Remember we're here 24/7 if you need us."
    ]

    # Common responses
    if any(word in user_input_lower for word in ["hello", "hi", "hey", "greetings"]):
        return random.choice(greeting_responses)

    if any(word in user_input_lower for word in ["thank you", "thanks", "appreciate"]):
        appreciation_responses = [
            "You're very welcome! It's my pleasure to assist you.",
            "No problem at all! Is there anything else I can help with?",
            "Happy to help! Don't hesitate to ask if you have more questions."
        ]
        return random.choice(appreciation_responses)

    if any(word in user_input_lower for word in ["bye", "goodbye", "see you"]):
        return random.choice(farewell_responses)

    # Section navigation with more natural language
    section_mapping = st.session_state.get('section_mapping', {
        "Patient History": {
            "keywords": ["patients", "history", "patient record", "consultant record", "records"],
            "description": "The Patient History section lets you view and download patient records."
        },
        "Appointments": {
            "keywords": ["appointment for consultation", "schedule", "booking", "visit", "consultation"],
            "description": "The Appointments section lets you book and view appointments."
        }
    })

    # Check for pending navigation confirmation
    if "pending_section" in st.session_state and user_input_lower in ["yes", "y", "ok", "sure", "please"]:
        section = st.session_state.pending_section
        del st.session_state.pending_section

        navigation_responses = [
            f"Taking you to the {section} section now...",
            f"Opening the {section} section for you...",
            f"Navigating to {section} as requested..."
        ]

        st.session_state.just_navigated = random.choice(navigation_responses)
        st.session_state.active_tab = section
        return st.session_state.just_navigated

    # Enhanced appointment booking flow
    if "appointment_state" in st.session_state and st.session_state.appointment_state.get("step", 0) > 1:
        return handle_appointment_booking(user_input, user_role)

    if any(word in user_input_lower for word in
           ["i want to book appointment with doctor", "visiting", "appointment", "see doctor"]):
        if "appointment_state" not in st.session_state:
            st.session_state.appointment_state = {
                "step": 1,
                "patient_name": "",
                "department": "",
                "doctor_name": "",
                "date": "",
                "time": ""
            }
        booking_responses = [
            "I can help book an appointment. Could you tell me the patient's name?",
            "Appointment booking started. Please provide the patient's name to begin."
        ]
        return random.choice(booking_responses)

    # Detect section requests
    for section, data in section_mapping.items():
        if any(keyword in user_input_lower for keyword in data["keywords"]):
            st.session_state.pending_section = section
            return f"It sounds like you're interested in {section}. Should I open that section for you?"

    # Enhanced help response
    if "help me" or "what can you do?" in user_input_lower:
        help_responses = [
            "I can help with: booking appointments, billing questions, patient records, emergency services, and more. What do you need help with?",
            "I specialize in hospital management tasks like appointments, billing, patient records, and room management. How can I assist you?",
            "My capabilities include: appointment scheduling, bill payments, medical records access, and hospital services information."
        ]
        return random.choice(help_responses)

    # Default response with suggestions
    suggestion_responses = [
        "I'm not quite sure what you're asking. You might want to try:",
        "Could you clarify? Here are some things I can help with:",
        "I might need more details. Here are some options:"
    ]

    suggestions = [
        "• Book an appointment with a doctor",
        "• Check your medical bills",
        "• View available hospital rooms",
        "• Get emergency assistance",
        "• Check medicine inventory"
    ]

    return (
        f"{random.choice(suggestion_responses)}\n\n"
        f"{chr(10).join(random.sample(suggestions, 3))}\n\n"
        "Or ask about any other hospital service!"
    )


# Custom CSS for chatbot interface
st.markdown(
    """
    <style>
    /* Chat container with scroll */
    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding: 15px;
        scroll-behavior: smooth;
    }

    /* Message bubbles */
    .message {
        margin: 10px 0;
        padding: 12px 15px;
        border-radius: 18px;
        max-width: 70%;
        word-wrap: break-word;
        position: relative;
        animation: fadeIn 0.3s ease;
    }

    /* User message */
    .user-message {
        background-color: #4B0082;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }

    /* Bot message */
    .bot-message {
        background-color: #e5e5ea;
        color: black;
        margin-right: auto;
        border-bottom-left-radius: 4px;
    }

    /* Message time */
    .message-time {
        font-size: 0.7em;
        color: #999;
        margin-top: 5px;
        text-align: right;
    }

    /* Input area - fixed at bottom */
    .input-container {
        position: sticky;
        bottom: 0;
        background: white;
        padding: 10px;
        border-top: 1px solid #eee;
    }

    /* Input field */
    .input-field {
        width: 100%;
        padding: 12px 15px;
        border: 1px solid #ddd;
        border-radius: 20px;
        outline: none;
        font-size: 16px;
    }

    /* Send button */
    .send-button {
        margin-top: 10px;
        padding: 10px 20px;
        background-color: #4B0082;
        color: white;
        border: none;
        border-radius: 20px;
        cursor: pointer;
        font-size: 16px;
        transition: background-color 0.3s;
        width: 100%;
    }

    .send-button:hover {
        background-color: #5a1199;
    }

    /* Spinner animation */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .spinner {
        border: 3px solid rgba(0,0,0,0.1);
        border-radius: 50%;
        border-top: 3px solid #4B0082;
        width: 20px;
        height: 20px;
        animation: spin 1s linear infinite;
        margin-right: 10px;
    }

    /* Generating message */
    .generating {
        display: flex;
        align-items: center;
        color: #666;
        font-style: italic;
        margin: 10px 0;
    }

    /* Fade in animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Title styling */
    .chatbot-title {
        text-align: center;
        color: #4B0082;
        margin-bottom: 20px;
        font-size: 24px;
        position: sticky;
        top: 0;
        background: white;
        padding: 10px 0;
        z-index: 100;
    }

    /* Section suggestion buttons */
    .section-suggestion {
        display: inline-block;
        margin: 5px;
        padding: 8px 12px;
        background-color: #f0f0f0;
        border-radius: 15px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .section-suggestion:hover {
        background-color: #4B0082;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Initialize session state for generating response
if "generating_response" not in st.session_state:
    st.session_state.generating_response = False


def handle_appointment_booking(user_input, user_role):
    if user_role not in ["Admin", "Doctor", "Nurse", "Receptionist", "Patient"]:  # Example role check
        return "❌ You don't have permission to book appointments."
    if "appointment_state" not in st.session_state:
        st.session_state.appointment_state = {
            "step": 1,
            "patient_name": "",
            "department": "",
            "doctor_name": "",
            "date": "",
            "time": ""
        }

    state = st.session_state.appointment_state

    if state["step"] == 1:
        state["step"] = 2
        return "To schedule an appointment, please provide the patient's full name:"

    elif state["step"] == 2:
        state["patient_name"] = user_input
        state["step"] = 3

        # Fetch available departments
        department_data = fetch_data("SELECT DISTINCT department FROM doctor", "doctor", columns=["Department"])
        if department_data.empty:
            del st.session_state.appointment_state
            return "No departments available. Please contact the administrator."

        depts = ", ".join(department_data["Department"].tolist())
        return f"Available departments: {depts}. Please specify which department you want:"

    elif state["step"] == 3:
        department = user_input.title()
        state["department"] = department

        # Fetch doctors in this department
        query = f"""
            SELECT s.staff_name AS doctor_name, s.shift
            FROM doctor d
            JOIN staff s ON d.staff_id = s.id
            WHERE d.department = '{department}'
        """
        doctor_data = fetch_data(query, "doctor", columns=["Doctor Name", "Shift"])

        if doctor_data.empty:
            del st.session_state.appointment_state
            return f"No doctors found in the {department} department. Please choose another department."

        doctors = ", ".join(doctor_data["Doctor Name"].tolist())
        state["step"] = 4
        return f"Available doctors in {department}: {doctors}. Please specify which doctor you prefer:"

    elif state["step"] == 4:
        state["doctor_name"] = user_input.title()
        state["step"] = 5
        return "Please enter the appointment date (YYYY-MM-DD format):"

    elif state["step"] == 5:
        try:
            datetime.strptime(user_input, "%Y-%m-%d")
            state["date"] = user_input
            state["step"] = 6
            return "Please enter the appointment time (HH:MM format, 24-hour clock):"
        except ValueError:
            return "Invalid date format. Please enter date in YYYY-MM-DD format:"

    elif state["step"] == 6:
        try:
            datetime.strptime(user_input, "%H:%M")
            state["time"] = user_input
            state["step"] = 7

            confirmation = (
                f"Please confirm the appointment details:\n\n"
                f"Patient: {state['patient_name']}\n"
                f"Department: {state['department']}\n"
                f"Doctor: {state['doctor_name']}\n"
                f"Date: {state['date']}\n"
                f"Time: {state['time']}\n\n"
                f"Type 'confirm' to book or 'cancel' to start over."
            )
            return confirmation
        except ValueError:
            return "Invalid time format. Please enter time in HH:MM format (24-hour clock):"

    elif state["step"] == 7:
        if user_input.lower() == "confirm":
            try:
                insert_data(
                    """
                    INSERT INTO appointments (patient_name, doctor_name, appointment_date, appointment_time)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (state["patient_name"], state["doctor_name"], state["date"], state["time"])
                )
                del st.session_state.appointment_state
                return "Appointment booked successfully! You can view it in the Appointments section."
            except Exception as e:
                del st.session_state.appointment_state
                return f"Error booking appointment: {str(e)}"
        elif user_input.lower() == "cancel":
            del st.session_state.appointment_state
            return "Appointment booking cancelled. How else can I help you?"
        else:
            return "Please type 'confirm' to book the appointment or 'cancel' to start over."


# In the response handling section:
if st.session_state.generating_response:
    last_user_message = st.session_state.chat_history[-1]["content"]
    time.sleep(1)

    # Check if we're in the middle of an appointment booking
    if "appointment_state" in st.session_state:
        bot_response = handle_appointment_booking(last_user_message, st.session_state.get('user_role', 'Patient'))
    else:
        bot_response = generate_response(last_user_message)

    st.session_state.chat_history.append({
        "role": "bot",
        "content": bot_response,
        "time": datetime.now().strftime("%H:%M")
    })
    st.session_state.generating_response = False
    st.rerun()


# Function to display chat messages
def display_chat():
    # Chat container with scroll
    st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)

    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(
                f'<div class="message user-message">{message["content"]}<div class="message-time">{message["time"]}</div></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="message bot-message">{message["content"]}<div class="message-time">{message["time"]}</div></div>',
                unsafe_allow_html=True
            )

    if st.session_state.generating_response:
        st.markdown(
            '<div class="generating"><div class="spinner"></div>Generating response...</div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)  # Close chat-container

    # Input area (fixed at bottom)
    with st.form(key='chat_form', clear_on_submit=True):
        st.markdown('<div class="input-container">', unsafe_allow_html=True)

        user_input = st.text_input(
            "Type your message...",
            value="",  # Ensures empty after submit
            key="user_input",
            placeholder="Ask me anything about the hospital system...",
            label_visibility="collapsed"
        )

        submit_button = st.form_submit_button("Send", use_container_width=True)
        st.rerun

        st.markdown('</div>', unsafe_allow_html=True)  # Close input-container

    st.markdown('</div>', unsafe_allow_html=True)  # Close main-container

    # Handle form submission
    if submit_button and user_input.strip():
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "time": datetime.now().strftime("%H:%M")
        })

        # Clear the input by forcing a rerun
        st.session_state.generating_response = True
        st.rerun()

    # Auto-scroll JavaScript remains the same...


# Main app function
def chatbot_page():
    st.markdown('<div class="header-lightblue"><h3>🤖 Hospital Management System Assistant</h3></div>',
                unsafe_allow_html=True)
    # Check authentication
    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
        st.warning("Please login to access the chatbot")
        return

    # Display chat interface
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(
                f'<div class="message user-message">{message["content"]}<div class="message-time">{message["time"]}</div></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="message bot-message">{message["content"]}<div class="message-time">{message["time"]}</div></div>',
                unsafe_allow_html=True
            )

    if st.session_state.generating_response:
        st.markdown(
            '<div class="generating"><div class="spinner"></div>Generating response...</div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)  # Close chat-container

    # Input area - using a form to properly handle input
    with st.form(key='chat_input_form'):
        user_input = st.text_input("Type your message...", "", key="user_input",
                                   placeholder="Ask me anything about the hospital system...",
                                   label_visibility="collapsed")

        if st.form_submit_button("Send"):
            if user_input.strip():
                # Add user message to chat history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input,
                    "time": datetime.now().strftime("%H:%M")
                })

                # Set generating response state
                st.session_state.generating_response = True
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # Close main-container


# ------------------ View Patient History ------------------
def view_patient_history():
    """
    View Patient History: Accessible to Admin, Doctor, and Nurse.
    """
    check_user_role(["Admin", "Doctor", "Nurse"])
    st.subheader("📜 Patient History")

    # Fetch and display patient history
    patient_history = fetch_data("SELECT * FROM patient_history", "patient_history")
    if patient_history.empty:
        st.warning("No patient history records found.")
    else:
        st.dataframe(patient_history)


def log_user_action(username, role, action):
    try:
        con = connection()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO user_logs (username, role, action) VALUES (%s, %s, %s)",
            (username, role, action)
        )
        con.commit()
    except sq.Error as er:
        logging.error(f"Error logging user action: {er}")


# --------------AutoAttendenceMArking-----------------------------
def mark_attendance(username, role):
    """Mark attendance for a user if not already marked for the day."""
    # Skip attendance marking for patients
    if role == "Patient":
        return
    try:
        con = connection()
        cur = con.cursor()

        # Check if attendance is already marked for the day
        cur.execute(
            "SELECT id FROM attendance WHERE username = %s AND attendance_date = CURDATE()",
            (username,)
        )
        if cur.fetchone():
            return  # Attendance already marked

        # Mark attendance
        cur.execute(
            "INSERT INTO attendance (username, role, attendance_date) VALUES (%s, %s, CURDATE())",
            (username, role)
        )
        con.commit()
    except sq.Error as er:
        logging.error(f"Error marking attendance: {er}")
        st.error(f"Failed to mark attendance: {str(er)}")  # Show error to user
    except Exception as e:
        logging.error(f"Unexpected error marking attendance: {e}")
        st.error("An unexpected error occurred while marking attendance")


def attendance_dashboard():
    st.markdown('<div class="header-lightblue"><h3>📊 Attendance Dashboard</h3></div>', unsafe_allow_html=True)

    # Use tabs instead of radio buttons
    tab1, tab2 = st.tabs(["Last 7 Days", "Monthly Summary"])

    with tab1:
        show_last_7_days_records()

    with tab2:
        show_monthly_summary()


def fetch_last_7_days_records():
    """Fetch attendance records for the last 7 days."""
    query = """
        SELECT 
            username, 
            role, 
            attendance_date 
        FROM 
            attendance 
        WHERE 
            attendance_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        ORDER BY 
            attendance_date DESC
    """
    return fetch_data(query, "attendance", columns=["Username", "Role", "Date"])


def show_last_7_days_records():
    st.write("### Last 7 Days Attendance Records")

    # Fetch data
    last_7_days_data = fetch_last_7_days_records()

    if last_7_days_data.empty:
        st.info("No attendance records found for the last 7 days.")
    else:
        # Display data in a table
        st.dataframe(last_7_days_data)

        # Create a bar chart for last 7 days attendance
        st.write("### Last 7 Days Attendance Visualization")
        fig = px.bar(
            last_7_days_data,
            x="Date",
            y="Username",
            color="Role",
            title="Last 7 Days Attendance by Role",
            labels={"Date": "Date", "Username": "User Count"},
            color_discrete_sequence=px.colors.qualitative.Vivid  # Vibrant colors
        )
        st.plotly_chart(fig)


def fetch_monthly_summary():
    """Fetch monthly attendance summary by role."""
    query = """
        SELECT 
            role, 
            COUNT(DISTINCT username) AS user_count 
        FROM 
            attendance 
        WHERE 
            attendance_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        GROUP BY 
            role
    """
    return fetch_data(query, "attendance", columns=["Role", "User Count"])


def show_monthly_summary():
    st.write("### Monthly Attendance Summary")

    # Fetch data
    monthly_data = fetch_monthly_summary()

    if monthly_data.empty:
        st.info("No attendance records found for the last month.")
    else:
        # Display data in a table
        st.dataframe(monthly_data)

        # Create a pie chart for monthly attendance
        st.write("### Monthly Attendance Visualization")
        fig = px.pie(
            monthly_data,
            values="User Count",
            names="Role",
            title="Monthly Attendance by Role",
            color_discrete_sequence=px.colors.qualitative.Pastel  # Pastel colors
        )
        st.plotly_chart(fig)


# ------------------ Doctor Section ------------------
def doctor_section():
    """
    Doctor Section: Accessible to Admin, Doctor, Receptionist, Nurse, and Patient (view-only).
    """
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])  # Added "Nurse" to allowed roles

    # Add tabs for Doctor section
    if st.session_state['user_role'] == "Patient":
        # Patients can only view doctors (no tabs for adding doctors)
        view_doctors()  # Call the view_doctors function directly
    else:
        # Admin, Doctor, Receptionist, and Nurse can add and view doctors
        doctor_tabs = st.tabs(["Add Doctor", "View Doctors"])  # Removed "Notes" tab
        with doctor_tabs[0]:
            add_doctor()  # Add Doctor page
        with doctor_tabs[1]:
            view_doctors()  # View Doctors page


def view_doctors():
    """
    View Doctors: Accessible to Admin, Doctor, Receptionist, Nurse, and Patient (view-only).
    """
    st.markdown('<div class="header-lightblue"><h3> 👨‍⚕️View Doctor</h3></div>', unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])

    # Fetch doctor data with staff names, roles, and shifts
    query = """
        SELECT d.id, s.staff_name AS doctor_name, d.department, d.role, s.shift
        FROM doctor d
        JOIN staff s ON d.staff_id = s.id
    """
    doctor_data = fetch_data(query, "doctor", columns=["ID", "Doctor Name", "Department", "Role", "Shift"])

    if doctor_data.empty:
        st.warning("No doctor records found.")
        return

    # Display doctor records
    st.dataframe(doctor_data)

    # Add a download button for exporting the doctor data
    if st.button("📥 Download Doctor Records as CSV"):
        csv = doctor_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="doctor_records.csv",
            mime="text/csv"
        )


def add_doctor():
    """
    Add Doctor: Accessible to Admin, Doctor, Receptionist, and Nurse.
    """
    st.markdown('<div class="header-lightblue"><h3> 👨‍⚕️Add Doctor</h3></div>', unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])  # Added "Nurse" to allowed roles

    # Fetch staff names, IDs, and roles for doctors
    staff_data = fetch_data("SELECT id, staff_name, role FROM staff WHERE role = 'Doctor'", "staff",
                            columns=["Staff ID", "Staff Name", "Role"])

    if staff_data.empty:
        st.warning("No doctors found in the staff table.")
        return

    # Select doctor name
    staff_name = st.selectbox("Select Doctor", staff_data["Staff Name"])
    staff_id = staff_data[staff_data["Staff Name"] == staff_name]["Staff ID"].iloc[0]
    role = staff_data[staff_data["Staff Name"] == staff_name]["Role"].iloc[0]

    # Input department
    department = st.text_input("Department*")

    if st.button("Add Doctor"):
        if not department:
            st.error("Department is required!")
            return

        # Insert doctor data into the doctor table
        insert_data(
            "INSERT INTO doctor (staff_id, department, role) VALUES (%s, %s, %s)",
            (staff_id, department, role)
        )
        st.success("Doctor added successfully!")


# ------------------ Manage Patients Section ------------------
def initialize_rooms_and_ambulances():
    """Initialize 50 general rooms, 25 ICU rooms, and 5 ambulances if they don't exist."""
    con = connection()
    cur = con.cursor()

    # Check if rooms already exist
    cur.execute("SELECT COUNT(*) FROM rooms")
    if cur.fetchone()[0] == 0:
        # Create 50 general rooms (Single, Double, Deluxe)
        for i in range(1, 51):
            room_type = "Single" if i <= 20 else ("Double" if i <= 40 else "Deluxe")
            cur.execute(
                "INSERT INTO rooms (room_number, room_type, availability, is_icu) VALUES (%s, %s, 'Not Booked', FALSE)",
                (f"GEN-{i}", room_type)
            )

        # Create 25 ICU rooms
        for i in range(1, 26):
            cur.execute(
                "INSERT INTO rooms (room_number, room_type, availability, is_icu) VALUES (%s, 'ICU', 'Not Booked', TRUE)",
                (f"ICU-{i}",)
            )

        con.commit()

    # Check if ambulances already exist
    cur.execute("SELECT COUNT(*) FROM ambulances")
    if cur.fetchone()[0] == 0:
        # Create 5 ambulances
        for i in range(1, 6):
            cur.execute(
                "INSERT INTO ambulances (ambulance_number, status) VALUES (%s, 'Available')",
                (f"AMB-{i}",)
            )

        con.commit()

    con.close()


# Call the function to initialize rooms and ambulances
initialize_rooms_and_ambulances()


def add_patient():
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])
    try:
        st.markdown('<div class="header-lightblue"><h3>📝 Add New Patient</h3></div>', unsafe_allow_html=True)

        # Patient Details
        name = st.text_input("Patient Name*")
        age = st.number_input("Age*", min_value=0)
        gender = st.selectbox("Gender*", ["M", "F"])
        address = st.text_area("Address*")
        contact_no = st.text_input("Contact Number*")
        dob = st.date_input(
            "Date of Birth* (YYYY-MM-DD)",
            help="Enter date in YYYY-MM-DD format",
            min_value=datetime(1900, 1, 1).date(),
            max_value=datetime.today().date()
        )

        # Fetch consultant names and departments from the doctor table
        doctor_data = fetch_data(
            """
            SELECT s.staff_name AS consultant_name, d.department 
            FROM doctor d 
            JOIN staff s ON d.staff_id = s.id
            """,
            "doctor",
            columns=["Consultant Name", "Department"]
        )

        if doctor_data.empty:
            st.warning("No doctors found. Please add doctors first.")
            return

        # Select consultant name
        consultant_name = st.selectbox("Consultant Name*", doctor_data["Consultant Name"])

        # Fetch the department for the selected consultant
        department = doctor_data[doctor_data["Consultant Name"] == consultant_name]["Department"].iloc[0]

        # Display the department as a read-only field
        st.text_input("Department*", value=department, disabled=True)

        # Rest of the patient details
        date_of_consultancy = st.date_input("Date of Consultancy*")
        diseases = st.text_input("Disease*")
        fees = st.number_input("Fees*", min_value=0.0, format="%.2f")

        # Fetch medicine from inventory
        inventory_items = fetch_data("SELECT item_name, quantity FROM inventory", "inventory",
                                     ["Item Name", "Quantity"])
        if not inventory_items.empty:
            medicine_options = {f"{row['Item Name']} (Available: {row['Quantity']})": row["Item Name"] for _, row in
                                inventory_items.iterrows()}
            selected_medicine = st.selectbox("Select Medicine", list(medicine_options.keys()))
            medicine_name = medicine_options.get(selected_medicine)
            max_quantity = inventory_items[inventory_items["Item Name"] == medicine_name]["Quantity"].iloc[0]
            quantity = st.number_input("Quantity*", min_value=1, max_value=max_quantity, value=1)
        else:
            st.warning("No medicine available in inventory.")
            medicine_name = None
            quantity = 0

        if st.button("Add Patient"):
            required_fields = [name, age, gender, address, contact_no, dob, consultant_name, date_of_consultancy,
                               department, diseases, fees]
            if not all(required_fields) or dob is None:
                st.error("Please fill all required fields (*) with valid data")
                logging.warning("Add Patient: Missing required fields.")
            else:
                # Insert patient data (without role)
                insert_data(
                    """
                    INSERT INTO patients (name, age, gender, address, contact_no, dob, consultant_name, department, date_of_consultancy, diseases, fees, medicine, quantity)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (name, age, gender, address, contact_no, dob, consultant_name, department, date_of_consultancy,
                     diseases, fees, medicine_name, quantity)
                )
                st.success("Patient added successfully!")
                logging.info(f"Patient {name} added successfully.")

                # Deduct the quantity from inventory
                if medicine_name and quantity > 0:
                    insert_data(
                        "UPDATE inventory SET quantity = quantity - %s WHERE item_name = %s",
                        (quantity, medicine_name)
                    )
                    st.success(f"{quantity} units of {medicine_name} deducted from inventory.")
    except Exception as e:
        st.error(f"Error adding patient: {e}")
        logging.error(f"Error adding patient: {e}")


def view_patients():
    st.markdown('<div class="header-lightblue"><h3>📋 Patient Records with Room and Medicine Details</h3></div>',
                unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])

    # Fetch patient data with room and medicine details
    query = """
        SELECT 
            p.id AS 'Patient ID',
            p.name AS 'Patient Name',
            p.age AS 'Age',
            p.gender AS 'Gender',
            p.address AS 'Address',
            p.contact_no AS 'Contact No',
            p.dob AS 'Date of Birth',
            p.consultant_name AS 'Consultant',
            p.date_of_consultancy AS 'Consultancy Date',
            p.department AS 'Department',
            p.diseases AS 'Disease',
            p.fees AS 'Fees',
            p.medicine AS 'Medicine',
            p.quantity AS 'Quantity',
            COALESCE(r.room_number, 'N/A') AS 'Room Number',
            COALESCE(r.room_type, 'N/A') AS 'Room Type'
        FROM 
            patients p
        LEFT JOIN 
            rooms r ON p.id = r.patient_id
    """
    patient_data = fetch_data(query, "patients", columns=[
        "Patient ID", "Patient Name", "Age", "Gender", "Address", "Contact No",
        "Date of Birth", "Consultant", "Consultancy Date", "Department",
        "Disease", "Fees", "Medicine", "Quantity", "Room Number", "Room Type"
    ])

    if patient_data.empty:
        st.info("No patient records found.")
    else:
        # Add search and filter functionality
        st.markdown("### 🔍 Search and Filter Patients")
        col1, col2 = st.columns(2)

        with col1:
            search_query = st.text_input("Search by Patient Name or ID")

        with col2:
            filter_department = st.selectbox("Filter by Department",
                                             ["All"] + list(patient_data["Department"].unique()))

        # Apply search and filter
        if search_query:
            patient_data = patient_data[
                patient_data["Patient Name"].str.contains(search_query, case=False) |
                patient_data["Patient ID"].astype(str).str.contains(search_query)
                ]

        if filter_department != "All":
            patient_data = patient_data[patient_data["Department"] == filter_department]

        # Display the filtered data
        st.dataframe(patient_data)

        # Add a download button for exporting the patient data
        if st.button("📥 Download Patient Records as CSV"):
            csv = patient_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="patient_records.csv",
                mime="text/csv"
            )

        # Add a simple visualization
        st.markdown("### 📊 Patient Distribution by Department")
        if not patient_data.empty:
            department_counts = patient_data["Department"].value_counts().reset_index()
            department_counts.columns = ["Department", "Number of Patients"]

            fig = px.bar(
                department_counts,
                x="Department",
                y="Number of Patients",
                title="Patient Distribution by Department",
                labels={"Department": "Department", "Number of Patients": "Number of Patients"},
                color="Department",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig)
        else:
            st.info("No data available for visualization.")


def discharge_patient():
    """Discharge patient, free up room, and record discharge details with reason."""
    st.markdown('<div class="header-lightblue"><h3>\U0001F3E2 Discharge Patient from Room</h3></div>',
                unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])

    # Fetch the list of patients currently allocated to rooms (both general and ICU)
    query = """
        SELECT 
            COALESCE(r.patient_id, ep.id) AS 'Patient ID',  -- General patient_id or ICU patient's emergency_patients.id
            COALESCE(p.name, ep.name) AS 'Patient Name',    -- Patient name from either table
            r.room_number AS 'Room Number', 
            r.room_type AS 'Room Type', 
            r.is_icu AS 'ICU Room',
            ep.id AS 'Emergency Patient ID'  -- Explicitly fetch emergency_patient_id
        FROM rooms r
        LEFT JOIN patients p ON r.patient_id = p.id
        LEFT JOIN emergency_patients ep ON r.id = ep.room_id
        WHERE r.availability = 'Booked'
    """
    patient_data = fetch_data(
        query,
        "patients",
        ["Patient ID", "Patient Name", "Room Number", "Room Type", "ICU Room", "Emergency Patient ID"]
    )

    # Check if there are any patients to discharge
    if patient_data.empty:
        st.info("No patients currently allocated to rooms.")
        return

    # Create a dropdown for selecting a patient to discharge
    patient_options = {
        f"{row['Patient Name']} (ID: {row['Patient ID']}) - {row['Room Number']} ({'ICU' if row['ICU Room'] else 'General'})":
            (row["Patient ID"], row["Emergency Patient ID"], row["Room Number"], row["ICU Room"])
        for _, row in patient_data.iterrows()
    }
    selected_patient = st.selectbox("Select Patient to Discharge", list(patient_options.keys()))
    patient_id, emergency_patient_id, room_number, is_icu = patient_options.get(selected_patient,
                                                                                (None, None, None, None))

    if selected_patient:
        # Fetch the selected patient's details
        patient_info = patient_data[
            (patient_data["Patient ID"] == patient_id) |
            (patient_data["Emergency Patient ID"] == emergency_patient_id)
            ]

        if not patient_info.empty:
            patient_info = patient_info.iloc[0]
            patient_id = int(patient_info["Patient ID"]) if not pd.isna(patient_info["Patient ID"]) else None
            emergency_patient_id = int(patient_info["Emergency Patient ID"]) if not pd.isna(
                patient_info["Emergency Patient ID"]) else None
            room_number = str(patient_info["Room Number"])
            room_type = str(patient_info["Room Type"])
            is_icu = bool(patient_info["ICU Room"])

            # Display patient details
            st.write(f"**Patient Name:** {patient_info['Patient Name']}")
            st.write(f"**Room Number:** {room_number}")
            st.write(f"**Room Type:** {room_type}")
            st.write(f"**ICU Room:** {'Yes' if is_icu else 'No'}")

            discharge_reason = st.text_area("Enter Discharge Reason")

            if st.button("Confirm Discharge"):
                if not discharge_reason.strip():
                    st.warning("Discharge Reason cannot be empty!")
                    return

                con = connection()
                cur = con.cursor()
                try:
                    # Insert discharge record based on patient type
                    if is_icu:
                        # Use emergency_patient_id for ICU patients and set patient_id to NULL
                        cur.execute(
                            """
                            INSERT INTO discharged_patients 
                            (patient_id, emergency_patient_id, patient_name, room_number, room_type, discharge_date, discharge_time, discharge_reason, is_icu)
                            VALUES (NULL, %s, %s, %s, %s, CURDATE(), CURTIME(), %s, %s)
                            """,
                            (emergency_patient_id, patient_info["Patient Name"], room_number, room_type,
                             discharge_reason, is_icu)
                        )
                    else:
                        # Use patient_id for general patients and set emergency_patient_id to NULL
                        cur.execute(
                            """
                            INSERT INTO discharged_patients 
                            (patient_id, emergency_patient_id, patient_name, room_number, room_type, discharge_date, discharge_time, discharge_reason, is_icu)
                            VALUES (%s, NULL, %s, %s, %s, CURDATE(), CURTIME(), %s, %s)
                            """,
                            (patient_id, patient_info["Patient Name"], room_number, room_type, discharge_reason, is_icu)
                        )

                    # Update room status
                    cur.execute(
                        "UPDATE rooms SET availability = 'Not Booked', patient_id = NULL WHERE room_number = %s",
                        (room_number,)
                    )

                    con.commit()
                    st.success(
                        f"✅ {patient_info['Patient Name']} discharged successfully! Room {room_number} is now available.")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    con.rollback()
                    st.error(f"Error during discharge: {e}")
                    logging.error(f"Discharge Error: {e}")
                finally:
                    con.close()
        else:
            st.error("Selected patient not found in the records.")
    else:
        st.warning("Please select a patient to discharge.")


def view_discharged_patients():
    st.markdown('<div class="header-lightblue"><h3>\U0001F4DC Discharged Patients Records</h3></div>',
                unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])

    # Fetch discharged patient records
    discharged_data = fetch_data(
        """
        SELECT 
            COALESCE(patient_id, emergency_patient_id) AS 'Patient ID',
            patient_name AS 'Patient Name',
            room_number AS 'Room Number',
            room_type AS 'Room Type',
            is_icu AS 'ICU Room',
            discharge_date AS 'Discharge Date',
            discharge_time AS 'Discharge Time',
            discharge_reason AS 'Discharge Reason'
        FROM discharged_patients
        """,
        "discharged_patients",
        ["Patient ID", "Patient Name", "Room Number", "Room Type", "ICU Room", "Discharge Date", "Discharge Time",
         "Discharge Reason"]
    )

    # Check if there are any discharged patients
    if discharged_data.empty:
        st.info("No discharged patient records found.")
    else:
        # Display the ICU room status
        discharged_data["ICU Room"] = discharged_data["ICU Room"].apply(lambda x: "Yes" if x else "No")
        st.dataframe(discharged_data)


def allocate_room():
    try:
        st.markdown('<div class="header-lightblue"><h3>\U0001F3E2 Allocate Room to Patient</h3></div>',
                    unsafe_allow_html=True)

        # Fetch patients without allocated rooms
        patients_without_rooms = fetch_data(
            "SELECT id, name FROM patients WHERE id NOT IN (SELECT patient_id FROM rooms WHERE patient_id IS NOT NULL)",
            "patients",
            ["Patient ID", "Patient Name"]
        )

        if not patients_without_rooms.empty:
            # Convert to native Python types
            patient_options = {
                f"{row['Patient Name']} (ID: {int(row['Patient ID'])})": int(row['Patient ID'])
                for _, row in patients_without_rooms.iterrows()
            }
            selected_patient = st.selectbox("Select Patient", list(patient_options.keys()))
            patient_id = patient_options.get(selected_patient)

            # Fetch available general rooms
            available_rooms = fetch_data(
                "SELECT id, room_number, room_type FROM rooms WHERE availability = 'Not Booked' AND is_icu = FALSE",
                "rooms",
                ["Room ID", "Room Number", "Room Type"]
            )

            if not available_rooms.empty:
                room_options = {
                    f"{row['Room Number']} ({row['Room Type']})": int(row['Room ID'])
                    for _, row in available_rooms.iterrows()
                }
                selected_room = st.selectbox("Select Room", list(room_options.keys()))
                room_id = room_options.get(selected_room)

                if st.button("Allocate Room") and patient_id and room_id:
                    # Convert to native Python int
                    patient_id = int(patient_id)
                    room_id = int(room_id)

                    insert_data(
                        "UPDATE rooms SET availability = 'Booked', patient_id = %s WHERE id = %s",
                        (patient_id, room_id)
                    )
                    st.success(f"Room {selected_room} allocated to {selected_patient}!")
            else:
                st.warning("No general rooms available.")
        else:
            st.info("No patients needing room allocation.")
    except Exception as e:
        st.error(f"Error allocating room: {e}")


# New function to handle discharging patients
def discharge_patient_ui():
    st.subheader("🚪 Discharge Patient")

    # Fetch all patients with allocated rooms (including ICU)
    patients_with_rooms = fetch_data(
        """
        SELECT p.id AS 'Patient ID', p.name AS 'Patient Name', r.room_number AS 'Room Number'
        FROM patients p
        JOIN rooms r ON p.id = r.patient_id
        WHERE r.availability = 'Booked'  <--- ADDED THIS LINE
        """,
        "patients",
        ["Patient ID", "Patient Name", "Room Number"]
    )

    if not patients_with_rooms.empty:
        # Create dropdown options with unique identifiers
        patient_options = {
            f"{row['Patient Name']} (ID: {int(row['Patient ID'])}) - Room {row['Room Number']}": int(row['Patient ID'])
            for _, row in patients_with_rooms.iterrows()
        }

        selected_patient = st.selectbox("Select Patient to Discharge", list(patient_options.keys()))
        patient_id = patient_options.get(selected_patient)

        if st.button("Discharge Patient") and patient_id:
            # Convert to native Python int
            patient_id = int(patient_id)
            result = discharge_patient(patient_id)
            st.success(result)
    else:
        st.info("No patients with allocated rooms found.")


# ---------------------------Emergency Unit-----------------------
def add_emergency_patient():
    st.markdown('<div class="header-lightblue"><h3>🚨 Add Emergency Patient</h3></div>', unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])

    # Create columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        # Patient Details
        name = st.text_input("Patient Name*")
        contact_no = st.text_input("Contact Number*")
        address = st.text_area("Address*")
        blood_type = st.selectbox("Blood Type*", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])

        # Added age and date of birth fields
        age = st.number_input("Age", min_value=0, max_value=120)

        # Calendar widget for Date of Birth input
        dob = st.date_input(
            "Date of Birth* (YYYY-MM-DD)",
            help="Enter date in YYYY-MM-DD format",
            min_value=datetime(1900, 1, 1).date(),
            max_value=datetime.today().date()
        )

    with col2:
        # Fees input with clear label and currency symbol
        fees = st.number_input("Fees (₹)*", min_value=0.0, format="%.2f", step=100.0)

        # Fetch available ICU rooms
        available_icu_rooms = fetch_data(
            "SELECT id, room_number FROM rooms WHERE is_icu = TRUE AND availability = 'Not Booked'",
            "rooms",
            ["ID", "Room Number"]
        )

        room_options = {
            f"{row['Room Number']}": int(row['ID'])
            for _, row in available_icu_rooms.iterrows()
        }
        selected_room = st.selectbox("Assign ICU Room", ["NA"] + list(room_options.keys()))

        # Doctor Assignment with department information
        doctor_data = fetch_data(
            """
            SELECT s.id, s.staff_name, d.department 
            FROM staff s
            JOIN doctor d ON s.id = d.staff_id
            WHERE s.role = 'Doctor'
            """,
            "staff",
            ["ID", "Doctor Name", "Department"]
        )

        if not doctor_data.empty:
            doctor_options = {
                f"{row['Doctor Name']} ({row['Department']})": row['ID']
                for _, row in doctor_data.iterrows()
            }

            # Display doctor selection with department info
            selected_doctor = st.selectbox("Assign Doctor*", list(doctor_options.keys()))
            doctor_id = doctor_options.get(selected_doctor)

            # Extract department from selection
            selected_dept = doctor_data[doctor_data['ID'] == doctor_id]['Department'].iloc[0]
            st.text_input("Doctor's Department", value=selected_dept, disabled=True)
        else:
            st.warning("No doctors available. Please add doctors first.")
            return

    if st.button("➕ Add Emergency Patient", type="primary"):
        required_fields = [name, contact_no, address, blood_type, selected_doctor, fees]
        if not all(required_fields):
            st.error("Please fill all required fields (*)")
        elif selected_room == "NA" and not selected_doctor:
            st.error("Doctor selection is mandatory when ICU room is not assigned")
        else:
            # If "NA" is selected, set room_id to NULL
            room_id = None if selected_room == "NA" else room_options.get(selected_room)

            try:
                # Insert emergency patient with additional fields
                insert_data(
                    """
                    INSERT INTO emergency_patients 
                    (name, contact_no, address, blood_type, room_id, doctor_id, fees, age, dob)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (name, contact_no, address, blood_type, room_id, doctor_id, fees, age, dob)
                )

                # If a room is assigned, update ICU room status
                if room_id:
                    insert_data(
                        "UPDATE rooms SET availability = 'Booked' WHERE id = %s",
                        (room_id,)
                    )

                st.success("Emergency patient added successfully!")

            except Exception as e:
                st.error(f"Error adding emergency patient: {str(e)}")
                logging.error(f"Error adding emergency patient: {str(e)}")


def view_emergency_patients():
    st.markdown('<div class="header-lightblue"><h3>🚨 Emergency Patients Records</h3></div>', unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])

    # Get ICU room status
    total_icu = fetch_data(
        "SELECT COUNT(*) FROM rooms WHERE is_icu = TRUE",
        "rooms"
    ).iloc[0, 0]

    available_icu = fetch_data(
        "SELECT COUNT(*) FROM rooms WHERE is_icu = TRUE AND availability = 'Not Booked'",
        "rooms"
    ).iloc[0, 0]

    st.write(f"**ICU Rooms:** {available_icu} Available / {total_icu} Total")

    # Fetch ALL emergency patient data (including those without room allocation)
    query = """
        SELECT 
            ep.id,
            ep.name,
            ep.contact_no,
            ep.address,
            ep.blood_type,
            ep.age,
            DATE(ep.dob) AS dob,
            COALESCE(r.room_number, 'Not Assigned') AS room_number,
            s.staff_name,
            d.department,
            DATE(ep.admission_date) AS admission_date,
            ep.fees,
            CASE WHEN r.id IS NULL THEN 'No Room' ELSE r.availability END AS room_status
        FROM 
            emergency_patients ep
        LEFT JOIN 
            rooms r ON ep.room_id = r.id
        LEFT JOIN 
            staff s ON ep.doctor_id = s.id
        LEFT JOIN
            doctor d ON s.id = d.staff_id
    """

    # Define the column names that match the SQL query results
    column_names = [
        "Patient ID",
        "Patient Name",
        "Contact Number",
        "Address",
        "Blood Type",
        "Age",
        "Date of Birth",
        "ICU Room",
        "Assigned Doctor",
        "Department",
        "Admission Date",
        "Fees (₹)",
        "Room Status"
    ]

    emergency_data = fetch_data(query, "emergency_patients", column_names)

    if emergency_data.empty:
        st.info("No emergency patient records found.")
    else:
        # Add search and filter functionality
        st.markdown("### 🔍 Search and Filter Emergency Patients")
        col1, col2 = st.columns(2)

        with col1:
            search_query = st.text_input("Search by Patient Name or ID")

        with col2:
            room_filter = st.selectbox("Filter by Room Status", ["All", "Assigned", "Not Assigned"])

        # Apply filters
        if search_query:
            emergency_data = emergency_data[
                emergency_data["Patient Name"].str.contains(search_query, case=False) |
                emergency_data["Patient ID"].astype(str).str.contains(search_query)
                ]

        if room_filter == "Assigned":
            emergency_data = emergency_data[emergency_data["ICU Room"] != "Not Assigned"]
        elif room_filter == "Not Assigned":
            emergency_data = emergency_data[emergency_data["ICU Room"] == "Not Assigned"]

        st.dataframe(emergency_data)

        # Add a download button
        if st.button("📥 Download Emergency Patient Records as CSV"):
            csv = emergency_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="emergency_patient_records.csv",
                mime="text/csv"
            )


def allocate_icu_room_to_emergency_patient(patient_id):
    con = connection()
    cur = con.cursor()

    # Get available ICU room
    cur.execute("SELECT id, room_number FROM rooms WHERE availability = 'Not Booked' AND is_icu = TRUE LIMIT 1")
    room = cur.fetchone()
    if room:
        room_id, room_number = room

        # Assign room to patient
        cur.execute("UPDATE rooms SET availability = 'Booked', patient_id = %s WHERE id = %s", (patient_id, room_id))
        con.commit()
        return f"ICU Room {room_number} allocated successfully!"
    else:
        return "No ICU rooms available!"


def discharge_emergency_patient_ui():
    st.subheader("🚪 Discharge Emergency Patient")

    # Fetch only emergency patients who are currently admitted (not discharged)
    emergency_patients_with_rooms = fetch_data(
        """
        SELECT ep.id AS 'Patient ID', ep.name AS 'Patient Name', r.room_number AS 'Room Number'
        FROM emergency_patients ep
        JOIN rooms r ON ep.room_id = r.id
        WHERE r.is_icu = TRUE 
          AND r.availability = 'Booked'
          AND ep.room_id IS NOT NULL
          AND (ep.discharge_reason IS NULL OR ep.discharge_reason = '')
          AND ep.discharge_date IS NULL
        """,
        "emergency_patients",
        ["Patient ID", "Patient Name", "Room Number"]
    )

    if not emergency_patients_with_rooms.empty:
        # Create dropdown options with unique identifiers
        patient_options = {
            f"{row['Patient Name']} (ID: {int(row['Patient ID'])}) - Room {row['Room Number']}": int(row['Patient ID'])
            for _, row in emergency_patients_with_rooms.iterrows()
        }

        selected_patient = st.selectbox("Select Emergency Patient to Discharge", list(patient_options.keys()))
        patient_id = patient_options.get(selected_patient)

        if st.button("Discharge Emergency Patient") and patient_id:
            # Convert to native Python int
            patient_id = int(patient_id)
            result = discharge_patient(patient_id)
            st.success(result)
    else:
        st.info("No emergency patients available for discharge (all current patients have already been discharged).")


def emergency_summary_metrics():
    st.markdown('<div class="header-lightblue"><h3>📊 Emergency Summary Metrics</h3></div>', unsafe_allow_html=True)

    # Total Emergency Patients
    total_patients = fetch_data("SELECT COUNT(*) FROM emergency_patients", "emergency_patients", columns=["count"])
    total_patients = total_patients.iloc[0, 0] if not total_patients.empty else 0

    # Available ICU Rooms
    available_icu_rooms = fetch_data(
        "SELECT COUNT(*) FROM rooms WHERE is_icu = TRUE AND availability = 'Not Booked'",
        "rooms",
        columns=["count"]
    )
    available_icu_rooms = available_icu_rooms.iloc[0, 0] if not available_icu_rooms.empty else 0

    # Assigned Doctors
    assigned_doctors = fetch_data(
        "SELECT COUNT(DISTINCT doctor_id) FROM emergency_patients",
        "emergency_patients",
        columns=["count"]
    )
    assigned_doctors = assigned_doctors.iloc[0, 0] if not assigned_doctors.empty else 0

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Emergency Patients", total_patients)
    with col2:
        st.metric("Available ICU Rooms", available_icu_rooms)
    with col3:
        st.metric("Assigned Doctors", assigned_doctors)


def emergency_patients_by_blood_type():
    st.write("### Emergency Patients by Blood Type")

    # Fetch data
    blood_type_data = fetch_data(
        "SELECT blood_type, COUNT(*) as count FROM emergency_patients GROUP BY blood_type",
        "emergency_patients",
        columns=["Blood Type", "Count"]
    )

    if not blood_type_data.empty:
        # Create pie chart
        fig = px.pie(
            blood_type_data,
            values="Count",
            names="Blood Type",
            title="Emergency Patients by Blood Type",
            color_discrete_sequence=px.colors.qualitative.Pastel  # Attractive colors
        )
        st.plotly_chart(fig)
    else:
        st.info("No blood type data available.")


def emergency_patients_over_time():
    st.write("### Emergency Patients Over Time")

    # Fetch data
    patients_over_time = fetch_data(
        "SELECT DATE(admission_date) as date, COUNT(*) as count FROM emergency_patients GROUP BY DATE(admission_date)",
        "emergency_patients",
        columns=["Date", "Count"]
    )

    if not patients_over_time.empty:
        # Create line chart
        fig = px.line(
            patients_over_time,
            x="Date",
            y="Count",
            title="Emergency Patients Over Time",
            labels={"Date": "Date", "Count": "Number of Patients"},
            color_discrete_sequence=["#FFA07A"]  # Light coral color
        )
        st.plotly_chart(fig)
    else:
        st.info("No admission data available.")


def icu_room_utilization():
    st.write("### ICU Room Utilization")

    # Fetch data
    room_utilization = fetch_data(
        "SELECT availability, COUNT(*) as count FROM rooms WHERE is_icu = TRUE GROUP BY availability",
        "rooms",
        columns=["Status", "Count"]
    )

    if not room_utilization.empty:
        # Create bar chart
        fig = px.bar(
            room_utilization,
            x="Status",
            y="Count",
            title="ICU Room Utilization",
            labels={"Status": "Room Status", "Count": "Number of Rooms"},
            color="Status",
            color_discrete_sequence=["#87CEEB", "#FF6347"]  # Sky blue and tomato colors
        )
        st.plotly_chart(fig)
    else:
        st.info("No ICU room data available.")


def emergency_dashboard():
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])

    # Display summary metrics
    emergency_summary_metrics()

    # Display visualizations
    col1, col2 = st.columns(2)
    with col1:
        emergency_patients_by_blood_type()
    with col2:
        icu_room_utilization()

    emergency_patients_over_time()


# ------------------ Room Info Section ------------------
def room_info_section():
    """Manage Room Information Section."""
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])
    st.markdown('<div class="header-lightblue"><h3>\U0001F3E2 Room Info</h3></div>', unsafe_allow_html=True)
    room_tabs = st.tabs(["Allocate Room", "View Rooms", "Discharge Patient", "View Discharged Patients"])

    with room_tabs[0]:
        allocate_room()

    with room_tabs[1]:
        view_rooms()

    with room_tabs[2]:
        discharge_patient()

    with room_tabs[3]:
        view_discharged_patients()


def view_rooms():
    st.markdown('<div class="header-lightblue"><h3>\U0001F3E2 Room Availability</h3></div>', unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])
    # Fetch total number of general rooms
    total_gen = fetch_data(
        "SELECT COUNT(*) FROM rooms WHERE room_type = 'Single' OR room_type = 'Double' OR room_type = 'Deluxe'",
        "rooms"
    ).iloc[0, 0]

    # Fetch number of available general rooms
    available_gen = fetch_data(
        "SELECT COUNT(*) FROM rooms WHERE (room_type = 'Single' OR room_type = 'Double' OR room_type = 'Deluxe') AND availability = 'Not Booked'",
        "rooms"
    ).iloc[0, 0]

    # Calculate allocated general rooms
    allocated_gen = total_gen - available_gen

    # Display the results
    st.write(f"**General Rooms:** {available_gen} Available | {allocated_gen} Allocated | {total_gen} Total")

    df = fetch_data(
        """
        SELECT 
            id AS 'ID', 
            room_number AS 'Room Number', 
            room_type AS 'Room Type', 
            availability AS 'Status', 
            is_icu AS 'ICU Room',
            patient_id AS 'Patient ID'
        FROM rooms
        """,
        "rooms",
        ["ID", "Room Number", "Room Type", "Status", "ICU Room", "Patient ID"]
    )
    if df.empty:
        st.info("No room records found.")
    else:
        # Replace NULL patient_id with "N/A" for better readability
        df["Patient ID"] = df["Patient ID"].fillna("N/A")
        st.dataframe(df)


# ------------------ Billing Section ------------------
def add_bill():
    try:
        st.markdown('<div class="header-lightblue"><h3>💸 Add New Bill</h3></div>', unsafe_allow_html=True)

        # Radio button to select patient type
        patient_type = st.radio("Patient Type", ["Regular Patient", "Emergency Patient"])

        if patient_type == "Regular Patient":
            # Fetch regular patient data
            patient_data = fetch_data("SELECT id, name FROM patients", "patients", ["id", "name"])
            patient_table = "patients"
        else:
            # Fetch emergency patient data
            patient_data = fetch_data("SELECT id, name FROM emergency_patients", "emergency_patients", ["id", "name"])
            patient_table = "emergency_patients"

        if not patient_data.empty:
            # Select patient
            patient_name = st.selectbox("Select Patient", patient_data["name"])
            patient_id = int(patient_data.loc[patient_data["name"] == patient_name, "id"].values[0])

            # Fetch patient details
            con = connection()
            cur = con.cursor()
            if patient_type == "Regular Patient":
                cur.execute("SELECT contact_no, fees FROM patients WHERE id = %s", (patient_id,))
                patient_type_db = "regular"
            else:
                cur.execute("SELECT contact_no, fees FROM emergency_patients WHERE id = %s", (patient_id,))
                patient_type_db = "emergency"

            patient_info = cur.fetchone()
            contact_no = patient_info[0]
            doctor_fees = patient_info[1]
            cur.close()
            con.close()

            # Input fields for bill details
            room_charges = st.number_input("Room Charges", min_value=0.0, format="%.2f")
            pathology_fees = st.number_input("Pathology Fees", min_value=0.0, format="%.2f")
            medicine_charges = st.number_input("Medicine Charges", min_value=0.0, format="%.2f")

            # Room type dropdown with allowed values
            room_type = st.selectbox("Room Type", ["NA", "Single", "Double", "ICU", "Deluxe"])

            # Calculate total amount
            total_amount = float(room_charges) + float(pathology_fees) + float(medicine_charges) + float(doctor_fees)
            st.write(f"### Total Amount: ₹ {total_amount:.2f}")

            # Add Bill button
            if st.button("Add Bill"):
                try:
                    # Handle "NA" room type
                    if room_type == "NA":
                        room_type = "NA"

                    # Insert bill details into the database
                    insert_data("""
                        INSERT INTO bill_details 
                        (bill_date, patient_type, regular_patient_id, emergency_patient_id, 
                         name, contact_no, room_charges, pathology_fees, 
                         medicine_charges, doctor_fees, room_type, total_amount)
                        VALUES (CURDATE(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        patient_type_db,
                        patient_id if patient_type == "Regular Patient" else None,
                        patient_id if patient_type == "Emergency Patient" else None,
                        patient_name, contact_no, room_charges, pathology_fees,
                        medicine_charges, doctor_fees, room_type, total_amount
                    ))

                    st.success("Bill added successfully!")
                except Exception as e:
                    st.error(f"Error adding bill: {e}")
        else:
            st.warning(f"No {patient_type.lower()} records found. Please add a {patient_type.lower()} first.")
    except Exception as e:
        st.error(f"Error in billing section: {e}")


def view_bills():
    st.markdown('<div class="header-lightblue"><h3>\U0001F4B8 Billing Information</h3></div>', unsafe_allow_html=True)

    # Radio button to filter by patient type
    filter_type = st.radio("Filter by Patient Type", ["All", "Regular Patients", "Emergency Patients"])

    # Base query for regular patients
    regular_query = """
        SELECT 
            b.bill_no AS 'Bill No', 
            b.bill_date AS 'Bill Date', 
            b.regular_patient_id AS 'Patient ID', 
            p.name AS 'Patient Name', 
            p.age AS 'Age', 
            p.gender AS 'Gender', 
            p.address AS 'Address', 
            p.contact_no AS 'Contact No', 
            p.dob AS 'Date of Birth', 
            p.consultant_name AS 'Consultant', 
            p.department AS 'Department', 
            p.diseases AS 'Disease', 
            p.fees AS 'Fees',
            b.room_charges AS 'Room Charges', 
            b.pathology_fees AS 'Pathology Fees', 
            b.medicine_charges AS 'Medicine Charges', 
            b.doctor_fees AS 'Doctor Fees', 
            b.total_amount AS 'Total Amount', 
            b.room_type AS 'Room Type',
            'Regular' AS 'Patient Type'
        FROM bill_details b
        JOIN patients p ON b.regular_patient_id = p.id
        WHERE b.patient_type = 'regular'
    """

    # Query for emergency patients
    emergency_query = """
        SELECT 
            b.bill_no AS 'Bill No', 
            b.bill_date AS 'Bill Date', 
            b.emergency_patient_id AS 'Patient ID', 
            ep.name AS 'Patient Name', 
            NULL AS 'Age', 
            NULL AS 'Gender', 
            ep.address AS 'Address', 
            ep.contact_no AS 'Contact No', 
            NULL AS 'Date of Birth', 
            s.staff_name AS 'Consultant', 
            'Emergency' AS 'Department', 
            'Emergency Care' AS 'Disease', 
            ep.fees AS 'Fees',
            b.room_charges AS 'Room Charges', 
            b.pathology_fees AS 'Pathology Fees', 
            b.medicine_charges AS 'Medicine Charges', 
            b.doctor_fees AS 'Doctor Fees', 
            b.total_amount AS 'Total Amount', 
            b.room_type AS 'Room Type',
            'Emergency' AS 'Patient Type'
        FROM bill_details b
        JOIN emergency_patients ep ON b.emergency_patient_id = ep.id
        LEFT JOIN staff s ON ep.doctor_id = s.id
        WHERE b.patient_type = 'emergency'
    """

    # Determine which query to use based on selection
    if filter_type == "All":
        query = f"{regular_query} UNION ALL {emergency_query}"
    elif filter_type == "Regular Patients":
        query = regular_query
    else:
        query = emergency_query

    columns = [
        "Bill No", "Bill Date", "Patient ID", "Patient Name", "Age", "Gender",
        "Address", "Contact No", "Date of Birth", "Consultant", "Department",
        "Disease", "Fees", "Room Charges", "Pathology Fees", "Medicine Charges",
        "Doctor Fees", "Total Amount", "Room Type", "Patient Type"
    ]

    df = fetch_data(query, "bill_details", columns)

    if df.empty:
        st.info("No billing records found.")
    else:
        # Add search functionality
        search_query = st.text_input("Search by Patient Name or ID")
        if search_query:
            df = df[
                df["Patient Name"].str.contains(search_query, case=False) |
                df["Patient ID"].astype(str).str.contains(search_query)
                ]

        st.dataframe(df)

        # Add download button
        if st.button("📥 Download Billing Records as CSV"):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="billing_records.csv",
                mime="text/csv"
            )


# ------------------ Dashboard Section ------------------
def show_dashboard():
    # Key Metrics Section
    st.markdown('<div class="header-lightblue"><h3>📊 Hospital Dashboard</h3></div>', unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])
    col1, col2, col3 = st.columns(3)

    with col1:
        data = fetch_data("SELECT COUNT(*) FROM patients WHERE DATE(date_of_consultancy) = CURDATE()", "patients")
        total_patients_today = data.iloc[0, 0] if not data.empty else 0
        st.metric("Total Patients Admitted Today", total_patients_today)

    with col2:
        data = fetch_data("SELECT COUNT(*) FROM rooms WHERE room_type = 'ICU' AND availability = 'Not Booked'", "rooms")
        available_icu_rooms = data.iloc[0, 0] if not data.empty else 0
        st.metric("Available ICU Rooms", available_icu_rooms)

    with col3:
        data = fetch_data("SELECT SUM(total_amount) FROM bill_details WHERE MONTH(bill_date) = MONTH(CURDATE())",
                          "bill_details")
        total_revenue_value = data.iloc[0, 0] if not data.empty and data.iloc[0, 0] is not None else 0.0
        total_revenue = f"₹ {total_revenue_value:.2f}"
        st.metric("Total Revenue This Month", total_revenue)

    # Alerts Section (Only Display When Necessary)
    st.markdown("### ⚠️ Alerts")

    # Initialize a variable to track if any alert is triggered
    alert_triggered = False

    # ICU Occupancy Alert
    total_icu_rooms = fetch_data("SELECT COUNT(*) FROM rooms WHERE is_icu = TRUE", "rooms").iloc[0, 0]
    occupied_icu_rooms = \
        fetch_data("SELECT COUNT(*) FROM rooms WHERE is_icu = TRUE AND availability = 'Booked'", "rooms").iloc[0, 0]
    icu_occupancy_rate = (occupied_icu_rooms / total_icu_rooms) * 100 if total_icu_rooms else 0

    # Display ICU Occupancy Alert Only if Occupancy > 80%
    if icu_occupancy_rate > 80:
        st.warning(f"⚠️ ICU Room Occupancy is at {icu_occupancy_rate:.2f}%. Consider expanding capacity.")
        alert_triggered = True

    # Low Stock Alert
    low_stock_items = fetch_data("SELECT COUNT(*) FROM inventory WHERE quantity < 5", "inventory").iloc[0, 0]
    if low_stock_items > 0:
        st.warning(f"⚠️ {low_stock_items} critical inventory items have low stock levels!")
        alert_triggered = True

    # Display "All Good" if no alerts are triggered
    if not alert_triggered:
        st.success("✅ All Good! No critical or alerting situations detected.")

    # 🔹 Enhanced Visualizations Section
    st.markdown("### 📊 Hospital Summarized Visualization")

    # Patient Demographics Card
    patient_demographics_card()

    revenue_dashboard()

    # Doctor-Patient Ratio Donut
    doctor_patient_ratio_donut()

    # Room Utilization Heatmap
    room_utilization_heatmap()

    # Staff Shift Sunburst
    staff_shift_sunburst()

    # Patient Age Distribution
    patient_age_distribution()

    # Live Inventory Gauge
    live_inventory_gauge()

    # Appointment Calendar
    appointment_calendar()

    # ICU and General Rooms Details
    st.markdown("### 🏨 Room Details")
    room_tabs = st.tabs(["ICU Rooms", "General Rooms"])

    with room_tabs[0]:
        icu_room_details()

    with room_tabs[1]:
        general_room_details()

    # Discharge Patients Graph
    discharge_patients_graph()

    # Add Patients Graph
    add_patients_graph()

    # Disease Word Cloud
    disease_word_cloud()

    # Emergency Response Time
    st.markdown("### 🚨 Emergency Response Time")
    emergency_response_time()

    # Patient Gender Ratio
    patient_gender_ratio()

    # Patient Department Distribution
    patient_department_distribution()

    # Room Allocation Chart
    room_allocation_chart()


def patient_demographics_card():
    try:
        # Fetch data
        patient_count_data = fetch_data("SELECT COUNT(*) FROM patients", "patients")
        avg_age_data = fetch_data("SELECT AVG(age) FROM patients", "patients")
        top_disease_data = fetch_data("SELECT diseases FROM patients GROUP BY diseases ORDER BY COUNT(*) DESC LIMIT 1",
                                      "patients")
        top_department_data = fetch_data(
            "SELECT department FROM patients GROUP BY department ORDER BY COUNT(*) DESC LIMIT 1", "patients")

        # Handle empty data
        patient_count = patient_count_data.iloc[0, 0] if not patient_count_data.empty else 0
        avg_age = avg_age_data.iloc[0, 0] if not avg_age_data.empty and avg_age_data.iloc[0, 0] is not None else 0.0
        top_disease = top_disease_data.iloc[0, 0] if not top_disease_data.empty else "No data"
        top_department = top_department_data.iloc[0, 0] if not top_department_data.empty else "No data"

        # Display the card
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; backdrop-filter: blur(10px); box-shadow: 0 8px 32px 0 rgba(135, 206, 235, 0.3);">
            <h3>👥 Patient Demographics</h3>
            <p>Total Patients: <span style="color: #87CEEB;">{patient_count}</span></p>
            <p>Avg Age: <span style="color: #FF6B6B;">{avg_age:.1f}</span></p>
            <p>Top Disease: <span style="color: #6BFF6B;">{top_disease}</span></p>
            <p>Most Common Department: <span style="color: #FFD700;">{top_department}</span></p>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error fetching patient demographics: {e}")
        logging.error(f"Error in patient_demographics_card: {e}")


def icu_room_details():
    try:
        # Fetch ICU room data
        icu_data = fetch_data(
            "SELECT room_number, availability FROM rooms WHERE is_icu = TRUE",
            "rooms",
            columns=["Room Number", "Status"]
        )

        # Check if ICU data is empty
        if icu_data.empty:
            st.warning("No ICU room data available.")
            return

        # Extract numerical part from room number for sorting
        icu_data['Room Num'] = icu_data['Room Number'].str.extract('(\d+)').astype(int)

        # Sort by the numerical value
        icu_data = icu_data.sort_values('Room Num')

        # Drop the temporary column
        icu_data = icu_data.drop(columns=['Room Num'])

        # Reset index for clean display
        icu_data = icu_data.reset_index(drop=True)

        # Display raw data first
        st.write("### ICU Room Details")
        st.dataframe(icu_data)

        # Create a mapping of room numbers to their status
        room_status = icu_data.set_index('Room Number')['Status'].to_dict()

        # Prepare data for plotting - ensure all rooms show both statuses
        plot_data = []
        for room, status in room_status.items():
            plot_data.append({'Room Number': room, 'Status': status, 'Count': 1})
            # Add opposite status with count 0
            opposite_status = "Booked" if status == "Not Booked" else "Not Booked"
            plot_data.append({'Room Number': room, 'Status': opposite_status, 'Count': 0})

        plot_df = pd.DataFrame(plot_data)

        # Extract numerical part for sorting the plot data
        plot_df['Room Num'] = plot_df['Room Number'].str.extract('(\d+)').astype(int)
        plot_df = plot_df.sort_values('Room Num')
        plot_df = plot_df.drop(columns=['Room Num'])

        # Create a bar chart for ICU room status
        fig = px.bar(
            plot_df,
            x="Room Number",
            y="Count",
            title="🏥 ICU Room Status (Numerical Order)",
            color="Status",
            color_discrete_sequence=["#FF6347", "#87CEEB"],  # Red for booked, Blue for available
            labels={"Room Number": "Room Number", "Count": ""},
            category_orders={"Status": ["Booked", "Not Booked"]},
            barmode='group'
        )

        # Customize the layout
        fig.update_layout(
            yaxis_title="",
            showlegend=True,
            xaxis={
                'categoryorder': 'array',
                'categoryarray': sorted(room_status.keys(),
                                        key=lambda x: int(x.split('-')[1]))
            }
        )

        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Error fetching ICU room details: {e}")
        logging.error(f"Error in icu_room_details: {e}")


def general_room_details():
    """Display general room details with availability and allocation."""
    try:
        # Fetch ALL general room data (both booked and not booked)
        general_data = fetch_data(
            "SELECT room_number, availability FROM rooms WHERE is_icu = FALSE",
            "rooms",
            columns=["Room Number", "Status"]
        )

        # Check if general room data is empty
        if general_data.empty:
            st.warning("No general room data available.")
            return

        # Create a function to extract the numeric part for proper sorting
        def extract_room_number(room_str):
            try:
                return int(room_str.split('-')[1])
            except:
                return float('inf')  # Put invalid formats at the end

        # Sort the DataFrame by room number numerically
        general_data['sort_key'] = general_data['Room Number'].apply(extract_room_number)
        general_data = general_data.sort_values('sort_key').drop('sort_key', axis=1)
        general_data.reset_index(drop=True, inplace=True)

        # Display the properly ordered data table
        st.write("### General Room Details ")
        st.dataframe(general_data)

        # Prepare data for plotting - create separate DataFrames for each status
        booked_rooms = general_data[general_data['Status'] == 'Booked']
        available_rooms = general_data[general_data['Status'] == 'Not Booked']

        # Create the figure
        fig = go.Figure()

        # Add Booked rooms trace
        fig.add_trace(go.Bar(
            x=booked_rooms['Room Number'],
            y=[1] * len(booked_rooms),
            name='Booked',
            marker_color='#FF6347',
            text='Booked',
            textposition='auto'
        ))

        # Add Available rooms trace
        fig.add_trace(go.Bar(
            x=available_rooms['Room Number'],
            y=[1] * len(available_rooms),
            name='Available',
            marker_color='#87CEEB',
            text='Available',
            textposition='auto'
        ))

        # Update layout
        fig.update_layout(
            title='🏨 General Room Status (Properly Ordered)',
            barmode='group',
            xaxis_title="Room Number",
            yaxis_title="",
            xaxis={'categoryorder': 'array', 'categoryarray': general_data['Room Number'].tolist()},
            showlegend=True
        )

        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Error fetching general room details: {e}")
        logging.error(f"Error in general_room_details: {e}")


def revenue_dashboard():
    # Create navigation tabs with improved styling
    st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            border-radius: 4px 4px 0 0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #6a0572;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Today's Revenue", "This Week's Revenue", "Monthly Revenue"])

    # Fetch data for all time periods at once
    today = datetime.now().strftime('%Y-%m-%d')
    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
    month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')

    # Today's Revenue Tab - Web Graph + Bubble Chart
    with tab1:
        st.header("💰 Today's Revenue Dashboard", divider='rainbow')

        # Fetch hourly data for today
        today_data = fetch_data(
            f"SELECT HOUR(bill_date) AS hour, SUM(total_amount) AS amount "
            f"FROM bill_details WHERE DATE(bill_date) = '{today}' "
            f"GROUP BY hour ORDER BY hour",
            "bill_details",
            columns=["hour", "amount"]
        )

        # Display KPI - convert to float right after summing
        today_total = float(today_data['amount'].sum()) if not today_data.empty else 0.0

        # Create a 3-column layout for KPIs
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("Total Revenue Today", f"₹{today_total:,.2f}")
        with kpi2:
            current_hour = datetime.now().hour
            current_hour_rev = float(today_data.loc[today_data['hour'] == current_hour, 'amount'].iloc[
                                         0]) if not today_data.empty and current_hour in today_data[
                'hour'].values else 0.0
            st.metric(f"Hour {current_hour} Revenue", f"₹{current_hour_rev:,.2f}")
        with kpi3:
            avg_hourly = float(today_data['amount'].mean()) if not today_data.empty else 0.0
            st.metric("Avg Hourly Revenue", f"₹{avg_hourly:,.2f}")

        if not today_data.empty:
            # Convert and prepare data
            today_data['amount_float'] = today_data['amount'].astype(float)
            today_data['hour_12'] = today_data['hour'].apply(
                lambda x: f"{x % 12 if x % 12 != 0 else 12}{'AM' if x < 12 else 'PM'}")

            # Create a 2-column layout for main visualizations
            col1, col2 = st.columns([1, 1])

            with col1:
                # Web Graph (Radar Chart) for today's revenue distribution
                fig_web = go.Figure()

                fig_web.add_trace(go.Scatterpolar(
                    r=today_data['amount_float'],
                    theta=today_data['hour_12'],
                    fill='toself',
                    fillcolor='rgba(106,5,114,0.3)',
                    line=dict(color='#6a0572', width=3),
                    marker=dict(
                        size=10,
                        color=today_data['amount_float'],
                        colorscale='Rainbow',
                        showscale=True,
                        line=dict(color='black', width=1)
                    ),
                    name='Hourly Revenue',
                    hovertemplate='<b>%{theta}</b><br>Revenue: ₹%{r:,.2f}<extra></extra>'
                ))

                fig_web.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, today_data['amount_float'].max() * 1.2],
                            tickfont=dict(size=10)
                        ),
                        angularaxis=dict(
                            direction='clockwise',
                            rotation=90
                        )
                    ),
                    title='<b>Revenue Web</b> - Hourly Distribution',
                    height=400,
                    margin=dict(l=50, r=50, t=50, b=50),
                    paper_bgcolor='rgba(245,245,245,1)'
                )
                st.plotly_chart(fig_web, use_container_width=True)

            with col2:
                # Bubble Chart with rainbow colors
                fig_bubble = go.Figure()

                fig_bubble.add_trace(go.Scatter(
                    x=today_data['hour'],
                    y=today_data['amount_float'],
                    mode='markers',
                    marker=dict(
                        size=today_data['amount_float'] * 0.05 + 20,  # Scale bubble sizes
                        color=today_data['amount_float'],
                        colorscale='Rainbow',
                        showscale=True,
                        opacity=0.8,
                        line=dict(width=1, color='DarkSlateGrey')
                    ),
                    text=today_data['hour_12'],
                    hovertemplate='<b>%{text}</b><br>Revenue: ₹%{y:,.2f}<extra></extra>',
                    name='Revenue Bubbles'
                ))

                fig_bubble.update_layout(
                    title='<b>Revenue Bubbles</b> - Hourly Performance',
                    xaxis=dict(
                        title='Hour of Day',
                        tickvals=today_data['hour'],
                        ticktext=today_data['hour_12']
                    ),
                    yaxis=dict(title='Revenue (₹)'),
                    height=400,
                    plot_bgcolor='rgba(245,245,245,1)',
                    paper_bgcolor='rgba(245,245,245,1)'
                )
                st.plotly_chart(fig_bubble, use_container_width=True)

            # Additional visualizations in full width
            st.subheader("Hourly Revenue Trends", divider='gray')

            # Create a 2-column layout for trend charts
            trend_col1, trend_col2 = st.columns([1, 1])

            with trend_col1:
                # Line chart with area fill
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(
                    x=today_data['hour'],
                    y=today_data['amount_float'],
                    fill='tozeroy',
                    mode='lines+markers',
                    line=dict(color='#6A0572', width=3),
                    marker=dict(size=10, color='#AB83A1'),
                    name='Revenue Flow',
                    hovertemplate='<b>Hour %{x}</b><br>Revenue: ₹%{y:,.2f}<extra></extra>'
                ))
                fig_line.update_layout(
                    title='Hourly Revenue Trend',
                    xaxis_title='Hour of Day',
                    yaxis_title='Revenue (₹)',
                    height=350,
                    plot_bgcolor='rgba(245,245,245,1)'
                )
                st.plotly_chart(fig_line, use_container_width=True)

            with trend_col2:
                # Bar chart with gradient colors
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    x=today_data['hour_12'],
                    y=today_data['amount_float'],
                    marker=dict(
                        color=today_data['amount_float'],
                        colorscale='Rainbow',
                        line=dict(color='black', width=1)
                    ),
                    hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:,.2f}<extra></extra>'
                ))
                fig_bar.update_layout(
                    title='Hourly Revenue Bars',
                    xaxis_title='Time',
                    yaxis_title='Revenue (₹)',
                    height=350,
                    plot_bgcolor='rgba(245,245,245,1)'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("No revenue data available for today.")

    # Weekly Revenue Tab - Sunburst + Stacked Area Chart (unchanged but better formatted)
    with tab2:
        st.header("📈 Weekly Revenue Dashboard", divider='rainbow')

        # Fetch daily data for current week
        week_data = fetch_data(
            f"SELECT DATE(bill_date) AS day, SUM(total_amount) AS amount "
            f"FROM bill_details WHERE DATE(bill_date) >= '{week_start}' "
            f"GROUP BY day ORDER BY day",
            "bill_details",
            columns=["day", "amount"]
        )

        # Display KPI
        week_total = week_data['amount'].sum() if not week_data.empty else 0

        # Create a 3-column layout for KPIs
        wk_col1, wk_col2, wk_col3 = st.columns(3)
        with wk_col1:
            st.metric("Total Revenue This Week", f"₹{week_total:,.2f}")
        with wk_col2:
            avg_daily = float(week_data['amount'].mean()) if not week_data.empty else 0.0
            st.metric("Avg Daily Revenue", f"₹{avg_daily:,.2f}")
        with wk_col3:
            best_day = week_data.loc[week_data['amount'].idxmax()] if not week_data.empty else None
            if best_day is not None:
                best_day_name = pd.to_datetime(best_day['day']).strftime('%A')
                st.metric("Best Day", f"{best_day_name} - ₹{best_day['amount']:,.2f}")

        if not week_data.empty:
            # Convert day column to datetime if it's not already
            week_data['day'] = pd.to_datetime(week_data['day'])
            week_data['day_name'] = week_data['day'].dt.day_name()
            week_data['week'] = 'Current Week'

            # Create a 2-column layout for main charts
            wk_chart1, wk_chart2 = st.columns([1, 1])

            with wk_chart1:
                # Sunburst chart (unchanged)
                fig_sunburst = go.Figure(go.Sunburst(
                    labels=week_data['day_name'] + "<br>₹" + week_data['amount'].round(2).astype(str),
                    parents=week_data['week'],
                    values=week_data['amount'],
                    marker=dict(
                        colors=px.colors.qualitative.Pastel,
                        line=dict(width=2, color='white')
                    ),
                    branchvalues="total",
                    hoverinfo="label+value",
                    textinfo="label"
                ))
                fig_sunburst.update_layout(
                    title="Revenue Distribution by Weekday",
                    margin=dict(t=30, l=0, r=0, b=0),
                    height=400
                )
                st.plotly_chart(fig_sunburst, use_container_width=True)

            with wk_chart2:
                # Stacked area chart for weekly trend (unchanged)
                fig_area = go.Figure()
                fig_area.add_trace(go.Scatter(
                    x=week_data['day'],
                    y=week_data['amount'],
                    stackgroup='one',
                    mode='lines',
                    line=dict(width=0.5, color='#FF9AA2'),
                    fillcolor='rgba(255,154,162,0.6)',
                    name='Revenue'
                ))
                fig_area.add_trace(go.Scatter(
                    x=week_data['day'],
                    y=week_data['amount'].cumsum(),
                    mode='lines+markers',
                    line=dict(width=3, color='#FF0000'),
                    marker=dict(size=10, color='#FF0000'),
                    name='Cumulative Revenue'
                ))
                fig_area.update_layout(
                    title='Weekly Revenue Breakdown',
                    xaxis_title='Day',
                    yaxis_title='Revenue (₹)',
                    hovermode='x unified',
                    height=400
                )
                st.plotly_chart(fig_area, use_container_width=True)
        else:
            st.warning("No revenue data available for this week.")

    # Monthly Revenue Tab - Treemap + Waterfall Chart (unchanged but better formatted)
    with tab3:
        st.header("📊 Monthly Revenue Dashboard", divider='rainbow')

        # Fetch monthly data
        monthly_data = fetch_data(
            "SELECT DATE_FORMAT(bill_date, '%Y-%m') AS month, SUM(total_amount) AS amount "
            "FROM bill_details GROUP BY month ORDER BY month",
            "bill_details",
            columns=["month", "amount"]
        )

        # Display KPI with animated counter
        current_month = datetime.now().strftime('%Y-%m')
        month_total = monthly_data.loc[monthly_data['month'] == current_month, 'amount'].iloc[
            0] if not monthly_data.empty else 0

        # Create a 3-column layout for KPIs
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric(f"Current Month Revenue", f"₹{month_total:,.2f}",
                      help="Revenue for current month")
        with m_col2:
            avg_revenue = float(monthly_data['amount'].mean()) if not monthly_data.empty else 0.0
            st.metric("Monthly Average", f"₹{avg_revenue:,.2f}",
                      delta=f"₹{float(month_total) - avg_revenue:,.2f} vs average",
                      help="Comparison with historical average")
        with m_col3:
            best_month = monthly_data.loc[monthly_data['amount'].idxmax()] if not monthly_data.empty else None
            if best_month is not None:
                st.metric("Best Month", f"{best_month['month']} - ₹{best_month['amount']:,.2f}",
                          help="Highest revenue month in history")

        if not monthly_data.empty:
            # Create a 2-column layout for main charts
            m_chart1, m_chart2 = st.columns([2, 1])

            with m_chart1:
                # Interactive Calendar Heatmap (unchanged)
                monthly_data['date'] = pd.to_datetime(monthly_data['month'] + '-01')
                monthly_data['year'] = monthly_data['date'].dt.year
                monthly_data['month_name'] = monthly_data['date'].dt.strftime('%b')

                fig_heatmap = px.imshow(
                    monthly_data.pivot(index='year', columns='month_name', values='amount'),
                    labels=dict(x="Month", y="Year", color="Revenue"),
                    color_continuous_scale='Viridis',
                    aspect="auto"
                )
                fig_heatmap.update_layout(
                    title="<b>Annual Revenue Heatmap</b>",
                    xaxis_title="Month",
                    yaxis_title="Year",
                    height=500,
                    hovermode="closest",
                    margin=dict(l=20, r=20, t=60, b=20)
                )
                fig_heatmap.update_traces(
                    hovertemplate="<b>%{y} %{x}</b><br>Revenue: ₹%{z:,.2f}<extra></extra>"
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)

            with m_chart2:
                # Polar Area Chart (unchanged)
                monthly_data['angle'] = 360 / len(monthly_data)
                monthly_data['radius'] = monthly_data['amount'] / monthly_data['amount'].max()

                fig_polar = px.bar_polar(
                    monthly_data,
                    r="radius",
                    theta="month",
                    color="amount",
                    template="plotly_dark",
                    color_continuous_scale=px.colors.cyclical.Twilight,
                    hover_name="month",
                    hover_data={"amount": ":,.2f", "radius": False}
                )
                fig_polar.update_layout(
                    title="<b>Monthly Distribution</b>",
                    polar=dict(
                        radialaxis=dict(visible=False),
                        angularaxis=dict(direction="clockwise")
                    ),
                    height=500,
                    showlegend=False
                )
                fig_polar.update_traces(
                    hovertemplate="<b>%{hovertext}</b><br>Revenue: ₹%{customdata[0]:,.2f}<extra></extra>"
                )
                st.plotly_chart(fig_polar, use_container_width=True)

            # Animated Bar Race Chart (unchanged)
            st.subheader("Revenue Growth Over Time")
            monthly_data_sorted = monthly_data.sort_values('date')
            monthly_data_sorted['month_name'] = monthly_data_sorted['date'].dt.strftime('%b')
            monthly_data_sorted['cumulative'] = monthly_data_sorted['amount'].cumsum()

            fig_race = px.bar(
                monthly_data_sorted,
                x='month_name',
                y='amount',
                color='amount',
                animation_frame='year',
                color_continuous_scale='Rainbow',
                range_y=[0, float(monthly_data['amount'].max()) * 1.1],
                category_orders={"month_name": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}
            )

            fig_race.update_layout(
                title="<b>Monthly Revenue Race</b>",
                xaxis_title="Month",
                yaxis_title="Revenue (₹)",
                height=500,
                transition={'duration': 1000},
                updatemenus=[dict(
                    type="buttons",
                    buttons=[dict(label="Play",
                                  method="animate",
                                  args=[None, {"frame": {"duration": 500, "redraw": True}}])]
                )]
            )
            fig_race.update_traces(
                hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.2f}<extra></extra>"
            )
            st.plotly_chart(fig_race, use_container_width=True)

            # 3D Surface Plot with Time Dimension (unchanged)
            st.subheader("Revenue Landscape")
            years = monthly_data['year'].nunique()
            months = 12

            if years >= 2:
                z_data = monthly_data.pivot(index='year', columns='month_name', values='amount').values

                fig_3d = go.Figure(go.Surface(
                    z=z_data,
                    colorscale='Plasma',
                    showscale=True,
                    contours={
                        "z": {"show": True, "usecolormap": True, "highlightcolor": "limegreen", "project_z": True}
                    }
                ))
                fig_3d.update_layout(
                    title="<b>Revenue Landscape</b>",
                    scene=dict(
                        xaxis=dict(title='Month', tickvals=list(range(12)),
                                   ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
                        yaxis=dict(title='Year'),
                        zaxis=dict(title='Revenue (₹)'),
                        camera=dict(
                            eye=dict(x=1.5, y=1.5, z=0.5)
                        )
                    ),
                    height=600,
                    margin=dict(l=0, r=0, b=0, t=30)
                )
                st.plotly_chart(fig_3d, use_container_width=True)
            else:
                st.warning("Need at least 2 years of data to show 3D surface plot")

        else:
            st.warning("No monthly revenue data available.")


def doctor_patient_ratio_donut():
    """Enhanced doctor-patient ratio visualization with dynamic colors."""
    doctor_count = fetch_data("SELECT COUNT(*) FROM staff WHERE role = 'Doctor'", "staff").iloc[0, 0]
    patient_count = fetch_data("SELECT COUNT(*) FROM patients", "patients").iloc[0, 0]
    fig = px.pie(values=[doctor_count, patient_count],
                 names=["Doctors", "Patients"],
                 hole=0.6,
                 title="⚕️ Doctor-Patient Ratio",
                 color_discrete_sequence=["#4B0082", "#87CEEB"],
                 labels={"value": "Count", "names": "Category"})
    fig.update_traces(textposition='inside', textinfo='percent+label', pull=[0.1, 0])
    st.plotly_chart(fig)


def patient_department_distribution():
    """Enhanced department distribution visualization with interactive filtering."""
    department_data = fetch_data(
        "SELECT department, COUNT(*) as count FROM patients GROUP BY department",
        "patients",
        columns=["Department", "Count"]
    )
    if not department_data.empty:
        fig = px.bar(department_data, x="Department", y="Count",
                     title="🏥 Patients per Department",
                     color="Department",  # Use "Department" for multi-color bars
                     color_discrete_sequence=px.colors.qualitative.Plotly,  # Use of qualitative color scale
                     labels={"Count": "Number of Patients", "Department": "Department"})
        fig.update_layout(xaxis_tickangle=-45, hovermode="x unified")
        st.plotly_chart(fig)
    else:
        st.warning("No department data available.")


def room_allocation_chart():
    """Enhanced room allocation visualization with dynamic filtering."""
    room_data = fetch_data(
        "SELECT room_type, COUNT(*) as count FROM rooms WHERE availability = 'Booked' GROUP BY room_type",
        "rooms",
        columns=["Room Type", "Count"]
    )

    if not room_data.empty:
        # Using the exact rainbow colors in the correct order
        rainbow_colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#8B00FF"]

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=room_data["Room Type"],
                    values=room_data["Count"],
                    hole=0.3,  # Donut effect
                    marker=dict(colors=rainbow_colors[:len(room_data)]),  # Assigning colors dynamically
                    textinfo="percent+label",
                    pull=[0.05] * len(room_data)  # Slightly pulling out each slice for emphasis
                )
            ]
        )

        fig.update_layout(
            title="🏨 Room Allocation by Type",
            font=dict(family="Arial, sans-serif", size=14, color="black"),
            showlegend=True,
            legend=dict(title="Room Categories", orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("⚠ No room allocation data available.")


def patient_gender_ratio():
    """Enhanced gender ratio visualization with dynamic colors."""
    gender_data = fetch_data(
        "SELECT gender, COUNT(*) as count FROM patients GROUP BY gender",
        "patients",
        columns=["Gender", "Count"]
    )
    if not gender_data.empty:
        gender_map = {"M": "Male", "F": "Female"}
        gender_data["Gender"] = gender_data["Gender"].map(gender_map)
        fig = px.pie(gender_data, values="Count", names="Gender",
                     title="⚕️ Patient Gender Ratio",
                     color_discrete_sequence=["#3498db", "#e74c3c"],
                     labels={"Count": "Number of Patients", "Gender": "Gender"})
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig)
    else:
        st.warning("No gender data available.")


def room_utilization_heatmap():
    """Enhanced room utilization heatmap with better color scaling."""
    room_status_matrix = fetch_data(
        "SELECT room_type, availability, COUNT(*) as count FROM rooms GROUP BY room_type, availability",
        "rooms",
        columns=["Room Type", "Status", "Count"]
    ).pivot(index="Room Type", columns="Status", values="Count")
    fig = px.imshow(room_status_matrix,
                    labels=dict(x="Status", y="Room Type", color="Count"),
                    color_continuous_scale=["#FF0000", "#00FF00"],
                    title="🏨 Room Utilization Heatmap")
    fig.update_xaxes(side="top")
    st.plotly_chart(fig)


def discharge_patients_graph():
    """Display discharge patients over time in Today/Weekly/Monthly tabs with improved layout and visualizations."""
    try:
        # Create navigation tabs with improved styling
        st.markdown("""
        <style>
            .stTabs [data-baseweb="tab-list"] {
                gap: 10px;
            }
            .stTabs [data-baseweb="tab"] {
                padding: 8px 16px;
                border-radius: 4px 4px 0 0;
            }
            .stTabs [aria-selected="true"] {
                background-color: #6a0572;
                color: white;
            }
        </style>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Today's Discharges", "This Week's Discharges", "Monthly Discharges"])

        # Fetch data for all time periods at once
        today = datetime.now().strftime('%Y-%m-%d')
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
        month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')

        # Today's Discharges Tab - Web Graph + Bubble Chart
        with tab1:
            st.header("🏥 Today's Discharge Dashboard", divider='rainbow')

            # Fetch hourly data for today
            today_data = fetch_data(
                f"SELECT HOUR(discharge_date) AS hour, COUNT(*) AS count "
                f"FROM discharged_patients WHERE DATE(discharge_date) = '{today}' "
                f"GROUP BY hour ORDER BY hour",
                "discharged_patients",
                columns=["hour", "count"]
            )

            # Display KPI
            today_total = int(today_data['count'].sum()) if not today_data.empty else 0

            # Create a 3-column layout for KPIs
            kpi1, kpi2, kpi3 = st.columns(3)
            with kpi1:
                st.metric("Total Discharges Today", f"{today_total}")
            with kpi2:
                current_hour = datetime.now().hour
                current_hour_discharges = int(today_data.loc[today_data['hour'] == current_hour, 'count'].iloc[
                                                  0]) if not today_data.empty and current_hour in today_data[
                    'hour'].values else 0
                st.metric(f"Hour {current_hour} Discharges", f"{current_hour_discharges}")
            with kpi3:
                avg_hourly = float(today_data['count'].mean()) if not today_data.empty else 0.0
                st.metric("Avg Hourly Discharges", f"{avg_hourly:,.1f}")

            if not today_data.empty:
                # Convert and prepare data
                today_data['hour_12'] = today_data['hour'].apply(
                    lambda x: f"{x % 12 if x % 12 != 0 else 12}{'AM' if x < 12 else 'PM'}")

                # Create a 2-column layout for main visualizations
                col1, col2 = st.columns([1, 1])

                with col1:
                    # Web Graph (Radar Chart) for today's discharge distribution
                    fig_web = go.Figure()

                    fig_web.add_trace(go.Scatterpolar(
                        r=today_data['count'],
                        theta=today_data['hour_12'],
                        fill='toself',
                        fillcolor='rgba(106,5,114,0.3)',
                        line=dict(color='#6a0572', width=3),
                        marker=dict(
                            size=10,
                            color=today_data['count'],
                            colorscale='Rainbow',
                            showscale=True,
                            line=dict(color='black', width=1)
                        ),
                        name='Hourly Discharges',
                        hovertemplate='<b>%{theta}</b><br>Discharges: %{r:,}<extra></extra>'
                    ))

                    fig_web.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, today_data['count'].max() * 1.2],
                                tickfont=dict(size=10)
                            ),
                            angularaxis=dict(
                                direction='clockwise',
                                rotation=90
                            )
                        ),
                        title='<b>Discharge Web</b> - Hourly Distribution',
                        height=400,
                        margin=dict(l=50, r=50, t=50, b=50),
                        paper_bgcolor='rgba(245,245,245,1)'
                    )
                    st.plotly_chart(fig_web, use_container_width=True)

                with col2:
                    # Bubble Chart with rainbow colors
                    fig_bubble = go.Figure()

                    fig_bubble.add_trace(go.Scatter(
                        x=today_data['hour'],
                        y=today_data['count'],
                        mode='markers',
                        marker=dict(
                            size=today_data['count'] * 0.5 + 20,  # Scale bubble sizes
                            color=today_data['count'],
                            colorscale='Rainbow',
                            showscale=True,
                            opacity=0.8,
                            line=dict(width=1, color='DarkSlateGrey')
                        ),
                        text=today_data['hour_12'],
                        hovertemplate='<b>%{text}</b><br>Discharges: %{y:,}<extra></extra>',
                        name='Discharge Bubbles'
                    ))

                    fig_bubble.update_layout(
                        title='<b>Discharge Bubbles</b> - Hourly Performance',
                        xaxis=dict(
                            title='Hour of Day',
                            tickvals=today_data['hour'],
                            ticktext=today_data['hour_12']
                        ),
                        yaxis=dict(title='Number of Discharges'),
                        height=400,
                        plot_bgcolor='rgba(245,245,245,1)',
                        paper_bgcolor='rgba(245,245,245,1)'
                    )
                    st.plotly_chart(fig_bubble, use_container_width=True)

                # Additional visualizations in full width
                st.subheader("Hourly Discharge Trends", divider='gray')

                # Create a 2-column layout for trend charts
                trend_col1, trend_col2 = st.columns([1, 1])

                with trend_col1:
                    # Line chart with area fill
                    fig_line = go.Figure()
                    fig_line.add_trace(go.Scatter(
                        x=today_data['hour'],
                        y=today_data['count'],
                        fill='tozeroy',
                        mode='lines+markers',
                        line=dict(color='#6A0572', width=3),
                        marker=dict(size=10, color='#AB83A1'),
                        name='Discharge Flow',
                        hovertemplate='<b>Hour %{x}</b><br>Discharges: %{y:,}<extra></extra>'
                    ))
                    fig_line.update_layout(
                        title='Hourly Discharge Trend',
                        xaxis_title='Hour of Day',
                        yaxis_title='Number of Discharges',
                        height=350,
                        plot_bgcolor='rgba(245,245,245,1)'
                    )
                    st.plotly_chart(fig_line, use_container_width=True)

                with trend_col2:
                    # Bar chart with gradient colors
                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(
                        x=today_data['hour_12'],
                        y=today_data['count'],
                        marker=dict(
                            color=today_data['count'],
                            colorscale='Rainbow',
                            line=dict(color='black', width=1)
                        ),
                        hovertemplate='<b>%{x}</b><br>Discharges: %{y:,}<extra></extra>'
                    ))
                    fig_bar.update_layout(
                        title='Hourly Discharge Bars',
                        xaxis_title='Time',
                        yaxis_title='Number of Discharges',
                        height=350,
                        plot_bgcolor='rgba(245,245,245,1)'
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("No discharge data available for today.")

        # Weekly Discharges Tab - Sunburst + Stacked Area Chart (unchanged but better formatted)
        with tab2:
            st.header("📈 Weekly Discharge Dashboard", divider='rainbow')

            # Fetch daily data for current week
            week_data = fetch_data(
                f"SELECT DATE(discharge_date) AS day, COUNT(*) AS count "
                f"FROM discharged_patients WHERE DATE(discharge_date) >= '{week_start}' "
                f"GROUP BY day ORDER BY day",
                "discharged_patients",
                columns=["day", "count"]
            )

            # Display KPI
            week_total = week_data['count'].sum() if not week_data.empty else 0

            # Create a 3-column layout for KPIs
            wk_col1, wk_col2, wk_col3 = st.columns(3)
            with wk_col1:
                st.metric("Total Discharges This Week", f"{week_total:,}")
            with wk_col2:
                avg_daily = float(week_data['count'].mean()) if not week_data.empty else 0.0
                st.metric("Avg Daily Discharges", f"{avg_daily:,.1f}")
            with wk_col3:
                best_day = week_data.loc[week_data['count'].idxmax()] if not week_data.empty else None
                if best_day is not None:
                    best_day_name = pd.to_datetime(best_day['day']).strftime('%A')
                    st.metric("Best Day", f"{best_day_name} - {best_day['count']:,}")

            if not week_data.empty:
                # Convert day column to datetime if it's not already
                week_data['day'] = pd.to_datetime(week_data['day'])
                week_data['day_name'] = week_data['day'].dt.day_name()
                week_data['week'] = 'Current Week'

                # Create a 2-column layout for main charts
                wk_chart1, wk_chart2 = st.columns([1, 1])

                with wk_chart1:
                    # Sunburst chart (unchanged)
                    fig_sunburst = go.Figure(go.Sunburst(
                        labels=week_data['day_name'] + "<br>" + week_data['count'].astype(str),
                        parents=week_data['week'],
                        values=week_data['count'],
                        marker=dict(
                            colors=px.colors.qualitative.Pastel,
                            line=dict(width=2, color='white')
                        ),
                        branchvalues="total",
                        hoverinfo="label+value",
                        textinfo="label"
                    ))
                    fig_sunburst.update_layout(
                        title="Discharge Distribution by Weekday",
                        margin=dict(t=30, l=0, r=0, b=0),
                        height=400
                    )
                    st.plotly_chart(fig_sunburst, use_container_width=True)

                with wk_chart2:
                    # Stacked area chart for weekly trend (unchanged)
                    fig_area = go.Figure()
                    fig_area.add_trace(go.Scatter(
                        x=week_data['day'],
                        y=week_data['count'],
                        stackgroup='one',
                        mode='lines',
                        line=dict(width=0.5, color='#FF9AA2'),
                        fillcolor='rgba(255,154,162,0.6)',
                        name='Discharges'
                    ))
                    fig_area.add_trace(go.Scatter(
                        x=week_data['day'],
                        y=week_data['count'].cumsum(),
                        mode='lines+markers',
                        line=dict(width=3, color='#FF0000'),
                        marker=dict(size=10, color='#FF0000'),
                        name='Cumulative Discharges'
                    ))
                    fig_area.update_layout(
                        title='Weekly Discharge Breakdown',
                        xaxis_title='Day',
                        yaxis_title='Number of Discharges',
                        hovermode='x unified',
                        height=400
                    )
                    st.plotly_chart(fig_area, use_container_width=True)
            else:
                st.warning("No discharge data available for this week.")

        # Monthly Discharges Tab - Treemap + Waterfall Chart (unchanged but better formatted)
        with tab3:
            st.header("📊 Monthly Discharge Dashboard", divider='rainbow')

            # Fetch monthly data
            monthly_data = fetch_data(
                "SELECT DATE_FORMAT(discharge_date, '%Y-%m') AS month, COUNT(*) AS count "
                "FROM discharged_patients GROUP BY month ORDER BY month",
                "discharged_patients",
                columns=["month", "count"]
            )

            # Display KPI with animated counter
            current_month = datetime.now().strftime('%Y-%m')
            month_total = monthly_data.loc[monthly_data['month'] == current_month, 'count'].iloc[
                0] if not monthly_data.empty else 0

            # Create a 3-column layout for KPIs
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric(f"Current Month Discharges", f"{month_total:,}", help="Discharges for current month")
            with m_col2:
                avg_discharges = float(monthly_data['count'].mean()) if not monthly_data.empty else 0.0
                st.metric("Monthly Average", f"{avg_discharges:,.1f}",
                          delta=f"{float(month_total) - avg_discharges:,.1f} vs average",
                          help="Comparison with historical average")
            with m_col3:
                best_month = monthly_data.loc[monthly_data['count'].idxmax()] if not monthly_data.empty else None
                if best_month is not None:
                    st.metric("Best Month", f"{best_month['month']} - {best_month['count']:,}",
                              help="Highest discharge month in history")

            if not monthly_data.empty:
                # Create a 2-column layout for main charts
                m_chart1, m_chart2 = st.columns([2, 1])

                with m_chart1:
                    # Interactive Calendar Heatmap
                    monthly_data['date'] = pd.to_datetime(monthly_data['month'] + '-01')
                    monthly_data['year'] = monthly_data['date'].dt.year
                    monthly_data['month_name'] = monthly_data['date'].dt.strftime('%b')

                    fig_heatmap = px.imshow(
                        monthly_data.pivot(index='year', columns='month_name', values='count'),
                        labels=dict(x="Month", y="Year", color="Discharges"),
                        color_continuous_scale='Viridis',
                        aspect="auto"
                    )
                    fig_heatmap.update_layout(
                        title="<b>Annual Discharge Heatmap</b>",
                        xaxis_title="Month",
                        yaxis_title="Year",
                        height=500,
                        hovermode="closest",
                        margin=dict(l=20, r=20, t=60, b=20)
                    )
                    fig_heatmap.update_traces(
                        hovertemplate="<b>%{y} %{x}</b><br>Discharges: %{z:,}<extra></extra>"
                    )
                    st.plotly_chart(fig_heatmap, use_container_width=True)

                with m_chart2:
                    # Polar Area Chart
                    monthly_data['angle'] = 360 / len(monthly_data)
                    monthly_data['radius'] = monthly_data['count'] / monthly_data['count'].max()

                    fig_polar = px.bar_polar(
                        monthly_data,
                        r="radius",
                        theta="month",
                        color="count",
                        template="plotly_dark",
                        color_continuous_scale=px.colors.cyclical.Twilight,
                        hover_name="month",
                        hover_data={"count": ":,.0f", "radius": False}
                    )
                    fig_polar.update_layout(
                        title="<b>Monthly Distribution</b>",
                        polar=dict(
                            radialaxis=dict(visible=False),
                            angularaxis=dict(direction="clockwise")
                        ),
                        height=500,
                        showlegend=False
                    )
                    fig_polar.update_traces(
                        hovertemplate="<b>%{hovertext}</b><br>Discharges: %{customdata[0]:,}<extra></extra>"
                    )
                    st.plotly_chart(fig_polar, use_container_width=True)

                # Animated Bar Race Chart
                st.subheader("Discharge Growth Over Time")
                monthly_data_sorted = monthly_data.sort_values('date')
                monthly_data_sorted['month_name'] = monthly_data_sorted['date'].dt.strftime('%b')
                monthly_data_sorted['cumulative'] = monthly_data_sorted['count'].cumsum()

                fig_race = px.bar(
                    monthly_data_sorted,
                    x='month_name',
                    y='count',
                    color='count',
                    animation_frame='year',
                    color_continuous_scale='Rainbow',
                    range_y=[0, float(monthly_data['count'].max()) * 1.1],
                    category_orders={"month_name": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}
                )

                fig_race.update_layout(
                    title="<b>Monthly Discharge Race</b>",
                    xaxis_title="Month",
                    yaxis_title="Discharges",
                    height=500,
                    transition={'duration': 1000},
                    updatemenus=[dict(
                        type="buttons",
                        buttons=[dict(
                            label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 500, "redraw": True}}]
                        )]
                    )]
                )

                fig_race.update_traces(
                    hovertemplate="<b>%{x}</b><br>Discharges: %{y:,}<extra></extra>"
                )

                st.plotly_chart(fig_race, use_container_width=True)

                # 3D Surface Plot with Time Dimension
                st.subheader("Discharge Landscape")
                years = monthly_data['year'].nunique()
                months = 12

                if years >= 2:
                    z_data = monthly_data.pivot(index='year', columns='month_name', values='count').values

                    fig_3d = go.Figure(go.Surface(
                        z=z_data,
                        colorscale='Plasma',
                        showscale=True,
                        contours={
                            "z": {"show": True, "usecolormap": True, "highlightcolor": "limegreen", "project_z": True}
                        }
                    ))
                    fig_3d.update_layout(
                        title="<b>Discharge Landscape</b>",
                        scene=dict(
                            xaxis=dict(title='Month', tickvals=list(range(12))),
                            yaxis=dict(title='Year'),
                            zaxis=dict(title='Discharges'),
                            camera=dict(eye=dict(x=1.5, y=1.5, z=0.5))
                        ),
                        height=600,
                        margin=dict(l=0, r=0, b=0, t=30)
                    )
                    st.plotly_chart(fig_3d, use_container_width=True)
                else:
                    st.warning("Need at least 2 years of data to show 3D surface plot")

            else:
                st.warning("No monthly discharge data available.")


    except Exception as e:
        st.error(f"Error generating discharge patients graph: {e}")
        logging.error(f"Error in discharge_patients_graph: {e}")


def add_patients_graph():
    """Display patients added over time in Today/Weekly/Monthly tabs with improved layout and visualizations."""
    try:
        # Create navigation tabs with improved styling
        st.markdown("""
        <style>
            .stTabs [data-baseweb="tab-list"] {
                gap: 10px;
            }
            .stTabs [data-baseweb="tab"] {
                padding: 8px 16px;
                border-radius: 4px 4px 0 0;
            }
            .stTabs [aria-selected="true"] {
                background-color: #6a0572;
                color: white;
            }
        </style>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Today's Additions", "This Week's Additions", "Monthly Additions"])

        # Fetch data for all time periods at once
        today = datetime.now().strftime('%Y-%m-%d')
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
        month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')

        # Today's Additions Tab - Web Graph + Bubble Chart
        with tab1:
            st.header("🏥 Today's Patient Additions", divider='rainbow')

            # Fetch hourly data for today
            today_data = fetch_data(
                f"SELECT HOUR(date_of_consultancy) AS hour, COUNT(*) AS count "
                f"FROM patients WHERE DATE(date_of_consultancy) = '{today}' "
                f"GROUP BY hour ORDER BY hour",
                "patients",
                columns=["hour", "count"]
            )

            # Display KPI
            today_total = int(today_data['count'].sum()) if not today_data.empty else 0

            # Create a 3-column layout for KPIs
            kpi1, kpi2, kpi3 = st.columns(3)
            with kpi1:
                st.metric("Total Additions Today", f"{today_total:,}")
            with kpi2:
                current_hour = datetime.now().hour
                current_hour_additions = int(today_data.loc[today_data['hour'] == current_hour, 'count'].iloc[
                                                 0]) if not today_data.empty and current_hour in today_data[
                    'hour'].values else 0
                st.metric(f"Hour {current_hour} Additions", f"{current_hour_additions:,}")
            with kpi3:
                avg_hourly = float(today_data['count'].mean()) if not today_data.empty else 0.0
                st.metric("Avg Hourly Additions", f"{avg_hourly:,.1f}")

            if not today_data.empty:
                # Convert and prepare data
                today_data['hour_12'] = today_data['hour'].apply(
                    lambda x: f"{x % 12 if x % 12 != 0 else 12}{'AM' if x < 12 else 'PM'}")

                # Create a 2-column layout for main visualizations
                col1, col2 = st.columns([1, 1])

                with col1:
                    # Web Graph (Radar Chart) for today's additions distribution
                    fig_web = go.Figure()

                    fig_web.add_trace(go.Scatterpolar(
                        r=today_data['count'],
                        theta=today_data['hour_12'],
                        fill='toself',
                        fillcolor='rgba(106,5,114,0.3)',
                        line=dict(color='#6a0572', width=3),
                        marker=dict(
                            size=10,
                            color=today_data['count'],
                            colorscale='Rainbow',
                            showscale=True,
                            line=dict(color='black', width=1)
                        ),
                        name='Hourly Additions',
                        hovertemplate='<b>%{theta}</b><br>Additions: %{r:,}<extra></extra>'
                    ))

                    fig_web.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, today_data['count'].max() * 1.2],
                                tickfont=dict(size=10)
                            ),
                            angularaxis=dict(
                                direction='clockwise',
                                rotation=90
                            )
                        ),
                        title='<b>Additions Web</b> - Hourly Distribution',
                        height=400,
                        margin=dict(l=50, r=50, t=50, b=50),
                        paper_bgcolor='rgba(245,245,245,1)'
                    )
                    st.plotly_chart(fig_web, use_container_width=True)

                with col2:
                    # Bubble Chart with rainbow colors
                    fig_bubble = go.Figure()

                    fig_bubble.add_trace(go.Scatter(
                        x=today_data['hour'],
                        y=today_data['count'],
                        mode='markers',
                        marker=dict(
                            size=today_data['count'] * 0.5 + 20,  # Scale bubble sizes
                            color=today_data['count'],
                            colorscale='Rainbow',
                            showscale=True,
                            opacity=0.8,
                            line=dict(width=1, color='DarkSlateGrey')
                        ),
                        text=today_data['hour_12'],
                        hovertemplate='<b>%{text}</b><br>Additions: %{y:,}<extra></extra>',
                        name='Addition Bubbles'
                    ))

                    fig_bubble.update_layout(
                        title='<b>Addition Bubbles</b> - Hourly Performance',
                        xaxis=dict(
                            title='Hour of Day',
                            tickvals=today_data['hour'],
                            ticktext=today_data['hour_12']
                        ),
                        yaxis=dict(title='Number of Additions'),
                        height=400,
                        plot_bgcolor='rgba(245,245,245,1)',
                        paper_bgcolor='rgba(245,245,245,1)'
                    )
                    st.plotly_chart(fig_bubble, use_container_width=True)

                # Additional visualizations in full width
                st.subheader("Hourly Addition Trends", divider='gray')

                # Create a 2-column layout for trend charts
                trend_col1, trend_col2 = st.columns([1, 1])

                with trend_col1:
                    # Line chart with area fill
                    fig_line = go.Figure()
                    fig_line.add_trace(go.Scatter(
                        x=today_data['hour'],
                        y=today_data['count'],
                        fill='tozeroy',
                        mode='lines+markers',
                        line=dict(color='#6A0572', width=3),
                        marker=dict(size=10, color='#AB83A1'),
                        name='Addition Flow',
                        hovertemplate='<b>Hour %{x}</b><br>Additions: %{y:,}<extra></extra>'
                    ))
                    fig_line.update_layout(
                        title='Hourly Addition Trend',
                        xaxis_title='Hour of Day',
                        yaxis_title='Number of Additions',
                        height=350,
                        plot_bgcolor='rgba(245,245,245,1)'
                    )
                    st.plotly_chart(fig_line, use_container_width=True)

                with trend_col2:
                    # Bar chart with gradient colors
                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(
                        x=today_data['hour_12'],
                        y=today_data['count'],
                        marker=dict(
                            color=today_data['count'],
                            colorscale='Rainbow',
                            line=dict(color='black', width=1)
                        ),
                        hovertemplate='<b>%{x}</b><br>Additions: %{y:,}<extra></extra>'
                    ))
                    fig_bar.update_layout(
                        title='Hourly Addition Bars',
                        xaxis_title='Time',
                        yaxis_title='Number of Additions',
                        height=350,
                        plot_bgcolor='rgba(245,245,245,1)'
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("No addition data available for today.")

        # Weekly Additions Tab - Sunburst + Stacked Area Chart (unchanged but better formatted)
        with tab2:
            st.header("📈 Weekly Patient Additions", divider='rainbow')

            # Fetch daily data for current week
            week_data = fetch_data(
                f"SELECT DATE(date_of_consultancy) AS day, COUNT(*) AS count "
                f"FROM patients WHERE DATE(date_of_consultancy) >= '{week_start}' "
                f"GROUP BY day ORDER BY day",
                "patients",
                columns=["day", "count"]
            )

            # Display KPI
            week_total = week_data['count'].sum() if not week_data.empty else 0

            # Create a 3-column layout for KPIs
            wk_col1, wk_col2, wk_col3 = st.columns(3)
            with wk_col1:
                st.metric("Total Additions This Week", f"{week_total:,}")
            with wk_col2:
                avg_daily = float(week_data['count'].mean()) if not week_data.empty else 0.0
                st.metric("Avg Daily Additions", f"{avg_daily:,.1f}")
            with wk_col3:
                best_day = week_data.loc[week_data['count'].idxmax()] if not week_data.empty else None
                if best_day is not None:
                    best_day_name = pd.to_datetime(best_day['day']).strftime('%A')
                    st.metric("Best Day", f"{best_day_name} - {best_day['count']:,}")

            if not week_data.empty:
                # Convert day column to datetime
                week_data['day'] = pd.to_datetime(week_data['day'])
                week_data['day_name'] = week_data['day'].dt.day_name()
                week_data['week'] = 'Current Week'

                wk_chart1, wk_chart2 = st.columns([1, 1])

                with wk_chart1:
                    fig_sunburst = go.Figure(go.Sunburst(
                        labels=week_data['day_name'] + "<br>" + week_data['count'].astype(str),
                        parents=week_data['week'],
                        values=week_data['count'],
                        marker=dict(
                            colors=px.colors.qualitative.Pastel,
                            line=dict(width=2, color='white')
                        ),
                        branchvalues="total",
                        hoverinfo="label+value",
                        textinfo="label"
                    ))
                    fig_sunburst.update_layout(
                        title="Addition Distribution by Weekday",
                        margin=dict(t=30, l=0, r=0, b=0),
                        height=400
                    )
                    st.plotly_chart(fig_sunburst, use_container_width=True)

                with wk_chart2:
                    fig_area = go.Figure()
                    fig_area.add_trace(go.Scatter(
                        x=week_data['day'],
                        y=week_data['count'],
                        stackgroup='one',
                        mode='lines',
                        line=dict(width=0.5, color='#FF9AA2'),
                        fillcolor='rgba(255,154,162,0.6)',
                        name='Additions'
                    ))
                    fig_area.add_trace(go.Scatter(
                        x=week_data['day'],
                        y=week_data['count'].cumsum(),
                        mode='lines+markers',
                        line=dict(width=3, color='#FF0000'),
                        marker=dict(size=10, color='#FF0000'),
                        name='Cumulative Additions'
                    ))
                    fig_area.update_layout(
                        title='Weekly Addition Breakdown',
                        xaxis_title='Day',
                        yaxis_title='Number of Additions',
                        hovermode='x unified',
                        height=400
                    )
                    st.plotly_chart(fig_area, use_container_width=True)
            else:
                st.warning("No addition data available for this week.")

        with tab3:
            st.header("📊 Monthly Patient Additions", divider='rainbow')

            monthly_data = fetch_data(
                "SELECT DATE_FORMAT(date_of_consultancy, '%Y-%m') AS month, COUNT(*) AS count "
                "FROM patients GROUP BY month ORDER BY month",
                "patients",
                columns=["month", "count"]
            )

            current_month = datetime.now().strftime('%Y-%m')
            month_total = monthly_data.loc[monthly_data['month'] == current_month, 'count'].iloc[
                0] if not monthly_data.empty else 0

            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric("Current Month Additions", f"{month_total:,}", help="Additions for current month")
            with m_col2:
                avg_additions = float(monthly_data['count'].mean()) if not monthly_data.empty else 0.0
                st.metric("Monthly Average", f"{avg_additions:,.1f}",
                          delta=f"{float(month_total) - avg_additions:,.1f} vs average",
                          help="Comparison with historical average")
            with m_col3:
                best_month = monthly_data.loc[monthly_data['count'].idxmax()] if not monthly_data.empty else None
                if best_month is not None:
                    st.metric("Best Month", f"{best_month['month']} - {best_month['count']:,}",
                              help="Highest addition month in history")

            if not monthly_data.empty:
                m_chart1, m_chart2 = st.columns([2, 1])

                with m_chart1:
                    monthly_data['date'] = pd.to_datetime(monthly_data['month'] + '-01')
                    monthly_data['year'] = monthly_data['date'].dt.year
                    monthly_data['month_name'] = monthly_data['date'].dt.strftime('%b')

                    fig_heatmap = px.imshow(
                        monthly_data.pivot(index='year', columns='month_name', values='count'),
                        labels=dict(x="Month", y="Year", color="Additions"),
                        color_continuous_scale='Viridis',
                        aspect="auto"
                    )
                    fig_heatmap.update_layout(
                        title="<b>Annual Addition Heatmap</b>",
                        xaxis_title="Month",
                        yaxis_title="Year",
                        height=500,
                        hovermode="closest",
                        margin=dict(l=20, r=20, t=60, b=20)
                    )
                    fig_heatmap.update_traces(
                        hovertemplate="<b>%{y} %{x}</b><br>Additions: %{z:,}<extra></extra>"
                    )
                    st.plotly_chart(fig_heatmap, use_container_width=True)

                with m_chart2:
                    monthly_data['angle'] = 360 / len(monthly_data)
                    monthly_data['radius'] = monthly_data['count'] / monthly_data['count'].max()

                    fig_polar = px.bar_polar(
                        monthly_data,
                        r="radius",
                        theta="month",
                        color="count",
                        template="plotly_dark",
                        color_continuous_scale=px.colors.cyclical.Twilight,
                        hover_name="month",
                        hover_data={"count": ":,.0f", "radius": False}
                    )
                    fig_polar.update_layout(
                        title="<b>Monthly Distribution</b>",
                        polar=dict(
                            radialaxis=dict(visible=False),
                            angularaxis=dict(direction="clockwise")
                        ),
                        height=500,
                        showlegend=False
                    )
                    fig_polar.update_traces(
                        hovertemplate="<b>%{hovertext}</b><br>Additions: %{customdata[0]:,}<extra></extra>"
                    )
                    st.plotly_chart(fig_polar, use_container_width=True)

                # Animated Bar Race Chart
                st.subheader("Addition Growth Over Time")
                monthly_data_sorted = monthly_data.sort_values('date')
                monthly_data_sorted['month_name'] = monthly_data_sorted['date'].dt.strftime('%b')
                monthly_data_sorted['cumulative'] = monthly_data_sorted['count'].cumsum()

                fig_race = px.bar(
                    monthly_data_sorted,
                    x='month_name',
                    y='count',
                    color='count',
                    animation_frame='year',
                    color_continuous_scale='Rainbow',
                    range_y=[0, float(monthly_data['count'].max()) * 1.1],
                    category_orders={"month_name": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}
                )

                fig_race.update_layout(
                    title="<b>Monthly Addition Race</b>",
                    xaxis_title="Month",
                    yaxis_title="Additions",
                    height=500,
                    transition={'duration': 1000},
                    updatemenus=[dict(
                        type="buttons",
                        buttons=[dict(
                            label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 500, "redraw": True}}]
                        )]
                    )]
                )

                fig_race.update_traces(
                    hovertemplate="<b>%{x}</b><br>Additions: %{y:,}<extra></extra>"
                )

                st.plotly_chart(fig_race, use_container_width=True)

                # 3D Surface Plot
                st.subheader("Addition Landscape")
                years = monthly_data['year'].nunique()
                months = 12

                if years >= 2:
                    z_data = monthly_data.pivot(index='year', columns='month_name', values='count').values

                    fig_3d = go.Figure(go.Surface(
                        z=z_data,
                        colorscale='Plasma',
                        showscale=True,
                        contours={
                            "z": {"show": True, "usecolormap": True, "highlightcolor": "limegreen", "project_z": True}
                        }
                    ))
                    fig_3d.update_layout(
                        title="<b>Addition Landscape</b>",
                        scene=dict(
                            xaxis=dict(title='Month'),
                            yaxis=dict(title='Year'),
                            zaxis=dict(title='Additions')
                        ),
                        height=600,
                        margin=dict(l=0, r=0, b=0, t=30)
                    )
                    st.plotly_chart(fig_3d, use_container_width=True)
                else:
                    st.warning("Need at least 2 years of data to show 3D surface plot")
            else:
                st.warning("No monthly addition data available.")

    except Exception as e:
        st.error(f"Error generating patients added graph: {e}")
        logging.error(f"Error in add_patients_graph: {e}")


def staff_shift_sunburst():
    """Enhanced staff shift visualization with vibrant rainbow colors for roles and shifts."""
    try:
        # Fetch staff shift data
        staff_data = fetch_data(
            "SELECT role, shift, COUNT(*) as count FROM staff GROUP BY role, shift",
            "staff",
            columns=["Role", "Shift", "Count"]
        )

        # Check if staff_data is empty
        if staff_data.empty:
            st.warning("No staff shift data available to display.")
            return

        # Define an extended rainbow color palette
        rainbow_colors = [
            "#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#8B00FF",
            "#FF1493", "#00FFFF", "#7FFF00", "#8A2BE2", "#FF4500", "#DA70D6", "#00CED1",
            "#FFD700", "#8B008B", "#20B2AA", "#FF69B4", "#7CFC00", "#9932CC"
        ]

        # Create a color mapping for roles and shifts
        roles = staff_data['Role'].unique()
        shifts = staff_data['Shift'].unique()
        color_mapping = {}

        # Assign unique rainbow colors to each role and shift combination
        color_index = 0
        for role in roles:
            for shift in shifts:
                color_mapping[f"{role}_{shift}"] = rainbow_colors[color_index % len(rainbow_colors)]
                color_index += 1

        # Map colors to the data
        staff_data['color'] = staff_data.apply(lambda row: color_mapping[f"{row['Role']}_{row['Shift']}"], axis=1)

        # Create the sunburst chart with rainbow colors
        fig = px.sunburst(
            staff_data,
            path=['Role', 'Shift'],
            color='color',  # Use custom colors
            color_discrete_map=color_mapping,  # Map colors to roles and shifts
            title="🌌 Staff Shift Distribution",
            labels={"Count": "Number of Staff"}
        )
        fig.update_traces(textinfo="label+percent parent")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating staff shift sunburst chart: {e}")
        logging.error(f"Error in staff_shift_sunburst: {e}")


def patient_age_distribution():
    age_data = fetch_data(
        """
        SELECT 
            CASE 
                WHEN age BETWEEN 0 AND 18 THEN '0-18'
                WHEN age BETWEEN 19 AND 30 THEN '19-30'
                WHEN age BETWEEN 31 AND 50 THEN '31-50'
                ELSE '51+' 
            END AS age_group, 
            COUNT(*) as count 
        FROM patients 
        GROUP BY age_group
        """,
        "patients",
        columns=["Age Group", "Count"]
    )
    if not age_data.empty:
        fig = px.bar(age_data, x="Age Group", y="Count",
                     title="📊 Patient Age Distribution",
                     color="Age Group",  # Use "Age Group" for multi-color bars
                     color_discrete_sequence=px.colors.qualitative.Vivid,  # Use a vibrant color palette
                     labels={"Count": "Number of Patients", "Age Group": "Age Group"})
        fig.update_layout(coloraxis_showscale=False, hovermode="x unified")
        st.plotly_chart(fig)
    else:
        st.warning("No patient age data available.")


def live_inventory_gauge():
    st.markdown("### 📦 Inventory Status")
    low_stock_percent_data = fetch_data(
        "SELECT COUNT(*) * 100.0 / (SELECT COUNT(*) FROM inventory) as percent FROM inventory WHERE quantity < 10",
        "inventory"
    )
    low_stock_percent = low_stock_percent_data.iloc[0, 0] if not low_stock_percent_data.empty else 0
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=low_stock_percent,
        title="⚠️ Critical Inventory",
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#FF10F0"},
            'steps': [
                {'range': [0, 50], 'color': "#87CEEB"},
                {'range': [50, 100], 'color': "#4B0082"}
            ]
        }
    ))
    st.plotly_chart(fig)


def appointment_calendar():
    appointment_data = fetch_data(
        "SELECT DAY(appointment_date) as day, MONTH(appointment_date) as month, COUNT(*) as count FROM appointments GROUP BY day, month",
        "appointments",
        columns=["Day", "Month", "Count"]
    )

    if not appointment_data.empty:
        # Create a line graph with multi-colors for each month
        fig = px.line(appointment_data, x='Day', y='Count', color='Month',
                      title="📅 Daily Appointments Over Months",
                      color_discrete_sequence=px.colors.qualitative.Vivid,  # Use a vibrant color palette
                      labels={"Day": "Day of Month", "Count": "Number of Appointments", "Month": "Month"})

        # Update layout for better readability
        fig.update_layout(
            xaxis_title="Day of Month",
            yaxis_title="Number of Appointments",
            hovermode="x unified",
            legend_title="Month",
            xaxis=dict(tickmode='linear', tick0=1, dtick=1),  # Show every day on the x-axis
            yaxis=dict(tickmode='linear', tick0=0)  # Start y-axis from 0
        )
        st.plotly_chart(fig)
    else:
        st.warning("No appointment data available.")


def disease_word_cloud():
    disease_freq_data = fetch_data(
        "SELECT diseases, COUNT(*) as count FROM patients GROUP BY diseases",
        "patients",
        columns=["Disease", "Count"]
    )
    if not disease_freq_data.empty:
        # Create a bar chart with multi-colors for each disease
        fig = px.bar(disease_freq_data, x="Disease", y="Count",
                     title="🦠 Disease Frequency",
                     labels={"Disease": "Disease Name", "Count": "Number of Cases"},
                     color="Disease",  # Use "Disease" for multi-color bars
                     color_discrete_sequence=px.colors.qualitative.Vivid,  # Use a vibrant color palette
                     )
        fig.update_layout(
            xaxis_tickangle=-45,  # Rotate x-axis labels for better readability
            hovermode="x unified",  # Show unified hover information
            showlegend=False  # Hide legend since colors are self-explanatory
        )
        st.plotly_chart(fig)
    else:
        st.warning("No disease data available to display.")


def emergency_response_time():
    response_time_data = fetch_data(
        "SELECT AVG(TIMESTAMPDIFF(MINUTE, admission_date, NOW())) FROM emergency_patients",
        "emergency_patients"
    )
    response_time = response_time_data.iloc[0, 0] if not response_time_data.empty and response_time_data.iloc[
        0, 0] is not None else 0
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=response_time,
        title="🚨 Emergency Response Time (Minutes)",
        gauge={
            'axis': {'range': [0, 30]},
            'bar': {'color': "#FF0000"},
            'steps': [
                {'range': [0, 10], 'color': "#FFD700"},
                {'range': [10, 30], 'color': "#FF4500"}
            ]
        }
    ))
    st.plotly_chart(fig)


# ------------------ Advanced Search ------------------
def advanced_search():
    st.markdown('<div class="header-lightblue"><h3>🔍 Advanced Search</h3></div>', unsafe_allow_html=True)

    # Define search options based on user role
    if st.session_state['user_role'] == "Patient":
        search_options = ["Patients", "Appointments", "Discharged Patients", "Bills"]
    else:
        search_options = [
            "Patients", "Staff", "Rooms", "Bills", "Appointments", "Inventory",
            "Emergency Patients", "Ambulance Service", "Discharged Patients", "Doctors"
        ]

    # Add a search type dropdown with dynamic options
    search_type = st.selectbox("Select Search Type", search_options)

    # Add a search query input field
    search_query = st.text_input(f"Enter {search_type} Name, ID, or Keyword")

    # Add a search button
    if st.button(f"Search {search_type}"):
        if not search_query.strip():
            st.warning("Please enter a search query!")
            return

        # Initialize results as an empty DataFrame
        results = pd.DataFrame()

        # Define the base query for each search type
        if search_type == "Patients":
            query = f"""
                SELECT 
                    p.id AS 'Patient ID', 
                    p.name AS 'Patient Name', 
                    p.age AS 'Age', 
                    p.gender AS 'Gender', 
                    p.address AS 'Address', 
                    p.contact_no AS 'Contact No', 
                    p.dob AS 'Date of Birth', 
                    p.consultant_name AS 'Consultant', 
                    p.date_of_consultancy AS 'Consultancy Date', 
                    p.department AS 'Department', 
                    p.diseases AS 'Disease', 
                    p.fees AS 'Fees',
                    p.medicine AS 'Medicine',
                    p.quantity AS 'Quantity',
                    COALESCE(r.room_number, 'N/A') AS 'Room Number',
                    COALESCE(r.room_type, 'N/A') AS 'Room Type',
                    COALESCE(d.discharge_date, 'N/A') AS 'Discharge Date',
                    COALESCE(d.discharge_reason, 'N/A') AS 'Discharge Reason'
                FROM patients p
                LEFT JOIN rooms r ON p.id = r.patient_id
                LEFT JOIN discharged_patients d ON p.id = d.patient_id
                WHERE p.name LIKE '%{search_query}%' 
                    OR p.id = '{search_query}'
                    OR p.medicine LIKE '%{search_query}%'
                    OR p.quantity = '{search_query}'
            """
            # Define the columns for the query results
            columns = [
                "Patient ID", "Patient Name", "Age", "Gender", "Address", "Contact No",
                "Date of Birth", "Consultant", "Consultancy Date", "Department",
                "Disease", "Fees", "Medicine", "Quantity", "Room Number", "Room Type",
                "Discharge Date", "Discharge Reason"
            ]
            results = fetch_data(query, "patients", columns)

        elif search_type == "Doctors":
            query = f"""
                SELECT 
                    d.id AS 'Doctor ID', 
                    s.staff_name AS 'Doctor Name', 
                    d.department AS 'Department', 
                    s.shift AS 'Shift', 
                    d.role AS 'Role'
                FROM doctor d
                JOIN staff s ON d.staff_id = s.id
                WHERE s.staff_name LIKE '%{search_query}%' 
                    OR d.id = '{search_query}'
                    OR d.department LIKE '%{search_query}%'
            """

            columns = ["Doctor ID", "Doctor Name", "Department", "Shift", "Role"]
            results = fetch_data(query, "doctor", columns)

        elif search_type == "Appointments":
            query = f"""
                SELECT 
                    a.id AS 'Appointment ID', 
                    a.patient_name AS 'Patient Name', 
                    a.doctor_name AS 'Doctor Name', 
                    a.appointment_date AS 'Appointment Date', 
                    a.appointment_time AS 'Appointment Time'
                FROM appointments a
                WHERE a.patient_name LIKE '%{search_query}%' 
                    OR a.doctor_name LIKE '%{search_query}%'
                    OR a.id = '{search_query}'
            """

            columns = ["Appointment ID", "Patient Name", "Doctor Name", "Appointment Date", "Appointment Time"]
            results = fetch_data(query, "appointments", columns)

        elif search_type == "Bills":
            query = f"""
                SELECT 
                    b.bill_no AS 'Bill No', 
                    b.bill_date AS 'Bill Date', 
                    b.patient_id AS 'Patient ID', 
                    b.name AS 'Patient Name', 
                    b.contact_no AS 'Contact No', 
                    b.room_charges AS 'Room Charges', 
                    b.pathology_fees AS 'Pathology Fees', 
                    b.medicine_charges AS 'Medicine Charges', 
                    b.doctor_fees AS 'Doctor Fees', 
                    b.total_amount AS 'Total Amount', 
                    b.room_type AS 'Room Type'
                FROM bill_details b
                WHERE b.name LIKE '%{search_query}%' 
                    OR b.patient_id = '{search_query}'
                    OR b.bill_no = '{search_query}'
            """
            # Define the columns for the query results
            columns = [
                "Bill No", "Bill Date", "Patient ID", "Patient Name", "Contact No",
                "Room Charges", "Pathology Fees", "Medicine Charges", "Doctor Fees",
                "Total Amount", "Room Type"
            ]
            results = fetch_data(query, "bill_details", columns)

        elif search_type == "Discharged Patients":
            query = f"""
                SELECT 
                    d.patient_id AS 'Patient ID', 
                    d.patient_name AS 'Patient Name', 
                    d.room_number AS 'Room Number', 
                    d.room_type AS 'Room Type', 
                    d.discharge_date AS 'Discharge Date', 
                    d.discharge_time AS 'Discharge Time', 
                    d.discharge_reason AS 'Discharge Reason', 
                    d.is_icu AS 'ICU Room'
                FROM discharged_patients d
                WHERE d.patient_name LIKE '%{search_query}%' 
                    OR d.patient_id = '{search_query}'
                    OR d.room_number = '{search_query}'
            """
            # Define the columns for the query results
            columns = [
                "Patient ID", "Patient Name", "Room Number", "Room Type",
                "Discharge Date", "Discharge Time", "Discharge Reason", "ICU Room"
            ]
            results = fetch_data(query, "discharged_patients", columns)

        elif search_type == "Emergency Patients":
            query = f"""
                SELECT 
                    ep.id AS 'ID', 
                    ep.name AS 'Patient Name', 
                    ep.contact_no AS 'Contact No', 
                    ep.address AS 'Address', 
                    ep.blood_type AS 'Blood Type', 
                    r.room_number AS 'Room Number', 
                    s.staff_name AS 'Assigned Doctor', 
                    ep.admission_date AS 'Admission Date'
                FROM emergency_patients ep
                LEFT JOIN rooms r ON ep.room_id = r.id
                LEFT JOIN staff s ON ep.doctor_id = s.id
                WHERE ep.name LIKE '%{search_query}%' 
                    OR ep.id = '{search_query}'
                    OR ep.contact_no = '{search_query}'
            """
            # Define the columns for the query results
            columns = [
                "ID", "Patient Name", "Contact No", "Address", "Blood Type",
                "Room Number", "Assigned Doctor", "Admission Date"
            ]
            results = fetch_data(query, "emergency_patients", columns)

        elif search_type == "Ambulance Service":
            query = f"""
                SELECT 
                    a.id AS 'Service ID', 
                    a.patient_name AS 'Patient Name', 
                    a.address AS 'Address', 
                    a.blood_type AS 'Blood Type', 
                    am.ambulance_number AS 'Ambulance Number', 
                    a.dispatch_time AS 'Dispatch Time', 
                    a.return_time AS 'Return Time'
                FROM ambulance_service a
                LEFT JOIN ambulances am ON a.ambulance_id = am.id
                WHERE a.patient_name LIKE '%{search_query}%' 
                    OR a.id = '{search_query}'
                    OR am.ambulance_number = '{search_query}'
            """
            # Define the columns for the query results
            columns = [
                "Service ID", "Patient Name", "Address", "Blood Type",
                "Ambulance Number", "Dispatch Time", "Return Time"
            ]
            results = fetch_data(query, "ambulance_service", columns)

        elif search_type == "Rooms":
            query = f"""
                SELECT 
                    r.id AS 'Room ID', 
                    r.room_number AS 'Room Number', 
                    r.room_type AS 'Room Type', 
                    r.availability AS 'Status', 
                    r.patient_id AS 'Patient ID'
                FROM rooms r
                WHERE r.room_number LIKE '%{search_query}%' 
                    OR r.id = '{search_query}'
                    OR r.patient_id = '{search_query}'
            """
            # Define the columns for the query results
            columns = ["Room ID", "Room Number", "Room Type", "Status", "Patient ID"]
            results = fetch_data(query, "rooms", columns)

        elif search_type == "Inventory":
            query = f"""
                SELECT 
                    i.id AS 'Item ID', 
                    i.item_name AS 'Item Name', 
                    i.quantity AS 'Quantity', 
                    i.expiry_date AS 'Expiry Date'
                FROM inventory i
                WHERE i.item_name LIKE '%{search_query}%' 
                    OR i.id = '{search_query}'
            """
            # Define the columns for the query results
            columns = ["Item ID", "Item Name", "Quantity", "Expiry Date"]
            results = fetch_data(query, "inventory", columns)

        elif search_type == "Staff":
            query = f"""
                SELECT 
                    s.id AS 'Staff ID', 
                    s.staff_name AS 'Staff Name', 
                    s.role AS 'Role', 
                    s.shift AS 'Shift'
                FROM staff s
                WHERE s.staff_name LIKE '%{search_query}%' 
                    OR s.id = '{search_query}'
            """
            # Define the columns for the query results
            columns = ["Staff ID", "Staff Name", "Role", "Shift"]
            results = fetch_data(query, "staff", columns)

        # Display the search results
        if not results.empty:
            st.success(f"Found {len(results)} matching records!")
            st.dataframe(results)
        else:
            st.warning("No matching records found.")


# ------------------ Schedule and View Appointments ------------------
def schedule_appointment():
    st.markdown('<div class="header-lightblue"><h3>📅 Schedule Appointment</h3></div>', unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])

    # Create a radio button to choose between existing or new patient
    patient_option = st.radio("Patient Type", ["Select Existing Patient", "Enter New Patient"])

    if patient_option == "Select Existing Patient":
        # Fetch patient data with columns that exist in your table
        patient_data = fetch_data("SELECT id, name, contact_no, age, dob, address, gender FROM patients",
                                  "patients",
                                  columns=["id", "name", "contact_no", "age", "dob", "address", "gender"])

        if patient_data.empty:
            st.warning("No patients found. Please add patients first or choose 'Enter New Patient'.")
            return

        # Select patient from dropdown
        selected_patient = st.selectbox("Select Patient", patient_data["name"])

        # Get all details for selected patient
        patient_info = patient_data[patient_data["name"] == selected_patient].iloc[0]
        patient_name = patient_info["name"]
        contact_no = patient_info["contact_no"]
        age = patient_info["age"]
        dob = patient_info["dob"]
        address = patient_info["address"]
        gender = patient_info["gender"]

        # Show existing patient details (read-only)
        st.info(f"Patient Details: {patient_name}, Phone: {contact_no}, Age: {age}, Gender: {gender}, DOB: {dob}")
        address = st.text_area("Address", value=address, key="existing_patient_address")

    else:
        # Enter new patient details manually
        patient_name = st.text_input("Enter Patient Name*", key="new_patient_name")
        contact_no = st.text_input("Enter Phone Number*", key="new_patient_phone")
        age = st.number_input("Enter Age", min_value=0, max_value=120, value=None, key="new_patient_age")
        dob = st.date_input(
            "Date of Birth* (YYYY-MM-DD)",
            help="Enter date in YYYY-MM-DD format",
            min_value=datetime(1900, 1, 1).date(),
            max_value=datetime.today().date(),
            key="new_patient_dob")
        gender = st.selectbox("Gender", ["M", "F"], key="new_patient_gender")
        address = st.text_area("Address", key="new_patient_address")

        if not patient_name or not contact_no:
            st.warning("Please enter at least patient name and phone number")
            return

    # Fetch unique departments from the doctor table
    department_data = fetch_data("SELECT DISTINCT department FROM doctor", "doctor", columns=["Department"])

    if department_data.empty:
        st.warning("No departments found. Please add doctors first.")
        return

    # Select department
    department = st.selectbox("Select Department", department_data["Department"])

    # Fetch doctors and shifts in the selected department
    query = f"""
        SELECT s.staff_name AS doctor_name, s.shift
        FROM doctor d
        JOIN staff s ON d.staff_id = s.id
        WHERE d.department = '{department}'
    """
    doctor_data = fetch_data(query, "doctor", columns=["Doctor Name", "Shift"])

    if doctor_data.empty:
        st.warning(f"No doctors found in the {department} department.")
        return

    # Select doctor
    doctor_name = st.selectbox("Select Doctor", doctor_data["Doctor Name"])

    # Fetch the shift for the selected doctor
    shift = doctor_data[doctor_data["Doctor Name"] == doctor_name]["Shift"].iloc[0]

    # Input appointment date and time
    appointment_date = st.date_input("Appointment Date*")
    appointment_time = st.time_input("Appointment Time*")

    if st.button("Schedule Appointment"):
        try:
            # Get both connection and cursor
            con, cursor = get_db_cursor()
            if not cursor:
                st.error("Failed to connect to database")
                return

            # Insert appointment data - matching your appointments table structure
            insert_query = """
                INSERT INTO appointments 
                (patient_name, doctor_name, appointment_date, appointment_time)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                patient_name,
                doctor_name,
                appointment_date,
                appointment_time
            ))

            # Get the appointment ID
            appointment_id = cursor.lastrowid
            con.commit()

            # Prepare confirmation message
            confirmation_message = f"""
            <h3>Appointment Confirmation</h3>
            <p>Dear {patient_name},</p>
            <p>Your appointment has been scheduled successfully!</p>

            <p><strong>Appointment Details:</strong></p>
            <ul>
                <li>Appointment ID: {appointment_id}</li>
                <li>Doctor: {doctor_name}</li>
                <li>Department: {department}</li>
                <li>Date: {appointment_date}</li>
                <li>Time: {appointment_time}</li>
            </ul>

            <p>Please arrive 15 minutes before your scheduled time.</p>
            <p>Thank you,<br>Hospital Management</p>
            """

            st.success("Appointment scheduled successfully!")

        except Exception as e:
            st.error(f"Error scheduling appointment: {str(e)}")
        finally:
            # Ensure proper cleanup
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'con' in locals() and con and con.is_connected():
                con.close()


def view_appointments():
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])
    st.markdown('<div class="header-lightblue"><h3>📅 Appointment Records</h3></div>', unsafe_allow_html=True)

    # Fetch appointment data with all details
    query = """
        SELECT a.id AS 'Appointment ID', 
               a.patient_name AS 'Patient Name',
               p.contact_no AS 'Phone Number',
               p.age AS 'Age',
               p.dob AS 'Date of Birth',
               p.address AS 'Address',
               p.gender AS 'Gender',
               s.staff_name AS 'Doctor Name', 
               d.department AS 'Department', 
               s.shift AS 'Shift', 
               a.appointment_date AS 'Appointment Date', 
               a.appointment_time AS 'Appointment Time',
               a.created_at AS 'Created At'
        FROM appointments a
        LEFT JOIN patients p ON a.patient_name = p.name
        JOIN staff s ON a.doctor_name = s.staff_name
        JOIN doctor d ON s.id = d.staff_id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """
    columns = ["Appointment ID", "Patient Name", "Phone Number", "Age", "Date of Birth", "Address", "Gender",
               "Doctor Name", "Department", "Shift", "Appointment Date", "Appointment Time", "Created At"]
    df = fetch_data(query, "appointments", columns)

    if df.empty:
        st.info("No appointment records found.")
    else:
        # Display appointment records
        st.dataframe(df)

        # Add a download button for exporting the appointment data
        if st.button("📥 Download Appointment Records as CSV"):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="appointment_records.csv",
                mime="text/csv"
            )


# ------------------ Inventory Management Section ------------------
def manage_inventory():
    check_user_role(["Admin", "Doctor", "Nurse"])
    st.markdown('<div class="header-lightblue"><h3>💊 Inventory Management</h3></div>', unsafe_allow_html=True)

    item_name = st.text_input("Item Name").strip()
    quantity = st.number_input("Quantity", min_value=0)
    expiry_date = st.date_input("Expiry Date")

    if st.button("Add Item"):
        if not item_name:
            st.error("Item name cannot be empty!")
            return

        try:
            insert_data("""
                INSERT INTO inventory (item_name, quantity, expiry_date)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    quantity = quantity + VALUES(quantity),
                    expiry_date = VALUES(expiry_date)
            """, (item_name, quantity, expiry_date))

            st.success("Item successfully added/updated in inventory!")

        except Exception as e:
            st.error(f"Error occurred: {str(e)}")


def view_inventory():
    st.markdown('<div class="header-lightblue"><h3>💊 Inventory Records</h3></div>', unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Nurse", "Receptionist"])

    # Updated columns to include expiry_date
    columns = ["id", "item_name", "quantity", "expiry_date", "last_updated"]

    # Fetch data from the inventory table
    df = fetch_data("SELECT * FROM inventory", "inventory", columns)

    if df.empty:
        st.info("No inventory records found.")
    else:
        # Display the DataFrame
        st.dataframe(df)

        # Add a download button for exporting the inventory data
        if st.button("📥 Download Inventory as CSV"):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="inventory_records.csv",
                mime="text/csv"
            )


# ------------------ Staff Management Section ------------------
def manage_staff():
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])
    st.markdown('<div class="header-lightblue"><h3>🧑‍⚕️ Staff Management</h3></div>', unsafe_allow_html=True)
    staff_name = st.text_input("Staff Name")
    role = st.selectbox("Role", ["Doctor", "Nurse", "Receptionist", "Admin"])
    shift = st.selectbox("Shift", ["Morning", "Afternoon", "Night"])
    if st.button("Add Staff"):
        insert_data("INSERT INTO staff (staff_name, role, shift) VALUES (%s, %s, %s)",
                    (staff_name, role, shift))
        st.success("Staff Added Successfully!")


def view_staff():
    st.markdown('<div class="header-lightblue"><h3>🧑‍⚕️ View Staff Records</h3></div>', unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])
    # Define all 5 columns to match the query result
    columns = ["Staff ID", "Staff Name", "Role", "Shift", "Created At"]

    # Fetch data from the staff table
    df = fetch_data("SELECT * FROM staff", "staff", columns)

    if df.empty:
        st.info("No staff records found.")
    else:
        # Display the DataFrame
        st.dataframe(df)


# ------------------ Patient History Section -----------------
def view_patient_history():
    st.markdown('<div class="header-lightblue"><h3>📜 Patient History</h3></div>', unsafe_allow_html=True)
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])

    # Search Box for Filtering Patients
    search_query = st.text_input("Search by Patient Name, ID, Medicine, or Quantity", "")

    # Query the view directly (no need for joins in Python)
    query = "SELECT * FROM patient_history"

    # Define column labels matching the view
    columns = [
        "patient_id", "patient_name", "date_of_birth", "contact_no",
        "consultant_name", "gender", "department", "diseases", "fees",
        "medicine", "quantity", "bill_numbers", "bill_amounts",
        "room_numbers", "room_types", "discharge_dates",
        "discharge_reasons", "emergency_admission_dates", "emergency_blood_types",
        "assigned_doctors"
    ]

    df = fetch_data(query, "patient_history", columns)

    if df.empty:
        st.info("No patient history records found.")
    else:
        # Clean and format data
        df = df.fillna('N/A')

        # Convert date formats for display
        if 'date_of_birth' in df.columns:
            df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce').dt.strftime('%Y-%m-%d')

        for col in ['discharge_dates', 'emergency_admission_dates']:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: ', '.join(
                        [pd.to_datetime(date.strip(), errors='coerce').strftime('%Y-%m-%d') for date in x.split(',') if
                         date.strip()]
                    ) if x != 'N/A' else 'N/A'
                )

        # Apply search filters
        if search_query:
            search_query = search_query.lower()
            df = df[df.apply(
                lambda row: (
                        search_query in str(row['patient_id']).lower() or
                        search_query in str(row['patient_name']).lower() or
                        search_query in str(row['medicine']).lower() or
                        search_query in str(row['quantity']).lower() or
                        search_query in str(row['assigned_doctors']).lower()
                ), axis=1
            )]

        # Display formatted DataFrame
        st.dataframe(df.rename(columns=lambda x: x.replace('_', ' ').title()))

        # Export as CSV
        if st.button("📥 Download Patient History as CSV"):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="patient_history.csv",
                mime="text/csv"
            )


# ------------------ Ambulance Service Section ------------------
def ambulance_service_section():
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse", "Patient"])

    # Initialize 5 ambulances (run once)
    def initialize_ambulances():
        con = connection()
        cur = con.cursor()
        # Check if ambulances exist
        cur.execute("SELECT COUNT(*) FROM ambulances")
        if cur.fetchone()[0] == 0:
            # Create 5 ambulances
            for i in range(1, 6):
                cur.execute("INSERT INTO ambulances (ambulance_number, status) VALUES (%s, 'Available')",
                            (f"AMB-00{i}",))
            con.commit()

    initialize_ambulances()

    # Add tabs for Ambulance Service section
    ambulance_tabs = st.tabs(["Add Request & Dispatch", "View Status"])

    with ambulance_tabs[0]:
        st.markdown('<div class="header-lightblue"><h3>📝 Add Ambulance Request</h3></div>', unsafe_allow_html=True)
        patient_name = st.text_input("Patient Name*")
        address = st.text_area("Address*")
        blood_type = st.selectbox("Blood Type*", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])

        if st.button("Save Request"):
            if not patient_name or not address or not blood_type:
                st.error("Please fill all required fields (*)")
            else:
                # Save the request
                insert_data(
                    """
                    INSERT INTO ambulance_service (patient_name, address, blood_type)
                    VALUES (%s, %s, %s)
                    """,
                    (str(patient_name), str(address), str(blood_type))  # Convert to native Python types
                )
                st.success("Ambulance request saved successfully!")

        st.markdown('<div class="header-lightblue"><h3>🚨 Dispatch Ambulance</h3></div>', unsafe_allow_html=True)

        # Fetch saved requests without dispatched ambulances
        requests = fetch_data(
            "SELECT id, patient_name, address, blood_type FROM ambulance_service WHERE ambulance_id IS NULL",
            "ambulance_service",
            ["ID", "Patient Name", "Address", "Blood Type"]
        )

        if not requests.empty:
            request_options = {f"{row['Patient Name']} - {row['Address']}": row["ID"] for _, row in requests.iterrows()}
            selected_request = st.selectbox("Select Request to Dispatch", list(request_options.keys()))
            request_id = request_options.get(selected_request)

            if st.button("Dispatch Ambulance"):
                # Find an available ambulance
                available_ambulance = fetch_data(
                    "SELECT id, ambulance_number FROM ambulances WHERE status = 'Available' LIMIT 1",
                    "ambulances",
                    ["ID", "Ambulance Number"]
                )

                if not available_ambulance.empty:
                    ambulance_id = int(available_ambulance.iloc[0]["ID"])  # Convert to native Python int
                    ambulance_number = str(
                        available_ambulance.iloc[0]["Ambulance Number"])  # Convert to native Python str

                    # Update ambulance status and assign to request
                    insert_data(
                        "UPDATE ambulances SET status = 'On Service' WHERE id = %s",
                        (ambulance_id,)  # Pass as native Python int
                    )
                    insert_data(
                        "UPDATE ambulance_service SET ambulance_id = %s, dispatch_time = NOW() WHERE id = %s",
                        (ambulance_id, int(request_id))  # Convert request_id to native Python int
                    )
                    st.success(f"Ambulance {ambulance_number} dispatched successfully!")
                else:
                    st.warning("No ambulances available for dispatch!")
        else:
            st.info("No pending ambulance requests.")

    with ambulance_tabs[1]:
        st.markdown('<div class="header-lightblue"><h3>🚑 Ambulance Status</h3></div>', unsafe_allow_html=True)

        # Fetch all ambulances
        ambulances = fetch_data(
            "SELECT id, ambulance_number, status FROM ambulances",
            "ambulances",
            ["ID", "Ambulance Number", "Status"]
        )

        if not ambulances.empty:
            # Add countdown timer for ambulances on service
            for index, row in ambulances.iterrows():
                if row["Status"] == "On Service":
                    # Fetch dispatch time
                    dispatch_time = fetch_data(
                        f"SELECT dispatch_time FROM ambulance_service WHERE ambulance_id = {int(row['ID'])} ORDER BY dispatch_time DESC LIMIT 1",
                        # Convert to native Python int
                        "ambulance_service",
                        ["Dispatch Time"]
                    ).iloc[0, 0]

                    if dispatch_time:
                        # Calculate remaining time (10 minutes countdown)
                        remaining_time = 600 - (datetime.now() - dispatch_time).total_seconds()
                        if remaining_time > 0:
                            ambulances.at[
                                index, "Status"] = f"On Service (Returning in {int(remaining_time // 60)}:{int(remaining_time % 60):02d})"
                        else:
                            # Automatically mark ambulance as available after 10 minutes
                            insert_data(
                                "UPDATE ambulances SET status = 'Available' WHERE id = %s",
                                (int(row["ID"]),)  # Convert to native Python int
                            )
                            insert_data(
                                "UPDATE ambulance_service SET return_time = NOW() WHERE ambulance_id = %s AND return_time IS NULL",
                                (int(row["ID"]),)  # Convert to native Python int
                            )
                            ambulances.at[index, "Status"] = "Available"

            # Display ambulance status table
            st.dataframe(ambulances)
        else:
            st.info("No ambulances found.")

        # Display Ambulance Availability
        total_ambulances = 5
        available_ambulances = fetch_data(
            "SELECT COUNT(*) FROM ambulances WHERE status = 'Available'",
            "ambulances"
        ).iloc[0, 0]

        if available_ambulances == 0:
            st.error("No ambulances are available right now!")
        else:
            st.write(
                f"**Ambulance Availability:** {int(available_ambulances)} Available / {total_ambulances} Total")  # Convert to native Python int

        # View Ambulance Records
        st.markdown('<div class="header-lightblue"><h3>📋 View Ambulance Records</h3></div>', unsafe_allow_html=True)

        # Fetch all ambulance service records
        records = fetch_data(
            """
            SELECT 
                s.id AS 'Service ID',
                s.patient_name AS 'Patient Name',
                s.address AS 'Address',
                s.blood_type AS 'Blood Type',
                a.ambulance_number AS 'Ambulance Number',
                s.dispatch_time AS 'Dispatch Time',
                s.return_time AS 'Return Time'
            FROM 
                ambulance_service s
            LEFT JOIN 
                ambulances a ON s.ambulance_id = a.id
            """,
            "ambulance_service",
            ["Service ID", "Patient Name", "Address", "Blood Type", "Ambulance Number", "Dispatch Time", "Return Time"]
        )

        if records.empty:
            st.info("No ambulance service records found.")
        else:
            st.dataframe(records)


# ----------------Reports ------------------
def generate_pdf_report(data, title, filename):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add title to the PDF
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=title, ln=True, align="C")
        pdf.ln(10)  # Add some space after the title

        # Set font for the table
        pdf.set_font("Arial", size=10)

        # Calculate column widths dynamically based on content
        col_widths = [pdf.get_string_width(str(col)) + 10 for col in data.columns]

        # Add table headers
        for i, col in enumerate(data.columns):
            pdf.cell(col_widths[i], 10, txt=col, border=1, align="C")
        pdf.ln()

        # Add table rows
        for index, row in data.iterrows():
            for i, col in enumerate(data.columns):
                pdf.cell(col_widths[i], 10, txt=str(row[col]), border=1, align="C")
            pdf.ln()

        # Save the PDF to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_file.name)
        return temp_file.name
    except Exception as e:
        st.error(f"Error generating PDF report: {e}")
        return None


def download_report(data, title, filename):
    if not data.empty:
        pdf_file = generate_pdf_report(data, title, filename)
        if pdf_file:
            try:
                with open(pdf_file, "rb") as file:
                    st.download_button(
                        label="📥 Download Report",
                        data=file,
                        file_name=filename,
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Error downloading report: {e}")
            finally:
                # Clean up the temporary file
                import os
                os.unlink(pdf_file)
    else:
        st.warning("No data available to generate the report.")


def generate_reports():
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])
    st.markdown('<div class="header-lightblue"><h3>📄 Generate Reports</h3></div>', unsafe_allow_html=True)
    report_type = st.selectbox("Select Report Type", [
        "Patient History", "Billing", "Staff", "Inventory", "Appointments",
        "Emergency Patients", "Rooms", "Doctors"
    ])

    try:
        if report_type == "Patient History":
            # Include medicine and quantity in the patient history report
            data = fetch_data("SELECT * FROM patients", "patients")
            download_report(data, "Patient History Report", "patient_history_report.pdf")

        elif report_type == "Billing":
            data = fetch_data("SELECT * FROM bill_details", "bill_details")
            download_report(data, "Billing Report", "billing_report.pdf")

        elif report_type == "Staff":
            data = fetch_data("SELECT * FROM staff", "staff")
            download_report(data, "Staff Report", "staff_report.pdf")

        elif report_type == "Inventory":
            data = fetch_data("SELECT * FROM inventory", "inventory")
            download_report(data, "Inventory Report", "inventory_report.pdf")

        elif report_type == "Appointments":
            data = fetch_data("SELECT * FROM appointments", "appointments")
            download_report(data, "Appointments Report", "appointments_report.pdf")

        elif report_type == "Emergency Patients":
            data = fetch_data("SELECT * FROM emergency_patients", "emergency_patients")
            download_report(data, "Emergency Patients Report", "emergency_patients_report.pdf")

        elif report_type == "Rooms":
            data = fetch_data("SELECT * FROM rooms", "rooms")
            download_report(data, "Rooms Report", "rooms_report.pdf")

        elif report_type == "Doctors":
            data = fetch_data("SELECT * FROM doctor", "doctor")
            download_report(data, "Doctors Report", "doctors_report.pdf")
    except Exception as e:
        st.error(f"Error fetching data for report generation: {e}")


# ------------------ Export Data Section ------------------
def export_data():
    check_user_role(["Admin", "Doctor", "Receptionist", "Nurse"])
    try:
        st.markdown('<div class="header-lightblue"><h3>📤 Export Data</h3></div>', unsafe_allow_html=True)

        # Dropdown to select data type
        data_type = st.selectbox("Select Data to Export", [
            "Patients", "Rooms", "Bills", "Appointments", "Staff", "Inventory",
            "Emergency Patients", "Discharged Patients", "Doctors"
        ])

        # Button to trigger export
        if st.button("Export to Excel"):
            # Define the downloads folder
            downloads_folder = str(Path.home() / "Downloads")

            # Mapping of data types to SQL queries and table names
            query_mapping = {
                "Patients": ("SELECT * FROM patients", "patients"),
                "Rooms": ("SELECT * FROM rooms", "rooms"),
                "Bills": ("SELECT * FROM bill_details", "bill_details"),
                "Appointments": ("SELECT * FROM appointments", "appointments"),
                "Staff": ("SELECT * FROM staff", "staff"),
                "Inventory": ("SELECT * FROM inventory", "inventory"),
                "Emergency Patients": ("SELECT * FROM emergency_patients", "emergency_patients"),
                "Discharged Patients": ("SELECT * FROM discharged_patients", "discharged_patients"),
                "Doctors": ("SELECT * FROM doctor", "doctor")
            }

            # Check if the selected data type is valid
            if data_type in query_mapping:
                query, table_name = query_mapping[data_type]

                # Fetch data from the database
                data = fetch_data(query, table_name)

                # Define the file path for the Excel file
                file_path = os.path.join(downloads_folder, f"{table_name}.xlsx")

                # Check if data is empty
                if data.empty:
                    st.warning(f"No data found for {data_type}. Export canceled.")
                    logging.warning(f"No data found for {data_type} during export.")
                else:
                    # Export data to Excel
                    data.to_excel(file_path, index=False)
                    st.success(f"{data_type} data exported successfully to {file_path}!")
                    logging.info(f"{data_type} data exported successfully to {file_path}.")
            else:
                st.error("Invalid data type selected.")
                logging.error(f"Invalid data type selected: {data_type}")
    except Exception as e:
        st.error(f"Error exporting data: {e}")
        logging.error(f"Error exporting data: {e}")


# ------------------ Streamlit UI ------------------
if 'startup_done' not in st.session_state:
    st.session_state["startup_done"] = False

# Show startup animation only once when the application starts
if not st.session_state["startup_done"]:
    startup_animation()
    st.session_state["startup_done"] = True

st.title("\U0001F3E5 Hospital Management System")

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Show passcode screen if not verified
if "passcode_verified" not in st.session_state:
    passcode = st.text_input("Enter Passcode", type="password", key="passcode_input")
    if st.button("Submit Passcode"):
        if check_passcode(passcode):
            st.session_state["passcode_verified"] = True
            st.rerun()
        else:
            st.error("Incorrect Passcode!")
            logging.warning("Incorrect passcode entered.")
    st.stop()

# Navigation Tabs in Sidebar
if st.session_state.get('authenticated'):
    if st.session_state['user_role'] == "Admin":
        menu = [
            "Dashboard", "Chatbot", "Advanced Search", "Attendance Dashboard", "Doctor Section", "Manage Patients",
            "Emergency Unit", "Emergency Dashboard", "Room Info", "Billing", "Appointments", "Inventory",
            "Staff", "Patient History", "Ambulance Service", "Generate Reports", "Export Data", "Logout"
        ]
    elif st.session_state['user_role'] == "Doctor":
        menu = [
            "Dashboard", "Chatbot", "Advanced Search", "Attendance Dashboard", "Doctor Section", "Manage Patients",
            "Emergency Unit", "Emergency Dashboard", "Room Info", "Appointments", "Patient History", "Logout"
        ]
    elif st.session_state['user_role'] == "Receptionist":
        menu = [
            "Dashboard", "Chatbot", "Advanced Search", "Attendance Dashboard", "Doctor Section", "Emergency Unit",
            "Emergency Dashboard", "Appointments", "Billing", "Inventory", "Generate Reports", "Export Data", "Logout"
        ]
    elif st.session_state['user_role'] == "Patient":
        menu = [
            "Dashboard", "Chatbot", "Advanced Search", "Doctor Section", "Emergency Unit", "Patient History",
            "Appointments", "Logout"
        ]
    elif st.session_state['user_role'] == "Nurse":
        menu = [
            "Dashboard", "Chatbot", "Advanced Search", "Attendance Dashboard", "Doctor Section",
            "Manage Patients",
            "Emergency Unit", "Emergency Dashboard", "Room Info", "Appointments", "Inventory", "Patient History",
            "Generate Reports", "Export Data", "Logout"
        ]
else:
    menu = ["Login", "Register"]

# Initialize session state for active tab
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = menu[0]

# Sidebar layout
with st.sidebar:
    st.markdown("### Navigation")
    for tab in menu:
        if st.button(tab, key=tab):
            st.session_state["active_tab"] = tab

# ------------------Main content based on the active tab-------------
choice = st.session_state["active_tab"]

if choice == "Login":
    st.subheader("\U0001F512 User Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_user(username, password):
            st.rerun()  # Rerun the app to reflect the changes
        else:
            st.error("Invalid Credentials!")
            logging.warning(f"Failed login attempt for username: {username}")

elif choice == "Dashboard":
    access_control()
    show_dashboard()

elif choice == "Register":
    st.subheader("\U0001F4DD New User Registration")
    new_username = st.text_input("Create Username")
    new_password = st.text_input("Create Password", type="password")
    full_name = st.text_input("Full Name")
    user_role = st.selectbox("Role", ["Admin", "Doctor", "Patient", "Receptionist", "Nurse"])  # Added "Nurse"
    if st.button("Register"):
        register_user(new_username, new_password, full_name, user_role)

elif choice == "Advanced Search":
    access_control()
    advanced_search()

elif choice == "Attendance Dashboard":
    access_control()
    attendance_dashboard()

elif choice == "Manage Patients":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Doctor", "Nurse"]:
        st.warning("Access Denied! This feature is only available to Admin, Doctors, and Nurses.")
        st.stop()

    patient_tabs = st.tabs(["Add Patient", "View Patients", "Discharge Patient", "View Discharged Patients"])

    with patient_tabs[0]:
        add_patient()

    with patient_tabs[1]:
        view_patients()

    with patient_tabs[2]:
        discharge_patient()

    with patient_tabs[3]:
        view_discharged_patients()


elif choice == "Emergency Unit":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Doctor", "Receptionist", "Patient", "Nurse"]:  # Added "Nurse"
        st.warning("Access Denied! This feature is only available to Admin, Doctors, Receptionists, and Nurses.")
        st.stop()

    emergency_tabs = st.tabs([
        "Add Emergency Patient",
        "View Emergency Patients",
        "Discharge Emergency Patient",
        "View Discharged Emergency Patients"
    ])

    with emergency_tabs[0]:
        add_emergency_patient()

    with emergency_tabs[1]:
        view_emergency_patients()

    with emergency_tabs[2]:
        discharge_patient()

    with emergency_tabs[3]:
        view_discharged_patients()

elif choice == "Emergency Dashboard":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Doctor", "Receptionist", "Nurse"]:  # Added "Nurse"
        st.warning("Access Denied! This feature is only available to Admin, Doctors, Receptionists, and Nurses.")
        st.stop()
    emergency_dashboard()

elif choice == "Room Info":
    access_control()
    # Restrict access to Admin, Doctor, and Nurse only
    if st.session_state.get('user_role') not in ["Admin", "Doctor", "Nurse"]:
        st.warning("🚫 Access Denied! This feature is only available to Admin, Doctors, and Nurses.")
        st.stop()

    room_tabs = st.tabs(["🏨 Allocate Room", "📋 View Rooms", "🚪 Discharge Patient", "📜 View Discharged Patients"])

    with room_tabs[0]:
        allocate_room()

    with room_tabs[1]:
        view_rooms()

    with room_tabs[2]:
        discharge_patient()

    with room_tabs[3]:
        view_discharged_patients()

elif choice == "Billing":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Receptionist"]:
        st.warning("Access Denied! This feature is only available to Admin, Receptionists, and Patients.")
        st.stop()
    billing_tabs = st.tabs(["Add Bill", "View Bills"])
    with billing_tabs[0]:
        add_bill()
    with billing_tabs[1]:
        view_bills()

elif choice == "Appointments":
    access_control()
    # Only Admin, Doctor, Receptionist, Nurse, and Patient can access this feature
    if st.session_state['user_role'] not in ["Admin", "Doctor", "Receptionist", "Nurse", "Patient"]:
        st.warning(
            "Access Denied! This feature is only available to Admin, Doctors, Receptionists, Nurses, and Patients."
        )
        st.stop()

    appointment_tabs = st.tabs(["Schedule Appointment", "View Appointments"])

    with appointment_tabs[0]:
        schedule_appointment()

    with appointment_tabs[1]:
        view_appointments()

elif choice == "Inventory":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Nurse", "Receptionist"]:
        st.warning("Access Denied! This feature is only available to Admin, Nurses, and Receptionists.")
        st.stop()
    inventory_tabs = st.tabs(["Add Item", "View Inventory"])
    with inventory_tabs[0]:
        manage_inventory()
    with inventory_tabs[1]:
        view_inventory()

elif choice == "Staff":
    access_control()
    if st.session_state['user_role'] != "Admin":
        st.warning("Access Denied! This feature is only available to Admin.")
        st.stop()
    staff_tabs = st.tabs(["Add Staff", "View Staff"])
    with staff_tabs[0]:
        manage_staff()
    with staff_tabs[1]:
        view_staff()

elif choice == "Patient History":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Doctor", "Patient", "Nurse"]:  # Added "Nurse"
        st.warning("Access Denied! This feature is only available to Admin, Doctors, Patients, and Nurses.")
        st.stop()
    view_patient_history()

elif choice == "Ambulance Service":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Doctor", "Receptionist"]:
        st.warning("Access Denied! This feature is only available to Admin, Doctors, and Receptionists.")
        st.stop()
    ambulance_service_section()

elif choice == "Generate Reports":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Nurse", "Receptionist"]:
        st.warning("Access Denied! This feature is only available to Admin, Nurses, and Receptionists.")
        st.stop()
    generate_reports()

elif choice == "Export Data":
    access_control()
    if st.session_state['user_role'] not in ["Admin", "Nurse", "Receptionist"]:
        st.warning("Access Denied! This feature is only available to Admin, Nurses, and Receptionists.")
        st.stop()
    export_data()

elif choice == "Doctor Section":
    access_control()
    doctor_section()

elif choice == "Chatbot":
    access_control()
    chatbot_page()

elif choice == "Logout":
    if st.session_state.get('authenticated'):
        logout()
        st.session_state["startup_done"] = False  # Reset startup animation flag
        st.rerun()
    else:
        st.info("Login Session Terminated")
# ------------------- Display Message When Not Authenticated ------------------
if not st.session_state['authenticated']:
    st.info("Please login to access and use the Hospital Management System features.")




