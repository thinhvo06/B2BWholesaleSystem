import copy
import io
import os
import subprocess
import docx
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.text.paragraph import Paragraph

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SC_DIR = os.path.join(BASE_DIR, "screenshots")
REPORT_PATH = os.path.join(BASE_DIR, "Report.docx")
README_PATH = os.path.join(BASE_DIR, "Readme.txt")
GIT = r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd\git.exe"


def set_cell_text_preserve_style(cell, text, bold=None, font_size=9.5):
    """Writes text into a table cell while preserving its paragraph style & cell shading/borders."""
    p = cell.paragraphs[0]
    for extra_p in cell.paragraphs[1:]:
        extra_p._element.getparent().remove(extra_p._element)
    font_name = "Calibri"
    color_rgb = None
    if p.runs:
        if p.runs[0].font.name:
            font_name = p.runs[0].font.name
        if p.runs[0].font.color and p.runs[0].font.color.rgb:
            color_rgb = p.runs[0].font.color.rgb
    p.text = ""
    run = p.add_run(text)
    run.font.name = font_name
    run.font.size = Pt(font_size)
    if bold is not None:
        run.bold = bold
    if color_rgb is not None:
        run.font.color.rgb = color_rgb


def reset_table_rows_with_template_style(table, data_rows, keep_header_rows=1, font_size=9.0, col_widths_in=None):
    """
    Replaces data rows of a table by deep-copying XML styling from the first template data row.
    Optionally sets fixed column widths so wide tables never overflow page margins.
    """
    tbl = table._tbl
    template_row_xml = copy.deepcopy(table.rows[keep_header_rows]._tr)

    while len(table.rows) > keep_header_rows:
        tbl.remove(table.rows[-1]._tr)

    for row_vals in data_rows:
        new_tr = copy.deepcopy(template_row_xml)
        tbl.append(new_tr)
        row = table.rows[-1]
        for ci, val in enumerate(row_vals):
            if ci < len(row.cells):
                is_bold = (ci == 0 and len(row_vals) <= 4 and val.lower() == "total")
                set_cell_text_preserve_style(row.cells[ci], val, bold=is_bold if is_bold else False, font_size=font_size)

    if col_widths_in is not None:
        table.autofit = False
        # Set tblLayout to fixed so Word strictly obeys column widths
        tblPr = tbl.tblPr
        for old_layout in tblPr.findall(qn("w:tblLayout")):
            tblPr.remove(old_layout)
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        tblPr.append(layout)

        # Set tblW to total width in dxa (1 inch = 1440 twips)
        total_dxa = int(sum(col_widths_in) * 1440)
        for old_w in tblPr.findall(qn("w:tblW")):
            tblPr.remove(old_w)
        tblW = OxmlElement("w:tblW")
        tblW.set(qn("w:w"), str(total_dxa))
        tblW.set(qn("w:type"), "dxa")
        tblPr.append(tblW)

        # Update tblGrid
        tblGrid = tbl.find(qn("w:tblGrid"))
        if tblGrid is not None:
            for gc in list(tblGrid):
                tblGrid.remove(gc)
            for w in col_widths_in:
                gc = OxmlElement("w:gridCol")
                gc.set(qn("w:w"), str(int(w * 1440)))
                tblGrid.append(gc)

        for row in table.rows:
            for ci, w in enumerate(col_widths_in):
                if ci < len(row.cells):
                    tcPr = row.cells[ci]._tc.get_or_add_tcPr()
                    for old_tcW in tcPr.findall(qn("w:tcW")):
                        tcPr.remove(old_tcW)
                    tcW = OxmlElement("w:tcW")
                    tcW.set(qn("w:w"), str(int(w * 1440)))
                    tcW.set(qn("w:type"), "dxa")
                    tcPr.append(tcW)


def wrappable(name: str) -> str:
    """Inserts zero-width space after underscores so long C# method names wrap neatly inside table cells."""
    return name.replace("_", "_\u200b")


def insert_paragraph_after(paragraph, text="", bold=False, italic=False, size=10.0, align=None, space_before=4, space_after=4, keep_with_next=False):
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    p = Paragraph(new_p, paragraph._parent)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = keep_with_next
    if align is not None:
        p.alignment = align
    if text:
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(size)
        run.bold = bold
        run.italic = italic
    return p


