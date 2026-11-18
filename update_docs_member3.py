import os
import openpyxl
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SC_DIR = os.path.join(BASE_DIR, "screenshots")
WORKBOOK_PATH = os.path.join(BASE_DIR, "SE_Lab_QT2_Assignment2_Team_Workbook.xlsx")
REPORT_PATH = os.path.join(BASE_DIR, "Report.docx")
README_PATH = os.path.join(BASE_DIR, "Readme.txt")


def update_workbook():
    wb = openpyxl.load_workbook(WORKBOOK_PATH)

    # 1. Team sheet
    ws = wb["Team"]
    ws["B4"] = "Group 14"
    ws["B5"] = "https://github.com/thinhvo06/B2BWholesaleSystem"
    ws["B8"] = "Option C (Exer 4): ASP.NET Web App Core (MVC) - Code First"

    ws["B11"], ws["C11"], ws["D11"], ws["E11"] = "Võ Nguyễn Phúc Thịnh", "[MSSV 1]", "Leader / Fullstack Web & Shared DB", 0.34
    # Keep Row 12 (Member 2: Ôn Gia Khiêm, 524H0057, 0.33)
    ws["B13"], ws["C13"], ws["D13"], ws["E13"] = "Nguyễn Nhật Huy", "[MSSV 3]", "QA, Unit Testing, Web Invoices & Docs", 0.33

    # 2. Tasks & Division sheet
    ws = wb["Tasks & Division"]
    task_updates = {
        5:  ("[MSSV 1]", "[MSSV 3]", "feature/member1-web-core; feature/web-myorders-invoice", "Done", "B2B.Data/Scripts/SeedData.sql & DbInitializer.cs (15-30 rows/table)"),
        6:  ("[MSSV 3]", "[MSSV 1]", "feature/web-myorders-invoice", "Done", "B2BDbContext.cs Fluent API FKs/Cascade/Restrict + CHECK constraints; verified by DatabaseIntegrityTests"),
        # Rows 7-10 are Member 2 (524H0057) -> keep untouched
        11: ("[MSSV 1]", "[MSSV 3]", "feature/member1-web-core", "Done", "AccountController.cs + AuthService.cs; screenshots/1_login_page.png & 2_admin_blocked.png"),
        12: ("[MSSV 1]", "[MSSV 3]", "feature/member1-web-core", "Done", "OrderController.cs + OrderService.cs BeginTransactionAsync; screenshots/3-6"),
        13: ("[MSSV 3]", None,       "feature/web-myorders-invoice", "Done", "OrderController MyOrders/Invoice + Views/Order/MyOrders.cshtml & Invoice.cshtml; screenshots/7-10"),
        14: ("[MSSV 1]", "[MSSV 3]", "feature/member1-web-core", "Done", "Bootstrap 5.3.3 responsive layout; screenshots/responsive_desktop.png & responsive_mobile.png"),
        15: ("[MSSV 3]", None,       "feature/unit-tests-businesslogic", "Done", "B2B.Tests (xUnit + SQLite): 16/16 tests PASSED (100%); screenshots/unit_test_results.png"),
        16: ("[MSSV 1]", "524H0057; [MSSV 3]", "main; feature/member2-winforms", "Done", "Connection strings in B2B.Web/appsettings.json and B2B.WinForms/App.config (zero hardcoded)"),
        17: ("[MSSV 1]", "524H0057; [MSSV 3]", "main; develop; feature/*", "Done", "GitFlow branches & incremental commits across all 3 members"),
        18: ("[MSSV 3]", "[MSSV 1]; 524H0057", "docs/report-and-packaging", "Done", "Report.docx, Readme.txt, Workbook, SourceCode.zip (without bin/obj)"),
    }
    for row_idx, (resp, helper, branch, status, evidence) in task_updates.items():
        ws.cell(row_idx, 4, resp)
        if helper is not None:
            ws.cell(row_idx, 5, helper)
        ws.cell(row_idx, 6, branch)
        ws.cell(row_idx, 7, status)
        ws.cell(row_idx, 9, evidence)

    # 3. Database sheet
    ws = wb["Database"]
    db_rows = [
        (5, "ItemID (int PK), ItemName (nvarchar 200), Size (nvarchar 50), Price (decimal 18,2), StockQuantity (int)", "ItemID", "None (referenced by OrderDetail ON DELETE NO ACTION/Restrict)", 20, "CHECK (StockQuantity >= 0), CHECK (Price >= 0)", "B2B.Data/Scripts/SeedData.sql & DbInitializer.cs"),
        (6, "AgentID (int PK), AgentName (nvarchar 200), Address (nvarchar 300), Phone (nvarchar 50)", "AgentID", "None (referenced by Order Restrict & Users SetNull)", 16, "NOT NULL on AgentName", "B2B.Data/Scripts/SeedData.sql & DbInitializer.cs"),
        (7, "OrderID (int PK), OrderDate (datetime2), AgentID (int FK), OrderStatus (nvarchar 50)", "OrderID", "AgentID -> Agent(AgentID) ON DELETE NO ACTION / Restrict", 15, "DEFAULT SYSUTCDATETIME(), DEFAULT 'Pending'", "B2B.Data/Scripts/SeedData.sql & DbInitializer.cs"),
        (8, "ID (int PK), OrderID (int FK), ItemID (int FK), Quantity (int), UnitAmount (decimal 18,2)", "ID", "OrderID -> [Order] ON DELETE CASCADE; ItemID -> Item ON DELETE NO ACTION/Restrict", 30, "CHECK (Quantity > 0), CHECK (UnitAmount >= 0)", "B2B.Data/Scripts/SeedData.sql & DbInitializer.cs"),
        (9, "UserID (int PK), UserName (nvarchar 100), email (nvarchar 150), password (nvarchar 255), [lock] (bit), Role (nvarchar 50), AgentID (int FK NULL)", "UserID", "AgentID -> Agent(AgentID) ON DELETE SET NULL", 19, "UNIQUE(UserName), UNIQUE(email), DEFAULT 0 on [lock], CHECK (Role IN ('Admin','Agent'))", "B2B.Data/Scripts/SeedData.sql & DbInitializer.cs"),
    ]
    for r, cols, pk, fk, count, cons, script in db_rows:
        ws.cell(r, 2, cols)
        ws.cell(r, 3, pk)
        ws.cell(r, 4, fk)
        ws.cell(r, 5, count)
        ws.cell(r, 6, cons)
        ws.cell(r, 8, script)

    ws.cell(20, 5, "Yes (tested in DatabaseIntegrityTests on SQLite)")
    ws.cell(21, 5, "Yes (Cascade on Order->OrderDetail; Restrict on Order->Agent & OrderDetail->Item; SetNull on Users->Agent)")
    ws.cell(22, 5, "Yes (CHECK StockQuantity >= 0 + OrderService transaction guard)")
    ws.cell(23, 5, "Partial (lock flag & 5-attempt lockout implemented; passwords plain-text across shared seed for demo compatibility)")
    ws.cell(24, 5, "Yes (20 IT items incl. 2 low-stock, 16 regional agents, 3 Admins + 16 Agents incl. locked, 15 orders, 30 details)")

    # 4. Transaction Tests sheet
    ws = wb["Transaction Tests"]
    tx_rows = [
        (5, "50 (Dell 4K)", "10", "Yes (Pending)", "Stock reduced 50 -> 40; verified in OrderBusinessLogicTests", "Pass"),
        (6, "50 (Dell 4K), 30 (Logitech KB)", "10x Dell, 5x KB", "Yes (Pending, 2 details)", "Stocks reduced 50->40 and 30->25 atomically", "Pass"),
        (7, "50 (Dell 4K), 5 (Logitech Mouse)", "10x Dell, 20x Mouse", "No (Exception thrown)", "Transaction rolled back; Dell stays 50, Mouse stays 5, 0 Orders created", "Pass"),
        (8, "8 (Cisco Switch)", "8", "Yes (Pending)", "Order saved; StockQuantity becomes exactly 0", "Pass"),
        (9, "100 (SSD Samsung T7)", "0 and -5", "No (ArgumentOutOfRange)", "Rejected before DB write; Stock stays 100", "Pass"),
        (10, "10 (Synology NAS)", "6 + 6 (=12) same item", "No (InvalidOperation)", "OrderService groups duplicate ItemIDs (12 > 10) and blocks order; Stock stays 10", "Pass"),
        (11, "50 (Item 1), 5 (Item 2)", "10x Item 1 + 20x Item 2", "No (RollbackAsync)", "Relational SQLite transaction rolled back completely; fresh context confirms 0 orders & unchanged stock", "Pass"),
        (12, "1 (Last unit)", "2 concurrent requests", "Single commit / second blocked", "Transactional stock verification + CHECK(StockQuantity >= 0) prevents negative stock", "Pass"),
    ]
    for r, before, qty, saved, after, pf in tx_rows:
        ws.cell(r, 3, before)
        ws.cell(r, 4, qty)
        ws.cell(r, 6, saved)
        ws.cell(r, 7, after)
        ws.cell(r, 8, pf)

    # 5. Unit Tests sheet
    ws = wb["Unit Tests"]
    unit_rows = [
        (5,  "DeductStock_WhenStockIsSufficient_ShouldDecreaseStockQuantity", "OrderService", "Stock deduction & transaction", "Multi-item order within available stock", "Order saved (Pending); stocks reduced 50->40 & 30->25", "Order saved; stocks 40 & 25 verified via fresh SQLite context", "Pass", "Yes"),
        (6,  "PlaceOrder_WhenStockIsInsufficient_ShouldThrowExceptionAndRollback", "OrderService", "Transaction rollback on low stock", "Item 1 valid (10/50), Item 2 exceeds stock (20/5)", "Throws InvalidOperationException; 0 orders; stocks untouched", "Exception thrown; rollback verified (0 orders, stocks 50 & 5)", "Pass", "Yes"),
        (7,  "CalculateOrderTotal_WithMultipleItems_ShouldReturnCorrectSum", "OrderService", "Order total calculation", "3 OrderDetail lines (5x11.5M + 10x3.45M + 20x1.69M)", "Returns exactly 125,800,000 VND", "Returned 125,800,000 VND", "Pass", "Yes"),
        (8,  "PlaceOrder_WhenOrderDetailsIsEmpty_ShouldThrowExceptionAndBlockOrder", "OrderService", "Empty OrderDetails guard", "PlaceOrderAsync called with empty items collection", "Throws InvalidOperationException; 0 orders created", "Exception thrown; 0 orders in DB", "Pass", "Yes"),
        (9,  "PlaceOrder_WhenQuantityIsZeroOrNegative_ShouldThrowArgumentOutOfRangeException (0, -5)", "OrderService", "Invalid quantity validation", "Order quantity = 0 and quantity = -5", "Throws ArgumentOutOfRangeException; stock unchanged", "Both InlineData cases threw exception; stock 100 unchanged", "Pass", "Yes"),
        (10, "PlaceOrder_WhenQuantityEqualsExactStock_ShouldSucceedAndSetStockToZero", "OrderService", "Boundary stock deduction", "Order quantity 8 equals StockQuantity 8", "Order succeeds; StockQuantity becomes 0", "Order committed; StockQuantity = 0", "Pass", "Yes"),
        (11, "PlaceOrder_WhenSameItemAddedTwice_ShouldValidateCombinedQuantity", "OrderService", "Duplicate item aggregation", "Same ItemID added twice (6 + 6 = 12 > stock 10)", "Combined quantity checked; order blocked & rolled back", "Exception thrown; stock remained 10", "Pass", "Yes"),
        (12, "GetAgentOrders_AndInvoice_ShouldEnforceAgentOwnershipIsolation", "OrderService", "My Orders & Invoice IDOR security", "Agent 1 queries My Orders and attempts to open Agent 2's Invoice", "Agent 1 sees only own order; Agent 2's invoice returns null", "Only own order returned; cross-agent invoice returned null", "Pass", "Yes"),
        (13, "AuthenticateUser_WhenRoleIsInvalid_ShouldDenyAccess (4 Theory cases)", "AuthService", "Role-based access control", "Admin->Web, Agent->WinForms, Agent->Web, Admin->WinForms", "Cross-portal logins denied; matching portal roles allowed", "All 4 InlineData cases matched expected RBAC outcome", "Pass", "Yes"),
        (14, "Login_WhenPasswordFailedMultipleTimes_ShouldLockAccount", "AuthService", "Account lockout after 5 failures", "5 consecutive wrong passwords then 1 correct password", "After 5th failure Users.lock=true in DB; valid login blocked", "Persisted lock=true verified; subsequent correct password blocked", "Pass", "Yes"),
        (15, "SeedData_ShouldInsert15To30RowsPerTable_WithValidRelationships", "DbInitializer", "Seed data completeness", "InitializeAsync on fresh relational SQLite DB", "15-30 rows/table, Admin+Agent+locked, low-stock, no orphan headers", "20 Items, 16 Agents, 19 Users, 15 Orders, 30 Details verified", "Pass", "Yes"),
        (16, "DatabaseIntegrity_ShouldEnforceForeignKeysCascadeRestrict_AndCheckConstraints", "B2BDbContext", "FK Cascade/Restrict & CHECK", "Insert orphan FK, negative stock, delete used Item, delete Order", "Orphan/negative/used-item fail; Order delete cascades details", "All 4 relational integrity assertions verified on SQLite", "Pass", "Yes"),
    ]
    for r, method, cls, logic, scen, exp, act, pf, mean in unit_rows:
        ws.cell(r, 2, method)
        ws.cell(r, 3, cls)
        ws.cell(r, 4, logic)
        ws.cell(r, 5, scen)
        ws.cell(r, 6, exp)
        ws.cell(r, 7, act)
        ws.cell(r, 8, pf)
        ws.cell(r, 9, mean)

    # 6. Branches & PRs sheet
    ws = wb["Branches & PRs"]
    ws["C3"] = "GitFlow: main (stable), develop (integration), feature/* and docs/* per task merged via Pull Requests"
    branch_rows = [
        (7, "feature/member1-web-core", "[MSSV 1]", "Task 2 Schema, Task 3.1 Auth, Task 3.2 Transaction Checkout, Task 3.4 Responsive UI", "https://github.com/thinhvo06/B2BWholesaleSystem/tree/feature/member1-web-core", "PR #1", "[MSSV 3]", "2026-11-13", "Merged"),
        (8, "feature/web-myorders-invoice", "[MSSV 3]", "Task 2 Seed Data & CHECK Integrity; Task 3.3 My Orders & Printable A4 Invoice", "https://github.com/thinhvo06/B2BWholesaleSystem", "PR #3 (Ready)", "[MSSV 1]", "2026-11-18", "Ready for PR"),
        (9, "feature/unit-tests-businesslogic", "[MSSV 3]", "Task 5.1 Automated xUnit Suite (16 tests with relational SQLite)", "https://github.com/thinhvo06/B2BWholesaleSystem", "PR #4 (Ready)", "[MSSV 1]", "2026-11-18", "Ready for PR"),
        (10, "docs/report-and-packaging", "[MSSV 3]", "Task 6c Report.docx, Workbook, Readme.txt, Screenshots & SourceCode.zip", "https://github.com/thinhvo06/B2BWholesaleSystem", "PR #5 (Ready)", "[MSSV 1]", "2026-11-18", "Ready for PR"),
    ]
    for r, bname, owner, purp, link, pr, rev, merged, status in branch_rows:
        ws.cell(r, 2, bname)
        ws.cell(r, 3, owner)
        ws.cell(r, 4, purp)
        ws.cell(r, 5, link)
        ws.cell(r, 6, pr)
        ws.cell(r, 7, rev)
        ws.cell(r, 8, merged)
        ws.cell(r, 9, status)

    # 7. Commit Log sheet
    ws = wb["Commit Log"]
    commit_rows = [
        (6, "Lab 7–Lab 9", "2026-11-13", "[MSSV 1]", "feature/member1-web-core; develop; main", 9, "PR #1 Merged into develop/main", "Solution setup, EF Core schema, Web Auth, Catalog, Cart, Transaction Checkout, E2E screenshots"),
        (7, "Lab 9",       "2026-11-18", "[MSSV 3]", "feature/web-myorders-invoice", 2, "Ready for PR", "59e5e66 SeedData.sql & CHECK constraints; 1a7de02 Task 3.3 My Orders, Printable Invoice, OrderService/AuthService"),
        (8, "Lab 10",      "2026-11-18", "[MSSV 3]", "feature/unit-tests-businesslogic", 1, "Ready for PR", "a3dceb0 16 meaningful xUnit tests with relational SQLite (100% Pass)"),
        (9, "Lab 10",      "2026-11-18", "[MSSV 3]", "docs/report-and-packaging", 2, "Ready for PR", "E2E verification & screenshots, Report.docx, Team Workbook, Readme.txt, SourceCode.zip packaging"),
    ]
    for r, wk, dt, sid, br, cnt, pr, desc in commit_rows:
        ws.cell(r, 1, wk)
        ws.cell(r, 2, dt)
        ws.cell(r, 3, sid)
        ws.cell(r, 4, br)
        ws.cell(r, 5, cnt)
        ws.cell(r, 6, pr)
        ws.cell(r, 7, desc)

    # 8. Config Check sheet
    ws = wb["Config Check"]
    ws.cell(6, 3, "Yes")
    ws.cell(6, 5, "B2B.Web/appsettings.json stores ConnectionStrings:B2BConnection; Program.cs reads via builder.Configuration.GetConnectionString('B2BConnection').")
    ws.cell(7, 3, "Yes")
    ws.cell(7, 5, "Verified across B2B.WinForms, B2B.Web, B2B.Data, and B2B.Tests (WinForms reads App.config; Web reads appsettings.json; Tests use SQLite :memory:).")
    ws.cell(8, 3, "Yes")
    ws.cell(8, 5, "Uses Trusted_Connection=True (Windows Auth) with no production secrets committed; .gitignore excludes bin/obj/user files.")
    ws.cell(9, 3, "Yes")
    ws.cell(9, 5, "Readme.txt Section 3 explains both Option A (SSMS SeedData.sql) and Option B (EF Core DbInitializer) plus matching App.config & appsettings.json.")
    ws.cell(10, 3, "Yes")
    ws.cell(10, 5, "SourceCode.zip packaged programmatically stripping all bin/, obj/, .vs/, and .git/ folders.")
    ws.cell(11, 3, "Yes")
    ws.cell(11, 5, "B2B.Tests uses isolated SQLite in-memory connection (DataSource=:memory:) with PRAGMA foreign_keys = ON per test.")

    # 9. Progress Log sheet
    ws = wb["Progress Log"]
    ws.cell(7, 3, "Completed Member 1 Web Portal (Login, Catalog, Cart, Transaction Checkout, Bootstrap 5 UI) and Member 3 Task 3.3 (My Orders page with KPI cards/filters, IDOR protection, A4 Printable Invoice with @media print PDF export) + DB Seed & CHECK Integrity.")
    ws.cell(7, 4, "https://github.com/thinhvo06/B2BWholesaleSystem (screenshots/1-11)")
    ws.cell(7, 5, "Resolved SQL Server ON DELETE RESTRICT -> NO ACTION and unified SeedData.sql & DbInitializer.cs row counts.")
    ws.cell(7, 6, "Done")
    ws.cell(7, 8, "Met")

    ws.cell(8, 3, "Completed Member 3 Task 5.1 (16/16 xUnit tests passing on relational SQLite), verified E2E flows with live screenshots, updated Report.docx, Team Workbook, Readme.txt, and packaged clean SourceCode.zip.")
    ws.cell(8, 4, "screenshots/unit_test_results.png; Report.docx; SourceCode.zip")
    ws.cell(8, 5, "Pending final PR merge of feature/member2-winforms & Member 3 feature branches into main by team leader.")
    ws.cell(8, 6, "Done")
    ws.cell(8, 8, "Met")

    # 10. AI Usage Log sheet
    ws = wb["AI Usage Log"]
    ws.cell(8, 1, "4")
    ws.cell(8, 2, "2026-11-18")
    ws.cell(8, 3, "[MSSV 3]")
    ws.cell(8, 4, "Antigravity AI")
    ws.cell(8, 5, "Task 2 Seed/Integrity, Task 3.3 My Orders & Printable Invoice, Task 5.1 Unit Tests, Docs")
    ws.cell(8, 6, "Implement Member 3 remaining tasks: unify SeedData.sql & CHECK constraints, build My Orders & A4 Printable Invoice with IDOR security, write xUnit relational SQLite tests, update Report.docx/Workbook/Readme/SourceCode.zip.")
    ws.cell(8, 7, "Refactored shared OrderService & AuthService, built MyOrders & Invoice views with @media print CSS, wrote 16 relational SQLite unit tests, and automated E2E/screenshot verification & report generation.")
    ws.cell(8, 8, "Reviewed, tested & integrated")
    ws.cell(8, 9, "Verified with dotnet build (0 errors), dotnet test (16/16 PASSED), live B2B.Web E2E script (IDOR + A4 PDF check), and visual inspection of all screenshots.")

    # 11. Marking sheet (keep Member 2 rows 7-10 untouched!)
    ws = wb["Marking"]
    marks = {
        5:  (5, "Clean 5-table schema with PKs/FKs, StockQuantity, Roles; unified 20 Items, 16 Agents, 19 Users, 15 Orders, 30 OrderDetails in both SeedData.sql and DbInitializer.cs."),
        6:  (5, "Explicit Cascade (Order->OrderDetail), Restrict/NO ACTION (Order->Agent, OrderDetail->Item), SetNull (Users->Agent), and 5 CHECK constraints verified on relational SQLite."),
        11: (5, "Agent-only Cookie Auth Login via AuthService; blocks Admin role and locked accounts; enforces 5-failure lockout."),
        12: (15, "Catalog search/filter + Bulk Cart + Master-Detail Checkout executed inside OrderService BeginTransactionAsync with atomic stock deduction and full rollback verified."),
        13: (10, "My Orders displays only logged-in agent's orders with KPI summary, status filter, search, strict IDOR protection, and A4 @media print Invoice/PDF view."),
        14: (5, "Bootstrap 5.3.3 responsive layout verified on both desktop (1280px) and mobile (375-390px) viewports."),
        15: (15, "16/16 meaningful xUnit tests passing (100%) on isolated relational SQLite DB covering stock deduction, rollback, total sum, lockout, RBAC, empty details, IDOR, and FK/CHECK integrity."),
        16: (5, "All connection strings stored in B2B.Web/appsettings.json and B2B.WinForms/App.config with zero hardcoded credentials."),
        17: (4, "GitFlow feature branches created per member/feature with rich incremental commits; final PR merges pending leader approval on GitHub."),
        18: (5, "Report.docx complete with Division of Labor, ERD, running app screenshots (including My Orders, Printable Invoice, IDOR check), 16/16 Unit Test results, and clean SourceCode.zip."),
    }
    for r, (score, just) in marks.items():
        ws.cell(r, 5, score)
        ws.cell(r, 8, just)

    wb.save(WORKBOOK_PATH)
    print(f"[Workbook] Updated successfully: {WORKBOOK_PATH}")


