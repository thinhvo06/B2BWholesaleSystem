using B2B.Data.Entities;

namespace B2B.Web.Models;

public class OrderSummaryItemViewModel
{
    public int OrderID { get; set; }
    public DateTime OrderDate { get; set; }
    public string OrderStatus { get; set; } = "Pending";
    public int LineCount { get; set; }
    public int TotalQuantity { get; set; }
    public decimal TotalAmount { get; set; }
    public List<string> ItemNamesPreview { get; set; } = new();
}

public class MyOrdersViewModel
{
    public int AgentID { get; set; }
    public string AgentName { get; set; } = string.Empty;
    public string? StatusFilter { get; set; }
    public string? SearchQuery { get; set; }

    public List<OrderSummaryItemViewModel> Orders { get; set; } = new();

    public int TotalOrdersCount => Orders.Count;
    public decimal TotalSpent => Orders.Sum(o => o.TotalAmount);
    public int PendingCount => Orders.Count(o => string.Equals(o.OrderStatus, "Pending", StringComparison.OrdinalIgnoreCase));
    public int ShippedOrDeliveredCount => Orders.Count(o =>
        string.Equals(o.OrderStatus, "Shipped", StringComparison.OrdinalIgnoreCase) ||
        string.Equals(o.OrderStatus, "Delivered", StringComparison.OrdinalIgnoreCase));
}

public class InvoiceViewModel
{
    public Order Order { get; set; } = null!;
    public string InvoiceNumber => $"INV-{Order.OrderDate:yyyyMMdd}-{Order.OrderID:D4}";
    public string AgentEmail { get; set; } = string.Empty;
    public int TotalQuantity => Order.OrderDetails.Sum(od => od.Quantity);
    public decimal SubTotal => Order.OrderDetails.Sum(od => od.UnitAmount * od.Quantity);
    public decimal VatAmount => 0m; // Wholesale B2B 0% / inclusive per Cart summary
    public decimal GrandTotal => SubTotal + VatAmount;
    public string AmountInWords => ConvertVndToVietnameseWords((long)Math.Round(GrandTotal));

    public static string ConvertVndToVietnameseWords(long number)
    {
        if (number <= 0) return "Không đồng";

        string[] units = { "", "nghìn", "triệu", "tỷ", "nghìn tỷ" };
        string[] digits = { "không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín" };

        var parts = new List<string>();
        int groupIndex = 0;

        while (number > 0 && groupIndex < units.Length)
        {
            int group = (int)(number % 1000);
            number /= 1000;

            if (group > 0)
            {
                bool hasHigherGroup = number > 0;
                string groupText = ReadThreeDigits(group, hasHigherGroup, digits);
                if (!string.IsNullOrEmpty(units[groupIndex]))
                {
                    groupText += " " + units[groupIndex];
                }
                parts.Insert(0, groupText);
            }

            groupIndex++;
        }

        string result = string.Join(" ", parts).Trim() + " đồng chẵn";
        return char.ToUpper(result[0]) + result[1..];
    }

    private static string ReadThreeDigits(int n, bool showZeroHundred, string[] digits)
    {
        int hundred = n / 100;
        int ten = (n % 100) / 10;
        int unit = n % 10;

        var words = new List<string>();

        if (hundred > 0 || showZeroHundred)
        {
            words.Add(digits[hundred] + " trăm");
        }

        if (ten > 1)
        {
            words.Add(digits[ten] + " mươi");
            if (unit == 1) words.Add("mốt");
            else if (unit == 4) words.Add("tư");
            else if (unit == 5) words.Add("lăm");
            else if (unit > 0) words.Add(digits[unit]);
        }
        else if (ten == 1)
        {
            words.Add("mười");
            if (unit == 5) words.Add("lăm");
            else if (unit > 0) words.Add(digits[unit]);
        }
        else if (unit > 0)
        {
            if (hundred > 0 || showZeroHundred) words.Add("lẻ");
            words.Add(digits[unit]);
        }

        return string.Join(" ", words);
    }
}
