"""
Simulates the ID generation logic from department/models.py and
employee/models.py without requiring a running Django instance.

Run:  python test_id_generation.py
"""

# ── Simulated in-memory stores ──────────────────────────────────────────────
_departments: list[dict] = []   # [{id, name, department_id}, ...]
_employees:   list[dict] = []   # [{id, name, department_id, employee_code}, ...]

# ── ID generators (mirror the real model helpers) ────────────────────────────

def generate_department_id(name: str) -> str:
    prefix = name.strip().upper().replace(" ", "")[:4].ljust(4, "X")
    next_number = len(_departments) + 1          # insertion-order counter
    suffix = str(next_number).zfill(2)
    return f"{prefix}{suffix}"


def generate_employee_code(dept: dict | None) -> str:
    dept_id = dept["department_id"] if dept else "UNKN00"

    global_count = len(_employees) + 1
    global_part  = str(global_count).zfill(6)

    dept_count = sum(
        1 for e in _employees if e["department_id"] == (dept["department_id"] if dept else None)
    ) + 1
    dept_part = str(dept_count).zfill(3)

    return f"{dept_id}-{global_part}-{dept_part}"


# ── Helper to add a department ────────────────────────────────────────────────

def add_department(name: str) -> dict:
    dept = {
        "id": len(_departments) + 1,
        "name": name,
        "department_id": generate_department_id(name),
    }
    _departments.append(dept)
    return dept


def get_department(name: str) -> dict | None:
    return next((d for d in _departments if d["name"] == name), None)


# ── Helper to add an employee ─────────────────────────────────────────────────

def add_employee(first_name: str, last_name: str, dept_name: str | None) -> dict:
    dept = get_department(dept_name) if dept_name else None
    emp = {
        "id": len(_employees) + 1,
        "name": f"{first_name} {last_name}",
        "department_id": dept["department_id"] if dept else None,
        "employee_code": generate_employee_code(dept),
    }
    _employees.append(emp)
    return emp


# ── Tests ─────────────────────────────────────────────────────────────────────

def run_tests():
    print("=" * 60)
    print("  ID Generation Logic — Simulation Tests")
    print("=" * 60)

    # ── Department IDs ───────────────────────────────────────────────────────
    print("\n── Departments ──")
    proc = add_department("Procurement")
    sale = add_department("Sales")
    hr   = add_department("Human Resources")
    fin  = add_department("Finance")

    for d in _departments:
        print(f"  {d['name']:<20} → {d['department_id']}")

    assert proc["department_id"] == "PROC01", f"Expected PROC01, got {proc['department_id']}"
    assert sale["department_id"] == "SALE02", f"Expected SALE02, got {sale['department_id']}"
    assert hr["department_id"]   == "HUMA03", f"Expected HUMA03, got {hr['department_id']}"
    assert fin["department_id"]  == "FINA04", f"Expected FINA04, got {fin['department_id']}"
    print("  ✓ All department IDs correct")

    # ── Employee codes ────────────────────────────────────────────────────────
    print("\n── Employees ──")
    #  Insertion order:
    #  1st → Procurement
    #  2nd → Sales
    #  3rd → Procurement   (global=3, dept=2)
    #  4th → Sales         (global=4, dept=2)
    #  5th → HR            (global=5, dept=1)
    #  6th → Procurement   (global=6, dept=3)
    #  7th → no dept       (global=7, dept=1 of UNKN00)

    scenarios = [
        ("Alice",   "Smith",  "Procurement",     "PROC01-000001-001"),
        ("Bob",     "Jones",  "Sales",           "SALE02-000002-001"),
        ("Carol",   "White",  "Procurement",     "PROC01-000003-002"),
        ("David",   "Brown",  "Sales",           "SALE02-000004-002"),
        ("Eve",     "Davis",  "Human Resources", "HUMA03-000005-001"),
        ("Frank",   "Miller", "Procurement",     "PROC01-000006-003"),
        ("Grace",   "Wilson", None,              "UNKN00-000007-001"),
    ]

    for first, last, dept_name, expected in scenarios:
        emp = add_employee(first, last, dept_name)
        status = "✓" if emp["employee_code"] == expected else "✗"
        print(f"  {status} {emp['name']:<15} dept={str(dept_name):<18} "
              f"code={emp['employee_code']}  (expected {expected})")
        assert emp["employee_code"] == expected, (
            f"FAIL: {emp['name']} → got {emp['employee_code']}, expected {expected}"
        )

    print("\n  ✓ All employee codes correct")
    print("\n" + "=" * 60)
    print("  All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()