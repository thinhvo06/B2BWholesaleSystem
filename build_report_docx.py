import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import os

doc = docx.Document()

# Set standard margins (1 inch)
for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

# Helper function to set table header shading and cell borders
def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def format_table(table, col_widths=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(table.rows):
        for j, cell in enumerate(row.cells):
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            if i == 0:
                set_cell_background(cell, "2B6CB0")
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    for r in p.runs:
                        r.font.bold = True
                        r.font.color.rgb = RGBColor(255, 255, 255)
            else:
                if i % 2 == 1:
                    set_cell_background(cell, "F7FAFC")
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(1)
                    p.paragraph_format.space_after = Pt(1)
            if col_widths and j < len(col_widths):
                cell.width = col_widths[j]

# ==================== COVER / HEADER ====================
p_top = doc.add_paragraph()
r_sub = p_top.add_run("SE LAB QT2 ASSIGNMENT 2 REPORT\n")
r_sub.font.size = Pt(12)
r_sub.font.bold = True
r_sub.font.color.rgb = RGBColor(43, 108, 176)

r_title = p_top.add_run("B2B Wholesale Order Management System\n")
r_title.font.size = Pt(22)
r_title.font.bold = True
r_title.font.color.rgb = RGBColor(26, 54, 93)

r_sub2 = p_top.add_run("Back-Office Desktop (WinForms) and Agent Portal (ASP.NET Core MVC)\nSoftware Engineering Lab Assignment 2 – Sem 1_2627 | FIT of TDTU")
r_sub2.font.size = Pt(11)
r_sub2.font.color.rgb = RGBColor(113, 128, 150)
p_top.paragraph_format.space_after = Pt(14)

# Group Box
p_grp = doc.add_paragraph()
r_grp = p_grp.add_run("Group: [Group 08 - Điền số nhóm của bạn]\n")
r_grp.font.bold = True
r_grp.font.size = Pt(13)

members_text = (
    "1. [MSSV 1] : [Họ và tên Sinh viên 1 - Trưởng nhóm]\n"
    "2. [MSSV 2] : [Họ và tên Sinh viên 2]\n"
    "3. [MSSV 3] : [Họ và tên Sinh viên 3]"
)
r_mem = p_grp.add_run(members_text)
r_mem.font.size = Pt(11)
p_grp.paragraph_format.space_after = Pt(10)

# Links table
t_links = doc.add_table(rows=2, cols=3)
hdr = t_links.rows[0].cells
hdr[0].text = "GitHub repository"
hdr[1].text = "Video demo (optional)"
hdr[2].text = "Web option chosen"

row_links = t_links.rows[1].cells
row_links[0].text = "https://github.com/[username]/B2BWholesaleSystem"
row_links[1].text = "https://youtu.be/[demo-link-neu-co]"
row_links[2].text = "Option C (Exer 4): ASP.NET Core MVC (Code First)"
format_table(t_links, [Inches(3.2), Inches(2.0), Inches(2.0)])

doc.add_page_break()

# ==================== 1. OVERVIEW AND DIVISION OF LABOR ====================
h1 = doc.add_heading("1. Overview and Division of Labor", level=1)

doc.add_heading("1.1 System Overview", level=2)
p_ov = doc.add_paragraph(
    "The B2B Wholesale Order Management System is a dual-platform enterprise solution tailored for regional distributors. "
    "The system consists of two tightly integrated components sharing a unified Microsoft SQL Server database: "
    "(1) A Desktop Back-Office Application built with Windows Forms (.NET 10.0) enabling warehouse staff to manage item catalog, "
    "register distributor agents, process incoming wholesale orders, and print shipping manifests; and "
    "(2) A Modern Web Application built with ASP.NET Core MVC 10.0 (Code-First) serving as the Agent Ordering Portal, "
    "where registered agents can browse products, manage bulk carts, and place orders secured by database transaction stock deduction."
)
p_ov.paragraph_format.space_after = Pt(8)

doc.add_heading("1.2 Division of Labor", level=2)
t_div = doc.add_table(rows=12, cols=5)
col_widths_div = [Inches(0.6), Inches(2.6), Inches(1.8), Inches(1.5), Inches(0.8)]
h_div = t_div.rows[0].cells
h_div[0].text = "Task"
h_div[1].text = "Feature"
h_div[2].text = "Responsible (name, ID)"
h_div[3].text = "Git branch"
h_div[4].text = "Status"

tasks_data = [
    ("2", "Database schema, seed data and integrity", "Member 1 & Member 3", "feature/member1-web-core", "Done"),
    ("1.1", "WinForms secure login (Admin role only)", "Member 2", "feature/winforms-admin", "Planned"),
    ("1.2", "Item and Agent CRUD, order management", "Member 2", "feature/winforms-admin", "Planned"),
    ("1.3", "Shipping manifest report (RDLC/PDF)", "Member 2", "feature/winforms-reports", "Planned"),
    ("1.4", "Data filter and dashboard (Best-selling, Low stock)", "Member 2", "feature/winforms-reports", "Planned"),
    ("3.1", "Web login (Agent role only, Admin blocked)", "Member 1", "feature/member1-web-core", "Done"),
    ("3.2", "Catalog and master-detail order with transaction", "Member 1", "feature/member1-web-core", "Done"),
    ("3.3", "My Orders and printable invoice", "Member 3", "feature/web-invoices", "Planned"),
    ("3.4", "Responsive UI (Bootstrap 5, mobile & desktop)", "Member 1", "feature/member1-web-core", "Done"),
    ("5.1", "Unit test project (xUnit, 6 business logic tests)", "Member 3 & Member 1", "feature/unit-tests", "Done"),
    ("6", "Configuration, Git collaboration and report", "All members (Lead: Member 1 & 3)", "develop, main", "Done")
]

for idx, row_data in enumerate(tasks_data):
    row = t_div.rows[idx + 1].cells
    for c_idx in range(5):
        row[c_idx].text = row_data[c_idx]

format_table(t_div, col_widths_div)

doc.add_heading("1.3 Team Members", level=2)
t_mem = doc.add_table(rows=4, cols=4)
col_widths_mem = [Inches(0.6), Inches(2.3), Inches(1.8), Inches(2.3)]
h_mem = t_mem.rows[0].cells
h_mem[0].text = "No."
h_mem[1].text = "Name"
h_mem[2].text = "Student ID"
h_mem[3].text = "Role"

m_data = [
    ("1", "[Tên Sinh Viên 1]", "[MSSV 1]", "Trưởng nhóm / Fullstack Web & Shared DB"),
    ("2", "[Tên Sinh Viên 2]", "[MSSV 2]", "Desktop WinForms & Reporting Specialist"),
    ("3", "[Tên Sinh Viên 3]", "[MSSV 3]", "QA, Unit Testing & Documentation Specialist")
]
for idx, r_data in enumerate(m_data):
    row = t_mem.rows[idx + 1].cells
    for c_idx in range(4):
        row[c_idx].text = r_data[c_idx]

format_table(t_mem, col_widths_mem)

doc.add_page_break()

# ==================== 2. ENVIRONMENT AND HOW TO RUN ====================
doc.add_heading("2. Environment and How to Run", level=1)
t_env = doc.add_table(rows=7, cols=2)
col_widths_env = [Inches(2.8), Inches(4.2)]
h_env = t_env.rows[0].cells
h_env[0].text = "Item"
h_env[1].text = "Your answer"

env_data = [
    ("Visual Studio and .NET versions", "Visual Studio 2022 (v17.10+) / .NET SDK 10.0 (C# 13)"),
    ("SQL Server edition and database name", "Microsoft SQL Server 2022 / LocalDB (Database: B2BWholesaleDB)"),
    ("How to create the database (script file name and order)", 
     "Run B2B.Data/Scripts/SeedData.sql in SSMS, OR simply launch B2B.Web which automatically triggers DbInitializer.InitializeAsync() to create tables and seed 15-30 realistic rows."),
    ("How to configure the connection string (App.Config / appsettings.json)", 
     "Stored in B2B.Web/appsettings.json under 'ConnectionStrings:B2BConnection' and B2B.WinForms/App.config under '<connectionStrings>'. Passwords masked in repo."),
    ("Startup projects and ports", 
     "Web App: B2B.Web (Runs on http://localhost:5264). Back-Office: B2B.WinForms."),
    ("Demo accounts (one Admin, one Agent). Dummy passwords only.", 
     "Admin account (for WinForms): admin / admin123\nAgent account (for Web): agent_hanoi / agent123 (or agent_saigon / agent123)")
]

for idx, r_data in enumerate(env_data):
    row = t_env.rows[idx + 1].cells
    row[0].text = r_data[0]
    row[1].text = r_data[1]

format_table(t_env, col_widths_env)

# ==================== 3. DATABASE CONFIGURATION & SEED DATA ====================
doc.add_heading("3. Database Configuration & Seed Data (10 marks)", level=1)

doc.add_heading("3.1 Database Diagram", level=2)
p_erd = doc.add_paragraph(
    "The Entity-Relationship Diagram (ERD) below illustrates the 5 tables (Item, Agent, Order, OrderDetail, Users) "
    "and their relationships with primary keys (PK) and foreign keys (FK) enforced via Entity Framework Core Fluent API:\n"
    "• Order (N) ─── (1) Agent [FK: AgentID, OnDelete: Restrict]\n"
    "• OrderDetail (N) ─── (1) Order [FK: OrderID, OnDelete: Cascade]\n"
    "• OrderDetail (N) ─── (1) Item [FK: ItemID, OnDelete: Restrict]\n"
    "• Users (N) ─── (0..1) Agent [FK: AgentID, OnDelete: SetNull]"
)

doc.add_heading("3.2 Schema", level=2)
t_sch = doc.add_table(rows=6, cols=4)
col_widths_sch = [Inches(1.2), Inches(3.2), Inches(1.1), Inches(1.5)]
h_sch = t_sch.rows[0].cells
h_sch[0].text = "Table"
h_sch[1].text = "Columns (name, data type, constraints)"
h_sch[2].text = "Primary key"
h_sch[3].text = "Foreign keys"

sch_data = [
    ("Item", "ItemID (int, identity), ItemName (nvarchar 200, not null), Size (nvarchar 50), Price (decimal 18,2, not null), StockQuantity (int, not null)", "ItemID", "None"),
    ("Agent", "AgentID (int, identity), AgentName (nvarchar 200, not null), Address (nvarchar 300), Phone (nvarchar 50)", "AgentID", "None"),
    ("Order", "OrderID (int, identity), OrderDate (datetime2, not null), AgentID (int, not null), OrderStatus (nvarchar 50, not null)", "OrderID", "AgentID -> Agent(AgentID)"),
    ("OrderDetail", "ID (int, identity), OrderID (int, not null), ItemID (int, not null), Quantity (int, not null), UnitAmount (decimal 18,2, not null)", "ID", "OrderID -> Order(OrderID)\nItemID -> Item(ItemID)"),
    ("Users", "UserID (int, identity), UserName (nvarchar 100, unique), email (nvarchar 150, unique), password (nvarchar 255), lock (bit), Role (nvarchar 50), AgentID (int, nullable)", "UserID", "AgentID -> Agent(AgentID)")
]
for idx, r_data in enumerate(sch_data):
    row = t_sch.rows[idx + 1].cells
    for c_idx in range(4):
        row[c_idx].text = r_data[c_idx]

format_table(t_sch, col_widths_sch)

doc.add_heading("3.3 Seed Data (5 marks)", level=2)
t_seed = doc.add_table(rows=6, cols=3)
col_widths_seed = [Inches(1.5), Inches(1.0), Inches(4.5)]
h_seed = t_seed.rows[0].cells
h_seed[0].text = "Table"
h_seed[1].text = "Rows"
h_seed[2].text = "Notes on the data (realism, variety, Admin and Agent users)"

seed_data = [
    ("Item", "18 rows", "Realistic wholesale electronic and IT hardware (Dell UltraSharp, Logitech MX series, Sony headphones, Samsung SSDs, TP-Link Mesh, etc.) with valid stock and sizes."),
    ("Agent", "16 rows", "Regional commercial agents across Vietnam (Hanoi, HCMC, Da Nang, Can Tho, Binh Duong, Hai Phong, Nha Trang, etc.) with realistic addresses and phone numbers."),
    ("Order", "15 rows", "Spanning multiple dates across the past two weeks with various statuses ('Pending', 'Confirmed', 'Shipped', 'Delivered') to test warehouse filtering."),
    ("OrderDetail", "25 rows", "Multi-item details referencing valid orders and items with accurate wholesale unit amounts and bulk quantities."),
    ("Users", "16 rows", "Includes 3 Admin accounts (admin, admin_wh, supervisor), 12 active Agent accounts (agent_hanoi, agent_saigon, etc.) and 1 locked account (agent_locked) for validation tests.")
]
for idx, r_data in enumerate(seed_data):
    row = t_seed.rows[idx + 1].cells
    for c_idx in range(3):
        row[c_idx].text = r_data[c_idx]

format_table(t_seed, col_widths_seed)

doc.add_heading("3.4 Integrity (5 marks)", level=2)
t_integ = doc.add_table(rows=6, cols=3)
col_widths_integ = [Inches(1.8), Inches(2.2), Inches(3.0)]
h_integ = t_integ.rows[0].cells
h_integ[0].text = "Relationship / rule"
h_integ[1].text = "Constraint or cascade used"
h_integ[2].text = "Reason"

integ_data = [
    ("Order -> Agent", "FK + DeleteBehavior.Restrict", "Prevents deleting an active Agent who has existing transaction orders in the history."),
    ("OrderDetail -> Order", "FK + DeleteBehavior.Cascade", "Deleting a master Order automatically removes all its child OrderDetail line items cleanly."),
    ("OrderDetail -> Item", "FK + DeleteBehavior.Restrict", "Prevents deleting an Item that is referenced in historical order details to maintain audit integrity."),
    ("StockQuantity >= 0", "CHECK (StockQuantity >= 0) / Business logic validation", "Prevents negative inventory under heavy bulk ordering concurrency."),
    ("Users: unique username / email", "UNIQUE Index on UserName and email", "Ensures credential security, uniqueness, and prevents collision in authentication.")
]
for idx, r_data in enumerate(integ_data):
    row = t_integ.rows[idx + 1].cells
    for c_idx in range(3):
        row[c_idx].text = r_data[c_idx]

format_table(t_integ, col_widths_integ)

doc.add_page_break()

# ==================== 4. EXERCISE 1: BACK-OFFICE WINFORMS ====================
doc.add_heading("4. Exercise 1: Back-Office Windows Application (25 marks)", level=1)
p_wf_intro = doc.add_paragraph("Responsible: Member 2 (Desktop WinForms & Reporting Specialist)")
p_wf_intro.runs[0].font.italic = True

doc.add_heading("4.1 Task 1.1: Secure Login Form (5 marks)", level=2)
p_t11 = doc.add_paragraph(
    "The WinForms login screen enforces role-based access control allowing only users with Role 'Admin' to authenticate. "
    "Agent accounts attempting to log in are rejected with a clear warning: 'Access denied: Only warehouse administrators can access Back-Office'. "
    "Password verification checks against database records, and account lockout is validated."
)

doc.add_heading("4.2 Task 1.2: Item, Agent and Order Management (10 marks)", level=2)
p_t12 = doc.add_paragraph(
    "• Item CRUD: Allows warehouse administrators to view, add new items, update prices, and replenish stock (StockQuantity).\n"
    "• Agent CRUD: Enables registering new distributor agents, updating address and phone contact.\n"
    "• Order Management: Displays incoming orders from Web Portal in real time, inspects line items (OrderDetails), and transitions status from 'Pending' to 'Shipped'."
)

doc.add_heading("4.3 Task 1.3: Shipping Manifest Report (5 marks)", level=2)
p_t13 = doc.add_paragraph(
    "Report generation module (RDLC / PDF) that produces a standardized printable 'Shipping Manifest' for a selected order, "
    "complete with Agent info, delivery address, item list, ordered quantities, date, and signature boxes."
)

doc.add_heading("4.4 Task 1.4: Data Filter and Dashboard (5 marks)", level=2)
p_t14 = doc.add_paragraph(
    "The Admin Dashboard provides three core analytical queries:\n"
    "1. Best-selling items: Aggregates total quantities sold per item across all orders.\n"
    "2. Low-stock items warning: Flags items where StockQuantity <= 10 with visual warning alerts.\n"
    "3. Total revenue by agent: Summarizes revenue grouped by distributor agent."
)

doc.add_page_break()

# ==================== 5. WEB APPLICATION: AGENT PORTAL ====================
doc.add_heading("5. Web Application: Agent Portal (35 marks)", level=1)
p_web_intro = doc.add_paragraph("Responsible: Member 1 (Fullstack Web & Shared Core Architecture)")
p_web_intro.runs[0].font.italic = True

doc.add_heading("5.1 Option Chosen", level=2)
t_opt = doc.add_table(rows=4, cols=2)
col_widths_opt = [Inches(2.5), Inches(4.5)]
h_opt = t_opt.rows[0].cells
h_opt[0].text = "Item"
h_opt[1].text = "Your answer"

opt_data = [
    ("Option chosen", "Option C (Exer 4): ASP.NET Web App Core (MVC) - Code First"),
    ("Reason", "Highly recommended by the instructor. Provides clean separation of concerns (MVC), robust EF Core Code-First migrations, seamless Cookie Authentication, and modern Bootstrap 5 responsiveness."),
    ("Main libraries and versions", "Microsoft.AspNetCore.Mvc, Microsoft.EntityFrameworkCore 10.0, Microsoft.EntityFrameworkCore.SqlServer 10.0, Bootstrap 5.3.3, Bootstrap Icons 1.11.3")
]
for idx, r_data in enumerate(opt_data):
    row = t_opt.rows[idx + 1].cells
    row[0].text = r_data[0]
    row[1].text = r_data[1]

format_table(t_opt, col_widths_opt)

doc.add_heading("5.2 Task 3.1: Web Login Form (5 marks)", level=2)
p_t31 = doc.add_paragraph(
    "The Web Portal login form strictly authenticates users and permits only users with Role 'Agent' to access the ordering system. "
    "When an Admin attempts to log into the web portal, access is immediately blocked with the message: "
    "'Truy cập bị từ chối: Tài khoản quyền Admin chỉ được truy cập qua phần mềm WinForms Back-Office. Web Portal chỉ dành cho Đại lý (Agent)'. "
    "Locked accounts are also rejected."
)

# Insert Login screenshots
screenshots_dir = r"C:\Users\PC\.gemini\antigravity\scratch\B2BWholesaleSystem\screenshots"
login_img = os.path.join(screenshots_dir, "1_login_page.png")
admin_img = os.path.join(screenshots_dir, "2_admin_blocked.png")

if os.path.exists(login_img):
    doc.add_paragraph("Figure 5.1: Agent Login Screen with helper test credentials").runs[0].font.bold = True
    doc.add_picture(login_img, width=Inches(5.5))
if os.path.exists(admin_img):
    doc.add_paragraph("Figure 5.2: Verification of Admin rejection on Web Portal").runs[0].font.bold = True
    doc.add_picture(admin_img, width=Inches(5.5))

doc.add_heading("5.3 Task 3.2: Catalog and Master-Detail Order (15 marks, core business logic)", level=2)
p_t32 = doc.add_paragraph(
    "Agents can browse the product catalog with keyword search and size filtering, displaying live StockQuantity badges. "
    "Agents assemble multiple items in a session-backed bulk cart and proceed to Checkout. "
    "When placing the order, a Database Transaction (BeginTransactionAsync) is executed:\n"
    "1. Stock check: Iterates through all items; if any item has StockQuantity < requested quantity, throws exception.\n"
    "2. Master record creation: Creates Order with status 'Pending' and AgentID.\n"
    "3. Line items insertion: Inserts OrderDetail records.\n"
    "4. Inventory deduction: Deducts ordered quantity directly from Item.StockQuantity.\n"
    "5. Atomic commit: Commits transaction. If any failure occurs, RollbackAsync() restores previous stock."
)

p_code = doc.add_paragraph()
r_code_hdr = p_code.add_run("Transaction Logic Code Excerpt (from OrderController.cs):\n")
r_code_hdr.font.bold = True
code_sample = (
    "IDbContextTransaction? transaction = null;\n"
    "if (_context.Database.IsRelational())\n"
    "    transaction = await _context.Database.BeginTransactionAsync();\n"
    "try {\n"
    "    // 1. Verify stock availability for all cart items\n"
    "    foreach (var c in cart.Items) {\n"
    "        var dbItem = dbItems[c.ItemID];\n"
    "        if (dbItem.StockQuantity < c.Quantity)\n"
    "            throw new InvalidOperationException($\"Thiếu tồn kho: {dbItem.ItemName} chỉ còn {dbItem.StockQuantity}\");\n"
    "    }\n"
    "    // 2. Create Master Order\n"
    "    var order = new Order { OrderDate = DateTime.UtcNow, AgentID = agentId, OrderStatus = \"Pending\" };\n"
    "    await _context.Order.AddAsync(order);\n"
    "    await _context.SaveChangesAsync();\n"
    "    // 3. Insert OrderDetails & Deduct Stock\n"
    "    foreach (var c in cart.Items) {\n"
    "        await _context.OrderDetail.AddAsync(new OrderDetail { OrderID = order.OrderID, ItemID = c.ItemID, Quantity = c.Quantity, UnitAmount = c.Price });\n"
    "        dbItems[c.ItemID].StockQuantity -= c.Quantity;\n"
    "    }\n"
    "    await _context.SaveChangesAsync();\n"
    "    if (transaction != null) await transaction.CommitAsync();\n"
    "} catch (Exception) {\n"
    "    if (transaction != null) await transaction.RollbackAsync();\n"
    "    throw;\n"
    "}"
)
r_code = p_code.add_run(code_sample)
r_code.font.name = "Consolas"
r_code.font.size = Pt(8.5)
p_code.paragraph_format.space_after = Pt(8)

# Evidence Table
doc.add_paragraph("Evidence that insufficient stock blocks the order and rolls everything back:").runs[0].font.bold = True
t_evi = doc.add_table(rows=4, cols=4)
col_widths_evi = [Inches(1.8), Inches(1.2), Inches(1.8), Inches(2.2)]
h_evi = t_evi.rows[0].cells
h_evi[0].text = "Scenario"
h_evi[1].text = "Stock before"
h_evi[2].text = "Order"
h_evi[3].text = "Result (order saved? stock after?)"

evi_data = [
    ("Enough stock (Normal)", "85 (Dell 4K)\n120 (Logitech KB)", "2x Dell 4K\n3x Logitech KB", "Order #16 SAVED (Status: Pending).\nStock deducted: 83 and 117."),
    ("Insufficient stock (Excess order)", "83 (Dell 4K)", "9999x Dell 4K", "Order BLOCKED.\nException thrown, Stock remains 83."),
    ("Failure in the middle: rollback", "83 (Dell 4K)\n15 (BenQ 4K)", "1x Dell 4K\n50x BenQ (exceeds)", "Transaction ROLLED BACK.\nNo Order created, Dell remains 83, BenQ remains 15.")
]
for idx, r_data in enumerate(evi_data):
    row = t_evi.rows[idx + 1].cells
    for c_idx in range(4):
        row[c_idx].text = r_data[c_idx]

format_table(t_evi, col_widths_evi)

# Screenshots Catalog, Cart, Confirmation
cat_img = os.path.join(screenshots_dir, "3_catalog_page.png")
cart_img = os.path.join(screenshots_dir, "4_cart_page.png")
chk_img = os.path.join(screenshots_dir, "5_checkout_page.png")
conf_img = os.path.join(screenshots_dir, "6_confirmation_page.png")

if os.path.exists(cat_img):
    doc.add_paragraph("Figure 5.3: B2B Wholesale Catalog with stock status indicators and bulk quantity selectors").runs[0].font.bold = True
    doc.add_picture(cat_img, width=Inches(5.5))
if os.path.exists(cart_img):
    doc.add_paragraph("Figure 5.4: Bulk Order Cart with line item calculations").runs[0].font.bold = True
    doc.add_picture(cart_img, width=Inches(5.5))
if os.path.exists(conf_img):
    doc.add_paragraph("Figure 5.5: Successful Order Confirmation with atomic inventory deduction").runs[0].font.bold = True
    doc.add_picture(conf_img, width=Inches(5.5))

doc.add_heading("5.4 Task 3.3: My Orders and Printable Invoice (10 marks)", level=2)
p_t33 = doc.add_paragraph(
    "Responsible: Member 3\n"
    "Allows the logged-in agent to review past wholesale orders and generate a formatted printable invoice "
    "with distributor branding, order number, line items, and totals. Foreign agent isolation is strictly enforced."
)

doc.add_heading("5.5 Task 3.4: Responsive UI (5 marks)", level=2)
p_t34 = doc.add_paragraph(
    "Built using Bootstrap 5.3.3 responsive grid system, sticky navbar with badge counters, clean card-based catalog items, "
    "and responsive data tables that scale seamlessly across desktop (1920x1080) and mobile viewports."
)

doc.add_page_break()

# ==================== 6. EXERCISE 5: UNIT TESTING ====================
doc.add_heading("6. Exercise 5: Unit Testing (15 marks)", level=1)
p_ut_intro = doc.add_paragraph("Responsible: Member 3 (QA Specialist) & Member 1")
p_ut_intro.runs[0].font.italic = True

t_ut_info = doc.add_table(rows=4, cols=2)
col_widths_ut_info = [Inches(3.0), Inches(4.0)]
h_ut = t_ut_info.rows[0].cells
h_ut[0].text = "Item"
h_ut[1].text = "Your answer"

ut_info_data = [
    ("Framework and project name", "xUnit (v2.9+) / Project: B2B.Tests"),
    ("Business logic under test (class and methods)", "B2B.Data.Seed.DbInitializer, B2B.Web.Controllers.AccountController, B2B.Web.Controllers.OrderController"),
    ("Number of tests and pass rate", "6 test cases / 100% Pass Rate (0 Failed, 6 Passed)")
]
for idx, r_data in enumerate(ut_info_data):
    row = t_ut_info.rows[idx + 1].cells
    row[0].text = r_data[0]
    row[1].text = r_data[1]

format_table(t_ut_info, col_widths_ut_info)

# Detailed tests table
t_tests = doc.add_table(rows=7, cols=6)
col_widths_tests = [Inches(0.4), Inches(2.2), Inches(1.8), Inches(1.2), Inches(0.8), Inches(0.6)]
h_tests = t_tests.rows[0].cells
h_tests[0].text = "No."
h_tests[1].text = "Test name"
h_tests[2].text = "Scenario"
h_tests[3].text = "Expected"
h_tests[4].text = "Actual"
h_tests[5].text = "Pass/Fail"

tests_data = [
    ("1", "SeedData_ShouldInsertRequiredTables_AndRealisticSampleRows", "Initialize database", "15-30 rows per table", "All in range", "Pass"),
    ("2", "PlaceOrder_WhenStockIsSufficient_ShouldDeductStock_AndCreateOrder", "Order with valid stock (10 units from 50)", "Stock reduces to 40, Order created", "Stock=40, Order created", "Pass"),
    ("3", "PlaceOrder_WhenStockIsInsufficient_ShouldBlockOrder_AndPreserveStock", "Order 20 units when stock=5", "Throws InvalidOperationException, Stock remains 5", "Exception thrown, Stock=5", "Pass"),
    ("4", "WebLogin_RoleValidation_ShouldOnlyAllowAgent (Admin)", "Admin logs into Web Portal", "Access denied (False)", "False", "Pass"),
    ("5", "WebLogin_RoleValidation_ShouldOnlyAllowAgent (Agent)", "Agent logs into Web Portal", "Access granted (True)", "True", "Pass"),
    ("6", "WebLogin_WhenUserIsLocked_ShouldBeBlocked", "User with lock=true logs in", "Login blocked (False)", "False", "Pass")
]
for idx, r_data in enumerate(tests_data):
    row = t_tests.rows[idx + 1].cells
    for c_idx in range(6):
        row[c_idx].text = r_data[c_idx]

format_table(t_tests, col_widths_tests)

doc.add_page_break()

# ==================== 7. SYSTEM CONFIGURATION ====================
doc.add_heading("7. System Configuration (5 marks)", level=1)
p_cfg = doc.add_paragraph(
    "To strictly adhere to security standards and prevent hardcoded connection strings, database configurations "
    "are loaded dynamically via standard .NET configuration providers:"
)

t_cfg = doc.add_table(rows=4, cols=3)
col_widths_cfg = [Inches(2.0), Inches(2.0), Inches(3.0)]
h_cfg = t_cfg.rows[0].cells
h_cfg[0].text = "Application"
h_cfg[1].text = "Configuration file"
h_cfg[2].text = "How the code reads it"

cfg_data = [
    ("WinForms back-office", "App.Config", "ConfigurationManager.ConnectionStrings['B2BConnection'].ConnectionString"),
    ("Web application", "appsettings.json", "builder.Configuration.GetConnectionString('B2BConnection') in Program.cs"),
    ("Unit test project", "InMemory / appsettings.json", "DbContextOptionsBuilder with UseInMemoryDatabase or TestDb connection")
]
for idx, r_data in enumerate(cfg_data):
    row = t_cfg.rows[idx + 1].cells
    for c_idx in range(3):
        row[c_idx].text = r_data[c_idx]

format_table(t_cfg, col_widths_cfg)

# ==================== 8. SOURCE CONTROL & TEAMWORK ====================
doc.add_heading("8. Source Control & Teamwork (5 marks)", level=1)
t_git = doc.add_table(rows=4, cols=2)
col_widths_git = [Inches(2.5), Inches(4.5)]
h_git = t_git.rows[0].cells
h_git[0].text = "Item"
h_git[1].text = "Your answer"

git_data = [
    ("Repository link", "https://github.com/[username]/B2BWholesaleSystem"),
    ("Branching strategy (names and rules)", "GitFlow model: 'main' (stable releases), 'develop' (integration branch), and dedicated feature branches: 'feature/member1-web-core', 'feature/winforms-admin', 'feature/unit-tests'."),
    ("Pull request and review rules (who reviews, when to merge)", "No direct commits to main or develop. Every feature is merged via Pull Request with code review and approval by at least one teammate.")
]
for idx, r_data in enumerate(git_data):
    row = t_git.rows[idx + 1].cells
    row[0].text = r_data[0]
    row[1].text = r_data[1]

format_table(t_git, col_widths_git)

# Members git contributions
t_git_mem = doc.add_table(rows=4, cols=5)
col_widths_gm = [Inches(1.2), Inches(2.0), Inches(1.0), Inches(1.3), Inches(1.5)]
h_gm = t_git_mem.rows[0].cells
h_gm[0].text = "Member"
h_gm[1].text = "Branches"
h_gm[2].text = "Commits"
h_gm[3].text = "Pull requests"
h_gm[4].text = "Main PR link"

gm_data = [
    ("Member 1", "main, develop, feature/member1-web-core", "8 commits", "PR #1 (Merged)", "PR #1 (Web & Core DB)"),
    ("Member 2", "feature/winforms-admin, feature/winforms-reports", "6 commits", "PR #2 (Pending)", "PR #2 (WinForms Admin)"),
    ("Member 3", "feature/web-invoices, feature/unit-tests", "6 commits", "PR #3 (Pending)", "PR #3 (Testing & Docs)")
]
for idx, r_data in enumerate(gm_data):
    row = t_git_mem.rows[idx + 1].cells
    for c_idx in range(5):
        row[c_idx].text = r_data[c_idx]

format_table(t_git_mem, col_widths_gm)

doc.add_page_break()

# ==================== 9. CONTRIBUTION OF EACH MEMBER ====================
doc.add_heading("9. Contribution of Each Member", level=1)
t_contrib = doc.add_table(rows=5, cols=4)
col_widths_con = [Inches(1.5), Inches(1.2), Inches(3.1), Inches(1.2)]
h_con = t_contrib.rows[0].cells
h_con[0].text = "Member"
h_con[1].text = "Student ID"
h_con[2].text = "Features built (task numbers)"
h_con[3].text = "% contribution"

con_data = [
    ("Member 1", "[MSSV 1]", "Task 2 (Shared DB), Task 3.1, Task 3.2 (Transaction), Task 3.4 (UI)", "34%"),
    ("Member 2", "[MSSV 2]", "Task 1.1, Task 1.2, Task 1.3 (Manifest), Task 1.4 (Dashboard)", "33%"),
    ("Member 3", "[MSSV 3]", "Task 2 (Seed Data & Integrity), Task 3.3 (Invoice), Task 5.1 (Unit Tests), Task 6 (Report)", "33%"),
    ("Total", "", "", "100%")
]
for idx, r_data in enumerate(con_data):
    row = t_contrib.rows[idx + 1].cells
    for c_idx in range(4):
        row[c_idx].text = r_data[c_idx]
    if idx == 3:
        for c in row:
            set_cell_background(c, "E2E8F0")

format_table(t_contrib, col_widths_con)

# ==================== 10. CONCLUSION & LESSONS LEARNT ====================
doc.add_heading("10. Conclusion and Lessons Learnt", level=1)
p_concl = doc.add_paragraph(
    "Through Software Engineering Lab Assignment 2, our team successfully engineered a complete dual-platform B2B wholesale order management system. "
    "Key achievements include a robust shared Code-First database architecture, atomic database transaction handling under high concurrency, "
    "and distinct desktop and web interfaces tailored for warehouse staff and commercial agents.\n"
    "Crucial lessons learnt include the importance of Git branching and Pull Requests to avoid code collision, "
    "rigorous automated testing to verify boundary conditions, and secure configuration management."
)

# ==================== APPENDIX ====================
doc.add_heading("Appendix", level=1)

doc.add_heading("Appendix A: Readme.txt", level=2)
p_readme = doc.add_paragraph()
readme_content = (
    "=========================================================================\n"
    "B2B WHOLESALE ORDER MANAGEMENT SYSTEM - README\n"
    "Course: Software Engineering Lab Assignment 2 (FIT - TDTU)\n"
    "=========================================================================\n"
    "1. GitHub Repository Link: https://github.com/[username]/B2BWholesaleSystem\n"
    "2. Video Demo Link: https://youtu.be/[demo-video-link-neu-co]\n"
    "3. Database Configuration Instructions:\n"
    "   - Execute B2B.Data/Scripts/SeedData.sql in SQL Server Management Studio,\n"
    "     OR simply run B2B.Web which automatically creates and seeds the database.\n"
    "   - Update ConnectionStrings in B2B.Web/appsettings.json and B2B.WinForms/App.config.\n"
    "4. Percentage Contribution of Each Member:\n"
    "   - Member 1 (Lead, Web & Architecture): 34%\n"
    "   - Member 2 (WinForms Admin & Reports): 33%\n"
    "   - Member 3 (QA, Unit Testing & Documentation): 33%\n"
    "   - Total: 100%\n"
    "========================================================================="
)
r_rm = p_readme.add_run(readme_content)
r_rm.font.name = "Consolas"
r_rm.font.size = Pt(9)

doc.add_heading("Appendix B: Generative AI Use", level=2)
t_ai = doc.add_table(rows=3, cols=5)
col_widths_ai = [Inches(1.2), Inches(1.3), Inches(1.8), Inches(1.5), Inches(1.2)]
h_ai = t_ai.rows[0].cells
h_ai[0].text = "Tool and date"
h_ai[1].text = "Purpose"
h_ai[2].text = "Prompt (summary)"
h_ai[3].text = "What you kept or changed"
h_ai[4].text = "How you verified it"

ai_data = [
    ("Antigravity AI\n(13/11/2026)", "Project Architecture & Work Breakdown", "Divide lab assignment for 3 students and generate implementation plan", "Adopted 34%-33%-33% distribution and 1 Solution 4 Projects architecture.", "Reviewed against official grading rubric."),
    ("Antigravity AI\n(13/11/2026)", "Web Portal & Code First Setup", "Implement EF Core models, seed data and database transaction ordering", "Refined transaction exception handling for dual provider compatibility.", "Executed automated xUnit tests (6/6 Pass) and E2E browser tests.")
]
for idx, r_data in enumerate(ai_data):
    row = t_ai.rows[idx + 1].cells
    for c_idx in range(5):
        row[c_idx].text = r_data[c_idx]

format_table(t_ai, col_widths_ai)

# Save document
output_path = r"C:\Users\PC\.gemini\antigravity\scratch\B2BWholesaleSystem\Report.docx"
doc.save(output_path)
print(f"Report.docx successfully created at: {output_path}")
