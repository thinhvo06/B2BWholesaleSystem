using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.EntityFrameworkCore;
using B2B.Data.Context;
using B2B.Data.Seed;
using B2B.Web.Services;

var builder = WebApplication.CreateBuilder(args);

// 1. Add MVC Controllers with Views
builder.Services.AddControllersWithViews();

// 2. Add HttpContextAccessor and Session Cart Service
builder.Services.AddHttpContextAccessor();
builder.Services.AddScoped<CartService>();

// 3. Configure Database Connection (SQL Server with resilient in-memory fallback)
var connectionString = builder.Configuration.GetConnectionString("B2BConnection")
    ?? "Server=localhost;Database=B2BWholesaleDB;Trusted_Connection=True;TrustServerCertificate=True;";

bool isSqlServerAvailable = false;
try
{
    using var testConn = new Microsoft.Data.SqlClient.SqlConnection(connectionString);
    testConn.Open();
    isSqlServerAvailable = true;
}
catch
{
    isSqlServerAvailable = false;
}

builder.Services.AddDbContext<B2BDbContext>(options =>
{
    if (isSqlServerAvailable)
    {
        options.UseSqlServer(connectionString, sqlOptions =>
        {
            sqlOptions.EnableRetryOnFailure(maxRetryCount: 3, maxRetryDelay: TimeSpan.FromSeconds(3), errorNumbersToAdd: null);
        });
    }
    else
    {
        // Resilient in-memory database fallback so web app can run and be demonstrated immediately
        options.UseInMemoryDatabase("B2BWholesaleDB");
    }
});

// 4. Configure Cookie Authentication & Authorization
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.LoginPath = "/Account/Login";
        options.LogoutPath = "/Account/Logout";
        options.AccessDeniedPath = "/Account/AccessDenied";
        options.ExpireTimeSpan = TimeSpan.FromHours(8);
        options.SlidingExpiration = true;
    });

// 5. Configure Distributed Cache & Session
builder.Services.AddDistributedMemoryCache();
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(60);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
});

var app = builder.Build();

// 6. Database Initialization & Seed Data (15-30 realistic rows per table)
using (var scope = app.Services.CreateScope())
{
    var services = scope.ServiceProvider;
    var logger = services.GetRequiredService<ILogger<Program>>();
    var context = services.GetRequiredService<B2BDbContext>();

    try
    {
        if (isSqlServerAvailable)
        {
            logger.LogInformation(">>> Đang kết nối SQL Server tại localhost... Khởi tạo và nạp Seed Data...");
        }
        else
        {
            logger.LogInformation(">>> SQL Server không có sẵn. Đang khởi tạo EF Core In-Memory Database và nạp Seed Data...");
        }

        await DbInitializer.InitializeAsync(context);
        logger.LogInformation(">>> Khởi tạo CSDL và nạp 15-30 dòng Seed Data thành công! <<<");
    }
    catch (Exception ex)
    {
        logger.LogError(ex, "Lỗi khi khởi tạo CSDL và Seed Data!");
    }
}

// 7. Configure HTTP Request Pipeline
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseStaticFiles();

app.UseRouting();

app.UseSession();
app.UseAuthentication();
app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Catalog}/{action=Index}/{id?}");

app.Run();
