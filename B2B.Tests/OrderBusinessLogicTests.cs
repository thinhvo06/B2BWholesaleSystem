using Microsoft.EntityFrameworkCore;
using B2B.Data.Entities;
using B2B.Data.Services;
using Xunit;

namespace B2B.Tests;

/// <summary>
/// Task 5.1 (Member 3 - QA & Unit Testing):
/// Core Order Business Logic, Atomic Database Transaction, Rollback, Total Calculation,
/// and My Orders / Invoice Authorization (IDOR) Tests.
/// </summary>
public class OrderBusinessLogicTests
{
    [Fact]
    public async Task DeductStock_WhenStockIsSufficient_ShouldDecreaseStockQuantity()
    {
        // Arrange
        await using var db = await SqliteTestContext.CreateAsync();
        var item1 = new Item { ItemName = "Màn hình Dell UltraSharp 27 inch 4K", Size = "27 inch", Price = 11500000m, StockQuantity = 50 };
        var item2 = new Item { ItemName = "Bàn phím cơ Logitech MX Mechanical", Size = "Fullsize", Price = 3450000m, StockQuantity = 30 };
        var agent = new Agent { AgentName = "Đại lý Phúc Anh Tech", Address = "15 Xã Đàn, Hà Nội", Phone = "02438572222" };

        db.Context.Item.AddRange(item1, item2);
        db.Context.Agent.Add(agent);
        await db.Context.SaveChangesAsync();

        var service = new OrderService(db.Context);
        var orderLines = new[]
        {
            new OrderItemRequest(item1.ItemID, 10),
            new OrderItemRequest(item2.ItemID, 5)
        };

        // Act
        var createdOrder = await service.PlaceOrderAsync(agent.AgentID, orderLines);

        // Assert (re-query via a fresh DbContext to verify persisted relational commit)
        await using var verifyCtx = db.CreateFreshContext();
        var persistedItem1 = await verifyCtx.Item.FindAsync(item1.ItemID);
        var persistedItem2 = await verifyCtx.Item.FindAsync(item2.ItemID);
        var persistedOrder = await verifyCtx.Order
            .Include(o => o.OrderDetails)
            .FirstOrDefaultAsync(o => o.OrderID == createdOrder.OrderID);

        Assert.NotNull(persistedItem1);
        Assert.NotNull(persistedItem2);
        Assert.NotNull(persistedOrder);
        Assert.Equal(40, persistedItem1!.StockQuantity); // 50 - 10
        Assert.Equal(25, persistedItem2!.StockQuantity); // 30 - 5
        Assert.Equal("Pending", persistedOrder!.OrderStatus);
        Assert.Equal(2, persistedOrder.OrderDetails.Count);
        Assert.Equal(132250000m, OrderService.CalculateOrderTotal(persistedOrder.OrderDetails));
    }

    [Fact]
    public async Task PlaceOrder_WhenStockIsInsufficient_ShouldThrowExceptionAndRollback()
    {
        // Arrange: Item 1 has enough stock (50), Item 2 does NOT (only 5, ordering 20)
        await using var db = await SqliteTestContext.CreateAsync();
        var item1 = new Item { ItemName = "Màn hình Dell UltraSharp 27 inch 4K", Size = "27 inch", Price = 11500000m, StockQuantity = 50 };
        var item2 = new Item { ItemName = "Chuột Logitech MX Master 3S", Size = "Medium", Price = 2390000m, StockQuantity = 5 };
        var agent = new Agent { AgentName = "Đại lý Phong Vũ Mega", Address = "264 NTMK, TP.HCM", Phone = "02873086666" };

        db.Context.Item.AddRange(item1, item2);
        db.Context.Agent.Add(agent);
        await db.Context.SaveChangesAsync();

        var service = new OrderService(db.Context);
        var orderLines = new[]
        {
            new OrderItemRequest(item1.ItemID, 10), // Valid quantity
            new OrderItemRequest(item2.ItemID, 20)  // Exceeds stock (5) -> must trigger full rollback
        };

        // Act & Assert
        var ex = await Assert.ThrowsAsync<InvalidOperationException>(() =>
            service.PlaceOrderAsync(agent.AgentID, orderLines));

        Assert.Contains("thiếu tồn kho", ex.Message, StringComparison.OrdinalIgnoreCase);

        // Verify full rollback via fresh context: NO Order created, NO OrderDetails, BOTH stocks untouched
        await using var verifyCtx = db.CreateFreshContext();
        Assert.Equal(0, await verifyCtx.Order.CountAsync());
        Assert.Equal(0, await verifyCtx.OrderDetail.CountAsync());
        Assert.Equal(50, (await verifyCtx.Item.FindAsync(item1.ItemID))!.StockQuantity);
        Assert.Equal(5, (await verifyCtx.Item.FindAsync(item2.ItemID))!.StockQuantity);
    }

