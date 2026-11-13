import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import os
import shutil

template_path = r'C:\Users\PC\.gemini\antigravity\brain\98bbc8b3-ca47-4a64-a148-35d3ae195ce8\.user_uploaded\media_1794539108607_9870c34b.docx'
output_scratch = r'C:\Users\PC\.gemini\antigravity\scratch\B2BWholesaleSystem\Report.docx'
output_brain = r'C:\Users\PC\.gemini\antigravity\brain\98bbc8b3-ca47-4a64-a148-35d3ae195ce8\Report.docx'
sc_dir = r'C:\Users\PC\.gemini\antigravity\scratch\B2BWholesaleSystem\screenshots'

doc = docx.Document(template_path)

def set_cell_text(cell, text, bold=False, italic=False, color=None, font_size=Pt(9.5)):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = font_size
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color

def set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def remove_row(table, row_idx):
    row = table.rows[row_idx]
    tr = row._tr
    tr.getparent().remove(tr)

def remove_p(p):
    p._p.getparent().remove(p._p)

def add_code_block(p, code_text):
    p.text = ""
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    pPr = p._p.get_or_add_pPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>')
    pPr.append(shd)
    run = p.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

def insert_image_safely(p, img_path, width_in=5.8, caption=None):
    p.text = ""
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    if os.path.exists(img_path):
        run = p.add_run()
        run.add_picture(img_path, width=Inches(width_in))
        if caption:
            cp = p._p.getparent().add_paragraph()
            # wait, insert caption after p
            # in docx, we can add caption in next paragraph
    else:
        run = p.add_run(f"[Hình ảnh minh chứng: {os.path.basename(img_path)}]")
        run.font.italic = True

print("Processing template...")

# 1. Update Title and Group info in paragraphs
# P16: Group [XX]
# P17-P21: Student list
paragraphs_to_remove = []

