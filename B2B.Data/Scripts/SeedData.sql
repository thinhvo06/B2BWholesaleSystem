/*
    B2BWholesaleDB - SAFE SETUP SCRIPT
    - Creates the database if it does not exist.
    - Creates only tables that are missing.
    - Seeds a table only when that table is empty.
    - Does NOT DROP tables or delete existing records.

    IMPORTANT:
    Run this script in SQL Server Management Studio (SSMS).
    Connect to: DESKTOP-BPGJP96\SQLEXPRESS (on your computer).
*/

IF DB_ID(N'B2BWholesaleDB') IS NULL
BEGIN
    CREATE DATABASE [B2BWholesaleDB];
END;
GO

USE [B2BWholesaleDB];
GO

/* 1. Item */
IF OBJECT_ID(N'dbo.Item', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Item
    (
        ItemID INT IDENTITY(1,1) NOT NULL,
        ItemName NVARCHAR(200) NOT NULL,
        Size NVARCHAR(50) NULL,
        Price DECIMAL(18,2) NOT NULL,
        StockQuantity INT NOT NULL,
        CONSTRAINT PK_Item PRIMARY KEY CLUSTERED (ItemID)
    );
END;
GO

/* 2. Agent */
IF OBJECT_ID(N'dbo.Agent', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Agent
    (
        AgentID INT IDENTITY(1,1) NOT NULL,
        AgentName NVARCHAR(200) NOT NULL,
        Address NVARCHAR(300) NULL,
        Phone NVARCHAR(50) NULL,
        CONSTRAINT PK_Agent PRIMARY KEY CLUSTERED (AgentID)
    );
END;
GO

/* 3. Users */
IF OBJECT_ID(N'dbo.Users', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Users
    (
        UserID INT IDENTITY(1,1) NOT NULL,
        UserName NVARCHAR(100) NOT NULL,
        email NVARCHAR(150) NOT NULL,
        password NVARCHAR(255) NOT NULL,
        [lock] BIT NOT NULL CONSTRAINT DF_Users_lock DEFAULT (0),
        Role NVARCHAR(50) NOT NULL,
        AgentID INT NULL,
        CONSTRAINT PK_Users PRIMARY KEY CLUSTERED (UserID),
        CONSTRAINT UQ_Users_UserName UNIQUE (UserName),
        CONSTRAINT UQ_Users_Email UNIQUE (email),
        CONSTRAINT FK_Users_Agent FOREIGN KEY (AgentID)
            REFERENCES dbo.Agent (AgentID) ON DELETE SET NULL
    );
END;
GO

/* 4. Order
   SQL Server uses NO ACTION (not RESTRICT) for restrictive foreign keys.
   Order is a keyword-like identifier, so always write [Order] in SQL. */
IF OBJECT_ID(N'dbo.Order', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.[Order]
    (
        OrderID INT IDENTITY(1,1) NOT NULL,
        OrderDate DATETIME2 NOT NULL CONSTRAINT DF_Order_OrderDate DEFAULT (SYSUTCDATETIME()),
        AgentID INT NOT NULL,
        OrderStatus NVARCHAR(50) NOT NULL CONSTRAINT DF_Order_OrderStatus DEFAULT (N'Pending'),
        CONSTRAINT PK_Order PRIMARY KEY CLUSTERED (OrderID),
        CONSTRAINT FK_Order_Agent FOREIGN KEY (AgentID)
            REFERENCES dbo.Agent (AgentID) ON DELETE NO ACTION
    );
END;
GO

/* 5. OrderDetail */
IF OBJECT_ID(N'dbo.OrderDetail', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.OrderDetail
    (
        ID INT IDENTITY(1,1) NOT NULL,
        OrderID INT NOT NULL,
        ItemID INT NOT NULL,
        Quantity INT NOT NULL,
        UnitAmount DECIMAL(18,2) NOT NULL,
        CONSTRAINT PK_OrderDetail PRIMARY KEY CLUSTERED (ID),
        CONSTRAINT FK_OrderDetail_Order FOREIGN KEY (OrderID)
            REFERENCES dbo.[Order] (OrderID) ON DELETE CASCADE,
        CONSTRAINT FK_OrderDetail_Item FOREIGN KEY (ItemID)
            REFERENCES dbo.Item (ItemID) ON DELETE NO ACTION
    );
END;
GO

/* SEED DATA
   Insert only if the corresponding table is empty.
   This prevents duplicate seed rows when you run the script again.
*/

/* 6. Seed Item (18 rows) */
IF NOT EXISTS (SELECT 1 FROM dbo.Item)
BEGIN
    SET IDENTITY_INSERT dbo.Item ON;
    INSERT INTO dbo.Item (ItemID, ItemName, Size, Price, StockQuantity) VALUES
    (1, N'Màn hình Dell UltraSharp 27 inch 4K', N'27 inch', 11500000.00, 85),
    (2, N'Bàn phím cơ không dây Logitech MX Mechanical', N'Fullsize', 3450000.00, 120),
    (3, N'Chuột công thái học Logitech MX Master 3S', N'Medium', 2390000.00, 150),
    (4, N'Tai nghe chống ồn Sony WH-1000XM5', N'Over-ear', 7490000.00, 60),
    (5, N'Ổ cứng di động SSD Samsung T7 Shield 1TB', N'1TB', 2850000.00, 200),
    (6, N'Bộ phát Wifi 6 Mesh TP-Link Deco X50 (Bộ 3)', N'Pack 3', 4250000.00, 45),
    (7, N'Máy in đa năng laser Brother DCP-L2520D', N'Standard', 4190000.00, 35),
    (8, N'Máy chiếu thông minh 4K BenQ TK700STi', N'Large', 28900000.00, 15),
    (9, N'Ghế công thái học Herman Miller Aeron', N'Size B', 32500000.00, 20),
    (10, N'Bàn làm việc nâng hạ Ergonomic SmartDesk Pro', N'160x80cm', 8900000.00, 40),
    (11, N'Webcam hội nghị trực tuyến Logitech Brio 4K', N'Compact', 4350000.00, 90),
    (12, N'Bộ sạc đa cổng Anker Prime 100W GaN', N'Small', 1690000.00, 250),
    (13, N'Đế làm mát Laptop nhôm nguyên khối HyperStand', N'15-17 inch', 650000.00, 180),
    (14, N'Cáp Thunderbolt 4 Belkin Pro 2m', N'2m', 1450000.00, 110),
    (15, N'Loa hội nghị Bluetooth Jabra Speak 710', N'Portable', 5890000.00, 50),
    (16, N'Pin sạc dự phòng Shargeek Storm 2 25600mAh', N'25600mAh', 4200000.00, 75),
    (17, N'Thẻ nhớ SanDisk Extreme Pro 256GB MicroSD', N'256GB', 890000.00, 300),
    (18, N'Bộ lưu điện UPS APC Back-UPS Pro 1500VA', N'1500VA', 6800000.00, 25);
    SET IDENTITY_INSERT dbo.Item OFF;
END;
GO

/* 7. Seed Agent (16 rows) */
IF NOT EXISTS (SELECT 1 FROM dbo.Agent)
BEGIN
    SET IDENTITY_INSERT dbo.Agent ON;
    INSERT INTO dbo.Agent (AgentID, AgentName, Address, Phone) VALUES
    (1, N'Đại lý Bán buôn Miền Bắc - Phúc Anh Tech', N'Số 15 Xã Đàn, Đống Đa, Hà Nội', N'02438572222'),
    (2, N'Đại lý Bán buôn Miền Nam - Phong Vũ Mega', N'264 Nguyễn Thị Minh Khai, Q.3, TP.HCM', N'02873086666'),
    (3, N'Tổng kho Thiết bị Miền Trung - Phi Long Plaza', N'52 Nguyễn Văn Linh, Hải Châu, Đà Nẵng', N'02363888000'),
    (4, N'Nhà phân phối Tây Nam Bộ - Cần Thơ Digital', N'84 Mậu Thân, Ninh Kiều, Cần Thơ', N'02923768888'),
    (5, N'Đại lý Khu Công nghiệp - Bình Dương Solution', N'Đại lộ Bình Dương, TP. Thủ Dầu Một', N'02743828999'),
    (6, N'Trung tâm Thiết bị Hải Phòng - Cenco Tech', N'120 Lạch Tray, Ngô Quyền, Hải Phòng', N'02253846666'),
    (7, N'Đại lý Bán lẻ & Bán buôn Biên Hòa Tech', N'38 Đồng Khởi, Tân Hiệp, Biên Hòa, Đồng Nai', N'02513898888'),
    (8, N'Tổng kho Tây Nguyên - Ban Mê Wholesale', N'79 Lê Duẩn, TP. Buôn Ma Thuột, Đắk Lắk', N'02623812345'),
    (9, N'Công ty TNHH Thiết bị Số Nha Trang', N'24 Quang Trung, Vạn Thạnh, Nha Trang', N'02583824444'),
    (10, N'Đại lý Vũng Tàu Logistics & Trade', N'184 Ba Cu, Phường 3, TP. Vũng Tàu', N'02543859999'),
    (11, N'Đại lý Công nghệ Quảng Ninh - Cẩm Phả Tech', N'25 Trần Phú, Cẩm Phả, Quảng Ninh', N'02033862222'),
    (12, N'Đại lý Phân phối An Giang - Long Xuyên Store', N'45 Thoại Ngọc Hầu, Long Xuyên, An Giang', N'02963841111'),
    (13, N'Đại lý Bắc Ninh Kho Vận & Phụ kiện', N'11 Lý Thái Tổ, Suối Hoa, TP. Bắc Ninh', N'02223838888'),
    (14, N'Nhà cung ứng Bán buôn Huế Heritage Tech', N'86 Hùng Vương, Phú Nhuận, TP. Huế', N'02343899777'),
    (15, N'Đại lý Thái Nguyên Electronic Supplies', N'68 Lương Ngọc Quyến, TP. Thái Nguyên', N'02083855555'),
    (16, N'Đại lý Lâm Đồng - Đà Lạt HighTech', N'30 Phan Đình Phùng, Phường 2, TP. Đà Lạt', N'02633827777');
    SET IDENTITY_INSERT dbo.Agent OFF;
END;
GO

/* 8. Seed Users (16 rows) */
IF NOT EXISTS (SELECT 1 FROM dbo.Users)
BEGIN
    SET IDENTITY_INSERT dbo.Users ON;
    INSERT INTO dbo.Users (UserID, UserName, email, password, [lock], Role, AgentID) VALUES
    (1, N'admin', N'admin@b2bwholesale.vn', N'admin123', 0, N'Admin', NULL),
    (2, N'admin_wh', N'warehouse_lead@b2bwholesale.vn', N'admin123', 0, N'Admin', NULL),
    (3, N'supervisor', N'supervisor@b2bwholesale.vn', N'admin123', 0, N'Admin', NULL),
    (4, N'agent_hanoi', N'contact@phucanh.vn', N'agent123', 0, N'Agent', 1),
    (5, N'agent_saigon', N'b2b@phongvu.vn', N'agent123', 0, N'Agent', 2),
    (6, N'agent_danang', N'wholesale@philong.com.vn', N'agent123', 0, N'Agent', 3),
    (7, N'agent_cantho', N'order@canthodigital.vn', N'agent123', 0, N'Agent', 4),
    (8, N'agent_binhduong', N'kinhdoanh@binhduongtech.vn', N'agent123', 0, N'Agent', 5),
    (9, N'agent_haiphong', N'sales@cencotech.vn', N'agent123', 0, N'Agent', 6),
    (10, N'agent_bienhoa', N'order@bienhoatech.vn', N'agent123', 0, N'Agent', 7),
    (11, N'agent_daklak', N'b2b@banmewholesale.vn', N'agent123', 0, N'Agent', 8),
    (12, N'agent_nhatrang', N'sales@nhatrangtech.vn', N'agent123', 0, N'Agent', 9),
    (13, N'agent_vungtau', N'vungtau.b2b@logistics.vn', N'agent123', 0, N'Agent', 10),
    (14, N'agent_quangninh', N'campha@quangninhtech.vn', N'agent123', 0, N'Agent', 11),
    (15, N'agent_angiang', N'angiang.digital@gmail.com', N'agent123', 0, N'Agent', 12),
    (16, N'agent_locked', N'locked_agent@b2bwholesale.vn', N'agent123', 1, N'Agent', 13);
    SET IDENTITY_INSERT dbo.Users OFF;
END;
GO

/* 9. Seed Order (15 rows) */
IF NOT EXISTS (SELECT 1 FROM dbo.[Order])
BEGIN
    SET IDENTITY_INSERT dbo.[Order] ON;
    INSERT INTO dbo.[Order] (OrderID, OrderDate, AgentID, OrderStatus) VALUES
    (1, DATEADD(DAY, -14, GETUTCDATE()), 1, N'Shipped'),
    (2, DATEADD(DAY, -12, GETUTCDATE()), 2, N'Shipped'),
    (3, DATEADD(DAY, -11, GETUTCDATE()), 3, N'Delivered'),
    (4, DATEADD(DAY, -10, GETUTCDATE()), 4, N'Shipped'),
    (5, DATEADD(DAY, -9, GETUTCDATE()), 5, N'Delivered'),
    (6, DATEADD(DAY, -7, GETUTCDATE()), 1, N'Pending'),
    (7, DATEADD(DAY, -6, GETUTCDATE()), 2, N'Pending'),
    (8, DATEADD(DAY, -5, GETUTCDATE()), 6, N'Confirmed'),
    (9, DATEADD(DAY, -4, GETUTCDATE()), 7, N'Shipped'),
    (10, DATEADD(DAY, -3, GETUTCDATE()), 8, N'Pending'),
    (11, DATEADD(DAY, -2, GETUTCDATE()), 9, N'Confirmed'),
    (12, DATEADD(DAY, -2, GETUTCDATE()), 10, N'Pending'),
    (13, DATEADD(DAY, -1, GETUTCDATE()), 3, N'Pending'),
    (14, DATEADD(HOUR, -6, GETUTCDATE()), 5, N'Pending'),
    (15, GETUTCDATE(), 2, N'Pending');
    SET IDENTITY_INSERT dbo.[Order] OFF;
END;
GO

/* 10. Seed OrderDetail (25 rows) */
IF NOT EXISTS (SELECT 1 FROM dbo.OrderDetail)
BEGIN
    SET IDENTITY_INSERT dbo.OrderDetail ON;
    INSERT INTO dbo.OrderDetail (ID, OrderID, ItemID, Quantity, UnitAmount) VALUES
    (1, 1, 1, 5, 11500000.00),
    (2, 1, 2, 10, 3450000.00),
    (3, 2, 3, 15, 2390000.00),
    (4, 2, 5, 8, 2850000.00),
    (5, 3, 4, 4, 7490000.00),
    (6, 3, 12, 20, 1690000.00),
    (7, 4, 6, 6, 4250000.00),
    (8, 4, 7, 3, 4190000.00),
    (9, 5, 9, 2, 32500000.00),
    (10, 5, 10, 5, 8900000.00),
    (11, 6, 11, 10, 4350000.00),
    (12, 6, 14, 15, 1450000.00),
    (13, 7, 8, 1, 28900000.00),
    (14, 7, 18, 4, 6800000.00),
    (15, 8, 13, 25, 650000.00),
    (16, 8, 17, 40, 890000.00),
    (17, 9, 15, 8, 5890000.00),
    (18, 9, 16, 12, 4200000.00),
    (19, 10, 1, 3, 11500000.00),
    (20, 10, 3, 10, 2390000.00),
    (21, 11, 2, 6, 3450000.00),
    (22, 11, 5, 10, 2850000.00),
    (23, 12, 6, 4, 4250000.00),
    (24, 13, 7, 2, 4190000.00),
    (25, 14, 4, 5, 7490000.00);
    SET IDENTITY_INSERT dbo.OrderDetail OFF;
END;
GO

/* 11. Verify required tables and sample row counts */
IF OBJECT_ID(N'dbo.Item', N'U') IS NULL
   OR OBJECT_ID(N'dbo.Agent', N'U') IS NULL
   OR OBJECT_ID(N'dbo.Users', N'U') IS NULL
   OR OBJECT_ID(N'dbo.Order', N'U') IS NULL
   OR OBJECT_ID(N'dbo.OrderDetail', N'U') IS NULL
BEGIN
    ;THROW 50001, N'B2BWholesaleDB setup is incomplete: one or more required tables are missing.', 1;
END;

SELECT N'Agent' AS TableName, COUNT_BIG(*) AS TotalRows FROM dbo.Agent
UNION ALL
SELECT N'Item', COUNT_BIG(*) FROM dbo.Item
UNION ALL
SELECT N'Order', COUNT_BIG(*) FROM dbo.[Order]
UNION ALL
SELECT N'OrderDetail', COUNT_BIG(*) FROM dbo.OrderDetail
UNION ALL
SELECT N'Users', COUNT_BIG(*) FROM dbo.Users
ORDER BY TableName;

PRINT N'B2BWholesaleDB setup completed. Existing tables and records were not dropped.';
GO
