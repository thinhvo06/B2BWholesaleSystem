using System.Configuration;
using System.Text.Json;
using B2B.Data.Context;
using Microsoft.EntityFrameworkCore;

namespace B2B.WinForms.DataAccess;

/// <summary>
/// Creates short-lived EF Core contexts for the desktop application.
/// The connection string is read from App.config and is never embedded in C# code.
/// </summary>
public static class AppDatabase
{
    private static readonly string ConnectionString = LoadConnectionString();

    private static string LoadConnectionString()
    {
        string configPath = Path.Combine(AppContext.BaseDirectory, "App.config");
        if (!File.Exists(configPath))
            throw new FileNotFoundException("Không tìm thấy App.config trong thư mục chạy ứng dụng.", configPath);

        var map = new ExeConfigurationFileMap { ExeConfigFilename = configPath };
        var configuration = ConfigurationManager.OpenMappedExeConfiguration(map, ConfigurationUserLevel.None);
        return configuration.ConnectionStrings.ConnectionStrings["B2BConnection"]?.ConnectionString
            ?? throw new InvalidOperationException("Không tìm thấy connection string 'B2BConnection' trong App.config.");
    }

    private static readonly DbContextOptions<B2BDbContext> Options =
        new DbContextOptionsBuilder<B2BDbContext>()
            .UseSqlServer(ConnectionString, sql => sql.EnableRetryOnFailure(3))
            .Options;

    public static B2BDbContext CreateContext() => new(Options);

    public static void VerifyConnection()
    {
        using var context = CreateContext();
        if (!context.Database.CanConnect())
        {
            throw new InvalidOperationException(
                "Không thể kết nối SQL Server. Hãy kiểm tra SQL Server đang chạy, " +
                "database B2BWholesaleDB đã được tạo và connection string trong App.config.");
        }
    }
}

/// <summary>
/// The shared Users table currently stores only a boolean lock flag (no failed-attempt column).
/// This tracker persists the consecutive failure counter in the current Windows user's Local AppData
/// and persists the final lock by setting Users.lock after five consecutive failed passwords.
/// </summary>
public static class LoginAttemptTracker
{
    private const int MaxAttempts = 5;
    private static readonly object Sync = new();
    private static readonly string StoragePath = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "B2BWholesaleSystem", "login-failures.json");
    private static readonly Dictionary<string, int> FailedAttempts = Load();

    public static bool RegisterFailure(string userName)
    {
        lock (Sync)
        {
            FailedAttempts.TryGetValue(userName, out int attempts);
            attempts++;
            FailedAttempts[userName] = attempts;
            Save();
            return attempts >= MaxAttempts;
        }
    }

    public static void Reset(string userName)
    {
        lock (Sync)
        {
            FailedAttempts.Remove(userName);
            Save();
        }
    }

    private static Dictionary<string, int> Load()
    {
        try
        {
            if (!File.Exists(StoragePath)) return new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
            string json = File.ReadAllText(StoragePath);
            var loaded = JsonSerializer.Deserialize<Dictionary<string, int>>(json);
            return loaded is null
                ? new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase)
                : new Dictionary<string, int>(loaded, StringComparer.OrdinalIgnoreCase);
        }
        catch
        {
            // A malformed local counter file must not prevent an Admin from opening the app.
            return new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
        }
    }

    private static void Save()
    {
        try
        {
            string? directory = Path.GetDirectoryName(StoragePath);
            if (!string.IsNullOrEmpty(directory)) Directory.CreateDirectory(directory);
            File.WriteAllText(StoragePath, JsonSerializer.Serialize(FailedAttempts));
        }
        catch
        {
            // The database lock flag remains the authoritative persisted lock state.
        }
    }
}

public sealed class AdminSession
{
    public int UserId { get; init; }
    public string UserName { get; init; } = string.Empty;
}
