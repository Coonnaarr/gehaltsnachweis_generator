import json
import os
import glob
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_pdfs_from_json(input_dir, output_dir=None):
    """Generate PDF payslips from JSON data files."""
    # If no output directory specified, use the input directory
    if output_dir is None:
        output_dir = input_dir
    
    # Make sure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Find all JSON files in the input directory (including subdirectories)
    json_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.json') and 'payslip_' in file:
                json_files.append(os.path.join(root, file))
    
    # Process each JSON file
    for json_file in json_files:
        try:
            # Load the JSON data
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Create output filename with same structure but .pdf extension
            pdf_filename = os.path.splitext(json_file)[0] + '.pdf'
            if output_dir != input_dir:
                # If different output directory, adjust the path
                pdf_filename = os.path.join(output_dir, os.path.basename(pdf_filename))
            
            # Generate the PDF
            create_payslip(pdf_filename, data)
            print(f"Generated PDF: {pdf_filename}")
            
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
    
    print(f"PDF generation complete. Processed {len(json_files)} files.")

def create_custom_styles():
    """Create and return custom styles for the payslip document."""
    styles = getSampleStyleSheet()
    
    # Define all custom styles
    custom_styles = {
        "title_style": ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=10,
            alignment=0,
            spaceAfter=2,
            leading=10,
            fontName="Helvetica-Bold",
        ),
        "normal_style": ParagraphStyle(
            "Normal", 
            parent=styles["Normal"], 
            fontSize=8, 
            leading=9
        ),
        "bold_style": ParagraphStyle(
            "Bold", 
            parent=styles["Normal"], 
            fontSize=8, 
            leading=9, 
            fontName="Helvetica-Bold"
        ),
        "header_style": ParagraphStyle(
            "Header",
            parent=styles["Heading2"],
            fontSize=9,
            textColor=colors.black,
            spaceAfter=6,
        ),
        "small_style": ParagraphStyle(
            "Small", 
            parent=styles["Normal"], 
            fontSize=7, 
            leading=8
        ),
        "micro_style": ParagraphStyle(
            "Micro",
            parent=styles["Normal"],
            fontSize=6,
            leading=7,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "notes_style": ParagraphStyle(
            "Notes",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            alignment="left",
            textColor=colors.black,
        ),
        "centered_style": ParagraphStyle(
            "Centered",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            alignment=1,  # 1 = center alignment
            textColor=colors.black,
        ),
    }
    
    return custom_styles

def create_header_left_table(data, styles):
    """Create the left part of the header section."""
    return Table(
        [
            [
                Paragraph(
                    "ENTGELTABRECHNUNG",
                    ParagraphStyle(
                        "Title",
                        parent=styles["micro_style"],
                        fontSize=8,
                        fontName="Helvetica-Bold",
                    ),
                )
            ],
            [
                Paragraph(
                    f"für den Zeitraum vom {data['abrechnungsdetails']['pay_period'].replace(' / ', '.12.2025 bis 31.')}.2025",
                    styles["micro_style"],
                )
            ],
            [
                Paragraph(
                    f"im Monat {data['abrechnungsdetails']['pay_period']} {data['abrechnungsdetails']['payroll_date']} Seite 1/1",
                    styles["micro_style"],
                )
            ],
            [Spacer(1, 0.1 * cm)],
            [Paragraph(data["arbeitgeber"]["unternehmen"], styles["bold_style"])],
            [Paragraph(data["arbeitgeber"]["unternehmen_adresse"], styles["micro_style"])],
            [Spacer(1, 0.2 * cm)],  # Add a small space between addresses
            [Paragraph(data["arbeitnehmer"]["gender"], styles["bold_style"])],
            [Paragraph(data["arbeitnehmer"]["name"], styles["normal_style"])],
            [Paragraph(data["arbeitnehmer"]["adresse"], styles["micro_style"])],
        ],
        colWidths=[10 * cm],
        style=TableStyle([("BOTTOMPADDING", (0, 0), (-1, -1), 5)]),
    )


