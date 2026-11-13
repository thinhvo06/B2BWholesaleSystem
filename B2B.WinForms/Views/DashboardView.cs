using B2B.WinForms.Common;
using B2B.WinForms.DataAccess;
using Microsoft.EntityFrameworkCore;

namespace B2B.WinForms.Views;

public sealed class DashboardView : UserControl
{
    private readonly DateTimePicker _from = new() { Format = DateTimePickerFormat.Short, Width = 130 };
    private readonly DateTimePicker _to = new() { Format = DateTimePickerFormat.Short, Width = 130 };
    private readonly Label _ordersValue = MetricValue();
    private readonly Label _revenueValue = MetricValue();
    private readonly Label _pendingValue = MetricValue();
    private readonly DataGridView _bestGrid = UiTheme.Grid();
    private readonly DataGridView _lowGrid = UiTheme.Grid();
    private readonly DataGridView _agentGrid = UiTheme.Grid();

    public DashboardView()
    {
        BackColor = UiTheme.Background;
        _from.Value = DateTime.Today.AddDays(-30);
        _to.Value = DateTime.Today;
        BuildLayout();
        Load += async (_, _) => await ReloadAsync();
    }

    private void BuildLayout()
    {
        var root = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 1, RowCount = 3, BackColor = UiTheme.Background };
        root.RowStyles.Add(new RowStyle(SizeType.Absolute, 58));
        root.RowStyles.Add(new RowStyle(SizeType.Absolute, 100));
        root.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        Controls.Add(root);

