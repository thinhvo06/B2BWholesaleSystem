using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;
using B2B.Data.Context;

namespace B2B.Tests;

/// <summary>
/// Creates an isolated relational SQLite in-memory B2BDbContext per test.
/// Unlike EF Core's non-relational InMemory provider, SQLite executes real
/// Database Transactions (Commit/Rollback), Foreign Key constraints, and CHECK constraints.
/// </summary>
public sealed class SqliteTestContext : IAsyncDisposable
{
    private readonly SqliteConnection _connection;
    public B2BDbContext Context { get; }

    private SqliteTestContext(SqliteConnection connection, B2BDbContext context)
    {
        _connection = connection;
        Context = context;
    }

    public static async Task<SqliteTestContext> CreateAsync()
    {
        var connection = new SqliteConnection("DataSource=:memory:");
        await connection.OpenAsync();

        // Enforce Foreign Keys on SQLite connection
        using (var pragmaCmd = connection.CreateCommand())
        {
            pragmaCmd.CommandText = "PRAGMA foreign_keys = ON;";
            await pragmaCmd.ExecuteNonQueryAsync();
        }

        var options = new DbContextOptionsBuilder<B2BDbContext>()
            .UseSqlite(connection)
            .Options;

        var context = new B2BDbContext(options);
        await context.Database.EnsureCreatedAsync();

        return new SqliteTestContext(connection, context);
    }

    public B2BDbContext CreateFreshContext()
    {
        var options = new DbContextOptionsBuilder<B2BDbContext>()
            .UseSqlite(_connection)
            .Options;

        return new B2BDbContext(options);
    }

    public async ValueTask DisposeAsync()
    {
        await Context.DisposeAsync();
        await _connection.DisposeAsync();
    }
}