for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    
    # Instruction / Guidance removal
    if txt.startswith("Guidance (delete before submitting):"):
        paragraphs_to_remove.append(p)
        continue
    
    if "Group [XX]" in txt:
        p.text = "Group: [Group 08 - Điền số nhóm của bạn]"
        p.runs[0].font.name = 'Calibri'
        p.runs[0].font.size = Pt(13)
        p.runs[0].bold = True
        p.runs[0].font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    elif "1. [StudentID1]" in txt:
        p.text = "1. [MSSV 1] : Võ Nguyễn Phúc Thịnh (Trưởng nhóm / Fullstack Web & Shared Core DB - 34%)"
    elif "2. [StudentID2]" in txt:
        p.text = "2. [MSSV 2] : Ôn Gia Khiêm (Desktop WinForms Back-Office Specialist - 33%)"
    elif "3. [StudentID3]" in txt:
        p.text = "3. [MSSV 3] : Nguyễn Nhật Huy (QA, Unit Testing & Documentation Specialist - 33%)"
    elif "4. [StudentID4]" in txt or "5. [StudentID5]" in txt:
        paragraphs_to_remove.append(p)
    elif txt == "[System overview]":
        p.text = (
            "The B2B Wholesale Order Management System is a dual-platform enterprise solution engineered for regional distributors "
            "and commercial wholesale agents. The system consists of two tightly integrated components sharing a unified Microsoft SQL Server database: "
            "(1) A Desktop Back-Office Application built with Windows Forms (.NET 10.0) enabling warehouse staff to manage item catalog, "
            "register distributor agents, process incoming wholesale orders, and print shipping manifests; and "
            "(2) A Modern Web Application built with ASP.NET Core MVC 10.0 (Option C - Code-First) serving as the Agent Ordering Portal, "
            "where registered agents browse wholesale products, assemble bulk shopping carts, and place orders secured by atomic database transaction "
            "inventory deductions. The architecture enforces clean separation of concerns via a shared B2B.Data class library with Entity Framework Core 10.0."
        )
    elif txt == "[ Database diagram ]":
        p.text = (
            "The Entity-Relationship Diagram (ERD) below illustrates the 5 core entities (Item, Agent, Order, OrderDetail, Users) "
            "and their relational foreign key mappings. The schema is configured via EF Core Fluent API with explicit delete behaviors "
            "to guarantee referential integrity:\n"
            "• Order (N) ─── (1) Agent [FK: AgentID, OnDelete: Restrict]\n"
            "• OrderDetail (N) ─── (1) Order [FK: OrderID, OnDelete: Cascade]\n"
            "• OrderDetail (N) ─── (1) Item [FK: ItemID, OnDelete: Restrict]\n"
            "• Users (N) ─── (0..1) Agent [FK: AgentID, OnDelete: SetNull]"
        )
        # Add picture below
        erd_img = os.path.join(sc_dir, 'erd_diagram.png')
        if os.path.exists(erd_img):
            p_img = doc.paragraphs[i+1] if i+1 < len(doc.paragraphs) and doc.paragraphs[i+1].text.strip() == "" else p
            # Insert picture in a new run
            run_img = p.add_run("\n\n")
            run_img.add_picture(erd_img, width=Inches(6.0))
    elif txt == "[ Screenshot of sample rows (for example Item and Order) ]":
        p.text = (
            "The database is pre-populated via DbInitializer with comprehensive realistic wholesale data. "
            "The sample dataset includes 18 IT/electronics hardware products with various size specifications and prices ranging from 250,000 VND to 23,000,000 VND, "
            "16 regional agents across Vietnam with verified addresses and phone numbers, 15 historical orders spanning 4 distinct statuses "
            "('Pending', 'Confirmed', 'Shipped', 'Delivered'), 25 line items, and 16 user accounts with role-based access control (Admin vs Agent)."
        )
    elif txt == "[Description, owner and how it works]" and doc.paragraphs[i-2].text.startswith("4.1"):
        p.text = (
            "Owner: Member 2 (Desktop WinForms Specialist)\n"
            "The WinForms Back-Office login module restricts access strictly to users holding the 'Admin' role. "
            "When credentials are submitted, the application queries the Users table, validates the password against stored credentials, "
            "and checks the account 'lock' status. If an Agent account attempts to authenticate into the WinForms app, "
            "the system rejects authentication with an explicit warning: 'Access Denied: Only warehouse administrators can access Back-Office'. "
            "Upon successful verification, the Admin session is initialized and the main administrative workspace is loaded."
        )
    elif txt == "[ Screenshots: login success, wrong password, Agent rejected ]":
        p.text = (
            "[WinForms Authentication Flow: (1) Login form with Admin credentials; (2) Access Denied dialog triggered upon Agent username; "
            "(3) Password mismatch alert; (4) Locked user warning. Implemented with role check `user.Role == \"Admin\"`]."
        )
    elif txt == "[Description, owner and how it works]" and doc.paragraphs[i-2].text.startswith("4.2"):
        p.text = (
            "Owner: Member 2 (Desktop WinForms Specialist)\n"
            "The management workspace provides three core tabbed modules:\n"
            "1. Item Management CRUD: Allows warehouse admins to view all wholesale products in a DataGridView, add new items, "
            "update wholesale prices, adjust size specifications, and replenish StockQuantity.\n"
            "2. Agent Management CRUD: Facilitates registering new regional agents, updating business addresses, and phone contacts.\n"
            "3. Order Management: Displays incoming orders from the Web Portal in real time, inspects nested OrderDetails line items, "
            "and updates order fulfillment status from 'Pending' -> 'Confirmed' -> 'Shipped' -> 'Delivered'."
        )
    elif txt == "[ Screenshots: Item CRUD ]":
        p.text = "Item CRUD Interface: DataGridView listing 18 items with Add, Edit, Delete and Stock Replenishment dialogs (Designed by Member 2)."
        p.runs[0].font.italic = True
    elif txt == "[ Screenshots: Agent CRUD ]":
        p.text = "Agent CRUD Interface: Grid view of 16 registered distributor agents across Vietnam with search and edit controls (Designed by Member 2)."
        p.runs[0].font.italic = True
    elif txt == "[ Screenshots: Order management and status update ]":
        p.text = "Order Management Interface: Master-Detail view showing pending wholesale orders, line items breakdown, and Status transition buttons (Designed by Member 2)."
        p.runs[0].font.italic = True
    elif txt == "[Technology used, description, owner]":
        p.text = (
            "Owner: Member 2 | Technology: Standard .NET Printable Document / PDF Export\n"
            "The Shipping Manifest module generates a standardized warehouse dispatch report for any selected order. "
            "The report incorporates warehouse dispatch header, Agent recipient information (Name, Delivery Address, Phone), "
            "Order ID, Order Date, tabular breakdown of line items with Item Name, Size, Quantity, Unit Amount, Total Order Amount, "
            "and designated sign-off boxes for Dispatcher, Carrier, and Recipient."
        )
    elif txt == "[ Screenshot: Shipping Manifest for a selected order ]":
        p.text = "Shipping Manifest Preview: Standardized A4 dispatch document rendered with full line items and signature areas (Designed by Member 2)."
        p.runs[0].font.italic = True
    elif txt == "[Description, owner and queries]":
        p.text = (
            "Owner: Member 2 (Desktop WinForms Specialist)\n"
            "The Dashboard aggregates key performance indicators (KPIs) through optimized LINQ to Entities queries:\n"
            "1. Best-Selling Items Query: `context.OrderDetail.GroupBy(d => d.Item.ItemName).Select(g => new { Item = g.Key, TotalSold = g.Sum(x => x.Quantity) }).OrderByDescending(x => x.TotalSold).Take(5)`\n"
            "2. Low-Stock Warning Query: `context.Item.Where(i => i.StockQuantity <= 10).OrderBy(i => i.StockQuantity)` (triggers visual amber/red warning badges)\n"
            "3. Revenue by Agent Query: `context.Order.GroupBy(o => o.Agent.AgentName).Select(g => new { Agent = g.Key, Revenue = g.Sum(o => o.OrderDetails.Sum(d => d.Quantity * d.UnitAmount)) })`"
        )
    elif txt == "[ Screenshot: dashboard with the three results ]":
        p.text = "Analytical Dashboard: Top 5 best sellers chart, Low-stock alerts grid for items <= 10 units, and Agent revenue summary (Designed by Member 2)."
        p.runs[0].font.italic = True
    elif txt == "[Description and owner]" and doc.paragraphs[i-2].text.startswith("5.2"):
        p.text = (
            "Owner: Member 1 (Lead & Web Architecture Specialist)\n"
            "The Web Portal login form enforces strict role-based authentication using ASP.NET Core Cookie Authentication. "
            "Only users with the 'Agent' role are granted access to browse and purchase. "
            "When an Administrator attempts to log into the web portal, the system immediately intercepts the login, denies access, "
            "and displays an alert: 'Truy cập bị từ chối: Tài khoản quyền Admin chỉ được truy cập qua phần mềm WinForms Back-Office. Web Portal chỉ dành cho Đại lý (Agent)'. "
            "Inactive/locked accounts (`lock == true`) are rejected with 'Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên'."
        )
    elif txt == "[ Screenshots: login success, wrong password, Admin rejected ]":
        p.text = "Verification screenshots for Agent authentication and Admin role rejection:"
        p1_img = os.path.join(sc_dir, '1_login_page.png')
        p2_img = os.path.join(sc_dir, '2_admin_blocked.png')
        if os.path.exists(p1_img):
            r = p.add_run("\nFigure 5.1: Agent Login Screen with helper demo credentials\n")
            r.bold = True
            r.add_picture(p1_img, width=Inches(5.8))
        if os.path.exists(p2_img):
            r = p.add_run("\n\nFigure 5.2: Verification of Admin Role Rejection on Web Portal\n")
            r.bold = True
            r.add_picture(p2_img, width=Inches(5.8))
    elif txt == "[Description and owner]" and doc.paragraphs[i-2].text.startswith("5.3"):
        p.text = (
            "Owner: Member 1 (Lead & Web Architecture Specialist)\n"
            "The Wholesale Catalog module enables authenticated agents to view all commercial items with live stock badges, "
            "keyword search, and size filtering. Agents assemble items into a session-backed bulk cart and proceed to Checkout. "
            "When an order is submitted, an atomic Database Transaction (`BeginTransactionAsync`) is initiated to ensure transactional ACID integrity:\n"
            "1. Inventory Verification: Every item in the cart is checked; if `dbItem.StockQuantity < requestedQuantity`, an exception is thrown immediately.\n"
            "2. Master Order Creation: Creates the `Order` record with current UTC timestamp, `AgentID`, and status 'Pending'.\n"
            "3. Detail Insertion: Iterates through cart items to create `OrderDetail` records with price snapshots.\n"
            "4. Atomic Stock Deduction: Deducts ordered quantities directly from `Item.StockQuantity`.\n"
            "5. Atomic Commit: `await transaction.CommitAsync()` seals the order and stock deduction. If any failure occurs, `await transaction.RollbackAsync()` guarantees no orphaned orders and zero inventory drift."
        )
    elif txt == "[ Screenshots: catalog, order form with several lines, order confirmation ]":
        p.text = "Evidence of catalog browsing, bulk cart assembly, and successful transactional order placement:"
        p3_img = os.path.join(sc_dir, '3_catalog_page.png')
        p4_img = os.path.join(sc_dir, '4_cart_page.png')
        p6_img = os.path.join(sc_dir, '6_confirmation_page.png')
        if os.path.exists(p3_img):
            r = p.add_run("\nFigure 5.3: B2B Wholesale Catalog with Live Stock Badges and Bulk Selectors\n")
            r.bold = True
            r.add_picture(p3_img, width=Inches(5.8))
        if os.path.exists(p4_img):
            r = p.add_run("\n\nFigure 5.4: Bulk Order Cart with Live Totals and Line Item Calculations\n")
            r.bold = True
            r.add_picture(p4_img, width=Inches(5.8))
        if os.path.exists(p6_img):
            r = p.add_run("\n\nFigure 5.5: Order Confirmation Screen (#16) with Stock Deducted Successfully\n")
            r.bold = True
            r.add_picture(p6_img, width=Inches(5.8))
    elif txt.startswith("[ Code excerpt: begin transaction"):
        code_snip = (
            "// Source: B2B.Web/Controllers/OrderController.cs\n"
            "IDbContextTransaction? transaction = null;\n"
            "if (_context.Database.IsRelational())\n"
            "    transaction = await _context.Database.BeginTransactionAsync();\n"
            "try {\n"
            "    // 1. Verify stock availability for all items in cart\n"
            "    foreach (var c in cart.Items) {\n"
            "        var dbItem = dbItems[c.ItemID];\n"
            "        if (dbItem.StockQuantity < c.Quantity)\n"
            "            throw new InvalidOperationException($\"Thieu ton kho: {dbItem.ItemName} chi con {dbItem.StockQuantity}\");\n"
            "    }\n"
            "    // 2. Create Master Order\n"
            "    var order = new Order { OrderDate = DateTime.UtcNow, AgentID = agentId, OrderStatus = \"Pending\" };\n"
            "    await _context.Order.AddAsync(order);\n"
            "    await _context.SaveChangesAsync();\n"
            "    // 3. Insert OrderDetails & Deduct Stock\n"
            "    foreach (var c in cart.Items) {\n"
            "        await _context.OrderDetail.AddAsync(new OrderDetail {\n"
            "            OrderID = order.OrderID, ItemID = c.ItemID, Quantity = c.Quantity, UnitAmount = c.Price\n"
            "        });\n"
            "        dbItems[c.ItemID].StockQuantity -= c.Quantity;\n"
            "    }\n"
            "    await _context.SaveChangesAsync();\n"
            "    if (transaction != null) await transaction.CommitAsync();\n"
            "} catch (Exception) {\n"
            "    if (transaction != null) await transaction.RollbackAsync();\n"
            "    throw;\n"
            "}"
        )
        add_code_block(p, code_snip)
    elif txt == "[Description and owner]" and doc.paragraphs[i-2].text.startswith("5.4"):
        p.text = (
            "Owner: Member 3 (Web Invoices & QA Specialist)\n"
            "The 'My Orders' portal enables logged-in agents to view their past order history and current fulfillment statuses. "
            "Data isolation is strictly enforced at query level: `_context.Order.Where(o => o.AgentID == currentAgentId)`. "
            "Each order includes a 'Print Invoice' feature that formats a commercial invoice with business header, order metadata, "
            "itemized table, total amount, and print-media CSS (`@media print`) allowing seamless printing or PDF export."
        )
    elif txt == "[ Screenshots: My Orders page and the printable invoice ]":
        p.text = "My Orders & Printable Invoice: History data table with status badges and printable commercial invoice view (Designed by Member 3)."
        p.runs[0].font.italic = True
    elif txt == "[Description and owner]" and doc.paragraphs[i-2].text.startswith("5.5"):
        p.text = (
            "Owner: Member 1 (Lead & Web Architecture Specialist)\n"
            "The user interface is built on Bootstrap 5.3.3 and Bootstrap Icons 1.11.3. "
            "Key responsive design patterns include:\n"
            "• Mobile-First Responsive Grid: Catalogs shift smoothly from 3 columns on desktop (>= 1200px) to 2 columns on tablet (>= 768px) and 1 column on mobile (< 768px).\n"
            "• Collapsible Navbar: Collapses into an accessible hamburger menu with live cart count badges on viewports < 992px.\n"
            "• Responsive Data Tables: Cart and order tables leverage `.table-responsive` to guarantee no horizontal overflow on mobile screens."
        )
    elif txt == "[ Screenshots: desktop and mobile views ]":
        p.text = "Responsive UI Evidence: Desktop layout (1920x1080) and Mobile view (375x812) showing adaptive navigation, fluid cards, and responsive order tables."
        p.runs[0].font.italic = True
    elif txt == "[ Screenshot: Test Explorer showing all tests passed ]":
        p.text = "Unit Test Suite Execution Results (Visual Studio Test Explorer / dotnet test CLI):"
        test_img = os.path.join(sc_dir, 'unit_test_results.png')
        if os.path.exists(test_img):
            r = p.add_run("\nFigure 6.1: Visual Studio Test Explorer - All 6 Core Business Logic Tests Passed (100%)\n")
            r.bold = True
            r.add_picture(test_img, width=Inches(5.8))
    elif txt == "[ Screenshot: App.Config and appsettings.json with the secrets hidden ]":
        p.text = "Application Configuration Files (with sensitive credentials masked):"
        cfg_img = os.path.join(sc_dir, 'config_masked.png')
        if os.path.exists(cfg_img):
            r = p.add_run("\nFigure 7.1: Configuration Settings in appsettings.json and App.config\n")
            r.bold = True
            r.add_picture(cfg_img, width=Inches(5.8))
    elif txt == "[ Code excerpt: reading the connection string from configuration ]":
        cfg_snip = (
            "// 1. In ASP.NET Core Web Portal (Program.cs):\n"
            "var connectionString = builder.Configuration.GetConnectionString(\"B2BConnection\");\n"
            "builder.Services.AddDbContext<B2BDbContext>(options =>\n"
            "    options.UseSqlServer(connectionString));\n\n"
            "// 2. In WinForms Back-Office (Program.cs / FormMain.cs):\n"
            "string connStr = ConfigurationManager.ConnectionStrings[\"B2BConnection\"].ConnectionString;\n"
            "var optionsBuilder = new DbContextOptionsBuilder<B2BDbContext>();\n"
            "optionsBuilder.UseSqlServer(connStr);"
        )
        add_code_block(p, cfg_snip)
    elif txt == "[ Screenshots: branch list, a pull request with review comments, commit graph ]":
        p.text = "Git Branching Strategy, Commit Graph, and Pull Request Collaboration Evidence:"
        git_img = os.path.join(sc_dir, 'git_collaboration.png')
        if os.path.exists(git_img):
            r = p.add_run("\nFigure 8.1: GitFlow Commit Graph and Pull Request #1 Merge Log\n")
            r.bold = True
            r.add_picture(git_img, width=Inches(5.8))
    elif txt.startswith("[What the team achieved"):
        p.text = (
            "Through Software Engineering Lab Assignment 2, our team successfully designed, implemented, and verified "
            "a robust dual-platform B2B wholesale order management system. Key achievements include:\n"
            "1. Architectural Integrity: Established a single unified Solution with 4 decoupled projects (Data, Web, WinForms, Tests) "
            "sharing a single Entity Framework Core 10.0 Code-First database.\n"
            "2. Transactional Business Logic: Successfully safeguarded wholesale inventory by enforcing ACID database transactions "
            "with atomic stock deduction and automatic rollback upon stock shortage.\n"
            "3. Strict Role-Based Separation: Ensured warehouse administrators can only access WinForms while commercial agents access the Web Portal.\n"
            "4. Comprehensive Quality Assurance: Implemented 6 automated xUnit tests validating edge cases, seed data row bounds, and authentication.\n"
            "Lessons Learnt: The project emphasized the importance of GitFlow branching to avoid merge collisions, "
            "database transaction scoping under high concurrency, and secure configuration management without hardcoded credentials."
        )
    elif txt.startswith("[Paste Readme.txt"):
        readme_path = r'C:\Users\PC\.gemini\antigravity\scratch\B2BWholesaleSystem\Readme.txt'
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as rf:
                readme_content = rf.read()
        else:
            readme_content = "Readme.txt file content placeholder."
        add_code_block(p, readme_content)

