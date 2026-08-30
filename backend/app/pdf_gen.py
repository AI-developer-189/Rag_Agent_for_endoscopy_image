import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_report_pdf(report_data: dict, original_img: str, preprocessed_img: str, heatmap_img: str, overlay_img: str, output_pdf_path: str):
    """Compiles the structured clinical report and multi-stage image assets into a professional PDF report."""
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
    
    # Establish document
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []
    styles = getSampleStyleSheet()

    # Define custom medical theme colors (Deep Teal & Slate Slate)
    primary_color = colors.HexColor("#0f4c5c")
    secondary_color = colors.HexColor("#e36414")
    neutral_dark = colors.HexColor("#2f3e46")
    neutral_light = colors.HexColor("#f8f9fa")
    border_color = colors.HexColor("#e9ecef")

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=primary_color,
        spaceAfter=15
    )

    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=primary_color,
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=neutral_dark,
        leading=14
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=primary_color
    )

    warning_style = ParagraphStyle(
        'WarningText',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#d90429"),
        leading=13
    )

    # 1. Header Title
    story.append(Paragraph("Structured Clinical Endoscopy Report", title_style))
    story.append(Spacer(1, 10))

    # 2. Patient & Procedure Metadata Table
    meta = report_data["metadata"]
    metadata_data = [
        [
            Paragraph("Patient Name:", meta_label_style), Paragraph(meta["patient_name"], body_style),
            Paragraph("Patient ID:", meta_label_style), Paragraph(meta["patient_id"], body_style)
        ],
        [
            Paragraph("Age / Gender:", meta_label_style), Paragraph(f"{meta['patient_age']} / {meta['patient_gender']}", body_style),
            Paragraph("Date of Procedure:", meta_label_style), Paragraph(meta["date_of_procedure"], body_style)
        ],
        [
            Paragraph("Image Quality:", meta_label_style), Paragraph(f"Blur Score: {meta['blur_score']}", body_style),
            Paragraph("Status:", meta_label_style), Paragraph("Validated", body_style)
        ]
    ]

    meta_table = Table(metadata_data, colWidths=[100, 160, 110, 150])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), neutral_light),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, border_color),
        ('LINEABOVE', (0,0), (-1,-1), 0.5, border_color),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # 3. Warning Alert Box (if triggered)
    if meta.get("warnings_triggered"):
        warning_data = []
        for w in meta["warnings_triggered"]:
            warning_data.append([Paragraph(w, warning_style)])
        
        warning_table = Table(warning_data, colWidths=[520])
        warning_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fff0f3")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#ffb3c1")),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(warning_table)
        story.append(Spacer(1, 15))

    # Section: Diagnostic Summary
    story.append(Paragraph("Clinical Summary", h2_style))
    story.append(Paragraph(report_data["clinical_summary"], body_style))
    story.append(Spacer(1, 10))

    # Section: Detailed Endoscopic Findings
    story.append(Paragraph("Endoscopic Findings", h2_style))
    story.append(Paragraph(report_data["endoscopic_findings"], body_style))
    story.append(Spacer(1, 10))

    # Diagnosis & Metrics Table
    diagnosis_headers = [
        Paragraph("<b>Condition Identified</b>", meta_label_style),
        Paragraph("<b>Severity Classification</b>", meta_label_style),
        Paragraph("<b>Inference Confidence</b>", meta_label_style)
    ]
    
    diagnosis_rows = [diagnosis_headers]
    for d in report_data["diagnoses"]:
        diagnosis_rows.append([
            Paragraph(d["condition"], body_style),
            Paragraph(d["severity"], body_style),
            Paragraph(d["confidence"], body_style)
        ])

    diag_table = Table(diagnosis_rows, colWidths=[200, 160, 160])
    diag_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2ece9")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(diag_table)
    story.append(Spacer(1, 20))

    # 4. Multi-Stage Image Grid
    story.append(Paragraph("Comparative Multi-Stage Image Overlays", h2_style))
    
    # We will load the 4 images and downscale them for PDF report layout
    img_width = 120
    img_height = 120
    
    img_original_flowable = Image(original_img, width=img_width, height=img_height)
    img_enhanced_flowable = Image(preprocessed_img, width=img_width, height=img_height)
    img_heatmap_flowable = Image(heatmap_img, width=img_width, height=img_height)
    img_overlay_flowable = Image(overlay_img, width=img_width, height=img_height)

    image_grid_data = [
        [img_original_flowable, img_enhanced_flowable, img_heatmap_flowable, img_overlay_flowable],
        [
            Paragraph("<b>1. Original Frame</b>", body_style),
            Paragraph("<b>2. Enhanced (CLAHE)</b>", body_style),
            Paragraph("<b>3. Grad-CAM</b>", body_style),
            Paragraph("<b>4. Segmentation</b>", body_style)
        ]
    ]

    image_table = Table(image_grid_data, colWidths=[130, 130, 130, 130])
    image_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,1), (-1,1), 10),
        ('TOPPADDING', (0,1), (-1,1), 4),
    ]))
    
    # Use KeepTogether to avoid splitting images across pages
    story.append(KeepTogether([image_table]))
    story.append(Spacer(1, 15))

    # 5. Treatment Plan & Recommended Investigations
    plan_data = []
    
    # Left column: Management Plan
    plan_elements = []
    plan_elements.append(Paragraph("Management Plan", h2_style))
    for step in report_data["management_plan"]:
        plan_elements.append(Paragraph(f"• {step}", body_style))
        plan_elements.append(Spacer(1, 4))
        
    # Right column: Recommended Investigations
    invest_elements = []
    invest_elements.append(Paragraph("Recommended Investigations", h2_style))
    for test in report_data["recommended_investigations"]:
        invest_elements.append(Paragraph(f"• {test}", body_style))
        invest_elements.append(Spacer(1, 4))

    # Let's combine them side-by-side using a borderless table
    col_width = 250
    plan_table = Table([[plan_elements, invest_elements]], colWidths=[col_width, col_width])
    plan_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(plan_table)
    story.append(Spacer(1, 15))

    # 6. Cited Guidelines & Clinical Evidence
    story.append(Paragraph("Cited Guidelines & Evidence", h2_style))
    evidence_rows = []
    for title in report_data["cited_evidence_titles"]:
        evidence_rows.append(Paragraph(f"• {title}", body_style))
        evidence_rows.append(Spacer(1, 3))
        
    story.append(KeepTogether(evidence_rows))

    # Compile PDF
    doc.build(story)
