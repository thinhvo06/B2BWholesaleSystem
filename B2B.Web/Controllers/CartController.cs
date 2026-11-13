using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using B2B.Data.Context;
using B2B.Web.Services;

namespace B2B.Web.Controllers;

[Authorize(Roles = "Agent")]
public class CartController : Controller
{
    private readonly B2BDbContext _context;
    private readonly CartService _cartService;

    public CartController(B2BDbContext context, CartService cartService)
    {
        _context = context;
        _cartService = cartService;
    }

    [HttpGet]
    public IActionResult Index()
    {
        var cart = _cartService.GetCart();
        return View(cart);
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> AddToCart(int itemId, int quantity = 1)
    {
        if (quantity <= 0)
        {
            TempData["Error"] = "Số lượng đặt phải lớn hơn 0.";
            return RedirectToAction("Index", "Catalog");
        }

        var item = await _context.Item.FindAsync(itemId);
        if (item == null)
        {
            TempData["Error"] = "Mặt hàng không tồn tại.";
            return RedirectToAction("Index", "Catalog");
        }

        if (item.StockQuantity < quantity)
        {
            TempData["Error"] = $"Không đủ số lượng tồn kho! Mặt hàng '{item.ItemName}' chỉ còn {item.StockQuantity} sản phẩm.";
            return RedirectToAction("Index", "Catalog");
        }

        _cartService.AddItem(item.ItemID, item.ItemName, item.Size, item.Price, quantity, item.StockQuantity);

        TempData["Success"] = $"Đã thêm {quantity} x '{item.ItemName}' vào giỏ hàng đặt buôn thành công!";
        return RedirectToAction("Index");
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> UpdateQuantity(int itemId, int quantity)
    {
        var item = await _context.Item.FindAsync(itemId);
        if (item != null && quantity > item.StockQuantity)
        {
            TempData["Error"] = $"Số lượng yêu cầu ({quantity}) vượt quá tồn kho hiện tại ({item.StockQuantity}) của sản phẩm '{item.ItemName}'.";
            return RedirectToAction("Index");
        }

        _cartService.UpdateQuantity(itemId, quantity);
        TempData["Success"] = "Đã cập nhật giỏ hàng.";
        return RedirectToAction("Index");
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public IActionResult RemoveItem(int itemId)
    {
        _cartService.RemoveItem(itemId);
        TempData["Success"] = "Đã xóa mặt hàng khỏi giỏ.";
        return RedirectToAction("Index");
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public IActionResult Clear()
    {
        _cartService.ClearCart();
        TempData["Success"] = "Đã dọn sạch giỏ hàng.";
        return RedirectToAction("Index");
    }
}
