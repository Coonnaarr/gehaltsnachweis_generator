import json
import os
import random
import copy
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker with German locale
fake = Faker('de_DE')

def generate_employee_data():
    """Generate random employee data using Faker."""
    gender = "Herr" if fake.boolean(chance_of_getting_true=60) else "Frau"
    first_name = fake.first_name_male() if gender == "Herr" else fake.first_name_female()
    last_name = fake.last_name()
    
    return {
        "gender": gender,
        "name": f"{first_name} {last_name}",
        "adresse": fake.address().replace('\n', ', '),
        "personal_nummer": f"22{fake.random_number(digits=6)}",
        "geburtsdatum": fake.date_of_birth(minimum_age=20, maximum_age=65).strftime("%Y-%m-%d"),
        "steuerklasse": str(random.randint(1, 6)),
        "eintrittsdatum": fake.date_between(start_date="-10y", end_date="today").strftime("%d.%m.%Y"),
        "urlaubstage": random.randint(24, 30),
        "sv_nummer": f"{fake.random_number(digits=8)}{last_name[0].upper()}{fake.random_number(digits=3)}",
        "krankenkasse": random.choice(["Techniker KK", "AOK", "Barmer", "DAK", "IKK"]),
        "beitragsgruppenschluessel": "1111",
        "steuer_id": f"7{fake.random_number(digits=10)}",
        "kv_prozentsatz": f"{random.uniform(7.8, 8.5):.2f} %",
        "rv_prozentsatz": "9.30 %",
        "av_prozentsatz": f"{random.uniform(1.2, 1.3):.2f} %",
        "pv_prozentsatz": f"{random.uniform(1.7, 1.9):.4f} %",
    }

def generate_bank_details():
    """Generate random bank details using Faker."""
    return {
        "bank_employee": fake.company() + " Bank",
        "iban_employee": fake.iban(),
        "bankleitzahl": f"{fake.random_number(digits=8)}",
        "Kto": f"{fake.random_number(digits=10)}",
    }

def calculate_financial_data(base_salary):
    """Calculate financial data based on base salary."""
    # Slightly higher than base for gross
    gesamt_brutto = round(base_salary * 1.0083, 2)
    steuer_brutto = round(base_salary * 1.0005, 2)
    
    # Tax calculation (simplified)
    tax_rate = 0.118
    lohnsteuer = round(steuer_brutto * tax_rate, 2)
    
    # Social security bases
    kv_brutto = round(base_salary * 0.9187, 2)
    rv_brutto = steuer_brutto
    av_brutto = steuer_brutto
    pv_brutto = kv_brutto
    
    # Social security contributions (simplified ratios)
    kv_beitrag = round(kv_brutto * 0.0825, 2)  # 8.25%
    rv_beitrag = round(rv_brutto * 0.093, 2)   # 9.30%
    av_beitrag = round(av_brutto * 0.013, 2)   # 1.30%
    pv_beitrag = round(pv_brutto * 0.018, 2)   # 1.80%
    
    # Total social contributions
    sv_total = kv_beitrag + rv_beitrag + av_beitrag + pv_beitrag
    
    # Net salary
    netto_verdienst = round(gesamt_brutto - lohnsteuer - sv_total, 2)
    
    # Final payout amount
    additional_deductions = 49.74  # GWV KV + insurance + benefits
    auszahlungsbetrag = round(netto_verdienst - additional_deductions, 2)
    
    # Create the financial data structure
    return {
        "verdienst": {
            "lohn_art": "Grundgehalt",
            "lohn_bezeichnung": "Monatsgehalt",
            "betrag": base_salary,
            "gesamt_brutto": gesamt_brutto,
        },
        "steuern_sozialversicherung": {
            "steuer_brutto": steuer_brutto,
            "steuerrechtliche_abzüge": lohnsteuer,
            "lohnsteuer": lohnsteuer,
            "kv_brutto": kv_brutto,
            "rv_brutto": rv_brutto,
            "av_brutto": av_brutto,
            "pv_brutto": kv_brutto,
            "kv_beitrag": kv_beitrag,
            "rv_beitrag": rv_beitrag,
            "av_beitrag": av_beitrag,
            "pv_beitrag": pv_beitrag,
            "sv_rechtliche_abzüge": round(sv_total, 2),
            "netto_verdienst": netto_verdienst,
        },
        "be_und_abzuege": {"gruppenunfallversicherung": "6,57"},
        "jahresübersicht": {
            "gesamt_jahres_brutto": round(gesamt_brutto * 12, 2),
            "gesamt_steuer_brutto": round(steuer_brutto * 12, 2),
            "lohnsteuer": round(lohnsteuer * 12, 2),
            "kirchensteuer": 0.00,
            "solidaritätszuschlag": 0.60,
            "steuerfreie_bezüge": 0.00,
            "sv_brutto": round(rv_brutto * 12, 2),
            "kv_beitrag": round(kv_beitrag * 12, 2),
            "rv_beitrag": round(rv_beitrag * 12, 2),
            "av_beitrag": round(av_beitrag * 12, 2),
            "pv_beitrag": round(pv_beitrag * 12, 2),
        },
        "zahlungsdetails": {
            "sv_ag_anteil": 1.05,
            "auszahlungsbetrag": auszahlungsbetrag,
        },
    }

