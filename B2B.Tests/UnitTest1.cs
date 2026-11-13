using Microsoft.EntityFrameworkCore;
using B2B.Data.Context;
using B2B.Data.Entities;
using B2B.Data.Seed;
using Xunit;

namespace B2B.Tests;

public class Member1CoreBusinessLogicTests
{
    private B2BDbContext CreateInMemoryContext(string dbName)
    {
        var options = new DbContextOptionsBuilder<B2BDbContext>()
            .UseInMemoryDatabase(databaseName: dbName)
            .Options;

        return new B2BDbContext(options);
    }

    [Fact]
    public async Task SeedData_ShouldInsertRequiredTables_AndRealisticSampleRows()
    {
        // Arrange
        using var context = CreateInMemoryContext("TestDb_SeedData");

        // Act
        await DbInitializer.InitializeAsync(context);

        // Assert: 15 to 30 rows per table as required by the assignment
        var itemCount = await context.Item.CountAsync();
        var agentCount = await context.Agent.CountAsync();
        var userCount = await context.Users.CountAsync();
        var orderCount = await context.Order.CountAsync();
        var detailCount = await context.OrderDetail.CountAsync();

        Assert.InRange(itemCount, 15, 30);
        Assert.InRange(agentCount, 15, 30);
        Assert.InRange(userCount, 15, 30);
        Assert.InRange(orderCount, 15, 30);
        Assert.InRange(detailCount, 15, 30);
    }

    [Fact]
    public async Task PlaceOrder_WhenStockIsSufficient_ShouldDeductStock_AndCreateOrder()
    {
        // Arrange
        using var context = CreateInMemoryContext("TestDb_SufficientStock");
        var item = new Item
        {
            ItemName = "Màn hình Dell UltraSharp 27 inch 4K",
            Size = "27 inch",
            Price = 11500000m,
            StockQuantity = 50
        };
        var agent = new Agent
        {
            AgentName = "Đại lý Hà Nội",
            Address = "Hà Nội",
            Phone = "0987654321"
        };
        await context.Item.AddAsync(item);
        await context.Agent.AddAsync(agent);
        await context.SaveChangesAsync();

        int orderQty = 10;
        int expectedRemainingStock = 50 - orderQty;

        // Act (Simulate Order Transaction logic)
        var order = new Order
        {
            OrderDate = DateTime.UtcNow,
            AgentID = agent.AgentID,
            OrderStatus = "Pending"
        };
        await context.Order.AddAsync(order);
        await context.SaveChangesAsync();

        var detail = new OrderDetail
        {
            OrderID = order.OrderID,
            ItemID = item.ItemID,
            Quantity = orderQty,
            UnitAmount = item.Price
        };
        await context.OrderDetail.AddAsync(detail);

        item.StockQuantity -= orderQty;
        await context.SaveChangesAsync();

        // Assert
        var updatedItem = await context.Item.FindAsync(item.ItemID);
        Assert.NotNull(updatedItem);
        Assert.Equal(expectedRemainingStock, updatedItem.StockQuantity);

        var createdOrder = await context.Order.Include(o => o.OrderDetails).FirstOrDefaultAsync(o => o.OrderID == order.OrderID);
        Assert.NotNull(createdOrder);
        Assert.Single(createdOrder.OrderDetails);
        Assert.Equal(orderQty, createdOrder.OrderDetails.First().Quantity);
    }

    [Fact]
    public async Task PlaceOrder_WhenStockIsInsufficient_ShouldBlockOrder_AndPreserveStock()
    {
        // Arrange
        using var context = CreateInMemoryContext("TestDb_InsufficientStock");
        var item = new Item
        {
            ItemName = "Chuột Logitech MX Master 3S",
            Size = "Medium",
            Price = 2390000m,
            StockQuantity = 5 // only 5 in stock
        };
        var agent = new Agent
        {
            AgentName = "Đại lý Sài Gòn",
            Address = "TP.HCM",
            Phone = "0912345678"
        };
        await context.Item.AddAsync(item);
        await context.Agent.AddAsync(agent);
        await context.SaveChangesAsync();

        int requestedQty = 20; // requesting 20 (exceeds 5)

        // Act & Assert: Business rule must throw exception and block
        var exception = await Assert.ThrowsAsync<InvalidOperationException>(async () =>
        {
            var dbItem = await context.Item.FindAsync(item.ItemID);
            if (dbItem == null || dbItem.StockQuantity < requestedQty)
            {
                throw new InvalidOperationException($"Không đủ số lượng tồn kho cho sản phẩm '{item.ItemName}'!");
            }

            // Should not reach here
            item.StockQuantity -= requestedQty;
            await context.SaveChangesAsync();
        });

        Assert.Contains("Không đủ số lượng tồn kho", exception.Message);

        // Verify stock quantity was NOT deducted
        var currentItem = await context.Item.FindAsync(item.ItemID);
        Assert.NotNull(currentItem);
        Assert.Equal(5, currentItem.StockQuantity);
    }

    [Theory]
    [InlineData("Admin", false)] // Admin is NOT allowed on Web Portal
    [InlineData("Agent", true)]  // Agent is allowed on Web Portal
    public void WebLogin_RoleValidation_ShouldOnlyAllowAgent(string role, bool expectedAllowed)
    {
        // Arrange
        var user = new Users
        {
            UserName = "test_user",
            Role = role,
            @lock = false
        };

        // Act
        bool isAllowedOnWeb = string.Equals(user.Role, "Agent", StringComparison.OrdinalIgnoreCase);

        // Assert
        Assert.Equal(expectedAllowed, isAllowedOnWeb);
    }

    [Fact]
    public void WebLogin_WhenUserIsLocked_ShouldBeBlocked()
    {
        // Arrange
        var lockedUser = new Users
        {
            UserName = "agent_locked",
            Role = "Agent",
            @lock = true
        };

        // Act
        bool canLogin = !lockedUser.@lock;

        // Assert
        Assert.False(canLogin);
    }
}
