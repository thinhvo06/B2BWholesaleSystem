using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage;
using B2B.Data.Context;
using B2B.Data.Entities;

namespace B2B.Data.Services;

public record OrderItemRequest(int ItemID, int Quantity);

public class OrderService
{
    private readonly B2BDbContext _context;

    public OrderService(B2BDbContext context)
    {
        _context = context;
    }

    /// <summary>
    /// Calculates the total order amount: Sum(UnitAmount * Quantity).
    /// </summary>
    public static decimal CalculateOrderTotal(IEnumerable<OrderDetail> details)
    {
        ArgumentNullException.ThrowIfNull(details);
        return details.Sum(od => od.UnitAmount * od.Quantity);
    }

    /// <summary>
    /// Places a Master-Detail wholesale order inside a single atomic Database Transaction:
    /// validates non-empty items, validates positive quantities, aggregates duplicate items,
    /// verifies stock availability, creates Order & OrderDetails, and deducts Item.StockQuantity.
    /// Rolls back completely on any failure.
    /// </summary>
    public async Task<Order> PlaceOrderAsync(int agentId, IReadOnlyCollection<OrderItemRequest> items)
    {
        if (items == null || items.Count == 0)
        {
            throw new InvalidOperationException("Danh sách chi tiết đơn hàng không được để trống (Empty OrderDetails).");
        }

        foreach (var line in items)
        {
            if (line.Quantity <= 0)
            {
                throw new ArgumentOutOfRangeException(nameof(items), $"Số lượng đặt cho mặt hàng #{line.ItemID} phải lớn hơn 0.");
            }
        }

        var agent = await _context.Agent.FindAsync(agentId);
        if (agent == null)
        {
            throw new InvalidOperationException($"Không tìm thấy thông tin Đại lý với mã #{agentId}.");
        }

        // Combine duplicate item lines in the same order so stock is checked against combined quantity
        var consolidatedItems = items
            .GroupBy(i => i.ItemID)
            .Select(g => new OrderItemRequest(g.Key, g.Sum(x => x.Quantity)))
            .ToList();

        IDbContextTransaction? transaction = null;
        if (_context.Database.IsRelational())
        {
            transaction = await _context.Database.BeginTransactionAsync();
        }

        try
        {
            var itemIds = consolidatedItems.Select(i => i.ItemID).ToList();
            var dbItems = await _context.Item
                .Where(i => itemIds.Contains(i.ItemID))
                .ToDictionaryAsync(i => i.ItemID);

            // Step 1: Pre-verify every requested item exists and has sufficient stock
            foreach (var req in consolidatedItems)
            {
                if (!dbItems.TryGetValue(req.ItemID, out var dbItem))
                {
                    throw new InvalidOperationException($"Mặt hàng mã #{req.ItemID} không còn tồn tại trong hệ thống.");
                }

                if (dbItem.StockQuantity < req.Quantity)
                {
                    throw new InvalidOperationException(
                        $"Đơn hàng bị chặn do thiếu tồn kho: Mặt hàng '{dbItem.ItemName}' chỉ còn {dbItem.StockQuantity} sản phẩm trong kho, nhưng đại lý yêu cầu đặt {req.Quantity} sản phẩm.");
                }
            }

            // Step 2: Create Master Order record with initial status 'Pending'
            var order = new Order
            {
                OrderDate = DateTime.UtcNow,
                AgentID = agentId,
                OrderStatus = "Pending"
            };

            await _context.Order.AddAsync(order);
            await _context.SaveChangesAsync();

            // Step 3: Insert OrderDetails & deduct Item.StockQuantity atomically
            foreach (var req in consolidatedItems)
            {
                var dbItem = dbItems[req.ItemID];

                var detail = new OrderDetail
                {
                    OrderID = order.OrderID,
                    ItemID = req.ItemID,
                    Quantity = req.Quantity,
                    UnitAmount = dbItem.Price
                };

                await _context.OrderDetail.AddAsync(detail);
                dbItem.StockQuantity -= req.Quantity;
            }

            await _context.SaveChangesAsync();

            // Step 4: Commit transaction
            if (transaction != null)
            {
                await transaction.CommitAsync();
            }

            return order;
        }
        catch
        {
            if (transaction != null)
            {
                await transaction.RollbackAsync();
            }

            // Detach any modified tracked entities on rollback so subsequent reads reflect clean DB state
            foreach (var entry in _context.ChangeTracker.Entries().ToList())
            {
                entry.State = EntityState.Detached;
            }

            throw;
        }
        finally
        {
            if (transaction != null)
            {
                await transaction.DisposeAsync();
            }
        }
    }

    /// <summary>
    /// Task 3.3: Retrieves ONLY the logged-in agent's past orders with optional status and keyword filters.
    /// </summary>
    public async Task<List<Order>> GetAgentOrdersAsync(int agentId, string? status = null, string? search = null)
    {
        var query = _context.Order
            .AsNoTracking()
            .Include(o => o.Agent)
            .Include(o => o.OrderDetails)
                .ThenInclude(od => od.Item)
            .Where(o => o.AgentID == agentId);

        if (!string.IsNullOrWhiteSpace(status) && !string.Equals(status, "All", StringComparison.OrdinalIgnoreCase))
        {
            var normalizedStatus = status.Trim();
            query = query.Where(o => o.OrderStatus == normalizedStatus);
        }

        var orders = await query
            .OrderByDescending(o => o.OrderDate)
            .ThenByDescending(o => o.OrderID)
            .ToListAsync();

        if (!string.IsNullOrWhiteSpace(search))
        {
            var keyword = search.Trim().TrimStart('#');
            orders = orders.Where(o =>
                o.OrderID.ToString().Contains(keyword, StringComparison.OrdinalIgnoreCase) ||
                o.OrderStatus.Contains(keyword, StringComparison.OrdinalIgnoreCase) ||
                o.OrderDetails.Any(od =>
                    od.Item != null &&
                    od.Item.ItemName.Contains(keyword, StringComparison.OrdinalIgnoreCase)))
                .ToList();
        }

        return orders;
    }

    /// <summary>
    /// Task 3.3: Retrieves a single order for printable invoice viewing, strictly enforcing ownership (IDOR protection).
    /// Returns null if the order does not exist or belongs to another agent.
    /// </summary>
    public async Task<Order?> GetAgentOrderInvoiceAsync(int orderId, int agentId)
    {
        return await _context.Order
            .AsNoTracking()
            .Include(o => o.Agent)
            .Include(o => o.OrderDetails)
                .ThenInclude(od => od.Item)
            .FirstOrDefaultAsync(o => o.OrderID == orderId && o.AgentID == agentId);
    }
}