def replace_paragraph_text_preserve_format(p, new_text):
    font_name = None
    font_size = None
    font_bold = None
    font_color = None
    if p.runs:
        r0 = p.runs[0]
        font_name = r0.font.name
        font_size = r0.font.size
        font_bold = r0.bold
        if r0.font.color and r0.font.color.rgb:
            font_color = r0.font.color.rgb
    p.text = ""
    run = p.add_run(new_text)
    if font_name:
        run.font.name = font_name
    if font_size:
        run.font.size = font_size
    if font_bold is not None:
        run.bold = font_bold
    if font_color is not None:
        run.font.color.rgb = font_color


def next_paragraph(p):
    """Returns the next <w:p> sibling directly in XML (immune to list index shifting!)."""
    el = p._p.getnext()
    while el is not None:
        if el.tag.endswith("}p"):
            return Paragraph(el, p._parent)
        el = el.getnext()
    return None


def enable_update_fields_on_open(doc):
    settings = doc.settings.element
    for existing in settings.findall(qn("w:updateFields")):
        settings.remove(existing)
    uf = OxmlElement("w:updateFields")
    uf.set(qn("w:val"), "true")
    settings.append(uf)


def main():
    # 1. Load official Assignment 2 template from origin/feature/member2-winforms:Report.docx
    raw = subprocess.check_output(
        [GIT, "show", "origin/feature/member2-winforms:Report.docx"],
        cwd=BASE_DIR
    )
    doc = docx.Document(io.BytesIO(raw))

    # 2. Remove the instruction page (everything before "B2B Wholesale Order Management System")
    body = doc.element.body
    children = list(body)
    cover_idx = None
    for idx, child in enumerate(children):
        txt = "".join(child.itertext()).strip()
        if "B2B Wholesale Order Management System" in txt and child.tag.endswith("}p"):
            cover_idx = idx
            break
    assert cover_idx is not None, "Could not locate Cover Page title!"

    for child in children[:cover_idx]:
        body.remove(child)

    # Clear pageBreakBefore on Cover Page title so Page 1 is the Cover Page
    cover_p_el = list(body)[0]
    pPr = cover_p_el.find(qn("w:pPr"))
    if pPr is not None:
        for pbb in pPr.findall(qn("w:pageBreakBefore")):
            pPr.remove(pbb)

    # 3. Enable automatic Table of Contents update in Word on open
    enable_update_fields_on_open(doc)

    # 4. Fix Footer: Group 08 -> Group 14 across all sections
    for section in doc.sections:
        for ftr in (section.footer, section.first_page_footer, section.even_page_footer):
            if ftr is None:
                continue
            for p in ftr.paragraphs:
                for run in p.runs:
                    if "Group 08" in run.text:
                        run.text = run.text.replace("Group 08", "Group 14")
                    if "Group XX" in run.text:
                        run.text = run.text.replace("Group XX", "Group 14")

    # 5. Update ONLY the 3 Cover Page student lines (Normal style & containing ":")
    for p in doc.paragraphs[:10]:
        txt = p.text.strip()
        if p.style.name == "Normal" and ":" in txt:
            if txt.startswith("1."):
                replace_paragraph_text_preserve_format(p, "1. 524H0069 : Võ Nguyễn Phúc Thịnh")
            elif txt.startswith("2."):
                replace_paragraph_text_preserve_format(p, "2. 524H0057 : Ôn Gia Khiêm")
            elif txt.startswith("3."):
                replace_paragraph_text_preserve_format(p, "3. 524H0052 : Nguyễn Nhật Huy")

    # 6. Update ALL 16 Tables preserving official template formatting
    assert len(doc.tables) == 16, f"Expected 16 tables, found {len(doc.tables)}"

    # Table 1: Section 1.2 Division of Labor
    reset_table_rows_with_template_style(doc.tables[1], [
        ("2a",  "Database schema & Seed Data (15–30 realistic rows/table)", "Võ Nguyễn Phúc Thịnh (524H0069) & Nguyễn Nhật Huy (524H0052)", "feature/member1-web-core; feature/web-myorders-invoice", "Done"),
        ("2b",  "Database integrity (FK Cascade/Restrict, CHECK constraints)", "Nguyễn Nhật Huy (524H0052)", "feature/web-myorders-invoice", "Done"),
        ("1.1", "WinForms secure login (Admin role only + 5-attempt lockout)", "Ôn Gia Khiêm (524H0057)", "feature/member2-winforms", "Done"),
        ("1.2", "Item & Agent CRUD (stock-in), Order Management screen", "Ôn Gia Khiêm (524H0057)", "feature/member2-winforms", "Done"),
        ("1.3", "Shipping Manifest report (A4 Preview / Print / PDF)", "Ôn Gia Khiêm (524H0057)", "feature/member2-winforms", "Done"),
        ("1.4", "Data Filter & Dashboard (Best-selling, Low-stock < 10, Revenue)", "Ôn Gia Khiêm (524H0057)", "feature/member2-winforms", "Done"),
        ("3.1", "Web Portal Login Form (Agent role only, Admin blocked)", "Võ Nguyễn Phúc Thịnh (524H0069)", "feature/member1-web-core", "Done"),
        ("3.2", "Catalog, Bulk Cart & Master-Detail Order Transaction", "Võ Nguyễn Phúc Thịnh (524H0069)", "feature/member1-web-core", "Done"),
        ("3.3", "My Orders (IDOR protected) & Printable A4 Invoice", "Nguyễn Nhật Huy (524H0052)", "feature/web-myorders-invoice", "Done"),
        ("3.4", "Modern Responsive UI (Bootstrap 5.3.3 desktop & mobile)", "Võ Nguyễn Phúc Thịnh (524H0069)", "feature/member1-web-core", "Done"),
        ("5.1", "Unit Test Project (xUnit + SQLite, 16 meaningful tests)", "Nguyễn Nhật Huy (524H0052)", "feature/unit-tests-businesslogic", "Done"),
        ("6",   "Secure Config, GitFlow PRs, Report.docx, Readme & Zip", "All Members (Docs & Packaging: Nguyễn Nhật Huy, 524H0052)", "docs/report-and-packaging", "Done"),
    ], font_size=8.8)

    # Table 2: Section 1.3 Team Members
    reset_table_rows_with_template_style(doc.tables[2], [
        ("1", "Võ Nguyễn Phúc Thịnh", "524H0069", "Leader / Fullstack Web & Shared Core DB (34%)"),
        ("2", "Ôn Gia Khiêm", "524H0057", "Desktop WinForms Back-Office & Reporting Specialist (33%)"),
        ("3", "Nguyễn Nhật Huy", "524H0052", "Seed/Integrity, Web Invoices, Unit Testing & Docs Specialist (33%)"),
    ], font_size=9.2)

    # Table 3: Section 2 Environment and How to Run
    reset_table_rows_with_template_style(doc.tables[3], [
        ("Visual Studio and .NET versions", "Visual Studio 2022 (v17.10+) / .NET SDK 10.0 (C# 14)"),
        ("SQL Server edition and database name", "Microsoft SQL Server 2022 / Express / LocalDB (Database: B2BWholesaleDB)"),
        ("How to create the database (script file name and order)", "Option A (Recommended): Execute B2B.Data/Scripts/SeedData.sql in SSMS (idempotent, creates 5 tables with FKs/CHECKs and seeds 15–30 rows/table).\nOption B: Launch B2B.Web so EF Core DbInitializer.InitializeAsync() creates and seeds B2BWholesaleDB automatically."),
        ("How to configure the connection string (App.Config / appsettings.json)", "Web Portal: B2B.Web/appsettings.json ('ConnectionStrings:B2BConnection').\nWinForms Back-Office: B2B.WinForms/App.config ('connectionStrings:B2BConnection').\nPoint both files to the same SQL Server instance for integrated Web + WinForms testing. Zero hardcoded strings in C#."),
        ("Startup projects and ports", "Web Portal: B2B.Web (dotnet run --urls http://localhost:5250).\nDesktop Admin: B2B.WinForms (dotnet run).\nUnit Tests: B2B.Tests (dotnet test)."),
        ("Demo accounts (one Admin, one Agent). Dummy passwords only.", "Admin (WinForms ONLY): admin / admin123 (also admin_wh, supervisor).\nAgent (Web Portal ONLY): agent_hanoi / agent123 (also agent_saigon, agent_danang).\nLocked Test Account: agent_locked / agent123 (lock = 1)."),
    ], font_size=9.0)

    # Table 5: Section 3.3 Seed Data
    reset_table_rows_with_template_style(doc.tables[5], [
        ("Item", "20 rows", "Realistic B2B IT & office hardware (Dell 4K, Logitech, Sony, Cisco Catalyst, Synology NAS), including 2 low-stock items (StockQuantity = 6 and 8) so the WinForms Dashboard Low-Stock Alert (< 10) activates immediately."),
        ("Agent", "16 rows", "Regional wholesale distributors across Vietnam (Hanoi, HCMC, Da Nang, Can Tho, Binh Duong, Hai Phong, Bien Hoa, Nha Trang, Hue, Da Lat, etc.) with full addresses and phone numbers."),
        ("Order", "15 rows", "Wholesale orders spanning the past 14 days across varied statuses (Pending, Confirmed, Shipped, Delivered) linked to valid AgentIDs."),
        ("OrderDetail", "30 rows", "Exactly 2 itemized line items for every single Order #1–#15 (zero orphan order headers) with realistic bulk quantities and unit prices."),
        ("Users", "19 rows", "Includes 3 Admin accounts (admin, admin_wh, supervisor) for WinForms and 16 Agent accounts mapped to Agents #1–#16, including 1 pre-locked account (agent_locked, lock = 1)."),
    ], font_size=9.0)

    # Table 6: Section 3.4 Integrity
    reset_table_rows_with_template_style(doc.tables[6], [
        ("Order -> Agent", "FK + DeleteBehavior.Restrict / ON DELETE NO ACTION", "Prevents deleting an active Agent who has historical orders; uses SQL Server compliant ON DELETE NO ACTION."),
        ("OrderDetail -> Order", "FK + DeleteBehavior.Cascade / ON DELETE CASCADE", "Deleting a master Order automatically deletes all child OrderDetails so zero orphan line items remain."),
        ("OrderDetail -> Item", "FK + DeleteBehavior.Restrict / ON DELETE NO ACTION", "Prevents deleting an Item referenced in historical OrderDetails (protects invoice & sales audit history)."),
        ("Users -> Agent", "FK + DeleteBehavior.SetNull / ON DELETE SET NULL", "Safely decouples Agent reference if an unassigned Agent is removed without breaking Users records."),
        ("Domain CHECK Constraints", "CHECK (StockQuantity >= 0), CHECK (Price >= 0), CHECK (Quantity > 0), CHECK (UnitAmount >= 0), CHECK (Role IN ('Admin','Agent'))", "Enforced in both EF Core Fluent API (B2BDbContext.cs) and T-SQL (SeedData.sql); verified on relational SQLite in DatabaseIntegrityTests."),
        ("Users: unique username / email", "UNIQUE Index on UserName and email", "Guarantees unique login identities and prevents duplicate account registration."),
    ], font_size=9.0)

    # Table 8: Section 5.3 Transaction Test Evidence
    reset_table_rows_with_template_style(doc.tables[8], [
        ("Enough stock (Normal)", "50 (Dell 4K)\n30 (Logitech KB)", "10x Dell 4K\n5x Logitech KB", "Order SAVED (Status: Pending, 2 details).\nStock deducted atomically: Dell = 40, KB = 25."),
        ("Insufficient stock (Excess order)", "83 (Dell 4K)", "9999x Dell 4K", "Order BLOCKED with InvalidOperationException.\nNo Order saved; Dell stock remains 83."),
        ("Failure in the middle: rollback", "50 (Dell 4K)\n5 (Logitech Mouse)", "10x Dell 4K (OK)\n20x Mouse (exceeds 5)", "Transaction ROLLED BACK atomically.\n0 Orders created; Dell stays 50, Mouse stays 5."),
        ("Duplicate item combined check", "10 (Synology NAS)", "6x NAS + 6x NAS (=12)", "OrderService aggregates duplicate ItemIDs (12 > 10), blocks order & rolls back. Stock stays 10."),
    ], font_size=9.0)

    # Table 9: Section 6 Unit Testing Summary
    reset_table_rows_with_template_style(doc.tables[9], [
        ("Framework and project name", "xUnit (v2.9.3) + Microsoft.EntityFrameworkCore.Sqlite / Project: B2B.Tests (.NET 10.0)"),
        ("Business logic under test (class and methods)", "B2B.Data.Services.OrderService (PlaceOrderAsync, CalculateOrderTotal, GetAgentOrdersAsync, GetAgentOrderInvoiceAsync), B2B.Data.Services.AuthService (AuthenticateAsync), LoginAttemptTracker, DbInitializer, B2BDbContext"),
        ("Number of tests and pass rate", "12 Test Methods (16 Test Executions) / 100% Pass Rate (16 Passed, 0 Failed, 0 Skipped)"),
    ], font_size=9.0)

    # Table 10: Section 6 Unit Test Cases (with fixed widths summing to 6.5 in & wrappable method names!)
    reset_table_rows_with_template_style(
        doc.tables[10],
        [
            ("1",  wrappable("DeductStock_WhenStockIsSufficient_ShouldDecreaseStockQuantity"), "Multi-item order within stock", "Order saved (Pending); stocks 50->40, 30->25", "Committed & verified via fresh SQLite context", "Pass"),
            ("2",  wrappable("PlaceOrder_WhenStockIsInsufficient_ShouldThrowExceptionAndRollback"), "Item 1 ok (10/50), Item 2 exceeds (20/5)", "Throws exception; full relational rollback", "0 Orders created; stocks untouched (50 & 5)", "Pass"),
            ("3",  wrappable("CalculateOrderTotal_WithMultipleItems_ShouldReturnCorrectSum"), "3 lines: 5x11.5M + 10x3.45M + 20x1.69M", "Exact sum = 125,800,000 VND", "Returned 125,800,000 VND", "Pass"),
            ("4",  wrappable("AuthenticateUser_WhenRoleIsInvalid_ShouldDenyAccess") + " (4 cases)", "Admin->Web, Agent->WinForms & valid roles", "Cross-portal denied; matching roles allowed", "All 4 InlineData cases passed", "Pass"),
            ("5",  wrappable("Login_WhenPasswordFailedMultipleTimes_ShouldLockAccount"), "5 wrong passwords then 1 correct password", "Sets Users.lock=true; blocks valid login", "Persisted lock=true verified; login blocked", "Pass"),
            ("6",  wrappable("PlaceOrder_WhenOrderDetailsIsEmpty_ShouldThrowExceptionAndBlockOrder"), "Place order with empty OrderDetails", "Throws InvalidOperationException; 0 orders", "Blocked; 0 orders created", "Pass"),
            ("7",  wrappable("PlaceOrder_WhenQuantityIsZeroOrNegative_ShouldThrowArgumentOutOfRangeException") + " (2 cases)", "Order quantity = 0 and -5", "Throws ArgumentOutOfRangeException", "Both cases rejected; stock unchanged (100)", "Pass"),
            ("8",  wrappable("PlaceOrder_WhenQuantityEqualsExactStock_ShouldSucceedAndSetStockToZero"), "Order qty 8 == StockQuantity 8", "Succeeds; remaining stock becomes 0", "Committed; StockQuantity = 0", "Pass"),
            ("9",  wrappable("PlaceOrder_WhenSameItemAddedTwice_ShouldValidateCombinedQuantity"), "Same ItemID twice: 6+6=12 > stock 10", "Validates combined qty & blocks order", "Exception thrown; stock stays 10", "Pass"),
            ("10", wrappable("GetAgentOrders_AndInvoice_ShouldEnforceAgentOwnershipIsolation"), "Agent 1 opens own & Agent 2's Invoice", "Own invoice OK; Agent 2's returns null", "IDOR blocked; strict agent isolation", "Pass"),
            ("11", wrappable("SeedData_ShouldInsert15To30RowsPerTable_WithValidRelationships"), "DbInitializer on fresh SQLite DB", "15–30 rows/table, roles, low-stock", "20/16/19/15/30 rows & all checks passed", "Pass"),
            ("12", wrappable("DatabaseIntegrity_ShouldEnforceForeignKeysCascadeRestrict_AndCheckConstraints"), "Orphan FK, Stock<0, Delete Item/Order", "Violations fail; Order cascades details", "All 4 relational SQLite checks passed", "Pass"),
        ],
        font_size=8.2,
        col_widths_in=[0.35, 1.95, 1.15, 1.25, 1.30, 0.50]
    )

    # Table 11: Section 7 System Configuration
    reset_table_rows_with_template_style(doc.tables[11], [
        ("WinForms back-office", "B2B.WinForms/App.config", "ConfigurationManager.OpenMappedExeConfiguration -> ConnectionStrings['B2BConnection'] (AppDatabase.cs)"),
        ("Web application", "B2B.Web/appsettings.json", "builder.Configuration.GetConnectionString('B2BConnection') in Program.cs"),
        ("Unit test project", "Isolated SQLite In-Memory", "SqliteTestContext opens 'DataSource=:memory:' with PRAGMA foreign_keys = ON per test (zero hardcoded prod DB credentials)"),
    ], font_size=9.0)

    # Table 12: Section 8 Git Repository & Branching Strategy
    reset_table_rows_with_template_style(doc.tables[12], [
        ("Repository link", "https://github.com/thinhvo06/B2BWholesaleSystem"),
        ("Branching strategy (names and rules)", "GitFlow model: 'main' (stable release), 'develop' (integration), and dedicated feature/docs branches per task: feature/member1-web-core, feature/member2-winforms, feature/web-myorders-invoice, feature/unit-tests-businesslogic, docs/report-and-packaging."),
        ("Pull request and review rules (who reviews, when to merge)", "No direct bulk uploads to main. Each member develops on feature branches with atomic commits, pushes to origin, and opens Pull Requests reviewed and approved by another team member before merging."),
    ], font_size=9.0)

    # Table 13: Section 8 Git Contributions per Member
    reset_table_rows_with_template_style(doc.tables[13], [
        ("Võ Nguyễn Phúc Thịnh (524H0069)", "main, develop, feature/member1-web-core", "9 commits", "PR #1 (Merged)", "Core DB, Web Auth, Catalog, Cart & Transaction Checkout"),
        ("Ôn Gia Khiêm (524H0057)", "feature/member2-winforms", "4 commits", "PR #2 (Open / Ready)", "WinForms Admin Login, CRUD, Shipping Manifest & Dashboard"),
        ("Nguyễn Nhật Huy (524H0052)", "feature/web-myorders-invoice, feature/unit-tests-businesslogic, docs/report-and-packaging", "7 commits", "PR #3–#5 (Open / Ready)", "Seed/Integrity, My Orders & A4 Invoice, 16 Unit Tests, Report & Packaging"),
    ], font_size=8.8)

    # Table 14: Section 9 Contribution of Each Member
    reset_table_rows_with_template_style(doc.tables[14], [
        ("Võ Nguyễn Phúc Thịnh (Member 1)", "524H0069", "Task 2a (Shared DB Schema & EF Core Code-First), Task 3.1 (Web Agent Login), Task 3.2 (Catalog, Bulk Cart, Master-Detail Transaction), Task 3.4 (Bootstrap 5 Responsive UI), GitHub Repo Setup", "34%"),
        ("Ôn Gia Khiêm (Member 2)", "524H0057", "Task 1.1 (WinForms Admin Login, 5-attempt lockout & App.config), Task 1.2 (Items/Agents CRUD, Stock-In & Order Management), Task 1.3 (A4 Shipping Manifest Preview/Print/PDF), Task 1.4 (Dashboard: Best-selling, Low-stock < 10, Revenue by Agent)", "33%"),
        ("Nguyễn Nhật Huy (Member 3)", "524H0052", "Task 2a/2b (Unified Seed Data 15–30 rows/table & CHECK/FK Integrity), Task 3.3 (My Orders, IDOR Security & A4 Printable Invoice), Task 5.1 (16 Relational SQLite xUnit Tests), Report.docx, Team Workbook, Readme.txt & SourceCode.zip", "33%"),
        ("Total", "", "All Assignment 2 Rubric Criteria Covered (100% Scope)", "100%"),
    ], font_size=8.8)

    # Table 15: Appendix B Generative AI Use
    reset_table_rows_with_template_style(doc.tables[15], [
        ("Antigravity AI (13/11/2026)", "Project Architecture & Work Breakdown (Member 1)", "Divide lab assignment for 3 students and design 1 Solution - 4 Projects architecture.", "Adopted 34%–33%–33% workload balance and EF Core Code-First shared B2B.Data library.", "Reviewed against official grading rubric and lecturer assignment sheet."),
        ("Antigravity AI (13/11/2026)", "Web Portal & Code-First Setup (Member 1)", "Implement EF Core models, Agent Login, Catalog, Cart, and Transaction Checkout.", "Refined transaction exception handling and Bootstrap 5 responsive UI.", "Verified via automated E2E browser script and responsive screenshots."),
        ("ChatGPT (13/11/2026)", "WinForms Back-Office & SQL Troubleshooting (Member 2)", "Implement WinForms Admin Login, CRUD, Shipping Manifest, Dashboard and fix SQL Server syntax.", "Adapted AppDatabase to App.config, implemented 5-attempt lockout, fixed ON DELETE NO ACTION.", "Built and ran B2B.WinForms locally against SQL Server."),
        ("Antigravity AI (18/11/2026)", "Member 3 Implementation, Unit Testing & Documentation", "Unify SeedData/CHECK integrity, build Task 3.3 My Orders & Printable A4 Invoice, write Task 5.1 SQLite xUnit tests, align Report.docx with official template.", "Extracted shared OrderService & AuthService, built MyOrders & @media print Invoice, wrote 16 relational SQLite unit tests, updated Workbook/Report/Zip.", "Verified via clean-room dotnet build (4/4 projects, 0 errors), dotnet test (16/16 PASSED), live E2E script (IDOR + A4 PDF), and visual inspection."),
    ], font_size=8.6)

    # 7. Snapshot paragraph list BEFORE inserting any new paragraphs (so indices NEVER shift!)
    snapshot_paragraphs = list(doc.paragraphs)
    sec54_desc = None

    for p in snapshot_paragraphs:
        txt = p.text.strip()

        if txt.startswith("Responsible: Member 2"):
            replace_paragraph_text_preserve_format(p, "Responsible: Member 2 — Ôn Gia Khiêm (524H0057) | Desktop WinForms & Reporting Specialist")

        elif txt.startswith("Responsible: Member 1"):
            replace_paragraph_text_preserve_format(p, "Responsible: Member 1 — Võ Nguyễn Phúc Thịnh (524H0069) | Fullstack Web & Shared Core Architecture")

        elif txt.startswith("4.1 Task 1.1: Secure Login Form"):
            np = next_paragraph(p)
            if np:
                replace_paragraph_text_preserve_format(
                    np,
                    "The WinForms LoginForm reads its SQL Server connection from B2B.WinForms/App.config via AppDatabase.cs (zero hardcoded connection strings) and strictly permits only users with Role = 'Admin'. Agent accounts are rejected with a clear role-violation warning. After 5 consecutive incorrect passwords, the failed-attempt tracker writes Users.lock = true persistently to block brute-force logins."
                )

        elif txt.startswith("4.3 Task 1.3: Shipping Manifest Report"):
            np = next_paragraph(p)
            if np:
                replace_paragraph_text_preserve_format(
                    np,
                    "Implemented in ManifestView.cs using A4 portrait PrintDocument with live Print Preview, direct printing, and Microsoft Print to PDF export. Each Shipping Manifest displays distributor header info, agent name and delivery address, itemized delivery lines (STT, Item ID, Item Name, Size, Quantity), manifest preparation date, and signature blocks for both warehouse dispatcher and receiving agent."
                )

        elif txt.startswith("5.4 Task 3.3: My Orders and Printable Invoice"):
            sec54_desc = next_paragraph(p)

        elif txt.startswith("Figure 5.6: Desktop View (1280px)"):
            replace_paragraph_text_preserve_format(p, "Figure 5.9: Desktop View (1280px) - 3-Column Responsive Grid, Header Navigation & Live Cart Badge")
            p.paragraph_format.keep_with_next = True

        elif txt.startswith("Figure 5.7: Mobile Responsive View (375px)"):
            replace_paragraph_text_preserve_format(p, "Figure 5.10: Mobile Responsive View (375px) - Collapsed Hamburger Menu, Single-Column Cards & Adaptive Layout")
            p.paragraph_format.keep_with_next = True

        elif txt.startswith("6. Exercise 5: Unit Testing"):
            # Insert clean intro paragraph right after Section 6 heading (before Table 9)
            insert_paragraph_after(
                p,
                "Responsible: Member 3 — Nguyễn Nhật Huy (524H0052) | QA & Unit Testing Specialist\n"
                "The B2B.Tests project uses xUnit 2.9.3 paired with Microsoft.EntityFrameworkCore.Sqlite (an isolated relational SQLite in-memory database per test with PRAGMA foreign_keys = ON). Every test executes real production business services (OrderService, AuthService, DbInitializer, B2BDbContext) with real SQL transactions, full rollbacks, FK Cascade/Restrict enforcement, CHECK constraints, RBAC role separation, 5-failure account lockout, and My Orders/Invoice IDOR isolation. All 16 / 16 test executions pass (100%).",
                size=10.0,
                space_before=4,
                space_after=6
            )

        elif txt.startswith("Figure 6.1:"):
            replace_paragraph_text_preserve_format(p, "Figure 6.1: xUnit Test Execution Output — All 16 Relational SQLite Business Logic Tests Passed (100%)")
            p.paragraph_format.keep_with_next = True
            img_p = next_paragraph(p)
            if img_p is not None:
                img_p.text = ""
                img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                ut_img = os.path.join(SC_DIR, "unit_test_results.png")
                if os.path.exists(ut_img):
                    img_p.add_run().add_picture(ut_img, width=Inches(6.2))

        elif txt == "Appendix A: Readme.txt":
            p_readme = next_paragraph(p)
            if p_readme is not None and os.path.exists(README_PATH):
                with open(README_PATH, "r", encoding="utf-8") as f:
                    readme_txt = f.read().strip()
                p_readme.text = ""
                p_readme.alignment = WD_ALIGN_PARAGRAPH.LEFT
                r = p_readme.add_run(readme_txt)
                r.font.name = "Consolas"
                r.font.size = Pt(8.2)

    # Now safely populate Section 5.4 and insert its 3 Figure + Image pairs (with keep_with_next=True on captions!)
    if sec54_desc is not None:
        sec54_desc.text = ""
        r_resp = sec54_desc.add_run("Responsible: Member 3 — Nguyễn Nhật Huy (524H0052) | Web Invoices, Testing & Documentation\n")
        r_resp.bold = True
        r_resp.font.name = "Calibri"
        r_resp.font.size = Pt(10)
        r_body = sec54_desc.add_run(
            "Implemented the complete 'My Orders' portal and A4 Printable Invoice feature in B2B.Web backed by the shared OrderService:\n"
            "• My Orders History (/Order/MyOrders): Calls OrderService.GetAgentOrdersAsync(currentAgentId, status, search) so each logged-in agent sees ONLY their own past orders. Displays 4 summary KPI cards (Total Orders, Total Value Spent, Pending Count, Shipped/Delivered Count), status filter, keyword search, and responsive Bootstrap 5 order table.\n"
            "• Strict IDOR Ownership Protection: OrderController.Invoice(int id) verifies order ownership via OrderService.GetAgentOrderInvoiceAsync(id, currentAgentId). Any attempt by Agent #1 to open Agent #2's invoice URL (e.g., /Order/Invoice/2) is immediately blocked with a security alert and redirected back to My Orders.\n"
            "• Printable A4 Wholesale Invoice (/Order/Invoice/{id}): Styled with dedicated CSS @media print rules (A4 portrait margins, d-print-none hiding navbar/footer/buttons) so clicking 'In Hóa Đơn / Xuất PDF' (window.print()) outputs a single-page professional B2B invoice containing inline SVG distributor logo, invoice number (INV-YYYYMMDD-XXXX), issue date, order status, Bill To / Ship To agent details, itemized table, subtotal/VAT/grand total, Vietnamese amount in words, and 3 signature blocks."
        )
        r_body.font.name = "Calibri"
        r_body.font.size = Pt(10)

        cursor = sec54_desc
        for cap_text, img_file, width_in in [
            ("Figure 5.6: My Orders Page — Agent #1 (Phúc Anh Tech) viewing only own orders (#1, #6) with KPI cards and filters", "7_my_orders_page.png", 5.6),
            ("Figure 5.7: Printable B2B Wholesale Invoice View (Order #1) — Logo, Itemized Breakdown, Amount in Words & Print/PDF Button", "8_invoice_page.png", 5.1),
            ("Figure 5.8: IDOR Security Verification — Agent #1 Blocked from Accessing Agent #2's Invoice (#2)", "10_my_orders_idor_blocked.png", 5.6),
        ]:
            img_path = os.path.join(SC_DIR, img_file)
            if os.path.exists(img_path):
                cap_p = insert_paragraph_after(
                    cursor, cap_text, bold=True, italic=True, size=9.5,
                    align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=2, keep_with_next=True
                )
                pic_p = insert_paragraph_after(
                    cap_p, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=8
                )
                pic_p.add_run().add_picture(img_path, width=Inches(width_in))
                cursor = pic_p

    # Also ensure every Figure caption in the entire doc keeps with its image
    for p in doc.paragraphs:
        if p.text.strip().startswith("Figure "):
            p.paragraph_format.keep_with_next = True

    doc.save(REPORT_PATH)

    # Final verification scan
    verify = docx.Document(REPORT_PATH)
    all_text = "\n".join([p.text for p in verify.paragraphs])
    for t in verify.tables:
        for row in t.rows:
            for c in row.cells:
                all_text += "\n" + c.text
    for s in verify.sections:
        for p in s.footer.paragraphs:
            all_text += "\n" + p.text

    for forbidden in ["[MSSV", "Group 08", "How to use this template", "Guidance (delete", "524h0057", "Nguyễn Nhật huy"]:
        assert forbidden not in all_text, f"Found leftover unwanted string: {forbidden}"
    assert "1. Overview and Division of Labor" in all_text
    assert "1.1 System Overview" in all_text

    print(f"[SUCCESS] Rebuilt clean official-template Report.docx -> {REPORT_PATH}")


if __name__ == "__main__":
    main()
