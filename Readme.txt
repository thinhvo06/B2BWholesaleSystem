B2B WHOLESALE ORDER & MANAGEMENT SYSTEM - ASSIGNMENT 2 (QT2)
Faculty of Information Technology - Ton Duc Thang University
Course: Software Engineering Lab (Sem 1_2627)
Instructor: Ky-Trung Pham

1. PROJECT REPOSITORY & DEMO
- GitHub Repository: https://github.com/thinhvo06/B2BWholesaleSystem
  (Branches: main, develop, feature/member1-web-core, feature/member2-winforms, feature/member3-reporting)
- Video Demo Link (Optional/YouTube/Google Drive): [YOUR_VIDEO_DEMO_LINK]

2. TEAM MEMBERS & PERCENTAGE OF CONTRIBUTION
No. | Student ID | Full Name              | Assigned Role      | % Contribution
1   | [MSSV 1]   | Võ Nguyễn Phúc Thịnh   | Leader / Member 1  | 34%
2   | 524H0057   | Ôn Gia Khiêm           | Member 2           | 33%
3   | [MSSV 3]   | Nguyễn Nhật Huy        | Member 3           | 33%


3. DATABASE CONFIGURATION & ENVIRONMENT SETUP
- Technology Stack: .NET 10.0 (C# 14), Entity Framework Core 10.0, SQL Server 2022
- Architecture: Onion / 3-Tier Layered Solution (Shared B2B.Data library)

Database Setup Options:
Option A (Automatic EF Core Migration & Seeding):
  1. Open 'B2BWholesaleSystem.slnx' in Visual Studio with the .NET 10 SDK and Windows Desktop development workload.
  2. Ensure SQL Server LocalDB or SQL Server Express/Developer is running.
  3. Connection string is configured in 'B2B.Web/appsettings.json' and 'B2B.WinForms/App.config'.
     Both applications must point to the SAME SQL Server instance and database (default Web server: localhost; database: B2BWholesaleDB).
  4. At first run, B2B.Web calls 'DbInitializer.InitializeAsync()' to create the schema and seed sample data when SQL Server is available.
  * Important: if B2B.Web falls back to EF Core InMemory because SQL Server is unavailable, its orders are NOT visible to WinForms. For the integrated demo, start SQL Server and use the same SQL connection in both configuration files.

Option B (Manual T-SQL Script):
  1. Open SQL Server Management Studio (SSMS).
  2. Open and execute 'B2B.Data/Scripts/SeedData.sql'.

4. DEFAULT TEST ACCOUNTS
- Admin Account (WinForms Desktop; from DbInitializer.cs and SeedData.sql):
  Username: admin / Password: admin123
  Other Admin users: admin_wh / admin123, supervisor / admin123
- Agent Accounts (Web Portal; from DbInitializer.cs and SeedData.sql):
  Username: agent_hanoi / Password: agent123
  Username: agent_saigon / Password: agent123
  Username: agent_danang / Password: agent123
  Username: agent_locked / Password: agent123 (locked account)

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

