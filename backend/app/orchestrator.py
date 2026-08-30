import os
import json
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import google.generativeai as genai

# State definition for the clinical report orchestrator
class PipelineState(TypedDict):
    patient_id: str
    patient_name: str
    patient_age: int
    patient_gender: str
    original_image_path: str
    preprocessed_path: str
    blur_score: int
    classification: Dict[str, Any]
    segmentation: Dict[str, Any]
    severity: Dict[str, Any]
    diagnosis_summary: str
    search_query: str
    retrieved_symptoms: List[str]
    retrieved_complications: List[str]
    retrieved_treatments: List[str]
    cited_evidence: List[Dict[str, Any]]
    draft_report: Dict[str, Any]
    validated_report: Dict[str, Any]
    warnings: List[str]
    errors: List[str]

# Node 1: Diagnosis Node
def diagnosis_node(state: PipelineState) -> Dict[str, Any]:
    label = state["classification"]["label"]
    confidence = state["classification"]["confidence"]
    percent_coverage = state["severity"]["percent_coverage"]
    severity_level = state["severity"]["severity_level"]

    if label == "Normal Mucosa":
        summary = "Endoscopy indicates normal, healthy mucosa. No active bleeding, mucosal lesions, or signs of inflammation."
    elif label == "Gastric Ulcer":
        summary = f"Endoscopy reveals Gastric Ulcer with a coverage of {percent_coverage}% of the mucosal ROI, classified as {severity_level} severity. Requires assessment of H. pylori status and ulcer bleeding risk."
    elif label == "Esophagitis":
        summary = f"Endoscopy identifies Esophagitis consistent with mucosal inflammation, with a coverage of {percent_coverage}% of the mucosal ROI ({severity_level} severity)."
    elif label == "Colon Polyp":
        summary = f"Endoscopy identifies a Colon Polyp with a coverage of {percent_coverage}% of the mucosal ROI ({severity_level} severity). Complete endoscopic resection and histopathology required."
    elif label == "Barrett's Esophagus":
        summary = f"Endoscopy indicates Barrett's Esophagus spanning {percent_coverage}% of the mucosal ROI ({severity_level} severity), showing signs of specialized intestinal metaplasia. Periodic surveillance required."
    else:
        summary = f"Abnormal finding detected: {label} ({severity_level} severity, {percent_coverage}% coverage)."

    return {"diagnosis_summary": summary}

# Node 2: Query Builder Node
def query_builder_node(state: PipelineState) -> Dict[str, Any]:
    label = state["classification"]["label"]
    severity_level = state["severity"]["severity_level"]
    
    # Formulate a search query
    query = f"endoscopy findings {label} {severity_level} guidelines symptoms complications treatment"
    return {"search_query": query}

# Node 3: Parallel FAISS Retrieval Node
def parallel_retrieval_node(state: PipelineState) -> Dict[str, Any]:
    # In a real system, this would make parallel calls to separate FAISS indices.
    # Here, we retrieve specific symptoms, complications, and treatments based on the diagnosis.
    label = state["classification"]["label"]
    severity = state["severity"]["severity_level"]
    
    symptoms = []
    complications = []
    treatments = []
    evidence = []

    if label == "Gastric Ulcer":
        symptoms = ["Epigastric pain postprandial", "Dyspepsia", "Nausea/vomiting", "Early satiety"]
        if severity == "Severe":
            complications = ["Active bleeding", "Gastric outlet obstruction", "Perforation", "Anemia"]
            treatments = ["Emergent endoscopic hemostasis", "Intravenous double-dose PPIs", "Blood transfusion if Hb < 7 g/dL"]
        else:
            complications = ["Recurrent ulceration", "Minor bleeding"]
            treatments = ["Oral PPIs (Omeprazole 40mg daily for 8 weeks)", "H. pylori triple therapy if positive", "Stop NSAIDs"]
            
        evidence = [
            {"title": "Management of peptic ulcer disease and H. pylori infection", "journal": "Gastroenterology", "year": 2022},
            {"title": "ACR Guidelines for Upper Gastrointestinal Bleeding", "journal": "Am J Gastroenterol", "year": 2021}
        ]
        
    elif label == "Esophagitis":
        symptoms = ["Heartburn (pyrosis)", "Acid regurgitation", "Dysphagia", "Odynophagia"]
        if severity == "Severe":
            complications = ["Esophageal stricture", "Barrett's Esophagus transition", "Ulceration with hematemesis"]
            treatments = ["Aggressive acid suppression (Esomeprazole 40mg BID)", "Endoscopic dilation (if stricture present)", "Sucralfate suspension"]
        else:
            complications = ["Minor erosions", "Discomfort"]
            treatments = ["Standard PPI therapy (Omeprazole 20mg QD)", "Antacids as needed", "Elevate head of bed", "Avoid fatty/spicy foods"]
            
        evidence = [
            {"title": "Updated guidelines for the management of gastroesophageal reflux disease", "journal": "Am J Gastroenterol", "year": 2022},
            {"title": "Los Angeles Classification of Esophagitis validity studies", "journal": "Gut", "year": 1999}
        ]
        
    elif label == "Colon Polyp":
        symptoms = ["Asymptomatic (screen detected)", "Occasional hematochezia", "Iron deficiency anemia"]
        complications = ["Adenocarcinoma transformation", "Polypectomy site bleeding", "Post-polypectomy syndrome"]
        treatments = ["Complete polypectomy (snare resection)", "Submucosal injection if sessile", "Histopathologic examination"]
        evidence = [
            {"title": "Surveillance after polypectomy: US Multi-Society Task Force guidelines", "journal": "Gastroenterology", "year": 2020}
        ]
        
    elif label == "Barrett's Esophagus":
        symptoms = ["Chronic heartburn", "Dysphagia", "Regurgitation"]
        complications = ["Low-grade dysplasia", "High-grade dysplasia", "Esophageal adenocarcinoma"]
        treatments = ["Ablative therapy (RFA) if dysplasia present", "Standard-dose PPI daily", "Surveillance endoscopy every 3 years"]
        evidence = [
            {"title": "ACG Clinical Guideline: Diagnosis and Management of Barrett's Esophagus", "journal": "Am J Gastroenterol", "year": 2022}
        ]
        
    else: # Normal or fallback
        symptoms = ["None reported", "Routine screening"]
        complications = ["None"]
        treatments = ["Routine follow-up as per standard screening guidelines"]
        evidence = [
            {"title": "ASGE Standards of Practice: Screening Endoscopy", "journal": "Gastrointest Endosc", "year": 2021}
        ]

    return {
        "retrieved_symptoms": symptoms,
        "retrieved_complications": complications,
        "retrieved_treatments": treatments,
        "cited_evidence": evidence
    }

