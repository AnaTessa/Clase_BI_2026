import streamlit as st

def show_header(text_title: str):
    # Layout: logo + title side by side
    col1, col2 = st.columns([1, 6])
    
    with col1:
        st.image("A95628AB-88C8-4FAA-A86D-A877C52152F0.jpg", width=200)
        
    with col2:
        st.title(text_title)
        st.caption("📘 Developed for: *Business Intelligence (Graduate Level)*")
        st.caption("Instructor: Edgar Avalos-Gauna (2025), Universidad Panamericana")

show_header()
