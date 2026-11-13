using Microsoft.EntityFrameworkCore;
using B2B.Data.Context;
using B2B.Data.Entities;

namespace B2B.Data.Seed;

public static class DbInitializer
{
    public static async Task InitializeAsync(B2BDbContext context)
    {
        // Ensure database is created (when using InMemory or relational provider)
        await context.Database.EnsureCreatedAsync();

        // 1. Seed Items if empty
        if (!await context.Item.AnyAsync())
        {
            var items = new List<Item>
            {
                new Item { ItemName = "Màn hình Dell UltraSharp 27 inch 4K", Size = "27 inch", Price = 11500000m, StockQuantity = 85 },
                new Item { ItemName = "Bàn phím cơ không dây Logitech MX Mechanical", Size = "Fullsize", Price = 3450000m, StockQuantity = 120 },
                new Item { ItemName = "Chuột công thái học Logitech MX Master 3S", Size = "Medium", Price = 2390000m, StockQuantity = 150 },
                new Item { ItemName = "Tai nghe chống ồn Sony WH-1000XM5", Size = "Over-ear", Price = 7490000m, StockQuantity = 60 },
                new Item { ItemName = "Ổ cứng di động SSD Samsung T7 Shield 1TB", Size = "1TB", Price = 2850000m, StockQuantity = 200 },
                new Item { ItemName = "Bộ phát Wifi 6 Mesh TP-Link Deco X50 (Bộ 3)", Size = "Pack 3", Price = 4250000m, StockQuantity = 45 },
                new Item { ItemName = "Máy in đa năng laser Brother DCP-L2520D", Size = "Standard", Price = 4190000m, StockQuantity = 35 },
                new Item { ItemName = "Máy chiếu thông minh 4K BenQ TK700STi", Size = "Large", Price = 28900000m, StockQuantity = 15 },
                new Item { ItemName = "Ghế công thái học Herman Miller Aeron", Size = "Size B", Price = 32500000m, StockQuantity = 20 },
                new Item { ItemName = "Bàn làm việc nâng hạ Ergonomic SmartDesk Pro", Size = "160x80cm", Price = 8900000m, StockQuantity = 40 },
                new Item { ItemName = "Webcam hội nghị trực tuyến Logitech Brio 4K", Size = "Compact", Price = 4350000m, StockQuantity = 90 },
                new Item { ItemName = "Bộ sạc đa cổng Anker Prime 100W GaN", Size = "Small", Price = 1690000m, StockQuantity = 250 },
                new Item { ItemName = "Đế làm mát Laptop nhôm nguyên khối HyperStand", Size = "15-17 inch", Price = 650000m, StockQuantity = 180 },
                new Item { ItemName = "Cáp Thunderbolt 4 Belkin Pro 2m", Size = "2m", Price = 1450000m, StockQuantity = 110 },
                new Item { ItemName = "Loa hội nghị Bluetooth Jabra Speak 710", Size = "Portable", Price = 5890000m, StockQuantity = 50 },
                new Item { ItemName = "Pin sạc dự phòng Shargeek Storm 2 25600mAh", Size = "25600mAh", Price = 4200000m, StockQuantity = 75 },
                new Item { ItemName = "Thẻ nhớ SanDisk Extreme Pro 256GB MicroSD", Size = "256GB", Price = 890000m, StockQuantity = 300 },
                new Item { ItemName = "Bộ lưu điện UPS APC Back-UPS Pro 1500VA", Size = "1500VA", Price = 6800000m, StockQuantity = 25 }
            };

            await context.Item.AddRangeAsync(items);
            await context.SaveChangesAsync();
        }

        // 2. Seed Agents if empty
        if (!await context.Agent.AnyAsync())
        {
            var agents = new List<Agent>
            {
                new Agent { AgentName = "Đại lý Bán buôn Miền Bắc - Phúc Anh Tech", Address = "Số 15 Xã Đàn, Đống Đa, Hà Nội", Phone = "02438572222" },
                new Agent { AgentName = "Đại lý Bán buôn Miền Nam - Phong Vũ Mega", Address = "264 Nguyễn Thị Minh Khai, Q.3, TP.HCM", Phone = "02873086666" },
                new Agent { AgentName = "Tổng kho Thiết bị Miền Trung - Phi Long Plaza", Address = "52 Nguyễn Văn Linh, Hải Châu, Đà Nẵng", Phone = "02363888000" },
                new Agent { AgentName = "Nhà phân phối Tây Nam Bộ - Cần Thơ Digital", Address = "84 Mậu Thân, Ninh Kiều, Cần Thơ", Phone = "02923768888" },
                new Agent { AgentName = "Đại lý Khu Công nghiệp - Bình Dương Solution", Address = "Đại lộ Bình Dương, TP. Thủ Dầu Một", Phone = "02743828999" },
                new Agent { AgentName = "Trung tâm Thiết bị Hải Phòng - Cenco Tech", Address = "120 Lạch Tray, Ngô Quyền, Hải Phòng", Phone = "02253846666" },
                new Agent { AgentName = "Đại lý Bán lẻ & Bán buôn Biên Hòa Tech", Address = "38 Đồng Khởi, Tân Hiệp, Biên Hòa, Đồng Nai", Phone = "02513898888" },
                new Agent { AgentName = "Tổng kho Tây Nguyên - Ban Mê Wholesale", Address = "79 Lê Duẩn, TP. Buôn Ma Thuột, Đắk Lắk", Phone = "02623812345" },
                new Agent { AgentName = "Công ty TNHH Thiết bị Số Nha Trang", Address = "24 Quang Trung, Vạn Thạnh, Nha Trang", Phone = "02583824444" },
                new Agent { AgentName = "Đại lý Vũng Tàu Logistics & Trade", Address = "184 Ba Cu, Phường 3, TP. Vũng Tàu", Phone = "02543859999" },
                new Agent { AgentName = "Đại lý Công nghệ Quảng Ninh - Cẩm Phả Tech", Address = "25 Trần Phú, Cẩm Phả, Quảng Ninh", Phone = "02033862222" },
                new Agent { AgentName = "Đại lý Phân phối An Giang - Long Xuyên Store", Address = "45 Thoại Ngọc Hầu, Long Xuyên, An Giang", Phone = "02963841111" },
                new Agent { AgentName = "Đại lý Bắc Ninh Kho Vận & Phụ kiện", Address = "11 Lý Thái Tổ, Suối Hoa, TP. Bắc Ninh", Phone = "02223838888" },
                new Agent { AgentName = "Nhà cung ứng Bán buôn Huế Heritage Tech", Address = "86 Hùng Vương, Phú Nhuận, TP. Huế", Phone = "02343899777" },
                new Agent { AgentName = "Đại lý Thái Nguyên Electronic Supplies", Address = "68 Lương Ngọc Quyến, TP. Thái Nguyên", Phone = "02083855555" },
                new Agent { AgentName = "Đại lý Lâm Đồng - Đà Lạt HighTech", Address = "30 Phan Đình Phùng, Phường 2, TP. Đà Lạt", Phone = "02633827777" }
            };

            await context.Agent.AddRangeAsync(agents);
            await context.SaveChangesAsync();
        }

        // 3. Seed Users if empty
        if (!await context.Users.AnyAsync())
        {
            var users = new List<Users>
            {
                // Admin users
                new Users { UserName = "admin", email = "admin@b2bwholesale.vn", password = "admin123", @lock = false, Role = "Admin" },
                new Users { UserName = "admin_wh", email = "warehouse_lead@b2bwholesale.vn", password = "admin123", @lock = false, Role = "Admin" },
                new Users { UserName = "supervisor", email = "supervisor@b2bwholesale.vn", password = "admin123", @lock = false, Role = "Admin" },

                // Agent accounts mapped to Agents
                new Users { UserName = "agent_hanoi", email = "contact@phucanh.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 1 },
                new Users { UserName = "agent_saigon", email = "b2b@phongvu.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 2 },
                new Users { UserName = "agent_danang", email = "wholesale@philong.com.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 3 },
                new Users { UserName = "agent_cantho", email = "order@canthodigital.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 4 },
                new Users { UserName = "agent_binhduong", email = "kinhdoanh@binhduongtech.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 5 },
                new Users { UserName = "agent_haiphong", email = "sales@cencotech.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 6 },
                new Users { UserName = "agent_bienhoa", email = "order@bienhoatech.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 7 },
                new Users { UserName = "agent_daklak", email = "b2b@banmewholesale.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 8 },
                new Users { UserName = "agent_nhatrang", email = "sales@nhatrangtech.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 9 },
                new Users { UserName = "agent_vungtau", email = "vungtau.b2b@logistics.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 10 },
                new Users { UserName = "agent_quangninh", email = "campha@quangninhtech.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 11 },
                new Users { UserName = "agent_angiang", email = "angiang.digital@gmail.com", password = "agent123", @lock = false, Role = "Agent", AgentID = 12 },
                new Users { UserName = "agent_bacninh", email = "bacninh.warehouse@b2b.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 13 },
                new Users { UserName = "agent_hue", email = "hue.heritage@tech.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 14 },
                new Users { UserName = "agent_thainguyen", email = "thainguyen.b2b@supplier.vn", password = "agent123", @lock = false, Role = "Agent", AgentID = 15 },
                new Users { UserName = "agent_locked", email = "locked_agent@b2bwholesale.vn", password = "agent123", @lock = true, Role = "Agent", AgentID = 16 }
            };

            await context.Users.AddRangeAsync(users);
            await context.SaveChangesAsync();
        }

        // 4. Seed Orders if empty
        if (!await context.Order.AnyAsync())
        {
            var baseDate = DateTime.UtcNow.AddDays(-14);
            var orders = new List<Order>
            {
                new Order { OrderDate = baseDate.AddDays(1), AgentID = 1, OrderStatus = "Shipped" },
                new Order { OrderDate = baseDate.AddDays(2), AgentID = 2, OrderStatus = "Shipped" },
                new Order { OrderDate = baseDate.AddDays(3), AgentID = 3, OrderStatus = "Delivered" },
                new Order { OrderDate = baseDate.AddDays(4), AgentID = 4, OrderStatus = "Shipped" },
                new Order { OrderDate = baseDate.AddDays(5), AgentID = 5, OrderStatus = "Delivered" },
                new Order { OrderDate = baseDate.AddDays(6), AgentID = 1, OrderStatus = "Pending" },
                new Order { OrderDate = baseDate.AddDays(7), AgentID = 2, OrderStatus = "Pending" },
                new Order { OrderDate = baseDate.AddDays(8), AgentID = 6, OrderStatus = "Confirmed" },
                new Order { OrderDate = baseDate.AddDays(9), AgentID = 7, OrderStatus = "Shipped" },
                new Order { OrderDate = baseDate.AddDays(10), AgentID = 8, OrderStatus = "Pending" },
                new Order { OrderDate = baseDate.AddDays(11), AgentID = 9, OrderStatus = "Confirmed" },
                new Order { OrderDate = baseDate.AddDays(12), AgentID = 10, OrderStatus = "Pending" },
                new Order { OrderDate = baseDate.AddDays(13), AgentID = 3, OrderStatus = "Pending" },
                new Order { OrderDate = baseDate.AddDays(13).AddHours(4), AgentID = 5, OrderStatus = "Pending" },
                new Order { OrderDate = baseDate.AddDays(14), AgentID = 2, OrderStatus = "Pending" }
            };

            await context.Order.AddRangeAsync(orders);
            await context.SaveChangesAsync();
        }

        // 5. Seed OrderDetails if empty
        if (!await context.OrderDetail.AnyAsync())
        {
            var details = new List<OrderDetail>
            {
                // Order 1 (Agent 1)
                new OrderDetail { OrderID = 1, ItemID = 1, Quantity = 5, UnitAmount = 11500000m },
                new OrderDetail { OrderID = 1, ItemID = 2, Quantity = 10, UnitAmount = 3450000m },

                // Order 2 (Agent 2)
                new OrderDetail { OrderID = 2, ItemID = 3, Quantity = 15, UnitAmount = 2390000m },
                new OrderDetail { OrderID = 2, ItemID = 5, Quantity = 8, UnitAmount = 2850000m },

                // Order 3 (Agent 3)
                new OrderDetail { OrderID = 3, ItemID = 4, Quantity = 4, UnitAmount = 7490000m },
                new OrderDetail { OrderID = 3, ItemID = 12, Quantity = 20, UnitAmount = 1690000m },

                // Order 4 (Agent 4)
                new OrderDetail { OrderID = 4, ItemID = 6, Quantity = 6, UnitAmount = 4250000m },
                new OrderDetail { OrderID = 4, ItemID = 7, Quantity = 3, UnitAmount = 4190000m },

                // Order 5 (Agent 5)
                new OrderDetail { OrderID = 5, ItemID = 9, Quantity = 2, UnitAmount = 32500000m },
                new OrderDetail { OrderID = 5, ItemID = 10, Quantity = 5, UnitAmount = 8900000m },

                // Order 6 (Agent 1)
                new OrderDetail { OrderID = 6, ItemID = 11, Quantity = 10, UnitAmount = 4350000m },
                new OrderDetail { OrderID = 6, ItemID = 14, Quantity = 15, UnitAmount = 1450000m },

                // Order 7 (Agent 2)
                new OrderDetail { OrderID = 7, ItemID = 8, Quantity = 1, UnitAmount = 28900000m },
                new OrderDetail { OrderID = 7, ItemID = 18, Quantity = 4, UnitAmount = 6800000m },

                // Order 8 (Agent 6)
                new OrderDetail { OrderID = 8, ItemID = 13, Quantity = 25, UnitAmount = 650000m },
                new OrderDetail { OrderID = 8, ItemID = 17, Quantity = 40, UnitAmount = 890000m },

                // Order 9 (Agent 7)
                new OrderDetail { OrderID = 9, ItemID = 15, Quantity = 8, UnitAmount = 5890000m },
                new OrderDetail { OrderID = 9, ItemID = 16, Quantity = 12, UnitAmount = 4200000m },

                // Order 10 (Agent 8)
                new OrderDetail { OrderID = 10, ItemID = 1, Quantity = 3, UnitAmount = 11500000m },
                new OrderDetail { OrderID = 10, ItemID = 3, Quantity = 10, UnitAmount = 2390000m },

                // Order 11 (Agent 9)
                new OrderDetail { OrderID = 11, ItemID = 2, Quantity = 6, UnitAmount = 3450000m },
                new OrderDetail { OrderID = 11, ItemID = 5, Quantity = 10, UnitAmount = 2850000m },

                // Order 12 (Agent 10)
                new OrderDetail { OrderID = 12, ItemID = 6, Quantity = 4, UnitAmount = 4250000m },
                new OrderDetail { OrderID = 12, ItemID = 12, Quantity = 15, UnitAmount = 1690000m },

                // Order 13 (Agent 3)
                new OrderDetail { OrderID = 13, ItemID = 7, Quantity = 2, UnitAmount = 4190000m },
                new OrderDetail { OrderID = 13, ItemID = 10, Quantity = 3, UnitAmount = 8900000m },

                // Order 14 (Agent 5)
                new OrderDetail { OrderID = 14, ItemID = 4, Quantity = 5, UnitAmount = 7490000m },
                new OrderDetail { OrderID = 14, ItemID = 11, Quantity = 8, UnitAmount = 4350000m },

                // Order 15 (Agent 2)
                new OrderDetail { OrderID = 15, ItemID = 14, Quantity = 12, UnitAmount = 1450000m },
                new OrderDetail { OrderID = 15, ItemID = 16, Quantity = 6, UnitAmount = 4200000m }
            };

            await context.OrderDetail.AddRangeAsync(details);
            await context.SaveChangesAsync();
        }
    }
}
