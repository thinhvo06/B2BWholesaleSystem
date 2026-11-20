B2B WHOLESALE ORDER & MANAGEMENT SYSTEM - ASSIGNMENT 2 (QT2)
Faculty of Information Technology - Ton Duc Thang University (TDTU)
Course: Software Engineering Lab (Sem 1_2627)
Instructor: Ky-Trung Pham (tg_phamthaikytrung@tdtu.edu.vn)

1. PROJECT REPOSITORY & DEMO
- GitHub Repository: https://github.com/thinhvo06/B2BWholesaleSystem
  Branches:
  * main (stable release)
  * develop (integration branch)
  * feature/member1-web-core (Member 1: Shared DB, Web Auth, Catalog, Cart, Transaction Checkout)
  * feature/member2-winforms (Member 2: WinForms Admin Login, CRUD, Orders, Shipping Manifest, Dashboard)
  * feature/web-myorders-invoice (Member 3: Seed Data & Integrity Constraints, Task 3.3 My Orders & Printable Invoice)
  * feature/unit-tests-businesslogic (Member 3: Task 5.1 Automated xUnit Test Suite - 16 Tests)
  * docs/report-and-packaging (Member 3: Report.docx, Workbook, Readme.txt, SourceCode.zip packaging)
- Video Demo Link: https://youtu.be/PafoyZpm9g0

2. TEAM MEMBERS & PERCENTAGE OF CONTRIBUTION
No. | Student ID | Full Name              | Assigned Role                               | % Contribution
1   | 524H0069   | Võ Nguyễn Phúc Thịnh   | Leader / Member 1 (Web Core & Shared DB)    | 34%
2   | 524H0057   | Ôn Gia Khiêm           | Member 2 (WinForms Back-Office & Reporting) | 33%
3   | 524H0052   | Nguyễn Nhật Huy        | Member 3 (Seed/Integrity, Invoices, QA/Doc) | 33%
Total Contribution: 100%

3. DATABASE CONFIGURATION & ENVIRONMENT SETUP
- Technology Stack: .NET 10.0 (C# 14), ASP.NET Core MVC (Option C - Code First),
  WinForms (.NET 10 Windows), Entity Framework Core 10.0, SQL Server 2022, xUnit 2.9 + SQLite.
- Architecture: 1 Solution - 4 Projects (B2B.Data, B2B.Web, B2B.WinForms, B2B.Tests).

Database Setup Options:
Option A (Manual T-SQL Script - Recommended for Integrated WinForms + Web Demo):
  1. Open SQL Server Management Studio (SSMS) and connect to your SQL Server instance (default: localhost or .\SQLEXPRESS).
  2. Open and execute 'B2B.Data/Scripts/SeedData.sql'.
     This idempotent script creates database 'B2BWholesaleDB', all 5 tables with PKs, FKs,
     Cascade/Restrict rules, CHECK constraints, and seeds 15-30 realistic rows per table:
       - Item        : 20 rows (including 2 low-stock items < 10 for Dashboard warning)
       - Agent       : 16 rows
       - Users       : 19 rows (3 Admin + 16 Agent including 1 locked account)
       - [Order]     : 15 rows (Pending, Confirmed, Shipped, Delivered)
       - OrderDetail : 30 rows (2 line items per order covering all 15 orders)

Option B (Automatic EF Core Initialization & Seeding):
  1. Open 'B2BWholesaleSystem.slnx' in Visual Studio (with .NET 10 SDK & Windows Desktop workload).
  2. Configure the SAME SQL Server connection string in both configuration files (no hardcoded strings in C#):
     - Web App  : 'B2B.Web/appsettings.json' -> ConnectionStrings:B2BConnection
     - WinForms : 'B2B.WinForms/App.config'  -> connectionStrings:B2BConnection
  3. On first startup, B2B.Web runs 'DbInitializer.InitializeAsync()' to create schema and seed data.
  * Note: If SQL Server is unreachable, B2B.Web automatically falls back to EF Core InMemory so the Web Portal
    can still be previewed standalone. For full Web + WinForms integration, point both configs to SQL Server.

4. DEFAULT TEST ACCOUNTS
- Admin Accounts (WinForms Back-Office ONLY - blocked on Web Portal):
  * admin      / admin123
  * admin_wh   / admin123
  * supervisor / admin123
- Agent Accounts (Web Portal ONLY - blocked on WinForms):
  * agent_hanoi  / agent123 (Agent #1 - Phúc Anh Tech, owns Orders #1, #6)
  * agent_saigon / agent123 (Agent #2 - Phong Vũ Mega, owns Orders #2, #7, #15)
  * agent_danang / agent123 (Agent #3 - Phi Long Plaza, owns Orders #3, #13)
  * agent_locked / agent123 (Locked account - lock = true, blocked at login)

5. HOW TO RUN THE APPLICATIONS & TESTS
A. Web Portal (B2B.Web - Tasks 3.1, 3.2, 3.3, 3.4):
   cd B2B.Web
   dotnet run --urls "http://localhost:5250"
   Open browser: http://localhost:5250
   Features: Agent login with role/lockout enforcement, Responsive Bootstrap 5 Catalog, Bulk Cart,
   Transactional Master-Detail Checkout, My Orders history (with status filter, search & IDOR protection),
   and A4 Printable Invoice view (HTML/CSS @media print / Save as PDF).

B. Back-Office Desktop Admin (B2B.WinForms - Tasks 1.1, 1.2, 1.3, 1.4):
   cd B2B.WinForms
   dotnet run
   Features: Admin-only login with lockout, Item & Agent CRUD + Stock-In, Order Management (Pending -> Shipped),
   A4 Shipping Manifest preview/print/PDF, and Analytical Dashboard (Best-selling, Low-stock < 10, Revenue by Agent).

C. Automated Unit Tests (B2B.Tests - Task 5.1):
   dotnet test B2B.Tests/B2B.Tests.csproj --logger "console;verbosity=detailed"
   Result: 16 / 16 tests PASSED (100%) using isolated relational SQLite in-memory databases verifying:
   - Stock deduction & atomic relational transaction commit/rollback
   - Order total calculation (Sum of UnitAmount * Quantity)
   - Empty OrderDetails & invalid quantity validation, duplicate item aggregation, boundary stock = 0
   - Role-based access control (Admin vs Agent) & 5-failure persistent account lockout
   - My Orders & Invoice agent ownership isolation (IDOR prevention)
   - Seed data counts (15-30 rows/table) & real relational FK Cascade/Restrict and CHECK constraints
