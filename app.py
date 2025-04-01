import streamlit as st
import pandas as pd
import numpy as np
import re
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
from PIL import Image
import nltk
from nltk.tokenize import sent_tokenize
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Terms and Conditions Analyzer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .title {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    .risk-high {
        color: #ff4b4b;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffa500;
        font-weight: bold;
    }
    .risk-low {
        color: #00cc66;
        font-weight: bold;
    }
    .highlight {
        background-color: #f0f8ff;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #4e8cff;
    }
    .section-header {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .stButton button {
        background-color: #4e8cff;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton button:hover {
        background-color: #3a7be8;
    }
</style>
""", unsafe_allow_html=True)

# Define color scheme
PRIMARY_COLOR = "#4e8cff"
HIGH_RISK_COLOR = "#ff4b4b"
MEDIUM_RISK_COLOR = "#ffa500"
LOW_RISK_COLOR = "#00cc66"
BACKGROUND_COLOR = "#f7f9fc"

def main():
    # App header
    st.markdown("<h1 class='title'>Terms and Conditions Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("### Analyze privacy policies and terms from a cybersecurity perspective")
    
    # Sidebar for app navigation and info
    with st.sidebar:
        st.markdown("## How It Works")
        st.markdown("""
        This tool analyzes Terms and Conditions or Privacy Policies to identify potential cybersecurity risks.
        
        1. Input your document using one of the provided methods
        2. Click 'Analyze' to process the text
        3. Review the categorized results and risk scores
        
        The analysis focuses on key areas relevant to data security and privacy.
        """)
        
        st.markdown("## About")
        st.markdown("""
        This application helps users understand the cybersecurity implications in legal documents without having to read through lengthy terms and conditions.
        
        The risk assessment is based on pattern recognition and keyword analysis of common phrases in privacy policies.
        """)
    
    # Main application content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## Document Input")
        input_method = st.radio("Select input method:", ["URL", "Text", "File Upload"], horizontal=True)
        
        document_text = ""
        
        if input_method == "URL":
            url = st.text_input("Enter the URL of the Terms & Conditions or Privacy Policy:")
            if url:
                with st.spinner("Fetching document from URL..."):
                    try:
                        response = requests.get(url)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            document_text = soup.get_text()
                            st.success("Document successfully retrieved!")
                        else:
                            st.error(f"Failed to retrieve document. Status code: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error fetching URL: {str(e)}")
        
        elif input_method == "Text":
            document_text = st.text_area("Paste the Terms & Conditions or Privacy Policy text here:", height=250)
        
        elif input_method == "File Upload":
            uploaded_file = st.file_uploader("Upload a document file:", type=["pdf", "txt", "html", "docx"])
            if uploaded_file is not None:
                with st.spinner("Processing uploaded file..."):
                    try:
                        # Get the file extension
                        file_type = uploaded_file.name.split('.')[-1].lower()
                        
                        if file_type == 'pdf':
                            # Process PDF file
                            pdf_reader = PyPDF2.PdfReader(uploaded_file)
                            document_text = ""
                            for page_num in range(len(pdf_reader.pages)):
                                document_text += pdf_reader.pages[page_num].extract_text()
                        
                        elif file_type == 'txt':
                            # Process text file
                            document_text = uploaded_file.read().decode('utf-8')
                        
                        elif file_type == 'html':
                            # Process HTML file
                            html_content = uploaded_file.read().decode('utf-8')
                            soup = BeautifulSoup(html_content, 'html.parser')
                            document_text = soup.get_text()
                        
                        elif file_type == 'docx':
                            st.warning("DOCX format support is limited. For best results, consider converting to PDF or TXT.")
                            # Note: Full DOCX support would require python-docx library
                            document_text = "DOCX format detected. Limited processing available."
                        
                        st.success(f"File processed successfully! ({len(document_text)} characters)")
                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")
    
    with col2:
        st.markdown("## Quick Tips")
        st.info("""
        - For best results, use direct links to privacy policies.
        - The analysis works best on English language documents.
        - Longer documents may take a few seconds to process.
        - The tool recognizes standard legal terminology used in privacy policies.
        """)
        
        # Add sample image or icon
        st.markdown("## Risk Levels")
        
        risk_levels = {
            "High Risk": "Major privacy or security concerns that could impact user data.",
            "Medium Risk": "Potential concerns that should be reviewed carefully.",
            "Low Risk": "Generally acceptable practices with minimal concerns."
        }
        
        for risk, description in risk_levels.items():
            if "High" in risk:
                st.markdown(f"<div style='color:{HIGH_RISK_COLOR}'><strong>{risk}</strong>: {description}</div>", unsafe_allow_html=True)
            elif "Medium" in risk:
                st.markdown(f"<div style='color:{MEDIUM_RISK_COLOR}'><strong>{risk}</strong>: {description}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='color:{LOW_RISK_COLOR}'><strong>{risk}</strong>: {description}</div>", unsafe_allow_html=True)
    
    # Analysis button
    analyze_button = st.button("Analyze Document", type="primary")
    
    # Document analysis logic
    if analyze_button and document_text:
        with st.spinner("Analyzing document... This may take a moment."):
            analysis_results = analyze_document(document_text)
            display_analysis_results(analysis_results, document_text)
    elif analyze_button and not document_text:
        st.warning("Please provide a document to analyze first.")


def analyze_document(text):
    """
    Analyze the document text and extract relevant information.
    Returns a dictionary with analysis results for each category.
    """
    # Dictionary to store analysis results
    results = {
        "data_collection": {
            "score": 0,
            "risk_level": "",
            "findings": [],
            "extracted_clauses": []
        },
        "data_sharing": {
            "score": 0,
            "risk_level": "",
            "findings": [],
            "extracted_clauses": []
        },
        "data_security": {
            "score": 0,
            "risk_level": "",
            "findings": [],
            "extracted_clauses": []
        },
        "user_rights": {
            "score": 0,
            "risk_level": "",
            "findings": [],
            "extracted_clauses": []
        },
        "liability": {
            "score": 0,
            "risk_level": "",
            "findings": [],
            "extracted_clauses": []
        },
        "policy_changes": {
            "score": 0,
            "risk_level": "",
            "findings": [],
            "extracted_clauses": []
        }
    }
    
    # Break text into sentences for analysis
    sentences = sent_tokenize(text)
    
    # Analysis patterns for each category
    patterns = {
        "data_collection": {
            "high_risk": [
                r"collect.*biometric", r"facial recognition", r"track.*exact location", 
                r"monitor.*activity", r"record.*conversations", r"store.*indefinitely",
                r"collect.*without.*consent"
            ],
            "medium_risk": [
                r"collect.*personal information", r"store.*data", r"cookies", r"track.*usage",
                r"retain.*information", r"collect.*IP address", r"analytics"
            ],
            "low_risk": [
                r"anonymous.*data", r"aggregate.*information", r"de-identified", 
                r"limited.*retention", r"minimal.*collection"
            ],
            "general": [r"collect", r"information", r"data", r"track", r"cookie", r"retention"]
        },
        "data_sharing": {
            "high_risk": [
                r"sell.*personal.*data", r"share.*with.*third.parties", r"transfer.*ownership", 
                r"disclose.*information", r"provide.*to.*advertisers", r"share.*without.*notice"
            ],
            "medium_risk": [
                r"share.*with.*partners", r"third.party.*service", r"affiliates", 
                r"business.*partners", r"vendors"
            ],
            "low_risk": [
                r"share.*only with consent", r"limited.*sharing", r"opt.out", 
                r"control.*over.*sharing", r"anonymized.*before.*sharing"
            ],
            "general": [r"share", r"third.party", r"partners", r"transfer", r"disclose"]
        },
        "data_security": {
            "high_risk": [
                r"no.*guarantee.*security", r"not.*responsible.*for.*breaches", r"as.is", 
                r"disclaim.*security", r"security.*not.*guaranteed"
            ],
            "medium_risk": [
                r"reasonable.*security", r"industry.*standard", r"encryption", 
                r"safeguards", r"security.*measures"
            ],
            "low_risk": [
                r"advanced.*encryption", r"robust.*security", r"regular.*audits", 
                r"promptly.*notify.*breach", r"comprehensive.*security.*framework"
            ],
            "general": [r"security", r"protect", r"encryption", r"breach", r"safeguard"]
        },
        "user_rights": {
            "high_risk": [
                r"no.*right.*to.*access", r"cannot.*delete", r"waive.*rights", 
                r"no.*control", r"surrender.*rights"
            ],
            "medium_risk": [
                r"may.*request.*deletion", r"contact.*us.*to.*access", r"limited.*control", 
                r"some.*rights"
            ],
            "low_risk": [
                r"right.*to.*access", r"right.*to.*delete", r"control.*your.*data", 
                r"manage.*preferences", r"GDPR", r"CCPA"
            ],
            "general": [r"rights", r"access", r"delete", r"control", r"request", r"opt.out"]
        },
        "liability": {
            "high_risk": [
                r"not.*liable", r"disclaim.*all.*liability", r"no.*warranties", 
                r"no.*responsibility", r"waive.*right.*to.*sue"
            ],
            "medium_risk": [
                r"limited.*liability", r"to.*the.*extent.*permitted.*by.*law", 
                r"cap.*on.*damages"
            ],
            "low_risk": [
                r"responsible", r"accountable", r"compensation.*for.*damages", 
                r"liability.*insurance"
            ],
            "general": [r"liability", r"disclaimer", r"damages", r"warranty", r"responsible"]
        },
        "policy_changes": {
            "high_risk": [
                r"change.*without.*notice", r"modify.*at.*any.*time", r"no.*notification", 
                r"deemed.*to.*accept.*changes"
            ],
            "medium_risk": [
                r"periodically.*update", r"check.*regularly", r"may.*notify", 
                r"post.*updates"
            ],
            "low_risk": [
                r"notify.*of.*changes", r"email.*about.*updates", r"consent.*required", 
                r"advance.*notice"
            ],
            "general": [r"changes", r"updates", r"modify", r"revise", r"amend"]
        }
    }
    
    # Analyze each category
    for category, pattern_set in patterns.items():
        high_risk_matches = []
        medium_risk_matches = []
        low_risk_matches = []
        general_matches = []
        
        # Check each sentence for patterns
        for sentence in sentences:
            # Check for high risk patterns
            for pattern in pattern_set["high_risk"]:
                if re.search(pattern, sentence, re.IGNORECASE):
                    high_risk_matches.append(sentence)
                    break
            
            # Check for medium risk patterns
            for pattern in pattern_set["medium_risk"]:
                if re.search(pattern, sentence, re.IGNORECASE):
                    medium_risk_matches.append(sentence)
                    break
            
            # Check for low risk patterns
            for pattern in pattern_set["low_risk"]:
                if re.search(pattern, sentence, re.IGNORECASE):
                    low_risk_matches.append(sentence)
                    break
            
            # Check for general category patterns
            for pattern in pattern_set["general"]:
                if re.search(pattern, sentence, re.IGNORECASE):
                    general_matches.append(sentence)
                    break
        
        # Calculate risk score based on matches
        high_risk_count = len(high_risk_matches)
        medium_risk_count = len(medium_risk_matches)
        low_risk_count = len(low_risk_matches)
        
        # Calculate normalized score (0-100)
        total_matches = high_risk_count + medium_risk_count + low_risk_count
        if total_matches > 0:
            score = (high_risk_count * 100 + medium_risk_count * 50) / total_matches
        else:
            # If no specific risk patterns matched but general category patterns did
            if len(general_matches) > 0:
                score = 50  # Default to medium risk if only general patterns match
            else:
                score = 0  # No relevant clauses found
        
        # Determine risk level
        if score >= 70:
            risk_level = "High"
        elif score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Compile findings based on risk level
        findings = []
        if risk_level == "High":
            if high_risk_count > 0:
                findings.append(f"Found {high_risk_count} high-risk clauses related to {category.replace('_', ' ')}.")
            if category == "data_collection":
                findings.append("Extensive data collection with limited transparency.")
            elif category == "data_sharing":
                findings.append("Broad rights to share data with third parties.")
            elif category == "data_security":
                findings.append("Limited security guarantees or disclaimers of responsibility.")
            elif category == "user_rights":
                findings.append("Limited user control over personal data.")
            elif category == "liability":
                findings.append("Broad liability disclaimers and limitations.")
            elif category == "policy_changes":
                findings.append("Changes can be made without explicit notification.")
        elif risk_level == "Medium":
            if medium_risk_count > 0:
                findings.append(f"Found {medium_risk_count} medium-risk clauses related to {category.replace('_', ' ')}.")
            if category == "data_collection":
                findings.append("Standard data collection practices with some transparency.")
            elif category == "data_sharing":
                findings.append("Some data sharing with third parties with partial limitations.")
            elif category == "data_security":
                findings.append("Standard security measures mentioned but with limitations.")
            elif category == "user_rights":
                findings.append("Some user rights acknowledged but may be limited.")
            elif category == "liability":
                findings.append("Some liability limitations but not overly broad.")
            elif category == "policy_changes":
                findings.append("Changes may be made with some form of notification.")
        else:
            if low_risk_count > 0:
                findings.append(f"Found {low_risk_count} low-risk clauses related to {category.replace('_', ' ')}.")
            if category == "data_collection":
                findings.append("Minimal data collection or strong transparency practices.")
            elif category == "data_sharing":
                findings.append("Restrictive data sharing policies or strong user controls.")
            elif category == "data_security":
                findings.append("Strong security measures and commitments.")
            elif category == "user_rights":
                findings.append("Strong user rights and control over personal data.")
            elif category == "liability":
                findings.append("Reasonable liability terms with user protections.")
            elif category == "policy_changes":
                findings.append("Clear notification process for policy changes.")
        
        # If no findings were generated but general matches exist
        if not findings and len(general_matches) > 0:
            findings.append(f"Found general clauses related to {category.replace('_', ' ')} but couldn't determine specific risk level.")
        
        # If no patterns matched at all
        if not findings and len(general_matches) == 0:
            findings.append(f"No specific clauses related to {category.replace('_', ' ')} were identified.")
            
        # Store results
        results[category]["score"] = score
        results[category]["risk_level"] = risk_level
        results[category]["findings"] = findings
        
        # Store extracted clauses (prioritize high risk, then medium, then low, then general)
        extracted_clauses = []
        extracted_clauses.extend(high_risk_matches[:3])  # Take up to 3 high risk matches
        
        if len(extracted_clauses) < 3:
            extracted_clauses.extend(medium_risk_matches[:3 - len(extracted_clauses)])
        
        if len(extracted_clauses) < 3:
            extracted_clauses.extend(low_risk_matches[:3 - len(extracted_clauses)])
        
        if len(extracted_clauses) < 3:
            extracted_clauses.extend(general_matches[:3 - len(extracted_clauses)])
        
        results[category]["extracted_clauses"] = extracted_clauses
    
    return results


def display_analysis_results(results, document_text):
    """Display the analysis results in a structured format."""
    st.markdown("## Analysis Results")
    
    # Calculate overall risk score
    risk_scores = [results[category]["score"] for category in results]
    overall_score = sum(risk_scores) / len(risk_scores)
    
    # Determine overall risk level
    if overall_score >= 70:
        overall_risk = "High"
        overall_color = HIGH_RISK_COLOR
    elif overall_score >= 30:
        overall_risk = "Medium"
        overall_color = MEDIUM_RISK_COLOR
    else:
        overall_risk = "Low"
        overall_color = LOW_RISK_COLOR
    
    # Display overall risk score
    st.markdown(f"### Overall Risk Assessment: <span style='color:{overall_color}'>{overall_risk} Risk</span>", unsafe_allow_html=True)
    
    # Create a radar chart for risk scores
    categories = [cat.replace('_', ' ').title() for cat in results.keys()]
    scores = [results[cat]["score"] for cat in results.keys()]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Risk Score',
        line_color=PRIMARY_COLOR,
        fillcolor=f'rgba(78, 140, 255, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        height=350,
    )
    
    # Display radar chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Create tabs for different sections of the analysis
    tabs = st.tabs(["Key Findings", "Detailed Analysis", "Document Statistics"])
    
    # Key Findings Tab
    with tabs[0]:
        st.markdown("### Key Cybersecurity Concerns")
        
        # Display high risk categories first
        high_risk_categories = [cat for cat in results if results[cat]["risk_level"] == "High"]
        if high_risk_categories:
            st.markdown("<div style='padding: 10px; background-color: #fff8f8; border-left: 5px solid #ff4b4b; margin-bottom: 20px;'>", unsafe_allow_html=True)
            st.markdown("#### High Risk Areas")
            for category in high_risk_categories:
                st.markdown(f"**{category.replace('_', ' ').title()}**: {' '.join(results[category]['findings'][:1])}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Display medium risk categories
        medium_risk_categories = [cat for cat in results if results[cat]["risk_level"] == "Medium"]
        if medium_risk_categories:
            st.markdown("<div style='padding: 10px; background-color: #fffbf0; border-left: 5px solid #ffa500; margin-bottom: 20px;'>", unsafe_allow_html=True)
            st.markdown("#### Medium Risk Areas")
            for category in medium_risk_categories:
                st.markdown(f"**{category.replace('_', ' ').title()}**: {' '.join(results[category]['findings'][:1])}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Display low risk categories
        low_risk_categories = [cat for cat in results if results[cat]["risk_level"] == "Low"]
        if low_risk_categories:
            st.markdown("<div style='padding: 10px; background-color: #f0fff8; border-left: 5px solid #00cc66; margin-bottom: 20px;'>", unsafe_allow_html=True)
            st.markdown("#### Low Risk Areas")
            for category in low_risk_categories:
                st.markdown(f"**{category.replace('_', ' ').title()}**: {' '.join(results[category]['findings'][:1])}")
            st.markdown("</div>", unsafe_allow_html=True)
        
    # Detailed Analysis Tab
    with tabs[1]:
        # Display detailed analysis for each category
        for category, data in results.items():
            # Determine color based on risk level
            if data["risk_level"] == "High":
                color = HIGH_RISK_COLOR
            elif data["risk_level"] == "Medium":
                color = MEDIUM_RISK_COLOR
            else:
                color = LOW_RISK_COLOR
            
            # Create expander for each category
            with st.expander(f"{category.replace('_', ' ').title()} - {data['risk_level']} Risk", expanded=(data['risk_level'] == 'High')):
                # Display risk level and score
                st.markdown(f"#### Risk Level: <span style='color:{color}'>{data['risk_level']}</span>", unsafe_allow_html=True)
                st.progress(data["score"]/100)
                
                # Display findings
                st.markdown("#### Key Findings:")
                for finding in data["findings"]:
                    st.markdown(f"- {finding}")
                
                # Display extracted clauses if available
                if data["extracted_clauses"]:
                    st.markdown("#### Extracted Clauses:")
                    for clause in data["extracted_clauses"]:
                        st.markdown(f"<div class='highlight'>{clause}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("No specific clauses extracted for this category.")
    
    # Document Statistics Tab
    with tabs[2]:
        st.markdown("### Document Statistics")
        
        # Document length
        char_count = len(document_text)
        word_count = len(document_text.split())
        sentence_count = len(sent_tokenize(document_text))
        
        # Create columns for statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Character Count", f"{char_count:,}")
        
        with col2:
            st.metric("Word Count", f"{word_count:,}")
        
        with col3:
            st.metric("Sentence Count", f"{sentence_count:,}")
        
        # Readability statistics (simplified)
        avg_sentence_length = word_count / max(1, sentence_count)
        st.markdown(f"**Average Sentence Length**: {avg_sentence_length:.1f} words")
        
        if avg_sentence_length > 25:
            st.warning("The document has very long sentences, which may make it difficult to understand.")
        
        # Show frequently used terms
        st.markdown("#### Frequently Mentioned Terms")
        
        # Simple frequency analysis for common terms
        common_terms = [
            "personal data", "information", "consent", "cookies", "third party", 
            "partners", "security", "rights", "access", "delete", "share", 
            "collect", "process", "privacy", "breach", "notification"
        ]
        
        term_counts = {}
        for term in common_terms:
            count = len(re.findall(r'\b' + re.escape(term) + r'\b', document_text, re.IGNORECASE))
            if count > 0:
                term_counts[term] = count
        
        # Sort by frequency
        sorted_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Create a bar chart of most common terms
        if sorted_terms:
            terms, counts = zip(*sorted_terms[:10])  # Top 10 terms
            
            term_df = pd.DataFrame({
                'Term': terms,
                'Count': counts
            })
            
            st.bar_chart(term_df.set_index('Term'))
        else:
            st.write("No common privacy terms detected.")
    
    # User feedback section
    st.markdown("## Your Feedback")
    st.markdown("Was this analysis helpful? Let us know what you think!")
    
    feedback_cols = st.columns([1, 1, 2])
    with feedback_cols[0]:
        st.button("👍 Helpful")
    with feedback_cols[1]:
        st.button("👎 Not Helpful")
    with feedback_cols[2]:
        feedback_text = st.text_input("Additional feedback (optional)")


if __name__ == "__main__":
    main()