# Node 4: Evidence Reranker Node
def evidence_reranker_node(state: PipelineState) -> Dict[str, Any]:
    # Simulates reranking evidence. We score each cited article and sort them.
    evidence = state["cited_evidence"]
    severity = state["severity"]["severity_level"]
    
    scored_evidence = []
    for item in evidence:
        score = 0.85
        # High relevance adjustments
        if "Bleeding" in item["title"] and severity == "Severe":
            score += 0.10
        if "guidelines" in item["title"].lower():
            score += 0.05
        
        scored_item = item.copy()
        scored_item["relevance_score"] = round(score, 2)
        scored_evidence.append(scored_item)
        
    scored_evidence.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {"cited_evidence": scored_evidence}

# Node 5: Report Generation Node
def report_generation_node(state: PipelineState) -> Dict[str, Any]:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    
    # Format current state for generation
    patient_info = f"Patient: {state['patient_name']} (ID: {state['patient_id']}, {state['patient_age']}yo {state['patient_gender']})"
    findings = (
        f"Classification: {state['classification']['label']} (Confidence: {state['classification']['confidence']*100}%)\n"
        f"Lesion Coverage: {state['severity']['percent_coverage']}%\n"
        f"Severity: {state['severity']['severity_level']}\n"
        f"Blur/Artifact Score: {state['blur_score']}"
    )
    evidence = (
        f"Symptoms: {', '.join(state['retrieved_symptoms'])}\n"
        f"Complications: {', '.join(state['retrieved_complications'])}\n"
        f"Treatments: {', '.join(state['retrieved_treatments'])}\n"
        f"Evidence: {json.dumps(state['cited_evidence'])}"
    )

    draft = {}

    if api_key:
        try:
            # Setup Gemini Client
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            You are an expert gastroenterologist compiling a structured clinical endoscopy report.
            Synthesize the following input data into a clean JSON document.
            
            === Patient Information ===
            {patient_info}
            
            === Endoscopy Findings ===
            {findings}
            
            === Retrieved Clinical Evidence ===
            {evidence}
            
            Output a JSON block (and nothing else) conforming to this schema:
            {{
                "clinical_summary": "Paragraph summarizing findings and patient presentation.",
                "endoscopic_findings": "Detailed description of lesion morphology, location, and mucosal properties.",
                "diagnoses": [
                    {{
                        "condition": "Condition name",
                        "severity": "Severity level",
                        "confidence": "Confidence percent"
                    }}
                ],
                "recommended_investigations": ["List of follow-up tests, e.g. biopsy, bloods"],
                "management_plan": ["List of treatment steps, prescription PPIs, or lifestyle rules"],
                "cited_evidence_titles": ["List of scientific titles relevant to this diagnosis"]
            }}
            """
            response = model.generate_content(prompt)
            # Try to strip markdown code blocks if any
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            draft = json.loads(text.strip())
        except Exception as e:
            print(f"Gemini API generation failed, falling back to template generator. Error: {e}")

    # Fallback to local template generator if Gemini key not set or failed
    if not draft:
        label = state["classification"]["label"]
        severity = state["severity"]["severity_level"]
        coverage = state["severity"]["percent_coverage"]
        
        if label == "Normal Mucosa":
            draft = {
                "clinical_summary": f"Routine endoscopic evaluation of patient {state['patient_name']} shows normal gastrointestinal mucosa. No evidence of inflammation, erosions, polyps, or malignant changes.",
                "endoscopic_findings": "Mucosa is pink, smooth, and vascular pattern is intact throughout the visualized segments. No active or recent bleeding.",
                "diagnoses": [
                    {"condition": "Normal Gastrointestinal Mucosa", "severity": "Normal", "confidence": f"{state['classification']['confidence']*100}%"}
                ],
                "recommended_investigations": ["None. Return to standard age-appropriate screening intervals."],
                "management_plan": ["Continue routine healthy diet.", "Re-evaluate if symptoms develop."],
                "cited_evidence_titles": [e["title"] for e in state["cited_evidence"]]
            }
        elif label == "Gastric Ulcer":
            draft = {
                "clinical_summary": f"Endoscopic examination of {state['patient_name']} revealed a single gastric mucosal lesion of {severity} severity, covering {coverage}% of the mucosal field, suggestive of a Gastric Ulcer. High priority follow-up needed.",
                "endoscopic_findings": f"Clean-based or clot-adherent ulcerated lesion observed in the gastric antrum/body. Surrounding mucosa is erythematous. Lesion area is quantified at {coverage}% of the field of view.",
                "diagnoses": [
                    {"condition": "Gastric Mucosa Ulceration", "severity": severity, "confidence": f"{state['classification']['confidence']*100}%"}
                ],
                "recommended_investigations": [
                    "Rapid Urease Test (RUT) or histopathological biopsy for H. pylori detection",
                    "Repeat endoscopy in 6-8 weeks to confirm complete ulcer healing and rule out malignancy",
                    "CBC to rule out chronic blood loss/anemia"
                ],
                "management_plan": [
                    "Prescribe Omeprazole 40mg PO daily for 8 weeks (or intravenous PPI if bleeding risk remains)",
                    "Initiate H. pylori eradication therapy (Clarithromycin + Amoxicillin + PPI) if biopsy returns positive",
                    "Strictly avoid NSAIDs, aspirin, and alcohol",
                    "Patient instructed to seek immediate emergency care if hematemesis or melena occurs"
                ],
                "cited_evidence_titles": [e["title"] for e in state["cited_evidence"]]
            }
        elif label == "Esophagitis":
            draft = {
                "clinical_summary": f"Endoscopy demonstrates esophageal mucosal breaks of {severity} severity ({coverage}% mucosal area coverage), indicating active reflux-induced Esophagitis.",
                "endoscopic_findings": f"Erythematous mucosal streaks and longitudinal erosions observed in the lower third of the esophagus above the gastroesophageal junction. Lesion coverage is {coverage}%.",
                "diagnoses": [
                    {"condition": "Reflux Esophagitis", "severity": severity, "confidence": f"{state['classification']['confidence']*100}%"}
                ],
                "recommended_investigations": [
                    "Biopsy of gastroesophageal junction (if Barrett's or malignancy suspected)",
                    "24-hour pH impedance monitoring if refractory to PPI therapy"
                ],
                "management_plan": [
                    "Initiate Esomeprazole 40mg PO daily (escalate to BID if symptoms persist/severe)",
                    "Add Sucralfate 1g suspension QID for symptomatic relief of mucosal burning",
                    "Lifestyle advice: elevate bed head by 6 inches, avoid lying down for 3 hours post meals, limit caffeine/chocolate/fats",
                    "Follow up in 4-6 weeks to assess symptom resolution"
                ],
                "cited_evidence_titles": [e["title"] for e in state["cited_evidence"]]
            }
        elif label == "Colon Polyp":
            draft = {
                "clinical_summary": f"Visualization of the colonic mucosa in patient {state['patient_name']} revealed a mucosal protrusion covering {coverage}% of the field, consistent with a Colon Polyp.",
                "endoscopic_findings": "Lobulated mucosal protrusion observed. Polypectomy was successfully executed. Clean resection margins.",
                "diagnoses": [
                    {"condition": "Colon Polyp (Resected)", "severity": severity, "confidence": f"{state['classification']['confidence']*100}%"}
                ],
                "recommended_investigations": [
                    "Histopathological evaluation of the resected polyp (Adenomatous vs Hyperplastic vs Sessile Serrated)",
                    "Repeat colonoscopy surveillance in 3-5 years pending pathology report"
                ],
                "management_plan": [
                    "Monitor for post-polypectomy bleeding (melena, hematochezia)",
                    "Maintain high-fiber diet and adequate hydration"
                ],
                "cited_evidence_titles": [e["title"] for e in state["cited_evidence"]]
            }
        else: # Barrett's or other
            draft = {
                "clinical_summary": f"Endoscopy shows salmon-colored mucosa extending proximally from the gastroesophageal junction, covering {coverage}% of the field, indicative of Barrett's Esophagus.",
                "endoscopic_findings": "Salmon-colored columnar mucosal projections observed above the Z-line. No nodules or visible ulcerations.",
                "diagnoses": [
                    {"condition": "Barrett's Esophagus", "severity": severity, "confidence": f"{state['classification']['confidence']*100}%"}
                ],
                "recommended_investigations": [
                    "Four-quadrant biopsies every 2 cm (Seattle protocol) to screen for dysplasia",
                    "Regular surveillance endoscopy at designated 3-year intervals"
                ],
                "management_plan": [
                    "Long-term PPI therapy for reflux control (Omeprazole 20mg daily)",
                    "Discuss endoscopic ablation therapy (RFA) if pathology confirms high-grade dysplasia"
                ],
                "cited_evidence_titles": [e["title"] for e in state["cited_evidence"]]
            }

    return {"draft_report": draft}

# Node 6: Validation Node
def validation_safety_node(state: PipelineState) -> Dict[str, Any]:
    draft = state["draft_report"]
    severity = state["severity"]["severity_level"]
    label = state["classification"]["label"]
    
    warnings = []
    validated_report = draft.copy()

    # Rule 1: Check for critical bleed risk
    if label == "Gastric Ulcer" and severity == "Severe":
        warnings.append("CRITICAL: High risk Gastric Ulcer detected. Monitor patient vitals for active internal bleeding. Ensure IV access is maintained.")
        
    # Rule 2: Validation of completeness
    if not validated_report.get("clinical_summary"):
        validated_report["clinical_summary"] = "Clinical endoscopy report details compiled successfully."
        
    # Rule 3: Ensure patient details are attached
    validated_report["metadata"] = {
        "patient_id": state["patient_id"],
        "patient_name": state["patient_name"],
        "patient_age": state["patient_age"],
        "patient_gender": state["patient_gender"],
        "date_of_procedure": os.path.basename(state["original_image_path"])[:10], # Try to parse date from file prefix if possible
        "blur_score": state["blur_score"],
        "warnings_triggered": warnings
    }

    return {"validated_report": validated_report, "warnings": warnings}


# Define the Orchestrator Pipeline Graph
def build_orchestrator_graph():
    workflow = StateGraph(PipelineState)

    # Register Nodes
    workflow.add_node("diagnosis", diagnosis_node)
    workflow.add_node("query_builder", query_builder_node)
    workflow.add_node("retrieval", parallel_retrieval_node)
    workflow.add_node("reranker", evidence_reranker_node)
    workflow.add_node("report_generation", report_generation_node)
    workflow.add_node("validation", validation_safety_node)

    # Establish Connections
    workflow.set_entry_point("diagnosis")
    workflow.add_edge("diagnosis", "query_builder")
    workflow.add_edge("query_builder", "retrieval")
    workflow.add_edge("retrieval", "reranker")
    workflow.add_edge("reranker", "report_generation")
    workflow.add_edge("report_generation", "validation")
    workflow.add_edge("validation", END)

    return workflow.compile()

def run_orchestrator(pipeline_data: dict) -> dict:
    """Invokes the LangGraph orchestrator on the preprocessed pipeline outcomes."""
    graph = build_orchestrator_graph()
    
    initial_state = PipelineState(
        patient_id=pipeline_data.get("patient_id", "PT-9999"),
        patient_name=pipeline_data.get("patient_name", "Unknown Patient"),
        patient_age=pipeline_data.get("patient_age", 50),
        patient_gender=pipeline_data.get("patient_gender", "M"),
        original_image_path=pipeline_data.get("original_image_path", ""),
        preprocessed_path=pipeline_data.get("preprocessed_path", ""),
        blur_score=pipeline_data.get("blur_score", 0),
        classification=pipeline_data.get("classification", {}),
        segmentation=pipeline_data.get("segmentation", {}),
        severity=pipeline_data.get("severity", {}),
        diagnosis_summary="",
        search_query="",
        retrieved_symptoms=[],
        retrieved_complications=[],
        retrieved_treatments=[],
        cited_evidence=[],
        draft_report={},
        validated_report={},
        warnings=[],
        errors=[]
    )

    final_state = graph.invoke(initial_state)
    return final_state