def create_header_right_table(data):
    """Create the right part of the header section with personal/organizational data."""
    return Table(
        [
            [Paragraph("<b>Persönliche / Organisatorische Daten</b>", ParagraphStyle("Bold", fontSize=7)), "", "", ""],
            [
                "Personalnummer",
                "Kostenstelle",
                "Tarifgruppe/-sufe",
                "Beschäftigungsgrad",
            ],
            [data["arbeitnehmer"]["personal_nummer"], data["arbeitgeber"]["kostenstelle"], "OT /", "100,00"],
            ["Geburtsdatum", "Eintritt", "Austritt", "Steuer-ID"],
            [
                data["arbeitnehmer"]["geburtsdatum"],
                data["arbeitnehmer"]["eintrittsdatum"],
                "",
                data["arbeitnehmer"]["steuer_id"],
            ],
            ["Steuerklasse", "Faktor", "Kinderfreibeträge", "Konfession AN/EG"],
            [data["arbeitnehmer"]["steuerklasse"], "0,0", "", "-- /"],
            ["KV-Prozentsatz", "RV-Prozentsatz", "AV-Prozentsatz", "PV-Prozentsatz"],
            [
                data["arbeitnehmer"]["kv_prozentsatz"],
                data["arbeitnehmer"]["rv_prozentsatz"],
                data["arbeitnehmer"]["av_prozentsatz"],
                data["arbeitnehmer"]["pv_prozentsatz"],
            ],
            ["Krankenkasse", "Bgrs", "RV-Nummer", ""],
            [
                data["arbeitnehmer"]["krankenkasse"],
                data["arbeitnehmer"]["beitragsgruppenschluessel"],
                data["arbeitnehmer"]["sv_nummer"],
                "",
            ],
        ],
        colWidths=[2.0 * cm, 2.0 * cm, 2.0 * cm, 3.0 * cm],
        style=TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 6),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.black),
                ("SPAN", (0, 0), (3, 0)),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("LINEBELOW", (0, 1), (-1, 1), 0.5, colors.black),
                ("LINEABOVE", (0, 3), (-1, 3), 0.5, colors.black),
                # Background styles for alternating rows
                ("BACKGROUND", (0, 0), (3, 0), colors.lightgrey),
                ("BACKGROUND", (0, 1), (-1, 1), colors.lightgrey),
                ("BACKGROUND", (0, 3), (-1, 3), colors.lightgrey),
                ("BACKGROUND", (0, 5), (-1, 5), colors.lightgrey),
                ("BACKGROUND", (0, 7), (-1, 7), colors.lightgrey),
                ("BACKGROUND", (0, 9), (-1, 9), colors.lightgrey),
            ]
        ),
    )


