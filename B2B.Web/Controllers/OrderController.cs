using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using B2B.Data.Context;
using B2B.Data.Services;
using B2B.Web.Models;
using B2B.Web.Services;

namespace B2B.Web.Controllers;

[Authorize(Roles = "Agent")]
public class OrderController : Controller
{
    private readonly B2BDbContext _context;
    private readonly CartService _cartService;
    private readonly OrderService _orderService;
    private readonly ILogger<OrderController> _logger;

    public OrderController(
        B2BDbContext context,
        CartService cartService,
        OrderService orderService,
        ILogger<OrderController> logger)
    {
        _context = context;
        _cartService = cartService;
        _orderService = orderService;
        _logger = logger;
    }

    private int GetCurrentAgentId()
    {
        var agentIdClaim = User.FindFirst("AgentID")?.Value;
        if (int.TryParse(agentIdClaim, out int agentId))
        {
            return agentId;
        }

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
    /// Executes Master-Detail order creation and stock deduction inside an atomic Database Transaction.
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

        try
        {
            _logger.LogInformation("Bắt đầu Database Transaction đặt hàng cho AgentID: {AgentID}...", agentId);

            var orderItems = cart.Items
                .Select(i => new OrderItemRequest(i.ItemID, i.Quantity))
                .ToList();

            var order = await _orderService.PlaceOrderAsync(agentId, orderItems);

            _logger.LogInformation("Database Transaction thành công! Đơn hàng #{OrderID} đã được tạo với {Count} món chi tiết.", order.OrderID, cart.Items.Count);

            _cartService.ClearCart();

            TempData["Success"] = $"Đặt hàng bán buôn thành công! Mã đơn hàng của bạn là #{order.OrderID}.";
            return RedirectToAction("OrderConfirmation", new { id = order.OrderID });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Database Transaction thất bại! Đã Rollback toàn bộ dữ liệu đơn hàng.");

            TempData["Error"] = ex.Message;

            model.Cart = cart;
            model.AgentID = agentId;
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
        var order = await _orderService.GetAgentOrderInvoiceAsync(id, agentId);

        if (order == null)
        {
            TempData["Error"] = "Không tìm thấy đơn hàng hoặc bạn không có quyền xem đơn hàng này.";
            return RedirectToAction("MyOrders");
        }

        return View(order);
    }

    /// <summary>
    /// Task 3.3 (10% - Member 3):
    /// "My Orders" page where the logged-in agent views ONLY their own past orders and order statuses.
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> MyOrders(string? status = null, string? search = null)
    {
        int agentId = GetCurrentAgentId();
        var agent = await _context.Agent.AsNoTracking().FirstOrDefaultAsync(a => a.AgentID == agentId);
        var orders = await _orderService.GetAgentOrdersAsync(agentId, status, search);

        var viewModel = new MyOrdersViewModel
        {
            AgentID = agentId,
            AgentName = agent?.AgentName ?? User.FindFirst("AgentName")?.Value ?? User.Identity?.Name ?? "Đại lý",
            StatusFilter = status,
            SearchQuery = search,
            Orders = orders.Select(o => new OrderSummaryItemViewModel
            {
                OrderID = o.OrderID,
                OrderDate = o.OrderDate,
                OrderStatus = o.OrderStatus,
                LineCount = o.OrderDetails.Count,
                TotalQuantity = o.OrderDetails.Sum(od => od.Quantity),
                TotalAmount = OrderService.CalculateOrderTotal(o.OrderDetails),
                ItemNamesPreview = o.OrderDetails
                    .Where(od => od.Item != null)
                    .Select(od => $"{od.Item!.ItemName} (x{od.Quantity})")
                    .ToList()
            }).ToList()
        };

        return View(viewModel);
    }

    /// <summary>
    /// Task 3.3 (10% - Member 3):
    /// Printable HTML/CSS Print Media Invoice View with strict Agent ownership enforcement (IDOR protection).
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> Invoice(int id)
    {
        int agentId = GetCurrentAgentId();
        var order = await _orderService.GetAgentOrderInvoiceAsync(id, agentId);

        if (order == null)
        {
            _logger.LogWarning("Agent #{AgentID} attempted to access unauthorized or non-existent Order #{OrderID}.", agentId, id);
            TempData["Error"] = $"Không tìm thấy hóa đơn cho đơn hàng #{id} hoặc bạn không có quyền truy cập đơn hàng của đại lý khác.";
            return RedirectToAction("MyOrders");
        }

        var agentEmail = User.FindFirst(ClaimTypes.Email)?.Value
            ?? (await _context.Users.AsNoTracking().FirstOrDefaultAsync(u => u.AgentID == agentId))?.email
            ?? "contact@b2bwholesale.vn";

        var viewModel = new InvoiceViewModel
        {
            Order = order,
            AgentEmail = agentEmail
        };

        return View(viewModel);
    }
}
