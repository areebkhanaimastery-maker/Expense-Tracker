#!/usr/bin/env python3
"""
Generate Synthetic Expense Dataset.

This script populates the SQLite database with realistic expense records
covering historical data (default 24 months). It models realistic PKRs,
weekday vs. weekend patterns, growth/inflation over time, monthly bills,
periodic education fees, and rare outliers for anomaly detection.
"""

import sys
from pathlib import Path

# Add project root to PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import argparse
import random
from collections import defaultdict
from datetime import datetime, timedelta

from app.config import settings
from app.models.expense import Expense
from app.repositories.sqlite_repository import SQLiteExpenseRepository
from app.validators.expense_validator import (
    validate_amount,
    validate_category,
    validate_description,
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate realistic synthetic expenses for Expense Tracker."
    )
    parser.add_argument(
        "--records",
        type=int,
        default=3500,
        help="Target number of total records to generate (default: 3500).",
    )
    parser.add_argument(
        "--months",
        type=int,
        default=24,
        help="Number of months of historical data (default: 24).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42).",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="Path to SQLite database (defaults to config settings).",
    )
    return parser.parse_args()


def generate_amount(category: str, is_outlier: bool, ratio: float) -> float:
    """
    Generate a realistic amount in PKR skewing towards smaller values.
    
    Uses power mapping u^k to make small expenses occur frequently.
    Also models inflation (for Food) and seasonal multipliers (for Shopping).
    """
    u = random.random()

    if is_outlier:
        if category == "Shopping":
            amount = 80000 + (250000 - 80000) * u
        elif category == "Health":
            amount = 100000 + (450000 - 100000) * u
        elif category == "Education":
            amount = 120000 + (400000 - 120000) * u
        else:  # Other
            amount = 60000 + (200000 - 60000) * u
        return round(amount, 2)

    # Base ranges and skew factors (k > 1 skews heavily towards the minimum value)
    if category == "Food":
        min_val, max_val, k = 150, 8000, 3.0
    elif category == "Transport":
        min_val, max_val, k = 100, 6000, 3.0
    elif category == "Shopping":
        min_val, max_val, k = 500, 50000, 4.0
    elif category == "Bills":
        # Mobile recharge or minor bills (regular monthly bills are handled separately)
        min_val, max_val, k = 200, 2000, 2.0
    elif category == "Entertainment":
        min_val, max_val, k = 300, 15000, 3.0
    elif category == "Health":
        min_val, max_val, k = 300, 30000, 4.0
    elif category == "Education":
        # General stationeries or small courses
        min_val, max_val, k = 500, 15000, 4.0
    else:  # Other
        min_val, max_val, k = 100, 25000, 3.0

    amount = min_val + (max_val - min_val) * (u ** k)

    # Apply temporal patterns:
    # 1. Food spending gradually increases (simulating 40% inflation/growth over the date range)
    if category == "Food":
        inflation_factor = 1.0 + 0.4 * ratio
        amount *= inflation_factor

    return round(amount, 2)


