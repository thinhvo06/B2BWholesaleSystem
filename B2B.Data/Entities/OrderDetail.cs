using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace B2B.Data.Entities;

public class OrderDetail
{
    [Key]
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int ID { get; set; }

    [Required]
    public int OrderID { get; set; }

    [Required]
    public int ItemID { get; set; }

    public int Quantity { get; set; }

    [Column(TypeName = "decimal(18, 2)")]
    public decimal UnitAmount { get; set; }

    // Navigation properties
    public virtual Order? Order { get; set; }
    public virtual Item? Item { get; set; }
}
