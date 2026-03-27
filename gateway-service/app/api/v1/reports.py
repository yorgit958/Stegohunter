import io
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.core.supabase_client import service_client
from app.api.dependencies import verify_token
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import datetime

router = APIRouter(prefix="/reports", tags=["Reports"])

from fastapi.responses import JSONResponse

@router.get("/pdf/{scan_id}")
async def generate_scan_pdf(
    scan_id: str,
    user_id: str = Depends(verify_token)
):
    try:
        # 1. Fetch Job Data using service_client to bypass anon RLS
        job_res = service_client.table("scan_jobs").select("*").eq("id", scan_id).eq("user_id", user_id).execute()
        if not job_res.data:
            raise HTTPException(status_code=404, detail="Scan job not found or unauthorized")
        
        scan_job = job_res.data[0]
        
        # 2. Fetch Analysis Results
        results_res = service_client.table("scan_results").select("*").eq("scan_job_id", scan_id).execute()
        scan_result = results_res.data[0] if results_res.data else None

        # --- PDF Generation Setup ---
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, spaceAfter=20, textColor=colors.HexColor("#0f172a"))
        subtitle_style = ParagraphStyle('SubTitle', parent=styles['Heading2'], fontSize=14, spaceAfter=15, textColor=colors.HexColor("#334155"))
        normal_style = styles["Normal"]
        
        story = []
        
        # --- Header ---
        story.append(Paragraph("StegoHunter Security Report", title_style))
        story.append(Paragraph(f"<b>Scan ID:</b> {scan_job['id']}", normal_style))
        story.append(Paragraph(f"<b>Date:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Spacer(1, 20))

        # --- File Metadata ---
        story.append(Paragraph("File Metadata", subtitle_style))
        metadata_data = [
            ["Attribute", "Details"],
            ["File Name", str(scan_job.get("file_name", "Unknown"))],
            ["File Size", f"{(scan_job.get('file_size_bytes') or 0) / 1024:.2f} KB"],
            ["Status", str(scan_job.get("status", "Unknown"))],
            ["Scan Date", str(scan_job.get("created_at", "Unknown"))]
        ]
        
        t_metadata = Table(metadata_data, colWidths=[150, 300])
        t_metadata.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#64748b")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1"))
        ]))
        story.append(t_metadata)
        story.append(Spacer(1, 25))

        # --- Analysis Results ---
        story.append(Paragraph("Threat Analysis Verdict", subtitle_style))
        
        if scan_result:
            is_stego = scan_result.get("is_stego", False)
            verdict_color_str = "#ef4444" if is_stego else "#22c55e"
            verdict_text = "THREAT DETECTED" if is_stego else "CLEAN"
            
            # Verdict Banner
            story.append(Paragraph(f"<font color='{verdict_color_str}'><b>VERDICT: {verdict_text}</b></font>", ParagraphStyle('Verdict', fontSize=16, spaceAfter=10)))
            
            verdict_data = [
                ["Metric", "Value"],
                ["Threat Level", str(scan_result.get("threat_level") or "none").upper()],
                ["Confidence Core", f"{(scan_result.get('confidence') or 0.0) * 100:.2f}%"]
            ]
            t_verdict = Table(verdict_data, colWidths=[150, 300])
            t_verdict.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#e2e8f0"))
            ]))
            story.append(t_verdict)
            story.append(Spacer(1, 20))

            # Detailed Detections
            details = scan_result.get("detection_methods")
            if details:
                story.append(Paragraph("Detailed Findings", subtitle_style))
                
                engines = details.get("engines", []) if isinstance(details, dict) else []
                if engines:
                    for eng in engines:
                        engine_name = eng.get("engine", "Unknown Engine")
                        story.append(Spacer(1, 10))
                        story.append(Paragraph(f"<b>Engine: {engine_name}</b>", normal_style))
                        
                        eng_data = [
                            ["Metric", "Value"],
                            ["Detection Score", f"{eng.get('score', 0)}"],
                            ["Engine Confidence", f"{eng.get('confidence', 0)}"]
                        ]
                        
                        eng_details = eng.get("details", {})
                        if isinstance(eng_details, dict):
                            for k, v in eng_details.items():
                                formatted_k = str(k).replace("_", " ").title()
                                eng_data.append([formatted_k, str(v)[:50]])
                                
                        t_eng = Table(eng_data, colWidths=[150, 300])
                        t_eng.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0"))
                        ]))
                        story.append(t_eng)
                        story.append(Spacer(1, 10))
                else:
                    import json
                    try:
                        formatted_details = json.dumps(details, indent=2)
                    except Exception:
                        formatted_details = str(details)
                    story.append(Preformatted(formatted_details, normal_style))

        else:
            story.append(Paragraph("Analysis pending or no results found for this scan.", normal_style))

        # --- Build PDF ---
        doc.build(story)
        
        # Prepare HTTP streaming response
        buffer.seek(0)
        
        # Setting appropriate headers for a download
        headers = {
            'Content-Disposition': f'attachment; filename="StegoHunter_Report_{scan_id[:8]}.pdf"',
            'Access-Control-Expose-Headers': 'Content-Disposition'
        }
        
        return StreamingResponse(buffer, media_type="application/pdf", headers=headers)
    except Exception as e:
        import traceback
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()})
    
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)