    [Fact]
    public void CalculateOrderTotal_WithMultipleItems_ShouldReturnCorrectSum()
    {
        // Arrange
        var details = new List<OrderDetail>
        {
            new OrderDetail { ItemID = 1, Quantity = 5, UnitAmount = 11500000m },  // 57,500,000
            new OrderDetail { ItemID = 2, Quantity = 10, UnitAmount = 3450000m },  // 34,500,000
            new OrderDetail { ItemID = 12, Quantity = 20, UnitAmount = 1690000m }  // 33,800,000
        };

        decimal expectedTotal = (5 * 11500000m) + (10 * 3450000m) + (20 * 1690000m); // 125,800,000

        // Act
        decimal actualTotal = OrderService.CalculateOrderTotal(details);

        // Assert
        Assert.Equal(expectedTotal, actualTotal);
        Assert.Equal(125800000m, actualTotal);
    }

    [Fact]
    public async Task PlaceOrder_WhenOrderDetailsIsEmpty_ShouldThrowExceptionAndBlockOrder()
    {
        // Arrange
        await using var db = await SqliteTestContext.CreateAsync();
        var agent = new Agent { AgentName = "Đại lý Đà Nẵng", Address = "52 Nguyễn Văn Linh", Phone = "02363888000" };
        db.Context.Agent.Add(agent);
        await db.Context.SaveChangesAsync();

        var service = new OrderService(db.Context);

        // Act & Assert
        var ex = await Assert.ThrowsAsync<InvalidOperationException>(() =>
            service.PlaceOrderAsync(agent.AgentID, Array.Empty<OrderItemRequest>()));

        Assert.Contains("không được để trống", ex.Message, StringComparison.OrdinalIgnoreCase);
        Assert.Equal(0, await db.Context.Order.CountAsync());
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-5)]
    public async Task PlaceOrder_WhenQuantityIsZeroOrNegative_ShouldThrowArgumentOutOfRangeException(int invalidQty)
    {
        // Arrange
        await using var db = await SqliteTestContext.CreateAsync();
        var item = new Item { ItemName = "SSD Samsung T7 1TB", Size = "1TB", Price = 2850000m, StockQuantity = 100 };
        var agent = new Agent { AgentName = "Đại lý Cần Thơ", Address = "84 Mậu Thân", Phone = "02923768888" };
        db.Context.Item.Add(item);
        db.Context.Agent.Add(agent);
        await db.Context.SaveChangesAsync();

        var service = new OrderService(db.Context);

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentOutOfRangeException>(() =>
            service.PlaceOrderAsync(agent.AgentID, new[] { new OrderItemRequest(item.ItemID, invalidQty) }));

        Assert.Equal(100, (await db.Context.Item.FindAsync(item.ItemID))!.StockQuantity);
    }

    [Fact]
    public async Task PlaceOrder_WhenQuantityEqualsExactStock_ShouldSucceedAndSetStockToZero()
    {
        // Arrange
        await using var db = await SqliteTestContext.CreateAsync();
        var item = new Item { ItemName = "Switch Cisco 24-Port", Size = "24-Port", Price = 14900000m, StockQuantity = 8 };
        var agent = new Agent { AgentName = "Đại lý Bình Dương", Address = "Thủ Dầu Một", Phone = "02743828999" };
        db.Context.Item.Add(item);
        db.Context.Agent.Add(agent);
        await db.Context.SaveChangesAsync();

        var service = new OrderService(db.Context);

        // Act
        var order = await service.PlaceOrderAsync(agent.AgentID, new[] { new OrderItemRequest(item.ItemID, 8) });

        // Assert
        await using var verifyCtx = db.CreateFreshContext();
        Assert.NotNull(order);
        Assert.Equal(0, (await verifyCtx.Item.FindAsync(item.ItemID))!.StockQuantity);
    }

    [Fact]
    public async Task PlaceOrder_WhenSameItemAddedTwice_ShouldValidateCombinedQuantity()
    {
        // Arrange: Stock is 10, but same item requested twice (6 + 6 = 12 > 10)
        await using var db = await SqliteTestContext.CreateAsync();
        var item = new Item { ItemName = "NAS Synology DS923+", Size = "4-Bay", Price = 16500000m, StockQuantity = 10 };
        var agent = new Agent { AgentName = "Đại lý Hải Phòng", Address = "120 Lạch Tray", Phone = "02253846666" };
        db.Context.Item.Add(item);
        db.Context.Agent.Add(agent);
        await db.Context.SaveChangesAsync();

        var service = new OrderService(db.Context);
        var duplicateLines = new[]
        {
            new OrderItemRequest(item.ItemID, 6),
            new OrderItemRequest(item.ItemID, 6)
        };

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(() =>
            service.PlaceOrderAsync(agent.AgentID, duplicateLines));

        await using var verifyCtx = db.CreateFreshContext();
        Assert.Equal(10, (await verifyCtx.Item.FindAsync(item.ItemID))!.StockQuantity);
        Assert.Equal(0, await verifyCtx.Order.CountAsync());
    }

    [Fact]
    public async Task GetAgentOrders_AndInvoice_ShouldEnforceAgentOwnershipIsolation()
    {
        // Arrange: Two separate agents each have their own order
        await using var db = await SqliteTestContext.CreateAsync();
        var item = new Item { ItemName = "Tai nghe Sony WH-1000XM5", Size = "Over-ear", Price = 7490000m, StockQuantity = 60 };
        var agent1 = new Agent { AgentName = "Đại lý Hà Nội", Address = "Hà Nội", Phone = "0241111111" };
        var agent2 = new Agent { AgentName = "Đại lý TP.HCM", Address = "TP.HCM", Phone = "0282222222" };

        db.Context.Item.Add(item);
        db.Context.Agent.AddRange(agent1, agent2);
        await db.Context.SaveChangesAsync();

        var service = new OrderService(db.Context);
        var orderOfAgent1 = await service.PlaceOrderAsync(agent1.AgentID, new[] { new OrderItemRequest(item.ItemID, 2) });
        var orderOfAgent2 = await service.PlaceOrderAsync(agent2.AgentID, new[] { new OrderItemRequest(item.ItemID, 3) });

        // Act
        var agent1Orders = await service.GetAgentOrdersAsync(agent1.AgentID);
        var ownInvoice = await service.GetAgentOrderInvoiceAsync(orderOfAgent1.OrderID, agent1.AgentID);
        var stolenInvoice = await service.GetAgentOrderInvoiceAsync(orderOfAgent2.OrderID, agent1.AgentID);

        // Assert: Agent 1 only sees Order 1, can print Order 1 invoice, and is blocked from Order 2 (IDOR protection)
        Assert.Single(agent1Orders);
        Assert.Equal(orderOfAgent1.OrderID, agent1Orders[0].OrderID);
        Assert.NotNull(ownInvoice);
        Assert.Null(stolenInvoice);
    }
}