def format_currency(value):
    """Format currency values according to German standards."""
    if value is None:
        return ""
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def create_lohnart_table(data, bold_style, normal_style):
    """Create the main salary table with all components."""
    # Entire Lohnart data
    lohnart_data = [
        # Header
        ["Lohnart", "", "", "", "", "Betrag", "Jahreswert"],
        # Section Headers
        [
            Paragraph("<b>Basisbezüge:</b>", bold_style),
            Paragraph("<b>Kenn.</b>", bold_style),
            Paragraph("<b>Anzahl</b>", bold_style),
            Paragraph("<b>Betrag/E</b>", bold_style),
            Paragraph("<b>Zusatz</b>", bold_style),
            "",
            "",
        ],
        [
            f"1005 {data['verdienst']['lohn_bezeichnung']}",
            "LSG",
            "1",
            "",
            "",
            format_currency(data["verdienst"]["betrag"]),
            format_currency(data["verdienst"]["gesamt_brutto"]),
        ],
        ["Zusätze:", "", "", "", "", "", ""],
        ["2301 GWV KV Zusatz MA", "LSG", "", "", "", "3,17", ""],
        ["2GUV Gruppenunfallversicherung", "", "", "6,57", "", "6,57", "6,57"],
        ["2072 SB 88 BENEFITS-Pass", "LSG", "", "", "", "40,00", ""],
        # ===== Bruttoentgelt Section ======
        [
            Paragraph("<b>Bruttoentgelt:</b>", bold_style),
            "",
            Paragraph("<b>Lfd.Bez:</b>", bold_style),
            Paragraph("<b>Ein.Bez:</b>", bold_style),
            Paragraph("<b>Summe:</b>", bold_style),
            "",
            "",
        ],
        [
            "Z10E Gesamtbrutto",
            "",
            "",
            "",
            "",
            format_currency(data["verdienst"]["gesamt_brutto"]),
            format_currency(data["verdienst"]["gesamt_brutto"]),
        ],
        [
            "ZSBS Steuerbrutto",
            "",
            format_currency(data["steuern_sozialversicherung"]["steuer_brutto"]),
            "",
            "",
            format_currency(data["steuern_sozialversicherung"]["steuer_brutto"]),
            format_currency(data["steuern_sozialversicherung"]["steuer_brutto"]),
        ],
        ["ZSTG Pausch ST-Brutto AG", "", "", "", "", "0,00", "0,00"],
        [
            "ZKBS SV-Brutto KV/PV",
            "",
            format_currency(data["steuern_sozialversicherung"]["kv_brutto"]),
            "",
            format_currency(data["steuern_sozialversicherung"]["kv_brutto"]),
            "",
            format_currency(data["steuern_sozialversicherung"]["kv_brutto"]),
        ],
        [
            "ZRBS SV-Brutto RV",
            "",
            format_currency(data["steuern_sozialversicherung"]["rv_brutto"]),
            "",
            format_currency(data["steuern_sozialversicherung"]["rv_brutto"]),
            "",
            format_currency(data["steuern_sozialversicherung"]["rv_brutto"]),
        ],
        [
            "ZRBS SV-Brutto AV",
            "",
            format_currency(data["steuern_sozialversicherung"]["av_brutto"]),
            "",
            format_currency(data["steuern_sozialversicherung"]["av_brutto"]),
            "",
            format_currency(data["steuern_sozialversicherung"]["av_brutto"]),
        ],
        # Gesetzliche Abzüge Section
        [Paragraph("<b>Gesetzliche Abzüge:</b>", bold_style), "", "", "", "", "", ""],
        [
            "ZLSS Lohnsteuer",
            "",
            format_currency(data["steuern_sozialversicherung"]["lohnsteuer"]) + "-",
            "",
            "",
            format_currency(data["steuern_sozialversicherung"]["lohnsteuer"]) + "-",
            "",
        ],
        [
            "ZKVS Krankenversicherung",
            "",
            format_currency(data["steuern_sozialversicherung"]["kv_beitrag"]) + "-",
            "",
            "",
            format_currency(data["steuern_sozialversicherung"]["kv_beitrag"]) + "-",
            "",
        ],
        [
            "ZRVS Rentenversicherung",
            "",
            format_currency(data["steuern_sozialversicherung"]["rv_beitrag"]) + "-",
            "",
            "",
            format_currency(data["steuern_sozialversicherung"]["rv_beitrag"]) + "-",
            "",
        ],
        [
            "ZAVS Arbeitslosenversicherung",
            "",
            format_currency(data["steuern_sozialversicherung"]["av_beitrag"]) + "-",
            "",
            "",
            format_currency(data["steuern_sozialversicherung"]["av_beitrag"]) + "-",
            "",
        ],
        [
            "ZPVS Pflegeversicherung",
            "",
            format_currency(data["steuern_sozialversicherung"]["pv_beitrag"]) + "-",
            "",
            "",
            format_currency(data["steuern_sozialversicherung"]["pv_beitrag"]) + "-",
            "",
        ],
        # Netto Section
        [
            Paragraph("<b>Netto:</b>", bold_style),
            "",
            "",
            "",
            "",
            format_currency(data["steuern_sozialversicherung"]["netto_verdienst"]),
            "",
        ],
        ["Gesetzliches Netto", "", "", "", "", "", ""],
        # Be- und Abzüge Section
        [Paragraph("<b>Be- und Abzüge:</b>", bold_style), "", "", "", "", "", ""],
        ["2301 GWV KV Zusatz MA", "", "", "", "", "3,17-", ""],
        ["ZGUV Gruppenunfallversicherung", "", "", "", "", "6,57-", ""],
        ["2072 SB 88 BENEFITS-Pass", "", "", "", "", "40,00-", ""],
        [
            "/408 LSt pausch AG",
            "",
            "",
            "",
            "",
            format_currency(data["zahlungsdetails"]["sv_ag_anteil"]),
            format_currency(data["zahlungsdetails"]["sv_ag_anteil"]),
        ],
        # Zahlungen Section
        [Paragraph("<b>Zahlungen:</b>", bold_style), "", "", "", "", "", ""],
        [
            "/559 Überweisung",
            "",
            "",
            "",
            "",
            format_currency(data["zahlungsdetails"]["auszahlungsbetrag"]) + " EUR",
            "",
        ],
        [
            data["zahlungsdetails"]["bank_employee"],
            f"BLZ: {data['zahlungsdetails']['bankleitzahl']}",
            "",
            f"Kto: {data['zahlungsdetails']['Kto']}",
            "",
            "",
        ],
        ["", data["zahlungsdetails"]["iban_employee"], "", "", "", "", ""],
    ]

    # Create the table with adjusted column widths
    lohnart_table = Table(
        lohnart_data,
        colWidths=[5 * cm, 1.5 * cm, 1.5 * cm, 2 * cm, 1.5 * cm, 2.5 * cm, 2.5 * cm],
    )

    # Custom style to match the borderless look
    lohnart_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("BACKGROUND", (0, 0), (6, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 1), (0, -1), colors.black),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (0, -1), 9),
                ("LINEAFTER", (4, 0), (5, -1), 0.5, colors.black),
            ]
        )
    )

    return lohnart_table