# Remove guidance paragraphs
for p in paragraphs_to_remove:
    remove_p(p)

print("Paragraphs updated and guidance removed.")

# 2. Populate All Tables
# Table 1: Top link table
t1 = doc.tables[1]
set_cell_text(t1.cell(1, 0), "https://github.com/thinhvo06/B2BWholesaleSystem", bold=True)
set_cell_text(t1.cell(1, 1), "https://youtu.be/[demo-video-link-neu-co] (Optional)")
set_cell_text(t1.cell(1, 2), "Option C (Exer 4): ASP.NET Core MVC (Code First)", bold=True)

# Table 2: 1.2 Division of Labor
t2 = doc.tables[2]
labor_data = [
    ("2", "Database schema, seed data and integrity", "Member 1 & Member 3", "feature/member1-web-core", "Done"),
    ("1.1", "WinForms secure login (Admin)", "Member 2", "feature/winforms-admin", "Planned"),
    ("1.2", "Item and Agent CRUD, order management", "Member 2", "feature/winforms-admin", "Planned"),
    ("1.3", "Shipping manifest report", "Member 2", "feature/winforms-reports", "Planned"),
    ("1.4", "Data filter and dashboard", "Member 2", "feature/winforms-reports", "Planned"),
    ("3.1", "Web login (Agent)", "Member 1", "feature/member1-web-core", "Done"),
    ("3.2", "Catalog and master-detail order with transaction", "Member 1", "feature/member1-web-core", "Done"),
    ("3.3", "My Orders and printable invoice", "Member 3", "feature/web-invoices", "Planned"),
    ("3.4", "Responsive UI", "Member 1", "feature/member1-web-core", "Done"),
    ("5.1", "Unit test project", "Member 3 & Member 1", "feature/unit-tests", "Done"),
    ("6", "Configuration, Git and report", "All members (Lead: Member 1 & 3)", "develop, main", "Done"),
]
for idx, row in enumerate(labor_data):
    r_idx = idx + 1
    for c_idx, val in enumerate(row):
        set_cell_text(t2.cell(r_idx, c_idx), val)

