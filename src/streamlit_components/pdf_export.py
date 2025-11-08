#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Component: Export PDF rapport estimation
US5 - Export PDF rapport
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from io import BytesIO
from typing import Dict, Optional


def generate_pdf_report(
    estimation_result: Dict,
    comparables_df: pd.DataFrame,
    bien_address: Optional[str] = None
) -> bytes:
    """
    Génère un rapport PDF simple (1 page) avec estimation et comparables.

    Args:
        estimation_result: Dict retourné par EstimationAlgorithm.estimate()
        comparables_df: DataFrame des comparables
        bien_address: Adresse du bien (optionnel)

    Returns:
        Bytes PDF
    """

    # Créer buffer PDF
    pdf_buffer = BytesIO()

    # Créer document
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        alignment=1  # Center
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=8,
        spaceBefore=8
    )

    body_style = styles['BodyText']

    # Éléments du document
    elements = []

    # === HEADER ===
    elements.append(Paragraph(
        "🏠 RAPPORT D'ESTIMATION IMMOBILIÈRE",
        title_style
    ))
    elements.append(Spacer(1, 0.1*inch))

    # Date et adresse
    date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    elements.append(Paragraph(
        f"<b>Date:</b> {date_str}",
        body_style
    ))
    if bien_address:
        elements.append(Paragraph(
            f"<b>Bien:</b> {bien_address}",
            body_style
        ))
    elements.append(Spacer(1, 0.15*inch))

    # === SECTION ESTIMATION ===
    estimation = estimation_result.get('estimation', {})
    fiabilite = estimation_result.get('fiabilite', {})
    bien = estimation_result.get('bien', {})

    prix_estime = estimation.get('prix_estime_eur')
    prix_min = estimation.get('prix_min_eur')
    prix_max = estimation.get('prix_max_eur')
    prix_au_m2 = estimation.get('prix_au_m2_eur')
    score_global = fiabilite.get('score_global', 0)
    evaluation = fiabilite.get('evaluation', 'N/A')
    nb_comparables = estimation_result.get('nb_comparables_utilises', 0)

    elements.append(Paragraph("ESTIMATION", heading_style))

    # Tableau estimation
    est_data = [
        ["Élément", "Valeur"],
        ["Prix estimé", f"{prix_estime:,.0f}€" if prix_estime else "N/A"],
        ["Prix minimum (25e %ile)", f"{prix_min:,.0f}€" if prix_min else "N/A"],
        ["Prix maximum (75e %ile)", f"{prix_max:,.0f}€" if prix_max else "N/A"],
        ["Prix au m²", f"{prix_au_m2:,.0f}€/m²" if prix_au_m2 else "N/A"],
        ["Score fiabilité", f"{score_global}/100 ({evaluation})"],
        ["Comparables utilisés", str(nb_comparables)],
    ]

    est_table = Table(est_data, colWidths=[3*inch, 2.5*inch])
    est_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    elements.append(est_table)
    elements.append(Spacer(1, 0.15*inch))

    # === SECTION BIEN ===
    elements.append(Paragraph("BIEN ESTIMÉ", heading_style))

    bien_data = [
        ["Type", bien.get('type', 'N/A')],
        ["Surface", f"{bien.get('surface_m2', 'N/A')} m²"],
        ["Latitude", f"{bien.get('latitude', 'N/A'):.4f}"],
        ["Longitude", f"{bien.get('longitude', 'N/A'):.4f}"],
    ]

    bien_table = Table(bien_data, colWidths=[3*inch, 2.5*inch])
    bien_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))

    elements.append(bien_table)
    elements.append(Spacer(1, 0.15*inch))

    # === SECTION FIABILITÉ ===
    elements.append(Paragraph("SCORE DE FIABILITÉ", heading_style))

    fid_data = [
        ["Composante", "Score"],
        ["Volume", f"{fiabilite.get('volume', 0)}/30"],
        ["Similarité", f"{fiabilite.get('similarite', 0)}/30"],
        ["Dispersion", f"{fiabilite.get('dispersion', 0)}/25"],
        ["Ancienneté", f"{fiabilite.get('anciennete', 0)}/15"],
        ["TOTAL", f"{score_global}/100"],
    ]

    fid_table = Table(fid_data, colWidths=[3*inch, 2.5*inch])
    fid_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4f8')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    elements.append(fid_table)
    elements.append(Spacer(1, 0.15*inch))

    # === SECTION TOP COMPARABLES ===
    if comparables_df is not None and len(comparables_df) > 0:
        elements.append(Paragraph("TOP COMPARABLES", heading_style))

        # Top 5 par score (si existe) ou par prix
        if 'score' in comparables_df.columns:
            df_sorted = comparables_df.sort_values('score', ascending=False).head(5)
        else:
            df_sorted = comparables_df.sort_values('valeurfonc', ascending=False).head(5)

        comp_data = [["Prix (€)", "Surface (m²)", "Distance (km)", "Score", "Date"]]

        for idx, row in df_sorted.iterrows():
            comp_data.append([
                f"{row.get('valeurfonc', 0):,.0f}",
                f"{row.get('sbati', 0):.0f}",
                f"{row.get('distance_km', 0):.1f}",
                f"{row.get('score', 0):.0f}",
                str(row.get('datemut', 'N/A'))[:10],
            ])

        comp_table = Table(comp_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(comp_table)
        elements.append(Spacer(1, 0.15*inch))

    # === FOOTER ===
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        "<i>Généré par Estimateur Immobilier MVP - Chablais/Annemasse</i>",
        body_style
    ))

    # Construire PDF
    doc.build(elements)

    # Retourner bytes
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def render_pdf_export(
    estimation_result: Dict,
    comparables_df: pd.DataFrame,
    bien_address: Optional[str] = None
) -> None:
    """
    Affiche bouton download PDF dans Streamlit.

    Args:
        estimation_result: Dict estimation
        comparables_df: DataFrame comparables
        bien_address: Adresse bien (optionnel)
    """

    st.markdown("## 📄 Export PDF")

    # Générer PDF
    pdf_bytes = generate_pdf_report(
        estimation_result,
        comparables_df,
        bien_address
    )

    # Bouton download
    st.download_button(
        label="📥 Télécharger rapport PDF",
        data=pdf_bytes,
        file_name=f"estimation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    st.success("✅ PDF généré avec succès")