def create_payslip(filename, data):
    """Create a PDF payslip with the given data."""
    # Set up the document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.0 * cm,
        bottomMargin=1.0 * cm,
    )

    # Get common styles
    styles = create_custom_styles()
    elements = []

    # Add vertical Space at the top
    elements.append(Spacer(1, 0.5 * cm))

    # Create header tables
    header_left_table = create_header_left_table(data, styles)
    header_right_table = create_header_right_table(data)
    
    # Combine header tables
    header_personal_table = Table(
        [[header_left_table, header_right_table]],
        colWidths=[10 * cm, 10 * cm],
        rowHeights=[5.5 * cm],
        style=TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        ),
    )
    elements.append(header_personal_table)

    # Add space after the header
    elements.append(Spacer(1, 1.1 * cm))

    # Add main salary table
    lohnart_table = create_lohnart_table(data, styles["bold_style"], styles["normal_style"])
    elements.append(lohnart_table)

    # Add footer section
    elements.append(Spacer(1, 1 * cm))
    
    # Footer text paragraphs
    elements.append(
        Paragraph(
            "Wenn du Fragen zu deiner Verdienstabrechnung hast, dann nutze bitte das HR Serviceportal. Dies findest du im Self-Service-Portal in<br/>"
            "Confluence unter 'Viel genutzt'- Human Resources.",
            styles["centered_style"],
        )
    )
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(
        Paragraph(
            "Bescheinigung gemäß § 108 Absatz 3 Satz 1 Gewerbeordnung. Bitte sorgfältig aufbewahren.<br/>"
            "Kennzeichen: (E)inmalzahlung, (L)ohnsteuer-, (S)V-pflichtig, (G)esamtbrutto",
            styles["centered_style"],
        )
    )

    elements.append(PageBreak())
    
    # Adjust bottom margin to ensure content fits
    doc.bottomMargin = 0.5 * cm

    # Build PDF
    doc.build(elements)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate PDF payslips from JSON data')
    parser.add_argument('--input', type=str, default='test_data', help='Input directory with JSON files')
    parser.add_argument('--output', type=str, default=None, help='Output directory for PDFs (default: same as input)')
    
    args = parser.parse_args()
    
    print(f"Generating PDFs from JSON files in {args.input}...")
    generate_pdfs_from_json(args.input, args.output)
    print("Done!")