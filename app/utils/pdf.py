"""PDF generation helpers — single source of truth for budget PDFs."""
import io
import base64


def build_budget_pdf(budget) -> bytes:
    """
    Build a budget PDF and return raw bytes.
    Called by both the download route and the send-email route.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        Table, TableStyle, HRFlowable, Image as RLImage
    )

    from app.models import BudgetConfig
    cfg = BudgetConfig.get()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm
    )
    story = []

    # ── Styles ──────────────────────────────────────────────────────────────
    brand = colors.HexColor('#6366f1')
    dark  = colors.HexColor('#1e293b')
    muted = colors.HexColor('#64748b')

    title_style = ParagraphStyle(
        'title', fontSize=26, textColor=dark,
        spaceAfter=2, fontName='Helvetica-Bold'
    )
    sub_style = ParagraphStyle(
        'sub', fontSize=11, textColor=muted, spaceAfter=4
    )
    note_style = ParagraphStyle(
        'note', fontSize=9, textColor=muted
    )
    company_name_style = ParagraphStyle(
        'cname', fontSize=14, textColor=dark, fontName='Helvetica-Bold', spaceAfter=2
    )
    company_detail_style = ParagraphStyle(
        'cdetail', fontSize=9, textColor=muted, spaceAfter=1
    )

    # ── Company header ───────────────────────────────────────────────────────
    logo_img = None
    if cfg.mostrar_logo and cfg.empresa_logo:
        try:
            logo_data = cfg.empresa_logo
            if ',' in logo_data:
                logo_data = logo_data.split(',', 1)[1]
            img_bytes = base64.b64decode(logo_data)
            img_buf = io.BytesIO(img_bytes)
            logo_img = RLImage(img_buf, width=4 * cm, height=2 * cm)
            logo_img.hAlign = 'LEFT'
        except Exception:
            logo_img = None

    company_lines = []
    if cfg.empresa_nombre:
        company_lines.append(Paragraph(cfg.empresa_nombre, company_name_style))
    if cfg.empresa_cuit:
        company_lines.append(Paragraph(f'CUIT: {cfg.empresa_cuit}', company_detail_style))
    if cfg.empresa_direccion:
        company_lines.append(Paragraph(f'Dir: {cfg.empresa_direccion}', company_detail_style))
    if cfg.empresa_telefono:
        company_lines.append(Paragraph(f'Tel: {cfg.empresa_telefono}', company_detail_style))
    if cfg.empresa_email:
        company_lines.append(Paragraph(f'Email: {cfg.empresa_email}', company_detail_style))

    title_lines = [
        Paragraph("PRESUPUESTO", title_style),
        Paragraph(f"N° {budget.budget_number}", sub_style),
    ]

    if company_lines or logo_img:
        left_content = []
        if logo_img:
            left_content.append(logo_img)
            left_content.append(Spacer(1, 0.2 * cm))
        left_content.extend(company_lines)
        header_table = Table(
            [[left_content, title_lines]],
            colWidths=[9 * cm, 8.3 * cm]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(header_table)
    else:
        story.append(Paragraph("PRESUPUESTO", title_style))
        story.append(Paragraph(f"N° {budget.budget_number}", sub_style))

    story.append(HRFlowable(width="100%", thickness=2, color=brand))
    story.append(Spacer(1, 0.4 * cm))

    # ── Client / budget info ─────────────────────────────────────────────────
    info_data = [
        ['CLIENTE', '', 'DATOS DEL PRESUPUESTO', ''],
        [budget.client_name, '', f'Fecha: {budget.created_at.strftime("%d/%m/%Y")}', ''],
        [budget.client_email or '-', '', f'Estado: {budget.status.upper()}', ''],
        [budget.client_phone or '-', '', 'Válido por: 30 días', ''],
    ]
    if budget.client_address:
        info_data.append([budget.client_address, '', '', ''])

    info_table = Table(info_data, colWidths=[8 * cm, 1 * cm, 6 * cm, 2.5 * cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('TEXTCOLOR', (0, 0), (-1, 0), brand),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TEXTCOLOR', (0, 1), (-1, -1), dark),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.6 * cm))

    # ── Items table ──────────────────────────────────────────────────────────
    rows = [['#', 'Descripción', 'Cant.', 'Precio Unit.', 'Subtotal']]
    for i, item in enumerate(budget.items, 1):
        rows.append([
            str(i),
            item.description,
            f"{item.quantity:g}",
            f"${item.unit_price:,.2f}",
            f"${item.subtotal:,.2f}",
        ])
    items_table = Table(rows, colWidths=[0.8 * cm, 9 * cm, 1.5 * cm, 3 * cm, 3 * cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), brand),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Totals ───────────────────────────────────────────────────────────────
    totals_data = [['', 'Subtotal:', f"${budget.subtotal:,.2f}"]]
    if budget.discount > 0:
        totals_data.append(['', f'Descuento ({budget.discount:.0f}%):', f"-${budget.discount_amount:,.2f}"])
    if budget.tax > 0:
        totals_data.append(['', f'IVA ({budget.tax:.0f}%):', f"${budget.tax_amount:,.2f}"])
    totals_data.append(['', 'TOTAL:', f"${budget.total:,.2f}"])

    totals_table = Table(totals_data, colWidths=[10.8 * cm, 3.5 * cm, 3 * cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -2), 10),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 13),
        ('TEXTCOLOR', (0, -1), (-1, -1), brand),
        ('LINEABOVE', (1, -1), (-1, -1), 1.5, brand),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(totals_table)

    # ── Notes ────────────────────────────────────────────────────────────────
    if budget.notes:
        story.append(Spacer(1, 0.6 * cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph('<b>Notas:</b>', note_style))
        story.append(Paragraph(budget.notes, note_style))

    # ── Footer ───────────────────────────────────────────────────────────────
    if cfg.pie_texto:
        story.append(Spacer(1, 0.8 * cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))
        story.append(Spacer(1, 0.2 * cm))
        footer_style = ParagraphStyle(
            'footer', fontSize=8, textColor=muted, alignment=1
        )
        story.append(Paragraph(cfg.pie_texto, footer_style))

    doc.build(story)
    return buffer.getvalue()
