using Microsoft.EntityFrameworkCore;
using B2B.Data.Entities;

namespace B2B.Data.Context;

public class B2BDbContext : DbContext
{
    public B2BDbContext(DbContextOptions<B2BDbContext> options) : base(options)
    {
    }

    public DbSet<Item> Item => Set<Item>();
    public DbSet<Agent> Agent => Set<Agent>();
    public DbSet<Order> Order => Set<Order>();
    public DbSet<OrderDetail> OrderDetail => Set<OrderDetail>();
    public DbSet<Users> Users => Set<Users>();

    // Plural aliases for convenience
    public DbSet<Item> Items => Item;
    public DbSet<Agent> Agents => Agent;
    public DbSet<Order> Orders => Order;
    public DbSet<OrderDetail> OrderDetails => OrderDetail;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // 1. Item table configuration
        modelBuilder.Entity<Item>(entity =>
        {
            entity.ToTable("Item");
            entity.HasKey(e => e.ItemID);
            entity.Property(e => e.ItemName).IsRequired().HasMaxLength(200);
            entity.Property(e => e.Size).HasMaxLength(50);
            entity.Property(e => e.Price).HasColumnType("decimal(18, 2)");
            entity.Property(e => e.StockQuantity).IsRequired();
        });

        // 2. Agent table configuration
        modelBuilder.Entity<Agent>(entity =>
        {
            entity.ToTable("Agent");
            entity.HasKey(e => e.AgentID);
            entity.Property(e => e.AgentName).IsRequired().HasMaxLength(200);
            entity.Property(e => e.Address).HasMaxLength(300);
            entity.Property(e => e.Phone).HasMaxLength(50);
        });

        // 3. Order table configuration
        modelBuilder.Entity<Order>(entity =>
        {
            entity.ToTable("Order");
            entity.HasKey(e => e.OrderID);
            entity.Property(e => e.OrderDate).IsRequired();
            entity.Property(e => e.OrderStatus).IsRequired().HasMaxLength(50);

            // Foreign Key to Agent: Restrict delete to prevent accidental agent deletion with active orders
            entity.HasOne(o => o.Agent)
                  .WithMany(a => a.Orders)
                  .HasForeignKey(o => o.AgentID)
                  .OnDelete(DeleteBehavior.Restrict);
        });

        // 4. OrderDetail table configuration
        modelBuilder.Entity<OrderDetail>(entity =>
        {
            entity.ToTable("OrderDetail");
            entity.HasKey(e => e.ID);
            entity.Property(e => e.Quantity).IsRequired();
            entity.Property(e => e.UnitAmount).HasColumnType("decimal(18, 2)");

            // Cascading delete: if Order is deleted, delete its OrderDetails
            entity.HasOne(od => od.Order)
                  .WithMany(o => o.OrderDetails)
                  .HasForeignKey(od => od.OrderID)
                  .OnDelete(DeleteBehavior.Cascade);

            // Restrict delete: do not allow Item deletion if referenced in OrderDetails
            entity.HasOne(od => od.Item)
                  .WithMany(i => i.OrderDetails)
                  .HasForeignKey(od => od.ItemID)
                  .OnDelete(DeleteBehavior.Restrict);
        });

        // 5. Users table configuration
        modelBuilder.Entity<Users>(entity =>
        {
            entity.ToTable("Users");
            entity.HasKey(e => e.UserID);
            entity.Property(e => e.UserName).IsRequired().HasMaxLength(100);
            entity.Property(e => e.email).IsRequired().HasMaxLength(150);
            entity.Property(e => e.password).IsRequired().HasMaxLength(255);
            entity.Property(e => e.@lock).IsRequired();
            entity.Property(e => e.Role).IsRequired().HasMaxLength(50);

            entity.HasIndex(e => e.UserName).IsUnique();
            entity.HasIndex(e => e.email).IsUnique();

            entity.HasOne(u => u.Agent)
                  .WithMany()
                  .HasForeignKey(u => u.AgentID)
                  .IsRequired(false)
                  .OnDelete(DeleteBehavior.SetNull);
        });
    }
}