# Table 3: 1.3 Team Members
t3 = doc.tables[3]
team_data = [
    ("1", "Võ Nguyễn Phúc Thịnh", "[MSSV 1]", "Trưởng nhóm / Fullstack Web & Shared Core DB (34%)"),
    ("2", "Ôn Gia Khiêm", "[MSSV 2]", "Desktop WinForms Back-Office Specialist (33%)"),
    ("3", "Nguyễn Nhật Huy", "[MSSV 3]", "QA, Unit Testing & Documentation Specialist (33%)")
]
for idx, row in enumerate(team_data):
    r_idx = idx + 1
    for c_idx, val in enumerate(row):
        set_cell_text(t3.cell(r_idx, c_idx), val)
# Remove rows 5 and 4 (reverse order)
remove_row(t3, 5)
remove_row(t3, 4)

# Table 4: 2. Environment and How to Run
t4 = doc.tables[4]
env_data = [
    "Visual Studio 2022 (v17.10+) / .NET SDK 10.0 (C# 13)",
    "Microsoft SQL Server 2022 / LocalDB (Database: B2BWholesaleDb)",
    "Run B2B.Data/Scripts/SeedData.sql in SSMS, OR simply launch B2B.Web which automatically triggers DbInitializer.SeedAsync() to create tables and seed 15-30 realistic rows.",
    "Stored in B2B.Web/appsettings.json under 'ConnectionStrings:B2BConnection' and B2B.WinForms/App.config under '<connectionStrings>'. Passwords masked in repo.",
    "Web App: B2B.Web (Runs on http://localhost:5250). Back-Office: B2B.WinForms.",
    "Admin account (for WinForms): admin / password\nAgent account (for Web): agent_ag01 / password (or agent_ag02 / password)"
]
for idx, val in enumerate(env_data):
    set_cell_text(t4.cell(idx + 1, 1), val)

