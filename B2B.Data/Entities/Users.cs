using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace B2B.Data.Entities;

public class Users
{
    [Key]
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int UserID { get; set; }

    [Required]
    [MaxLength(100)]
    public string UserName { get; set; } = string.Empty;

    [Required]
    [EmailAddress]
    [MaxLength(150)]
    public string email { get; set; } = string.Empty;

    [Required]
    [MaxLength(255)]
    public string password { get; set; } = string.Empty;

    public bool @lock { get; set; } = false;

    [Required]
    [MaxLength(50)]
    public string Role { get; set; } = "Agent"; // Admin or Agent

    // Optional link to AgentID if the user is an Agent
    public int? AgentID { get; set; }
    public virtual Agent? Agent { get; set; }
}