def get_description(category: str, amount: float, is_outlier: bool) -> str:
    """Generate a realistic description based on the category and amount."""
    if is_outlier:
        outlier_descriptions = {
            "Shopping": [
                "Flagship Smartphone Purchase",
                "Designer Wedding Shalwar Kameez",
                "Living Room Sofa Set",
                "Home Air Conditioner Unit",
            ],
            "Health": [
                "Emergency Hospitalization & Care",
                "Dental Implant Surgery Fee",
                "Laser Eye Corrective Surgery",
                "MRI Scan and Specialist Consultation",
            ],
            "Education": [
                "International Professional Certification",
                "University Semester Tuition Fee Outlier",
                "High-end Laptop for Engineering Classes",
            ],
            "Other": [
                "Generator Repair and Engine Overhaul",
                "Home Security CCTV System Installation",
                "Professional DSLR Camera Kit",
                "Emergency House Water Tank Reconstruction",
            ],
        }
        return random.choice(outlier_descriptions.get(category, ["Unanticipated Large Expense"]))

    # Standard descriptions
    if category == "Food":
        if amount < 500:
            return random.choice(["Office Samosa & Chai", "Evening Coffee", "Soft Drinks & Chips", "Naan Chanay Breakfast"])
        elif amount < 2000:
            return random.choice(["Lunch at Canteen", "Foodpanda Burger Meal", "Local Groceries", "Pizza Slice & Drink"])
        else:
            return random.choice(["Dinner at Bistro Restaurant", "Supermarket Groceries Run", "Family Buffet Dinner", "KFC Family Bucket"])

    elif category == "Transport":
        if amount < 500:
            return random.choice(["Bykea Ride", "Metro Bus Fare", "Local Rickshaw Commute"])
        elif amount < 1500:
            return random.choice(["Uber Ride to Office", "Careem Ride to Mall", "Office Pick-up Taxi"])
        else:
            return random.choice(["Fuel Refill (Car)", "Car Oil & Filter Change", "Car Wash and Detail"])

    elif category == "Shopping":
        if amount < 2000:
            return random.choice(["Casual T-Shirt", "Socks Multi-Pack", "Kitchen Spatula & Bowls"])
        elif amount < 10000:
            return random.choice(["Leather Shoes from Borjan", "Denim Jeans", "Cotton Bedsheet Set"])
        else:
            return random.choice(["Winter Leather Jacket", "Designer Kurta", "Microwave Oven", "Room Air Cooler"])

    elif category == "Bills":
        return random.choice(["Mobile Recharge (Jazz)", "Mobile Recharge (Zong)", "Mobile Recharge (Telenor)"])

    elif category == "Entertainment":
        if amount < 1000:
            return random.choice(["Netflix Monthly Plan", "Spotify Premium Family", "Arcade Tokens"])
        elif amount < 4000:
            return random.choice(["Nueplex Movie Tickets", "Liberty Books Novel", "Bowling Session with Friends"])
        else:
            return random.choice(["Concert Entry Pass", "Amusement Park Family Ticket", "Weekend Getaway Resort Fee"])

    elif category == "Health":
        if amount < 1500:
            return random.choice(["Panadol & Cough Syrup", "Multivitamins Pack", "First Aid Ointments"])
        elif amount < 6000:
            return random.choice(["General Physician Checkup", "Chughtai Lab Blood Test", "Reading Glasses Prescription"])
        else:
            return random.choice(["Root Canal Dental Treatment", "Physiotherapist Consultation", "Specialized MRI Scan"])

    elif category == "Education":
        if amount < 3000:
            return random.choice(["Notebooks & Stationery", "Online Python Course on Udemy", "Photocopying & Notes"])
        elif amount < 15000:
            return random.choice(["University Reference Textbook", "Academic Exam Registration", "Calculus & Algebra Reference Books"])
        else:
            return random.choice(["Short Certificate Tuition Fee", "IELTS Prep Material & Mock Tests"])

    else:  # Other
        if amount < 1500:
            return random.choice(["Laundry Service", "Home Carpet Cleaning", "Duplicate Door Key Locksmith"])
        elif amount < 8000:
            return random.choice(["Plumber Repair Charges", "Electrician Service Fee", "House Cleaning Supplies"])
        else:
            return random.choice(["Smart Phone Screen Replacement", "Gas Geyser Valve Repair", "Sadqah / Charity Donation"])