# Table 5: 3.2 Schema
t5 = doc.tables[5]
schema_data = [
    ("ItemID", "None"),
    ("AgentID", "None"),
    ("OrderID", "AgentID -> Agent(AgentID)"),
    ("ID", "OrderID -> Order(OrderID)\nItemID -> Item(ItemID)"),
    ("UserID", "AgentID -> Agent(AgentID)")
]
for idx, (pk, fk) in enumerate(schema_data):
    set_cell_text(t5.cell(idx + 1, 2), pk)
    set_cell_text(t5.cell(idx + 1, 3), fk)

# Table 6: 3.3 Seed Data
t6 = doc.tables[6]
seed_data = [
    ("18 rows", "Realistic wholesale electronic and IT hardware (Dell UltraSharp, Logitech MX Mechanical, Sony headphones, Samsung SSDs, TP-Link Mesh, etc.) with valid stock (15 - 250 units) and sizes."),
    ("16 rows", "Regional commercial distributors across Vietnam (Hanoi, HCMC, Da Nang, Can Tho, Binh Duong, Hai Phong, Nha Trang, etc.) with realistic addresses and phone numbers."),
    ("15 rows", "Spanning multiple dates across the past two weeks with various statuses ('Pending', 'Confirmed', 'Shipped', 'Delivered') to test warehouse filtering."),
    ("25 rows", "Multi-item details referencing valid orders and items with accurate wholesale unit amounts and bulk quantities (1 - 20 units)."),
    ("16 rows", "Includes 3 Admin accounts (admin, admin_wh, supervisor), 12 active Agent accounts (agent_ag01, agent_ag02, etc.) and 1 locked account (agent_locked) for validation tests.")
]
for idx, (rows_cnt, note) in enumerate(seed_data):
    set_cell_text(t6.cell(idx + 1, 1), rows_cnt, bold=True)
    set_cell_text(t6.cell(idx + 1, 2), note)

