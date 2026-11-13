using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace B2B.Data.Entities;

public class Order
{
    [Key]
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int OrderID { get; set; }

    public DateTime OrderDate { get; set; } = DateTime.UtcNow;

    [Required]
    public int AgentID { get; set; }

    [Required]
    [MaxLength(50)]
    public string OrderStatus { get; set; } = "Pending"; // e.g. Pending, Shipped, Delivered, Cancelled

    // Navigation properties
    public virtual Agent? Agent { get; set; }
    public virtual ICollection<OrderDetail> OrderDetails { get; set; } = new List<OrderDetail>();
}
