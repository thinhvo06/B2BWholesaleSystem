using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using B2B.Data.Context;
using B2B.Data.Entities;
using B2B.Web.Models;
using B2B.Web.Services;

namespace B2B.Web.Controllers;

[Authorize(Roles = "Agent")]
public class OrderController : Controller
{
    private readonly B2BDbContext _context;
    private readonly CartService _cartService;
    private readonly ILogger<OrderController> _logger;

    public OrderController(B2BDbContext context, CartService cartService, ILogger<OrderController> logger)
    {
        _context = context;
        _cartService = cartService;
        _logger = logger;
    }

    private int GetCurrentAgentId()
    {
        var agentIdClaim = User.FindFirst("AgentID")?.Value;
        if (int.TryParse(agentIdClaim, out int agentId))
        {
            return agentId;
        }

        // Fallback: lookup user
        var userName = User.Identity?.Name;
        var user = _context.Users.FirstOrDefault(u => u.UserName == userName);
        return user?.AgentID ?? 1;
    }

    [HttpGet]
    public async Task<IActionResult> Checkout()
    {
        var cart = _cartService.GetCart();
        if (cart.IsEmpty)
        {
            TempData["Error"] = "Giỏ hàng hiện đang trống. Vui lòng chọn sản phẩm vào giỏ trước khi đặt hàng.";
            return RedirectToAction("Index", "Catalog");
        }

        int agentId = GetCurrentAgentId();
        var agent = await _context.Agent.FindAsync(agentId);

        var model = new CheckoutViewModel
        {
            Cart = cart,
            AgentID = agentId,
            AgentName = agent?.AgentName ?? User.Identity?.Name ?? "Đại lý",
            Address = agent?.Address ?? "Chưa cập nhật",
            Phone = agent?.Phone ?? "Chưa cập nhật"
        };

        return View(model);
    }

    /// <summary>
    /// Task 3.2 (15% - Core Business Logic):
    /// Crucial: When an order is placed, you must use a Database Transaction to create
    /// the Order, insert the OrderDetails, AND deduct the ordered quantity from the
    /// Item.StockQuantity. If there is insufficient stock, the order must be blocked.
    /// </summary>
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> PlaceOrder(CheckoutViewModel model)
    {
        var cart = _cartService.GetCart();
        if (cart.IsEmpty)
        {
            TempData["Error"] = "Giỏ hàng trống! Không thể tiến hành đặt hàng.";
            return RedirectToAction("Index", "Catalog");
        }

        int agentId = GetCurrentAgentId();
        var agent = await _context.Agent.FindAsync(agentId);
        if (agent == null)
        {
            TempData["Error"] = "Không tìm thấy thông tin Đại lý tương ứng.";
            return RedirectToAction("Index", "Catalog");
        }

        // START DATABASE TRANSACTION
        using var transaction = await _context.Database.BeginTransactionAsync();
        try
        {
            _logger.LogInformation("Bắt đầu Database Transaction đặt hàng cho AgentID: {AgentID}...", agentId);

            // Step 1: Pre-verify all items in the database for stock availability
            var itemIds = cart.Items.Select(i => i.ItemID).ToList();
            var dbItems = await _context.Item
                .Where(i => itemIds.Contains(i.ItemID))
                .ToDictionaryAsync(i => i.ItemID);

            foreach (var cartItem in cart.Items)
            {
                if (!dbItems.TryGetValue(cartItem.ItemID, out var dbItem))
                {
                    throw new InvalidOperationException($"Mặt hàng mã #{cartItem.ItemID} ('{cartItem.ItemName}') không còn tồn tại trong hệ thống.");
                }

                // Check insufficient stock constraint
                if (dbItem.StockQuantity < cartItem.Quantity)
                {
                    throw new InvalidOperationException(
                        $"Đơn hàng bị chặn do thiếu tồn kho: Mặt hàng '{dbItem.ItemName}' chỉ còn {dbItem.StockQuantity} sản phẩm trong kho, nhưng đại lý yêu cầu đặt {cartItem.Quantity} sản phẩm.");
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
            await _context.SaveChangesAsync(); // Generates order.OrderID

            // Step 3: Insert OrderDetail records & deduct Item.StockQuantity
            foreach (var cartItem in cart.Items)
            {
                var dbItem = dbItems[cartItem.ItemID];

                var orderDetail = new OrderDetail
                {
                    OrderID = order.OrderID,
                    ItemID = cartItem.ItemID,
                    Quantity = cartItem.Quantity,
                    UnitAmount = dbItem.Price
                };

                await _context.OrderDetail.AddAsync(orderDetail);

                // Deduct stock quantity
                dbItem.StockQuantity -= cartItem.Quantity;
                _logger.LogInformation("Trừ kho mặt hàng #{ItemID} ('{ItemName}'): Giảm {Qty}, Tồn kho mới = {NewStock}",
                    dbItem.ItemID, dbItem.ItemName, cartItem.Quantity, dbItem.StockQuantity);
            }

            // Save details and updated stock quantities
            await _context.SaveChangesAsync();

            // Step 4: Commit the Transaction atomically
            await transaction.CommitAsync();

            _logger.LogInformation("Database Transaction thành công! Đơn hàng #{OrderID} đã được tạo với {Count} món chi tiết.", order.OrderID, cart.Items.Count);

            // Step 5: Clear Cart in session
            _cartService.ClearCart();

            TempData["Success"] = $"Đặt hàng bán buôn thành công! Mã đơn hàng của bạn là #{order.OrderID}.";
            return RedirectToAction("OrderConfirmation", new { id = order.OrderID });
        }
        catch (Exception ex)
        {
            // Transaction Rollback on any failure
            await transaction.RollbackAsync();
            _logger.LogError(ex, "Database Transaction thất bại! Đã Rollback toàn bộ dữ liệu đơn hàng.");

            TempData["Error"] = ex.Message;

            // Re-populate view model for checkout review
            model.Cart = cart;
            model.AgentName = agent.AgentName;
            model.Address = agent.Address;
            model.Phone = agent.Phone;
            return View("Checkout", model);
        }
    }

    [HttpGet]
    public async Task<IActionResult> OrderConfirmation(int id)
    {
        int agentId = GetCurrentAgentId();

        var order = await _context.Order
            .Include(o => o.Agent)
            .Include(o => o.OrderDetails)
                .ThenInclude(od => od.Item)
            .FirstOrDefaultAsync(o => o.OrderID == id && o.AgentID == agentId);

        if (order == null)
        {
            TempData["Error"] = "Không tìm thấy đơn hàng.";
            return RedirectToAction("Index", "Catalog");
        }

        return View(order);
    }
}
