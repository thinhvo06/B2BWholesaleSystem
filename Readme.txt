================================================================================
B2B WHOLESALE ORDER & MANAGEMENT SYSTEM - ASSIGNMENT 2 (QT2)
Faculty of Information Technology - Ton Duc Thang University
Course: Software Engineering Lab (Sem 1_2627)
Instructor: Ky-Trung Pham
================================================================================

1. PROJECT REPOSITORY & DEMO
- GitHub Repository: https://github.com/thinhvo06/B2BWholesaleSystem
  (Branches: main, develop, feature/member1-web-core, feature/member2-winforms, feature/member3-reporting)
- Video Demo Link (Optional/YouTube/Google Drive): [YOUR_VIDEO_DEMO_LINK]

2. TEAM MEMBERS & PERCENTAGE OF CONTRIBUTION
--------------------------------------------------------------------------------
No. | Student ID | Full Name              | Assigned Role      | % Contribution
--------------------------------------------------------------------------------
1   | [MSSV 1]   | Võ Nguyễn Phúc Thịnh   | Leader / Member 1  | 34%
2   | [MSSV 2]   | Ôn Gia Khiêm           | Member 2           | 33%
3   | [MSSV 3]   | Nguyễn Nhật Huy        | Member 3           | 33%
--------------------------------------------------------------------------------
TOTAL: 100%

3. DATABASE CONFIGURATION & ENVIRONMENT SETUP
- Technology Stack: .NET 10.0 (C# 14), Entity Framework Core 10.0, SQL Server 2022
- Architecture: Onion / 3-Tier Layered Solution (Shared B2B.Data library)

Database Setup Options:
Option A (Automatic EF Core Migration & Seeding):
  1. Open 'B2BWholesaleSystem.slnx' in Visual Studio 2022 / 2025.
  2. Ensure SQL Server LocalDB or SQL Server Express/Developer is running.
  3. Connection string is configured in 'appsettings.json' (B2B.Web) and 'App.config' (B2B.WinForms):
     "Server=(localdb)\\mssqllocaldb;Database=B2BWholesaleDb;Trusted_Connection=True;MultipleActiveResultSets=true;TrustServerCertificate=True"
  4. At first run, 'DbInitializer.SeedAsync()' automatically checks, creates the schema, and populates 15+ seed records for all 5 tables.
  * Note: If SQL Server is temporarily offline, B2B.Web automatically falls back to EF Core InMemory database for instant review and zero-friction grading!

Option B (Manual T-SQL Script):
  1. Open SQL Server Management Studio (SSMS).
  2. Open and execute 'B2B.Data/Scripts/SeedData.sql'.

4. DEFAULT TEST ACCOUNTS
- Admin Account (WinForms Desktop):
  Username: admin / Password: password
- Agent Accounts (Web Portal):
  Username: agent_ag01 / Password: password (Agent: MegaMart District 1, 15M Credit)
  Username: agent_ag02 / Password: password (Agent: SuperCo Tan Binh, 10M Credit)
  Username: agent_ag03 / Password: password (Agent: BachHoaGoVap, 8M Credit)
  Username: agent_locked / Password: password (Status: Inactive / Blocked)

5. HOW TO RUN THE APPLICATIONS
A. Web Portal (B2B.Web):
   - Command Line:
     cd B2B.Web
     dotnet run --urls "http://localhost:5250"
   - Browser URL: http://localhost:5250
   - Features: Agent login, Responsive Catalog, Bulk Cart, Transactional Master-Detail Checkout, Invoice view.

B. Back-Office Desktop Admin (B2B.WinForms):
   - Command Line:
     cd B2B.WinForms
     dotnet run
   - Features: Admin login, Item/Agent CRUD, Low Stock Alerts, Shipping Manifest, Analytical Dashboard.

C. Automated Unit Tests (B2B.Tests):
   - Command Line:
     dotnet test
   - 6 test cases verifying transactions, seed data constraints, role checks, and concurrency.
================================================================================