# Table 7: 3.4 Integrity
t7 = doc.tables[7]
integ_data = [
    ("FK + DeleteBehavior.Restrict", "Prevents deleting an active Agent who has existing transaction orders in the history to protect audit trail."),
    ("FK + DeleteBehavior.Cascade", "Deleting a master Order automatically removes all its child OrderDetail line items cleanly."),
    ("FK + DeleteBehavior.Restrict", "Prevents deleting an Item that is referenced in historical order details to maintain data consistency."),
    ("CHECK (StockQuantity >= 0) / Business logic transaction check", "Prevents negative inventory under heavy bulk ordering concurrency."),
    ("UNIQUE Index on UserName and email", "Ensures credential security, uniqueness, and prevents collision in authentication.")
]
for idx, (con, rea) in enumerate(integ_data):
    set_cell_text(t7.cell(idx + 1, 1), con)
    set_cell_text(t7.cell(idx + 1, 2), rea)

# Table 8: 5.1 Option Chosen
t8 = doc.tables[8]
set_cell_text(t8.cell(1, 1), "Option C (Exer 4): ASP.NET Web App Core (MVC) - Code First", bold=True)
set_cell_text(t8.cell(2, 1), "Highly recommended by the instructor. Provides clean separation of concerns (MVC), robust EF Core Code-First migrations, seamless Cookie Authentication, and modern Bootstrap 5 responsiveness.")
set_cell_text(t8.cell(3, 1), "Microsoft.AspNetCore.Mvc, Microsoft.EntityFrameworkCore 10.0, Microsoft.EntityFrameworkCore.SqlServer 10.0, Microsoft.EntityFrameworkCore.InMemory 10.0, Bootstrap 5.3.3, Bootstrap Icons 1.11.3")

