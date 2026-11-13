using System.Text.Json;
using B2B.Web.Models;

namespace B2B.Web.Services;

public class CartService
{
    private const string CartSessionKey = "B2B_Wholesale_Cart";
    private readonly IHttpContextAccessor _httpContextAccessor;

    public CartService(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    private ISession Session => _httpContextAccessor.HttpContext?.Session
        ?? throw new InvalidOperationException("Session is not available.");

    public CartViewModel GetCart()
    {
        var json = Session.GetString(CartSessionKey);
        if (string.IsNullOrEmpty(json))
        {
            return new CartViewModel();
        }

        try
        {
            return JsonSerializer.Deserialize<CartViewModel>(json) ?? new CartViewModel();
        }
        catch
        {
            return new CartViewModel();
        }
    }

    public void SaveCart(CartViewModel cart)
    {
        var json = JsonSerializer.Serialize(cart);
        Session.SetString(CartSessionKey, json);
    }

    public void AddItem(int itemId, string itemName, string size, decimal price, int quantity, int availableStock)
    {
        var cart = GetCart();
        var existing = cart.Items.FirstOrDefault(i => i.ItemID == itemId);

        if (existing != null)
        {
            existing.Quantity += quantity;
            existing.AvailableStock = availableStock;
        }
        else
        {
            cart.Items.Add(new CartItemViewModel
            {
                ItemID = itemId,
                ItemName = itemName,
                Size = size,
                Price = price,
                Quantity = quantity,
                AvailableStock = availableStock
            });
        }

        SaveCart(cart);
    }

    public void UpdateQuantity(int itemId, int quantity)
    {
        var cart = GetCart();
        var item = cart.Items.FirstOrDefault(i => i.ItemID == itemId);
        if (item != null)
        {
            if (quantity <= 0)
            {
                cart.Items.Remove(item);
            }
            else
            {
                item.Quantity = quantity;
            }
            SaveCart(cart);
        }
    }

    public void RemoveItem(int itemId)
    {
        var cart = GetCart();
        var item = cart.Items.FirstOrDefault(i => i.ItemID == itemId);
        if (item != null)
        {
            cart.Items.Remove(item);
            SaveCart(cart);
        }
    }

    public void ClearCart()
    {
        Session.Remove(CartSessionKey);
    }
}