def generate_synthetic_dataset(
    target_count: int, months_back: int, seed: int
) -> tuple[list[Expense], int]:
    """
    Generate list of synthetic Expense objects with realistic distributions and temporal patterns.
    
    Returns (expenses_list, outlier_count).
    """
    random.seed(seed)
    
    # Anchor the end date to a fixed datetime for reproducibility and idempotency across runs
    end_date = datetime(2026, 8, 13, 12, 0, 0)
    start_date = (end_date - timedelta(days=30 * months_back)).replace(microsecond=0)

    # 1. Generate all dates day-by-day
    all_dates: list[datetime] = []
    curr = start_date
    while curr <= end_date:
        all_dates.append(curr)
        curr += timedelta(days=1)

    # Group dates by month to allocate monthly utility bills
    dates_by_month: dict[tuple[int, int], list[datetime]] = defaultdict(list)
    for dt in all_dates:
        dates_by_month[(dt.year, dt.month)].append(dt)

    fixed_expenses: list[Expense] = []
    outlier_count = 0

    # 2. Generate deterministic monthly utility bills
    for (year, month), dates in dates_by_month.items():
        # First week dates
        first_week_dates = [d for d in dates if d.day <= 8]
        if not first_week_dates:
            first_week_dates = dates[:3]

        # Monthly electricity bill (10,000 - 40,000)
        elec_date = random.choice(first_week_dates)
        elec_hour = random.randint(9, 17)
        elec_dt = elec_date.replace(hour=elec_hour, minute=random.randint(0, 59), second=random.randint(0, 59))
        elec_amount = round(10000.0 + random.random() * 30000.0, 2)
        fixed_expenses.append(
            Expense(
                id=0,
                amount=elec_amount,
                category="Bills",
                description="Electricity Bill",
                date=elec_dt
            )
        )

        # Monthly internet bill (2,500 - 8,000)
        net_date = random.choice(first_week_dates)
        net_hour = random.randint(9, 17)
        net_dt = net_date.replace(hour=net_hour, minute=random.randint(0, 59), second=random.randint(0, 59))
        net_amount = round(2500.0 + random.random() * 5500.0, 2)
        fixed_expenses.append(
            Expense(
                id=0,
                amount=net_amount,
                category="Bills",
                description="Monthly Internet Bill",
                date=net_dt
            )
        )

        # Sui Gas Bill (1,500 - 8,000)
        gas_date = random.choice(first_week_dates)
        gas_hour = random.randint(9, 17)
        gas_dt = gas_date.replace(hour=gas_hour, minute=random.randint(0, 59), second=random.randint(0, 59))
        gas_amount = round(1500.0 + random.random() * 6500.0, 2)
        fixed_expenses.append(
            Expense(
                id=0,
                amount=gas_amount,
                category="Bills",
                description="Sui Gas Bill",
                date=gas_dt
            )
        )

        # Semester Tuition Fee: university semester starts in February (Month 2) and September (Month 9)
        # Occurs twice a year
        if month in (2, 9):
            sem_date = random.choice(dates)
            sem_hour = random.randint(9, 15)
            sem_dt = sem_date.replace(hour=sem_hour, minute=random.randint(0, 59), second=random.randint(0, 59))
            sem_amount = round(150000.0 + random.random() * 250000.0, 2)
            fixed_expenses.append(
                Expense(
                    id=0,
                    amount=sem_amount,
                    category="Education",
                    description="University Semester Tuition Fee",
                    date=sem_dt
                )
            )

    # 3. Generate remaining random expenses based on probability weights
    remaining_count = target_count - len(fixed_expenses)
    if remaining_count < 0:
        remaining_count = 0

    # Calculate day-of-week and month weights for selecting dates
    weights = []
    for dt in all_dates:
        w = 1.0
        # Month multipliers (Seasonal changes)
        if dt.month in (11, 12):  # Nov, Dec (spikes for shopping & end-of-year holidays)
            w *= 1.3
        elif dt.month in (6, 7):  # Jun, Jul (slight spike for summer)
            w *= 1.1
        
        # Day of week multiplier (More active on weekends)
        if dt.weekday() in (5, 6):  # Sat, Sun
            w *= 1.4
            
        weights.append(w)

    chosen_dates = random.choices(all_dates, weights=weights, k=remaining_count)
    # Sort dates to ensure chronological processing
    chosen_dates.sort()

    random_expenses: list[Expense] = []
    total_time_span = (end_date - start_date).total_seconds()

    for dt in chosen_dates:
        # Assign a realistic hour/minute/second
        # Generally active hours are 8:00 to 23:00
        hour = random.randint(8, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        expense_dt = dt.replace(hour=hour, minute=minute, second=second)

        weekday = expense_dt.weekday()
        is_weekend = (weekday in (5, 6))

        # Select category based on weekday vs. weekend patterns
        if not is_weekend:
            # More Transport, Food, less Shopping/Entertainment
            categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Education", "Other"]
            cat_weights = [0.30, 0.35, 0.08, 0.08, 0.05, 0.06, 0.04, 0.04]
        else:
            # Less Transport, more Food, Shopping, Entertainment
            categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Education", "Other"]
            cat_weights = [0.42, 0.08, 0.22, 0.02, 0.16, 0.04, 0.01, 0.05]

        category = random.choices(categories, weights=cat_weights, k=1)[0]

        # Model Outliers: 0.5% rate in realistic categories
        is_outlier = False
        if category in ("Shopping", "Health", "Education", "Other") and random.random() < 0.005:
            is_outlier = True
            outlier_count += 1

        # Calculate time ratio for inflation/gradual growth
        elapsed_seconds = (expense_dt - start_date).total_seconds()
        ratio = elapsed_seconds / total_time_span if total_time_span > 0 else 0.0

        # Generate amount and description
        amount = generate_amount(category, is_outlier, ratio)
        
        # Apply Shopping spike multiplier in Nov/Dec
        if category == "Shopping" and expense_dt.month in (11, 12) and not is_outlier:
            amount = round(amount * 1.25, 2)

        description = get_description(category, amount, is_outlier)

        random_expenses.append(
            Expense(
                id=0,
                amount=amount,
                category=category,
                description=description,
                date=expense_dt
            )
        )

    # Combine all generated expenses and sort by date
    all_generated = fixed_expenses + random_expenses
    all_generated.sort(key=lambda e: e.date)

    return all_generated, outlier_count


def validate_expenses(expenses: list[Expense]) -> None:
    """Validate all generated expenses using project validator logic."""
    for i, exp in enumerate(expenses):
        try:
            validate_amount(exp.amount)
            validate_category(exp.category)
            validate_description(exp.description)
        except Exception as e:
            print(f"Validation failed at index {i}: Expense({exp.amount}, {exp.category}, {exp.description}, {exp.date})")
            raise e


def insert_expenses_safely(repository: SQLiteExpenseRepository, expenses: list[Expense]) -> int:
    """
    Insert expenses to database using a single transaction.
    
    Maintains database safety: ignores records that match existing signatures
    (same amount, category, description, and date) to prevent duplicate runs.
    """
    # Retrieve existing records to verify duplicates
    existing_rows = repository.get_all()
    existing_signatures = {
        (e.amount, e.category, e.description, e.date.isoformat())
        for e in existing_rows
    }

    expenses_to_insert = [
        e for e in expenses
        if (e.amount, e.category, e.description, e.date.isoformat()) not in existing_signatures
    ]

    if not expenses_to_insert:
        return 0

    with repository._connect() as connection:
        connection.execute("BEGIN")
        try:
            connection.executemany(
                """
                INSERT INTO expenses (amount, category, description, date)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (e.amount, e.category, e.description, e.date.isoformat())
                    for e in expenses_to_insert
                ]
            )
            connection.commit()
        except Exception as err:
            connection.execute("ROLLBACK")
            raise err

    return len(expenses_to_insert)


def print_validation_report(expenses: list[Expense]) -> None:
    """Print the summary statistics matching the required format."""
    total_records = len(expenses)
    if total_records == 0:
        print("No records generated.")
        return

    total_spending = sum(e.amount for e in expenses)
    avg_expense = total_spending / total_records
    min_expense = min(e.amount for e in expenses)
    max_expense = max(e.amount for e in expenses)

    # Category percentages
    cat_counts = defaultdict(int)
    for e in expenses:
        cat_counts[e.category] += 1
    
    sorted_categories = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)

    # Monthly totals
    monthly_totals = defaultdict(float)
    monthly_counts = defaultdict(int)
    for e in expenses:
        m_key = e.date.strftime("%Y-%m")
        monthly_totals[m_key] += e.amount
        monthly_counts[m_key] += 1

    sorted_months = sorted(monthly_totals.keys())

    print("\nSynthetic Dataset Generated")
    print("---------------------------")
    print(f"Records: {total_records:,}")
    print(f"Total: Rs. {total_spending:,.2f}")
    print(f"Average: Rs. {avg_expense:,.2f}")
    print(f"Minimum: Rs. {min_expense:,.2f}")
    print(f"Maximum: Rs. {max_expense:,.2f}")
    print("\nCategory Distribution:")
    for cat, count in sorted_categories:
        percentage = (count / total_records) * 100
        print(f"{cat}: {percentage:.1f}%")

    print("\nMonthly Distribution:")
    for m_key in sorted_months:
        m_total = monthly_totals[m_key]
        m_cnt = monthly_counts[m_key]
        print(f"{m_key}: Rs. {m_total:,.2f} ({m_cnt:,} records)")


def main() -> None:
    """Main execution block."""
    args = parse_args()

    print(f"Generating synthetic dataset of approx {args.records} records spanning {args.months} months...")
    print(f"Using random seed: {args.seed}")

    # 1. Generate the dataset
    expenses, outlier_count = generate_synthetic_dataset(args.records, args.months, args.seed)
    
    # 2. Validate the dataset
    validate_expenses(expenses)
    
    # 3. Initialize repository
    db_path = args.db_path or settings.database_path
    print(f"Using database: {db_path}")
    repository = SQLiteExpenseRepository(db_path)

    # 4. Insert records safely
    inserted_count = insert_expenses_safely(repository, expenses)
    print(f"Database insertion complete. Newly inserted records: {inserted_count:,}")
    if inserted_count == 0:
        print("Note: 0 records were inserted because identical synthetic data was already found in the database (Idempotent bypass).")

    # 5. Print Summary Report
    print_validation_report(expenses)
    print(f"Number of outlier records: {outlier_count}")


if __name__ == "__main__":
    main()