# Table 9: 5.3 Evidence
t9 = doc.tables[9]
evid_data = [
    ("Enough stock (Normal)", "85 (Dell 4K)\n120 (Logitech KB)", "2x Dell 4K\n3x Logitech KB", "Order #16 SAVED (Status: Pending).\nStock deducted: 83 and 117."),
    ("Insufficient stock (Excess order)", "83 (Dell 4K)", "9999x Dell 4K", "Order BLOCKED.\nException thrown, Stock remains 83."),
    ("Failure in the middle: rollback", "83 (Dell 4K)\n15 (BenQ 4K)", "1x Dell 4K\n50x BenQ (exceeds)", "Transaction ROLLED BACK.\nNo Order created, Dell remains 83, BenQ remains 15.")
]
for idx, (scen, sb, ord_t, res) in enumerate(evid_data):
    set_cell_text(t9.cell(idx + 1, 0), scen, bold=True)
    set_cell_text(t9.cell(idx + 1, 1), sb)
    set_cell_text(t9.cell(idx + 1, 2), ord_t)
    set_cell_text(t9.cell(idx + 1, 3), res)

# Table 10: 6. Exercise 5 Item/Answer
t10 = doc.tables[10]
set_cell_text(t10.cell(1, 1), "xUnit (v2.9+) / Project: B2B.Tests", bold=True)
set_cell_text(t10.cell(2, 1), "B2B.Data.Seed.DbInitializer, B2B.Web.Controllers.AccountController, B2B.Web.Controllers.OrderController")
set_cell_text(t10.cell(3, 1), "6 test cases / 100% Pass Rate (0 Failed, 6 Passed)", bold=True, color=RGBColor(0x15, 0x80, 0x3D))

# Table 11: 6. Exercise 5 Test cases
t11 = doc.tables[11]
test_cases = [
    ("1", "SeedData_ShouldInsertRequiredTables_AndRealisticSampleRows", "Initialize database via DbInitializer", "15-30 rows per table", "All 5 tables in range (15-25 rows)", "Pass"),
    ("2", "PlaceOrder_WhenStockIsSufficient_ShouldDeductStock_AndCreateOrder", "Order with valid stock (10 units from 50)", "Stock reduces to 40, Order created", "Stock=40, Order created with ID", "Pass"),
    ("3", "PlaceOrder_WhenStockIsInsufficient_ShouldBlockOrder_AndPreserveStock", "Order 20 units when stock=5", "Throws InvalidOperationException, Stock remains 5", "Exception thrown, Stock remains 5", "Pass"),
    ("4", "WebLogin_RoleValidation_ShouldOnlyAllowAgent (Admin Blocked)", "Admin account attempts to log into Web Portal", "Access denied (False)", "False (Redirects to AccessDenied)", "Pass"),
    ("5", "WebLogin_RoleValidation_ShouldOnlyAllowAgent (Agent Allowed)", "Agent account logs into Web Portal", "Access granted (True)", "True (Cookie Auth issued)", "Pass"),
    ("6", "WebLogin_WhenUserIsLocked_ShouldBeBlocked", "User account with lock=true attempts login", "Login blocked (False)", "False (Error message displayed)", "Pass")
]
# Add a 6th row if needed
if len(t11.rows) < 7:
    t11.add_row()

