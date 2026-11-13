# B2B.WinForms – Member 2 delivery notes

## Included features

- SQL Server connection read from `App.config` (`B2BConnection`); no connection string is hard-coded in C#.
- Admin-only login using the existing `Users` table and `Role` field.
- A persistent lock flag is written to `Users.lock` after five consecutive incorrect passwords. The failed-attempt counter is stored locally under `%LOCALAPPDATA%\\B2BWholesaleSystem\\login-failures.json` because the shared database model does not currently contain a failed-attempt counter column.
- Items: add, edit, delete (deletion is rejected when order history references the item), search, and stock-in.
- Agents: add, edit, delete (deletion is rejected when orders reference the agent), and search.
- Orders: view order header and details; change `Pending` or `Confirmed` to `Shipped`. This action does not deduct stock again because the Web checkout already deducts stock.
- Shipping Manifest: select an order, preview, print, or choose **Microsoft Print to PDF** in the Windows print dialog. The layout is A4 portrait and includes agent details, delivery lines, date, and signature areas.
- Dashboard: date filter, best-selling items, low-stock warning (`StockQuantity < 10`), and revenue by agent. Revenue is calculated from `OrderDetail.UnitAmount * Quantity` for non-cancelled orders in the selected period.

## Database and login setup

The default `App.config` points to `Server=localhost;Database=B2BWholesaleDB`. This matches the default SQL Server instance in `B2B.Web/appsettings.json`. If the group uses another SQL Server instance, update both files to the same server and database.

Create and seed the database by running `B2B.Data/Scripts/SeedData.sql` in SSMS, or start the Web app while SQL Server is available so `DbInitializer.InitializeAsync()` can initialize it. **Warning:** `SeedData.sql` drops and recreates the existing application tables; run it only on a fresh/test database or after backing up data. Do not use the Web app's InMemory fallback for the integrated demo: InMemory data is not shared with the WinForms SQL Server connection.

Default Admin credentials from the actual seed code:

- `admin` / `admin123`
- `admin_wh` / `admin123`
- `supervisor` / `admin123`

The current Web app compares `Users.password` directly with the submitted password and the seed files store plain-text sample passwords. The WinForms login keeps compatibility with that existing shared behavior. Password hashing should be introduced as a coordinated change across both applications and the seed data, not only in WinForms.

## Run

Open `B2BWholesaleSystem.slnx` in a Windows installation of Visual Studio with the .NET 10 SDK and Windows Desktop development workload. Restore NuGet packages, set `B2B.WinForms` as the startup project, then run.

The desktop app checks SQL Server connectivity at startup. It does not silently create a new database, so a missing database or an incorrect connection string is reported instead of producing a separate empty database.

## Important shared-schema constraint

The current `Users` entity contains only a boolean `lock` flag, not a failed-login count or lockout timestamp. The WinForms implementation therefore stores the consecutive attempt counter in the current Windows user's Local AppData and persists the final lock by setting `Users.lock = true`. This avoids changing the shared database schema without Member 1's approval.

The current `Order` entity has no `ShippingDate` field. The manifest therefore prints the date on which the manifest is prepared; it does not claim that this is an independently recorded actual delivery timestamp.