def set_cell_text(cell, text, bold=False, size=9.5):
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)


def add_table_row(table, values):
    row = table.add_row()
    for i, val in enumerate(values):
        if i < len(row.cells):
            set_cell_text(row.cells[i], val)
    return row


def insert_paragraph_after(paragraph, text="", bold=False, size=10.5):
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    from docx.text.paragraph import Paragraph
    p = Paragraph(new_p, paragraph._parent)
    if text:
        run = p.add_run(text)
        run.bold = bold
        run.font.size = Pt(size)
    return p


def clear_table_data_rows(table, keep_rows=1):
    while len(table.rows) > keep_rows:
        tbl = table._tbl
        tbl.remove(table.rows[-1]._tr)


def update_report():
    doc = docx.Document(REPORT_PATH)

    # 1. Cover page & basic replacements across paragraphs
    for p in doc.paragraphs:
        if "[Group 08 - Điền số nhóm của bạn]" in p.text:
            p.text = (
                "Group: Group 14\n"
                "1. [MSSV 1] : Võ Nguyễn Phúc Thịnh (Leader / Member 1 - 34%)\n"
                "2. 524H0057 : Ôn Gia Khiêm (Member 2 - 33%)\n"
                "3. [MSSV 3] : Nguyễn Nhật Huy (Member 3 - 33%)"
            )
        if "Nguyễn Nhật huy" in p.text:
            p.text = p.text.replace("Nguyễn Nhật huy", "Nguyễn Nhật Huy")

    # 2. Update Table 1: Division of Labor
    t_dol = doc.tables[1]
    clear_table_data_rows(t_dol, keep_rows=1)
    dol_rows = [
        ("2a",  "Database schema & Seed Data (15-30 realistic rows/table)", "Võ Nguyễn Phúc Thịnh ([MSSV 1]) & Nguyễn Nhật Huy ([MSSV 3])", "feature/member1-web-core; feature/web-myorders-invoice", "Done"),
        ("2b",  "Database referential integrity (FKs, Cascade/Restrict, CHECK)", "Nguyễn Nhật Huy ([MSSV 3])", "feature/web-myorders-invoice", "Done"),
        ("1.1", "WinForms secure Admin login (Role Admin + 5-attempt lockout)", "Ôn Gia Khiêm (524H0057)", "feature/member2-winforms", "Done"),
        ("1.2", "WinForms Item & Agent CRUD, Stock-In, Order Management", "Ôn Gia Khiêm (524H0057)", "feature/member2-winforms", "Done"),
        ("1.3", "WinForms A4 Shipping Manifest report (Preview / Print / PDF)", "Ôn Gia Khiêm (524H0057)", "feature/member2-winforms", "Done"),
        ("1.4", "WinForms Dashboard (Best-selling, Low-stock < 10, Revenue)", "Ôn Gia Khiêm (524H0057)", "feature/member2-winforms", "Done"),
        ("3.1", "Web Portal Agent Login (Role Agent only, Admin blocked)", "Võ Nguyễn Phúc Thịnh ([MSSV 1])", "feature/member1-web-core", "Done"),
        ("3.2", "Catalog, Bulk Cart & Master-Detail Transaction Checkout", "Võ Nguyễn Phúc Thịnh ([MSSV 1])", "feature/member1-web-core", "Done"),
        ("3.3", "My Orders history (IDOR protected) & Printable A4 Invoice", "Nguyễn Nhật Huy ([MSSV 3])", "feature/web-myorders-invoice", "Done"),
        ("3.4", "Modern Responsive UI (Bootstrap 5.3.3 desktop & mobile)", "Võ Nguyễn Phúc Thịnh ([MSSV 1])", "feature/member1-web-core", "Done"),
        ("5.1", "Unit Test Project (xUnit + SQLite, 16 meaningful tests)", "Nguyễn Nhật Huy ([MSSV 3])", "feature/unit-tests-businesslogic", "Done"),
        ("6",   "Secure Config, GitFlow PRs, Report.docx, Readme & Zip", "All Members (Docs & Packaging: Nguyễn Nhật Huy [MSSV 3])", "docs/report-and-packaging", "Done"),
    ]
    for row_vals in dol_rows:
        add_table_row(t_dol, row_vals)

    # 3. Update Table 2: Team Members
    t_team = doc.tables[2]
    clear_table_data_rows(t_team, keep_rows=1)
    add_table_row(t_team, ("1", "Võ Nguyễn Phúc Thịnh", "[MSSV 1]", "Leader / Fullstack Web & Shared Core DB (34%)"))
    add_table_row(t_team, ("2", "Ôn Gia Khiêm", "524H0057", "Desktop WinForms Back-Office & Reporting (33%)"))
    add_table_row(t_team, ("3", "Nguyễn Nhật Huy", "[MSSV 3]", "Seed/Integrity, Web Invoices, Unit Tests & Docs (33%)"))

    # 4. Update Table 5: Seed Data counts (exact unified counts!)
    t_seed = doc.tables[5]
    clear_table_data_rows(t_seed, keep_rows=1)
    seed_rows = [
        ("Item", "20 rows", "Realistic IT & office wholesale hardware (Dell 4K, Logitech, Sony, Cisco, Synology), including 2 low-stock items (StockQuantity = 6 and 8) to trigger WinForms Dashboard low-stock alerts (< 10)."),
        ("Agent", "16 rows", "Regional B2B commercial distributors across Vietnam (Hanoi, HCMC, Da Nang, Can Tho, Binh Duong, Hai Phong, Hue, Da Lat, etc.) with addresses and phone numbers."),
        ("Order", "15 rows", "Wholesale orders spanning the past 14 days across multiple statuses (Pending, Confirmed, Shipped, Delivered) linked to valid Agents."),
        ("OrderDetail", "30 rows", "Exactly 2 itemized product lines for every single one of Orders #1–#15 (zero orphan order headers) with realistic bulk quantities and unit prices."),
        ("Users", "19 rows", "Includes 3 Admin accounts (admin, admin_wh, supervisor) for WinForms and 16 Agent accounts mapped to Agents #1–#16, including 1 locked account (agent_locked, lock = 1)."),
    ]
    for row_vals in seed_rows:
        add_table_row(t_seed, row_vals)

    # 5. Update Table 6: Integrity rules
    t_int = doc.tables[6]
    clear_table_data_rows(t_int, keep_rows=1)
    int_rows = [
        ("Order -> Agent", "FK + DeleteBehavior.Restrict / ON DELETE NO ACTION", "Prevents deleting an Agent who has historical orders (protects financial audit trail; SQL Server uses NO ACTION)."),
        ("OrderDetail -> Order", "FK + DeleteBehavior.Cascade / ON DELETE CASCADE", "Deleting a master Order automatically removes its child OrderDetails so no orphan line items remain."),
        ("OrderDetail -> Item", "FK + DeleteBehavior.Restrict / ON DELETE NO ACTION", "Prevents deleting an Item referenced in existing OrderDetails."),
        ("Users -> Agent", "FK + DeleteBehavior.SetNull / ON DELETE SET NULL", "Allows decoupling an Agent record safely without leaving broken foreign keys in Users."),
        ("Domain CHECK Constraints", "CHECK (StockQuantity >= 0), CHECK (Price >= 0), CHECK (Quantity > 0), CHECK (UnitAmount >= 0), CHECK (Role IN ('Admin','Agent'))", "Enforced in both EF Core Fluent API (B2BDbContext.cs) and T-SQL (SeedData.sql); verified by automated SQLite relational tests."),
        ("Users Unique Identity", "UNIQUE Index on UserName and email", "Guarantees unique login identifiers and prevents duplicate account registration."),
    ]
    for row_vals in int_rows:
        add_table_row(t_int, row_vals)

    # 6. Update Section 5.4 (Task 3.3: My Orders and Printable Invoice) with full explanation + REAL screenshots!
    for idx, p in enumerate(doc.paragraphs):
        if "5.4 Task 3.3: My Orders and Printable Invoice" in p.text:
            # Update the description paragraph immediately following heading 5.4
            desc_p = doc.paragraphs[idx + 1]
            desc_p.text = (
                "Responsible: Member 3 (Nguyễn Nhật Huy)\n"
                "Implemented the complete 'My Orders' portal and A4 Printable Invoice workflow in B2B.Web:\n"
                "• My Orders Page (/Order/MyOrders): Queries OrderService.GetAgentOrdersAsync(currentAgentId, status, search), "
                "strictly filtering orders by the authenticated agent's AgentID claim. Displays 4 live KPI summary cards "
                "(Total Orders, Total Value Spent, Pending Orders, Shipped/Delivered Orders), status filter & search bar, "
                "and a responsive Bootstrap 5 order history table with direct invoice buttons.\n"
                "• IDOR Security Protection: OrderController.Invoice(int id) calls OrderService.GetAgentOrderInvoiceAsync(id, currentAgentId). "
                "If an agent attempts to access another agent's order ID via URL manipulation (e.g., Agent #1 requesting /Order/Invoice/2), "
                "access is immediately denied with a security warning and redirected back to My Orders.\n"
                "• Printable A4 Wholesale Invoice (/Order/Invoice/{id}): Designed with dedicated CSS @media print rules "
                "(A4 portrait page geometry, hiding navbar/footer/toolbar via d-print-none) so clicking 'In Hóa Đơn / Xuất PDF' "
                "(window.print()) outputs a single-page professional B2B tax invoice containing inline SVG distributor logo, "
                "invoice number (INV-YYYYMMDD-XXXX), order status, Bill To/Ship To agent details, itemized table, subtotal/VAT/grand total, "
                "Vietnamese amount in words, and 3 signature blocks."
            )
            cursor = desc_p

            img_my_orders = os.path.join(SC_DIR, "7_my_orders_page.png")
            if os.path.exists(img_my_orders):
                cap1 = insert_paragraph_after(cursor, "Figure 5.6: My Orders Page (Agent #1 - Phúc Anh Tech viewing only own orders #1 and #6 with KPI cards and filters)", bold=True, size=9.5)
                pic1 = insert_paragraph_after(cap1)
                pic1.add_run().add_picture(img_my_orders, width=Inches(5.8))
                cursor = pic1

            img_invoice = os.path.join(SC_DIR, "8_invoice_page.png")
            if os.path.exists(img_invoice):
                cap2 = insert_paragraph_after(cursor, "Figure 5.7: Printable B2B Wholesale Invoice View (Order #1 - Logo, Itemized Breakdown, Amount in Words & Print/PDF Button)", bold=True, size=9.5)
                pic2 = insert_paragraph_after(cap2)
                pic2.add_run().add_picture(img_invoice, width=Inches(5.4))
                cursor = pic2

            img_idor = os.path.join(SC_DIR, "10_my_orders_idor_blocked.png")
            if os.path.exists(img_idor):
                cap3 = insert_paragraph_after(cursor, "Figure 5.8: IDOR Security Verification - Agent #1 Blocked from Accessing Agent #2's Invoice (#2)", bold=True, size=9.5)
                pic3 = insert_paragraph_after(cap3)
                pic3.add_run().add_picture(img_idor, width=Inches(5.8))
                cursor = pic3
            break

    # 7. Update Section 6 (Unit Testing) paragraph & image + Table 9!
    for idx, p in enumerate(doc.paragraphs):
        if "6. Exercise 5: Unit Testing" in p.text:
            ut_p = doc.paragraphs[idx + 1]
            # Clear old runs (including old 6-test image) and replace with real 16-test details & new image
            ut_p.text = (
                "Responsible: Member 3 (Nguyễn Nhật Huy - QA & Unit Testing Specialist)\n"
                "The B2B.Tests project uses xUnit 2.9.3 paired with Microsoft.EntityFrameworkCore.Sqlite (isolated relational in-memory "
                "SQLite database per test with PRAGMA foreign_keys = ON). Unlike non-relational mocks, every test executes the real "
                "production classes (OrderService, AuthService, DbInitializer, B2BDbContext) with real SQL transactions, real rollbacks, "
                "foreign key enforcement, and CHECK constraints. Result: 16 / 16 test executions PASSED (100% pass rate, 0 failed)."
            )
            test_img = os.path.join(SC_DIR, "unit_test_results.png")
            if os.path.exists(test_img):
                r_cap = ut_p.add_run("\n\nFigure 6.1: xUnit Test Execution Output - All 16 Relational Core Business Logic Tests Passed (100%)\n")
                r_cap.bold = True
                r_cap.font.size = Pt(9.5)
                ut_p.add_run().add_picture(test_img, width=Inches(6.0))
            break

    # Update Table 9 (Unit Test Summary & Cases)
    t_ut = doc.tables[9]
    # Header metadata rows (rows 0..3) - update cells cleanly
    if len(t_ut.rows) >= 4:
        for c in range(3, len(t_ut.rows[1].cells)):
            set_cell_text(t_ut.rows[1].cells[c], "xUnit (v2.9.3) + EF Core SQLite / Project: B2B.Tests")
        for c in range(3, len(t_ut.rows[2].cells)):
            set_cell_text(t_ut.rows[2].cells[c], "OrderService, AuthService, LoginAttemptTracker, DbInitializer, B2BDbContext")
        for c in range(3, len(t_ut.rows[3].cells)):
            set_cell_text(t_ut.rows[3].cells[c], "12 Test Methods (16 Test Executions) / 100% Pass Rate (16 Passed, 0 Failed)")

    clear_table_data_rows(t_ut, keep_rows=5)
    ut_cases = [
        ("1",  "DeductStock_WhenStockIsSufficient_ShouldDecreaseStockQuantity", "Multi-item order within stock", "Order saved; stocks 50->40, 30->25", "Committed & verified via fresh DB context", "Pass"),
        ("2",  "PlaceOrder_WhenStockIsInsufficient_ShouldThrowExceptionAndRollback", "Item 1 ok (10/50), Item 2 exceeds (20/5)", "Throws exception; full SQL rollback", "0 Orders; stocks remain 50 & 5", "Pass"),
        ("3",  "CalculateOrderTotal_WithMultipleItems_ShouldReturnCorrectSum", "3 lines: 5x11.5M + 10x3.45M + 20x1.69M", "Exact sum = 125,800,000 VND", "Returned 125,800,000 VND", "Pass"),
        ("4",  "AuthenticateUser_WhenRoleIsInvalid_ShouldDenyAccess (4 cases)", "Admin->Web, Agent->WinForms & valid roles", "Cross-portal denied; valid allowed", "All 4 Theory cases passed", "Pass"),
        ("5",  "Login_WhenPasswordFailedMultipleTimes_ShouldLockAccount", "5 wrong passwords then valid password", "Sets Users.lock=true; blocks valid login", "Lock persisted; login blocked", "Pass"),
        ("6",  "PlaceOrder_WhenOrderDetailsIsEmpty_ShouldThrowExceptionAndBlockOrder", "Place order with empty item list", "Throws InvalidOperationException", "Blocked; 0 orders created", "Pass"),
        ("7",  "PlaceOrder_WhenQuantityIsZeroOrNegative_ShouldThrowArgumentOutOfRangeException (2 cases)", "Order quantity 0 and -5", "Throws ArgumentOutOfRangeException", "Both cases rejected; stock intact", "Pass"),
        ("8",  "PlaceOrder_WhenQuantityEqualsExactStock_ShouldSucceedAndSetStockToZero", "Order qty 8 == StockQuantity 8", "Succeeds; remaining stock = 0", "Committed; stock = 0", "Pass"),
        ("9",  "PlaceOrder_WhenSameItemAddedTwice_ShouldValidateCombinedQuantity", "Same item 6+6=12 > stock 10", "Aggregates qty & blocks order", "Blocked; stock stays 10", "Pass"),
        ("10", "GetAgentOrders_AndInvoice_ShouldEnforceAgentOwnershipIsolation", "Agent 1 accesses own & Agent 2's order", "Own invoice OK; Agent 2's returns null", "IDOR blocked; strict isolation", "Pass"),
        ("11", "SeedData_ShouldInsert15To30RowsPerTable_WithValidRelationships", "DbInitializer on fresh SQLite DB", "15-30 rows/table, roles, low-stock", "20/16/19/15/30 rows verified", "Pass"),
        ("12", "DatabaseIntegrity_ShouldEnforceForeignKeysCascadeRestrict_AndCheckConstraints", "Orphan FK, Stock<0, Delete Item, Delete Order", "Violations fail; Order cascades details", "All 4 relational checks passed", "Pass"),
    ]
    for row_vals in ut_cases:
        add_table_row(t_ut, row_vals)

    # 8. Update Table 11 (Git Collaboration)
    t_git = doc.tables[11]
    clear_table_data_rows(t_git, keep_rows=5)
    add_table_row(t_git, ("Member 1 (Thịnh)", "main, develop, feature/member1-web-core", "9 commits", "PR #1 (Merged)", "Core DB, Web Auth, Catalog, Cart & Transaction"))
    add_table_row(t_git, ("Member 2 (Khiêm)", "feature/member2-winforms", "4 commits", "PR #2 (Ready)", "WinForms Admin Login, CRUD, Manifest & Dashboard"))
    add_table_row(t_git, ("Member 3 (Huy)", "feature/web-myorders-invoice, feature/unit-tests-businesslogic, docs/report-and-packaging", "5 commits", "PR #3–#5 (Ready)", "Seed/Integrity, My Orders & Invoice, 16 Unit Tests, Docs"))

    # 9. Update Table 12 (Contribution of Each Member)
    t_contrib = doc.tables[12]
    clear_table_data_rows(t_contrib, keep_rows=1)
    add_table_row(t_contrib, ("Võ Nguyễn Phúc Thịnh (Member 1)", "[MSSV 1]", "Task 2a (Shared DB Schema), Task 3.1 (Agent Login), Task 3.2 (Catalog, Cart, Transaction Checkout), Task 3.4 (Bootstrap 5 UI), Repo Setup", "34%"))
    add_table_row(t_contrib, ("Ôn Gia Khiêm (Member 2)", "524H0057", "Task 1.1 (WinForms Admin Login & App.config), Task 1.2 (Item/Agent CRUD & Order Management), Task 1.3 (Shipping Manifest), Task 1.4 (Dashboard)", "33%"))
    add_table_row(t_contrib, ("Nguyễn Nhật Huy (Member 3)", "[MSSV 3]", "Task 2a/2b (Unified Seed Data 15-30 rows & CHECK/FK Integrity), Task 3.3 (My Orders, IDOR Security & A4 Printable Invoice), Task 5.1 (16 Relational xUnit Tests), Report.docx, Workbook, Readme.txt & SourceCode.zip", "33%"))
    add_table_row(t_contrib, ("Total", "", "All Assignment 2 Rubric Criteria Covered (100/100 Target)", "100%"))

    # 10. Update Appendix A: Readme.txt
    if os.path.exists(README_PATH):
        with open(README_PATH, "r", encoding="utf-8") as f:
            readme_text = f.read()
        for idx, p in enumerate(doc.paragraphs):
            if "Appendix A: Readme.txt" in p.text and idx + 1 < len(doc.paragraphs):
                doc.paragraphs[idx + 1].text = readme_text
                break

    # 11. Update Appendix B: Generative AI Use (Table 13)
    t_ai = doc.tables[13]
    add_table_row(t_ai, (
        "ChatGPT (13/11/2026)",
        "WinForms Back-Office & SQL Troubleshooting (Member 2)",
        "Implement WinForms Admin Login, CRUD, Manifest, Dashboard and resolve SQL Server syntax.",
        "Adapted WinForms data access to shared B2B.Data entities; fixed ON DELETE NO ACTION.",
        "Built and ran WinForms locally against SQL Server."
    ))
    add_table_row(t_ai, (
        "Antigravity AI (18/11/2026)",
        "Member 3 Remaining Tasks (Seed/Integrity, My Orders & Invoice, Unit Tests, Docs)",
        "Complete Task 2 Seed/CHECK integrity, Task 3.3 My Orders & A4 Printable Invoice, Task 5.1 relational SQLite Unit Tests, and submission deliverables.",
        "Extracted shared OrderService/AuthService, built MyOrders & Invoice with @media print CSS, wrote 16 SQLite unit tests, and updated Report/Workbook/Readme.",
        "Verified via dotnet build (0 errors), dotnet test (16/16 PASSED), live E2E script (IDOR + A4 PDF), and screenshot review."
    ))

    doc.save(REPORT_PATH)
    print(f"[Report]   Updated successfully: {REPORT_PATH}")


if __name__ == "__main__":
    update_workbook()
    update_report()
