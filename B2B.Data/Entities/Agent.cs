using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace B2B.Data.Entities;

public class Agent
{
    [Key]
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int AgentID { get; set; }

    [Required]
    [MaxLength(200)]
    public string AgentName { get; set; } = string.Empty;

    [MaxLength(300)]
    public string Address { get; set; } = string.Empty;

    [MaxLength(50)]
    public string Phone { get; set; } = string.Empty;

    // Navigation property
    public virtual ICollection<Order> Orders { get; set; } = new List<Order>();
}