        var filter = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.LeftToRight, WrapContents = false, Padding = new Padding(0, 8, 0, 8) };
        filter.Controls.Add(UiTheme.Label("Từ ngày", 9, true));
        filter.Controls.Add(_from);
        filter.Controls.Add(UiTheme.Label("Đến ngày", 9, true));
        filter.Controls.Add(_to);
        var apply = UiTheme.Button("Áp dụng bộ lọc", primary: true);
        apply.Click += async (_, _) => await ReloadAsync();
        filter.Controls.Add(apply);
        root.Controls.Add(filter, 0, 0);

        var metrics = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 3, RowCount = 1, Padding = new Padding(0, 2, 0, 12) };
        metrics.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 33.33f));
        metrics.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 33.33f));
        metrics.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 33.34f));
        metrics.Controls.Add(MetricCard("ĐƠN HÀNG TRONG KỲ", _ordersValue, UiTheme.Blue), 0, 0);
        metrics.Controls.Add(MetricCard("DOANH THU ƯỚC TÍNH", _revenueValue, UiTheme.Success), 1, 0);
        metrics.Controls.Add(MetricCard("ĐƠN ĐANG CHỜ", _pendingValue, UiTheme.Warning), 2, 0);
        root.Controls.Add(metrics, 0, 1);

        var analytics = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 3, RowCount = 1 };
        analytics.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 36));
        analytics.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 30));
        analytics.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 34));
        analytics.Controls.Add(GridCard("TOP SẢN PHẨM BÁN CHẠY", _bestGrid), 0, 0);
        analytics.Controls.Add(GridCard("CẢNH BÁO TỒN KHO (DƯỚI 10)", _lowGrid), 1, 0);
        analytics.Controls.Add(GridCard("DOANH THU THEO ĐẠI LÝ", _agentGrid), 2, 0);
        root.Controls.Add(analytics, 0, 2);
    }

    private static Label MetricValue() => new()
    {
        Text = "—",
        AutoSize = true,
        Font = UiTheme.BodyFont(22, FontStyle.Bold),
        ForeColor = UiTheme.Navy,
        Location = new Point(18, 37)
    };

    private static Control MetricCard(string titleText, Label value, Color accent)
    {
        var panel = new Panel { Dock = DockStyle.Fill, BackColor = UiTheme.Surface, Margin = new Padding(0, 0, 12, 0), Padding = new Padding(18) };
        var stripe = new Panel { Dock = DockStyle.Left, Width = 5, BackColor = accent };
        var title = UiTheme.Label(titleText, 8.2f, true, UiTheme.Muted);
        title.Location = new Point(20, 14);
        value.Location = new Point(20, 38);
        panel.Controls.Add(title);
        panel.Controls.Add(value);
        panel.Controls.Add(stripe);
        return panel;
    }

    private static Control GridCard(string titleText, DataGridView grid)
    {
        var panel = new Panel { Dock = DockStyle.Fill, BackColor = UiTheme.Surface, Padding = new Padding(12), Margin = new Padding(0, 0, 12, 0) };
        var title = UiTheme.Label(titleText, 8.2f, true, UiTheme.Muted);
        title.Dock = DockStyle.Top;
        title.Height = 32;
        panel.Controls.Add(grid);
        panel.Controls.Add(title);
        return panel;
    }

    private async Task ReloadAsync()
    {
        if (_to.Value.Date < _from.Value.Date)
        {
            UiTheme.ShowError(FindForm()!, "Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.");
            return;
        }

        try
        {
            using var context = AppDatabase.CreateContext();
            DateTime from = _from.Value.Date;
            DateTime toExclusive = _to.Value.Date.AddDays(1);

            var orders = await context.Order.AsNoTracking()
                .Include(o => o.Agent)
                .Include(o => o.OrderDetails).ThenInclude(d => d.Item)
                .Where(o => o.OrderDate >= from && o.OrderDate < toExclusive)
                .ToListAsync();

            var activeOrders = orders.Where(o => !string.Equals(o.OrderStatus, "Cancelled", StringComparison.OrdinalIgnoreCase)).ToList();
            decimal revenue = activeOrders.SelectMany(o => o.OrderDetails)
                .Sum(d => d.UnitAmount * d.Quantity);

            _ordersValue.Text = orders.Count.ToString("N0");
            _revenueValue.Text = revenue.ToString("N0") + " đ";
            _pendingValue.Text = orders.Count(o => string.Equals(o.OrderStatus, "Pending", StringComparison.OrdinalIgnoreCase)).ToString("N0");

            var bestSelling = activeOrders.SelectMany(o => o.OrderDetails)
                .Where(d => d.Item is not null)
                .GroupBy(d => new { d.ItemID, d.Item!.ItemName, d.Item.Size })
                .Select(g => new { g.Key.ItemID, g.Key.ItemName, g.Key.Size, QuantitySold = g.Sum(d => d.Quantity), Revenue = g.Sum(d => d.Quantity * d.UnitAmount) })
                .OrderByDescending(x => x.QuantitySold)
                .Take(10)
                .ToList();
            _bestGrid.DataSource = bestSelling;
            SetHeader(_bestGrid, "ItemID", "Mã hàng");
            SetHeader(_bestGrid, "ItemName", "Sản phẩm");
            SetHeader(_bestGrid, "Size", "Kích cỡ");
            SetHeader(_bestGrid, "QuantitySold", "Đã bán");
            SetHeader(_bestGrid, "Revenue", "Doanh thu");
            FormatMoney(_bestGrid, "Revenue");

            var lowStock = await context.Item.AsNoTracking()
                .Where(i => i.StockQuantity < 10)
                .OrderBy(i => i.StockQuantity)
                .Select(i => new { i.ItemID, i.ItemName, i.Size, i.StockQuantity })
                .ToListAsync();
            _lowGrid.DataSource = lowStock;
            SetHeader(_lowGrid, "ItemID", "Mã hàng");
            SetHeader(_lowGrid, "ItemName", "Sản phẩm");
            SetHeader(_lowGrid, "Size", "Kích cỡ");
            SetHeader(_lowGrid, "StockQuantity", "Tồn kho");
            foreach (DataGridViewRow row in _lowGrid.Rows)
            {
                row.DefaultCellStyle.BackColor = Color.FromArgb(255, 235, 237);
                row.DefaultCellStyle.ForeColor = UiTheme.Danger;
            }

            var revenueByAgent = activeOrders
                .GroupBy(o => o.Agent?.AgentName ?? $"Agent #{o.AgentID}")
                .Select(g => new { AgentName = g.Key, OrderCount = g.Count(), Revenue = g.SelectMany(o => o.OrderDetails).Sum(d => d.Quantity * d.UnitAmount) })
                .OrderByDescending(x => x.Revenue)
                .ToList();
            _agentGrid.DataSource = revenueByAgent;
            SetHeader(_agentGrid, "AgentName", "Đại lý");
            SetHeader(_agentGrid, "OrderCount", "Số đơn");
            SetHeader(_agentGrid, "Revenue", "Doanh thu");
            FormatMoney(_agentGrid, "Revenue");
        }
        catch (Exception ex)
        {
            UiTheme.ShowError(FindForm()!, "Không tải được dữ liệu Dashboard.\n" + ex.GetBaseException().Message);
        }
    }

    private static void SetHeader(DataGridView grid, string key, string title)
    {
        if (grid.Columns.Contains(key)) grid.Columns[key].HeaderText = title;
    }

    private static void FormatMoney(DataGridView grid, string key)
    {
        if (grid.Columns.Contains(key)) grid.Columns[key].DefaultCellStyle.Format = "N0";
    }
}
