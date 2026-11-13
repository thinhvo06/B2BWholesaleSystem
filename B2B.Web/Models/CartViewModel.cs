namespace B2B.Web.Models;

public class CartItemViewModel
{
    public int ItemID { get; set; }
    public string ItemName { get; set; } = string.Empty;
    public string Size { get; set; } = string.Empty;
    public decimal Price { get; set; }
    public int Quantity { get; set; }
    public int AvailableStock { get; set; }

    public decimal TotalAmount => Price * Quantity;
}

public class CartViewModel
{
    public List<CartItemViewModel> Items { get; set; } = new();

    public decimal TotalAmount => Items.Sum(i => i.TotalAmount);
    public int TotalQuantity => Items.Sum(i => i.Quantity);
    public bool IsEmpty => Items.Count == 0;
}
