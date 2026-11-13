using System.ComponentModel.DataAnnotations;
using B2B.Data.Entities;

namespace B2B.Web.Models;

public class CheckoutViewModel
{
    public CartViewModel Cart { get; set; } = new();

    public int AgentID { get; set; }
    public string AgentName { get; set; } = string.Empty;
    public string Address { get; set; } = string.Empty;
    public string Phone { get; set; } = string.Empty;

    [Display(Name = "Ghi chú giao hàng (nếu có)")]
    public string? Notes { get; set; }
}