def generate_payslip_data(base_salary=None):
    """Generate complete payslip data for one employee and one month."""
    # Company data - could be made variable too
    company_data = {
        "arbeitgeber": {
            "unternehmen": fake.company(),
            "unternehmen_adresse": fake.street_address() + ", " + fake.postcode() + " " + fake.city(),
            "kostenstelle": f"SV{fake.random_number(digits=6)}",
        }
    }
    
    # Generate random employee data
    employee_data = {"arbeitnehmer": generate_employee_data()}
    
    # Generate random bank details
    bank_details = generate_bank_details()
    
    # If no base salary provided, generate one
    if base_salary is None:
        base_salary = round(random.uniform(3000, 8000), 2)
    
    # Calculate financial data based on the base salary
    financial_data = calculate_financial_data(base_salary)
    
    # Combine all data
    payslip_data = {
        **company_data,
        **employee_data,
        "abrechnungsdetails": {
            "title": "Lohnabrechnung",
            "pay_period": "01 / 2025",  # Will be updated per month
            "payroll_date": "31.01.2025",  # Will be updated per month
        },
        **financial_data,
    }
    
    # Update zahlungsdetails with bank information
    payslip_data["zahlungsdetails"].update(bank_details)
    
    return payslip_data

def generate_test_data(num_employees=5, months_per_employee=3, output_dir="test_data"):
    """Generate test data for multiple employees across multiple months."""
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    all_datasets = []
    
    for emp_id in range(num_employees):
        employee_dir = f"{output_dir}/employee_{emp_id+1}"
        if not os.path.exists(employee_dir):
            os.makedirs(employee_dir)
        
        # Generate base data for this employee
        base_data = generate_payslip_data()
        base_salary = base_data["verdienst"]["betrag"]
        
        employee_payslips = []
        
        # Generate data for each month
        for month in range(1, months_per_employee + 1):
            # Create a copy for this month
            month_data = copy.deepcopy(base_data)
            
            # Update month-specific information
            month_str = f"{month:02d}"
            month_data["abrechnungsdetails"]["pay_period"] = f"{month_str} / 2025"
            month_data["abrechnungsdetails"]["payroll_date"] = f"31.{month_str}.2025"
            
            # Optional: slight salary variation per month
            monthly_variation = round(random.uniform(-100, 100), 2)
            month_salary = max(2000, base_salary + monthly_variation)  # Ensure minimum wage
            
            # Recalculate financial data if salary varies
            if monthly_variation != 0:
                financial_data = calculate_financial_data(month_salary)
                # Update financial parts of the data
                month_data["verdienst"] = financial_data["verdienst"]
                month_data["steuern_sozialversicherung"] = financial_data["steuern_sozialversicherung"]
                month_data["jahresübersicht"] = financial_data["jahresübersicht"]
                month_data["zahlungsdetails"]["auszahlungsbetrag"] = financial_data["zahlungsdetails"]["auszahlungsbetrag"]
            
            # Create filename based on employee name
            clean_name = month_data["arbeitnehmer"]["name"].replace(' ', '_')
            json_filename = f"{employee_dir}/payslip_{clean_name}_{month_str}_2025.json"
            
            # Save as JSON
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(month_data, f, ensure_ascii=False, indent=2)
            
            # Record the filename
            employee_payslips.append(json_filename)
        
        all_datasets.append(employee_payslips)
        print(f"Generated {months_per_employee} payslips for {base_data['arbeitnehmer']['name']}")
    
    return all_datasets

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate payslip test data')
    parser.add_argument('--employees', type=int, default=5, help='Number of employees')
    parser.add_argument('--months', type=int, default=3, help='Number of months per employee')
    parser.add_argument('--output', type=str, default='test_data', help='Output directory')
    
    args = parser.parse_args()
    
    print(f"Generating test data for {args.employees} employees with {args.months} months each...")
    datasets = generate_test_data(
        num_employees=args.employees, 
        months_per_employee=args.months, 
        output_dir=args.output
    )
    
    print(f"Done! Generated {len(datasets)} employee datasets with {args.months} months each.")
    print(f"Output directory: {args.output}/")