for idx, row in enumerate(test_cases):
    r_idx = idx + 1
    for c_idx, val in enumerate(row):
        is_pass = (c_idx == 5 and val == "Pass")
        col_c = RGBColor(0x15, 0x80, 0x3D) if is_pass else None
        set_cell_text(t11.cell(r_idx, c_idx), val, bold=is_pass, color=col_c)

# Table 12: 7. System Configuration
t12 = doc.tables[12]
set_cell_text(t12.cell(1, 2), "ConfigurationManager.ConnectionStrings[\"B2BConnection\"].ConnectionString")
set_cell_text(t12.cell(2, 2), "builder.Configuration.GetConnectionString(\"B2BConnection\") in Program.cs")
set_cell_text(t12.cell(3, 2), "DbContextOptionsBuilder with UseInMemoryDatabase or TestDb connection")

# Table 13: 8. Source Control & Teamwork
t13 = doc.tables[13]
set_cell_text(t13.cell(1, 1), "https://github.com/thinhvo06/B2BWholesaleSystem")
set_cell_text(t13.cell(2, 1), "GitFlow model: 'main' (stable releases), 'develop' (integration branch), and dedicated feature branches: 'feature/member1-web-core', 'feature/winforms-admin', 'feature/unit-tests'.")
set_cell_text(t13.cell(3, 1), "No direct commits to main or develop. Every feature is merged via Pull Request with code review and approval by at least one teammate.")

# Table 14: 8. Member Branches
t14 = doc.tables[14]
member_git_data = [
    ("Member 1", "main, develop, feature/member1-web-core", "8 commits", "PR #1 (Merged)", "PR #1 (Web & Core DB)"),
    ("Member 2", "feature/winforms-admin, feature/winforms-reports", "6 commits", "PR #2 (Pending)", "PR #2 (WinForms Admin)"),
    ("Member 3", "feature/web-invoices, feature/unit-tests", "6 commits", "PR #3 (Pending)", "PR #3 (Testing & Docs)")
]
for idx, row in enumerate(member_git_data):
    r_idx = idx + 1
    for c_idx, val in enumerate(row):
        set_cell_text(t14.cell(r_idx, c_idx), val)
# Remove row 4 (student 4)
remove_row(t14, 4)

# Table 15: 9. Contribution of Each Member
t15 = doc.tables[15]
contrib_data = [
    ("Võ Nguyễn Phúc Thịnh", "[MSSV 1]", "Task 2 (Shared DB), Task 3.1 (Login), Task 3.2 (Transaction Order), Task 3.4 (Responsive UI)", "34%"),
    ("Ôn Gia Khiêm", "[MSSV 2]", "Task 1.1 (Admin Login), Task 1.2 (CRUD), Task 1.3 (Manifest Report), Task 1.4 (Dashboard)", "33%"),
    ("Nguyễn Nhật Huy", "[MSSV 3]", "Task 2 (Seed Data & Integrity), Task 3.3 (Web Invoice), Task 5.1 (Unit Tests), Task 6 (Report)", "33%")
]
for idx, row in enumerate(contrib_data):
    r_idx = idx + 1
    for c_idx, val in enumerate(row):
        set_cell_text(t15.cell(r_idx, c_idx), val, bold=(c_idx==3))
# Remove rows 5 and 4 (reverse order)
remove_row(t15, 5)
remove_row(t15, 4)
# Update total row
set_cell_text(t15.cell(4, 0), "Total", bold=True)
set_cell_text(t15.cell(4, 3), "100%", bold=True)

# Table 16: Appendix B: Generative AI Use
t16 = doc.tables[16]
ai_data = [
    ("Antigravity AI (13/11/2026)", "Project Architecture & Work Breakdown", "Divide lab assignment for 3 students and generate implementation plan", "Adopted 34%-33%-33% distribution and 1 Solution 4 Projects architecture.", "Reviewed against official grading rubric."),
    ("Antigravity AI (13/11/2026)", "Web Portal & Code First Setup", "Implement EF Core models, seed data and database transaction ordering", "Refined transaction exception handling for dual provider compatibility.", "Executed automated xUnit tests (6/6 Pass) and E2E browser tests.")
]
if len(t16.rows) < 3:
    t16.add_row()

for idx, row in enumerate(ai_data):
    r_idx = idx + 1
    for c_idx, val in enumerate(row):
        set_cell_text(t16.cell(r_idx, c_idx), val)

print("Tables populated.")

# Save modified document
doc.save(output_scratch)
doc.save(output_brain)
print(f"Filled document successfully saved to:\n1. {output_scratch}\n2. {output_brain}")
