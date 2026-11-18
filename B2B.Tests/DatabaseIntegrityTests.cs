using Microsoft.EntityFrameworkCore;
using B2B.Data.Entities;
using B2B.Data.Seed;
using Xunit;

namespace B2B.Tests;

/// <summary>
/// Task 2 & Task 5.1 (Member 3 - Seed Data & Database Referential Integrity Tests):
/// Verifies 15-30 realistic seed rows per table and enforces real relational Foreign Key,
/// Cascade/Restrict, and CHECK constraints on SQLite.
/// </summary>
public class DatabaseIntegrityTests
{
    [Fact]
    public async Task SeedData_ShouldInsert15To30RowsPerTable_WithValidRelationships()
    {
        // Arrange
        await using var db = await SqliteTestContext.CreateAsync();

        // Act
        await DbInitializer.InitializeAsync(db.Context);

        // Assert: All 5 tables have 15 to 30 realistic rows
        int itemCount = await db.Context.Item.CountAsync();
        int agentCount = await db.Context.Agent.CountAsync();
        int userCount = await db.Context.Users.CountAsync();
        int orderCount = await db.Context.Order.CountAsync();
        int detailCount = await db.Context.OrderDetail.CountAsync();

        Assert.InRange(itemCount, 15, 30);
        Assert.InRange(agentCount, 15, 30);
        Assert.InRange(userCount, 15, 30);
        Assert.InRange(orderCount, 15, 30);
        Assert.InRange(detailCount, 15, 30);

        // Verify both Admin and Agent users exist, plus a locked account and low-stock items (< 10)
        Assert.True(await db.Context.Users.AnyAsync(u => u.Role == "Admin"));
        Assert.True(await db.Context.Users.AnyAsync(u => u.Role == "Agent"));
        Assert.True(await db.Context.Users.AnyAsync(u => u.@lock));
        Assert.True(await db.Context.Item.AnyAsync(i => i.StockQuantity < 10));

        // Verify every seeded order has at least one OrderDetail (no empty orphan headers)
        var ordersWithoutDetails = await db.Context.Order
            .Where(o => !o.OrderDetails.Any())
            .CountAsync();
        Assert.Equal(0, ordersWithoutDetails);
    }

    [Fact]
    public async Task DatabaseIntegrity_ShouldEnforceForeignKeysCascadeRestrict_AndCheckConstraints()
    {
        // Arrange
        await using var db = await SqliteTestContext.CreateAsync();
        await DbInitializer.InitializeAsync(db.Context);

        // 1. Orphan FK check: Inserting an Order with non-existent AgentID must fail
        db.Context.Order.Add(new Order { AgentID = 99999, OrderStatus = "Pending" });
        await Assert.ThrowsAsync<DbUpdateException>(() => db.Context.SaveChangesAsync());
        db.Context.ChangeTracker.Clear();

        // 2. CHECK constraint: StockQuantity < 0 must fail at DB level
        db.Context.Item.Add(new Item { ItemName = "Invalid Negative Stock Item", Size = "S", Price = 100000m, StockQuantity = -1 });
        await Assert.ThrowsAsync<DbUpdateException>(() => db.Context.SaveChangesAsync());
        db.Context.ChangeTracker.Clear();

        // 3. Restrict Delete: Deleting an Item referenced by OrderDetail must fail
        var referencedItem = await db.Context.Item.FirstAsync(i => i.ItemID == 1);
        db.Context.Item.Remove(referencedItem);
        await Assert.ThrowsAsync<DbUpdateException>(() => db.Context.SaveChangesAsync());
        db.Context.ChangeTracker.Clear();

        // 4. Cascade Delete: Deleting an Order automatically removes its child OrderDetails
        var orderToDelete = await db.Context.Order.FirstAsync(o => o.OrderID == 15);
        int detailsBefore = await db.Context.OrderDetail.CountAsync(od => od.OrderID == 15);
        Assert.True(detailsBefore > 0);

        db.Context.Order.Remove(orderToDelete);
        await db.Context.SaveChangesAsync();

        int detailsAfter = await db.Context.OrderDetail.CountAsync(od => od.OrderID == 15);
        Assert.Equal(0, detailsAfter);
    }
}
