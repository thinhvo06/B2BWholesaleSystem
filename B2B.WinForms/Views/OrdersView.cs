using B2B.WinForms.Common;
using B2B.WinForms.DataAccess;
using Microsoft.EntityFrameworkCore;

namespace B2B.WinForms.Views;

public sealed class OrdersView : UserControl
{
    private readonly Action<int> _openManifest;
    private readonly DataGridView _ordersGrid = UiTheme.Grid();
    private readonly DataGridView _detailsGrid = UiTheme.Grid();
    private readonly TextBox _search = UiTheme.TextBox("Tìm mã đơn, đại lý hoặc trạng thái...");
    private readonly Label _detailTitle = UiTheme.Label("CHI TIẾT ĐƠN HÀNG", 8.5f, true, UiTheme.Muted);
    private bool _loading;

    public OrdersView(Action<int> openManifest)
    {
        _openManifest = openManifest;
        BackColor = UiTheme.Background;
        BuildLayout();
        Load += async (_, _) => await ReloadOrdersAsync();
        _search.TextChanged += async (_, _) => await ReloadOrdersAsync();
        _ordersGrid.SelectionChanged += async (_, _) =>
        {
            if (!_loading) await LoadSelectedDetailsAsync();
        };
    }

    private void BuildLayout()
    {
        var root = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 1, RowCount = 2, BackColor = UiTheme.Background };
        root.RowStyles.Add(new RowStyle(SizeType.Absolute, 60));
        root.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        Controls.Add(root);

        var toolbar = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.LeftToRight, WrapContents = false, Padding = new Padding(0, 8, 0, 8) };
        _search.Width = 310;
        var refresh = UiTheme.Button("Làm mới");
        var shipped = UiTheme.Button("Chuyển sang Shipped", primary: true);
        var manifest = UiTheme.Button("In phiếu giao hàng");
        refresh.Click += async (_, _) => await ReloadOrdersAsync();
        shipped.Click += async (_, _) => await MarkAsShippedAsync();
        manifest.Click += (_, _) =>
        {
            int? id = SelectedOrderId();
            if (id.HasValue) _openManifest(id.Value);
        };
        toolbar.Controls.AddRange([_search, refresh, shipped, manifest]);
        root.Controls.Add(toolbar, 0, 0);

        var split = new SplitContainer
        {
            Dock = DockStyle.Fill,
            Orientation = Orientation.Horizontal,
            Size = new Size(1200, 680),
            SplitterDistance = 360,
            BackColor = UiTheme.Background,
            BorderStyle = BorderStyle.None,
            Panel1MinSize = 190,
            Panel2MinSize = 170
        };
        var orderPanel = new Panel { Dock = DockStyle.Fill, BackColor = UiTheme.Surface, Padding = new Padding(12) };
        var orderCaption = UiTheme.Label("DANH SÁCH ĐƠN HÀNG TỪ WEB PORTAL", 8.5f, true, UiTheme.Muted);
        orderCaption.Dock = DockStyle.Top;
        orderCaption.Height = 28;
        orderPanel.Controls.Add(_ordersGrid);
        orderPanel.Controls.Add(orderCaption);
        split.Panel1.Controls.Add(orderPanel);

        var detailsPanel = new Panel { Dock = DockStyle.Fill, BackColor = UiTheme.Surface, Padding = new Padding(12) };
        _detailTitle.Dock = DockStyle.Top;
        _detailTitle.Height = 28;
        detailsPanel.Controls.Add(_detailsGrid);
        detailsPanel.Controls.Add(_detailTitle);
        split.Panel2.Controls.Add(detailsPanel);
        root.Controls.Add(split, 0, 1);
    }

    private async Task ReloadOrdersAsync()
    {
        if (_loading) return;
        _loading = true;
        try
        {
            using var context = AppDatabase.CreateContext();
            string keyword = _search.Text.Trim();
            var query = context.Order.AsNoTracking().Include(o => o.Agent).AsQueryable();
            if (!string.IsNullOrWhiteSpace(keyword))
            {
                if (int.TryParse(keyword, out int orderId))
                    query = query.Where(o => o.OrderID == orderId || o.OrderStatus.Contains(keyword) || (o.Agent != null && o.Agent.AgentName.Contains(keyword)));
                else
                    query = query.Where(o => o.OrderStatus.Contains(keyword) || (o.Agent != null && o.Agent.AgentName.Contains(keyword)));
            }

            var rows = await query.OrderByDescending(o => o.OrderDate)
                .Select(o => new
                {
                    o.OrderID,
                    o.OrderDate,
                    o.AgentID,
                    AgentName = o.Agent != null ? o.Agent.AgentName : "(Đại lý không xác định)",
                    o.OrderStatus,
                    Total = o.OrderDetails.Sum(d => (decimal?)(d.UnitAmount * d.Quantity)) ?? 0m
                })
                .ToListAsync();

            _ordersGrid.DataSource = rows;
            SetHeader(_ordersGrid, "OrderID", "Mã đơn");
            SetHeader(_ordersGrid, "OrderDate", "Ngày đặt");
            SetHeader(_ordersGrid, "AgentID", "Mã đại lý");
            SetHeader(_ordersGrid, "AgentName", "Đại lý");
            SetHeader(_ordersGrid, "OrderStatus", "Trạng thái");
            SetHeader(_ordersGrid, "Total", "Tổng tiền (VND)");
            if (_ordersGrid.Columns.Contains("OrderDate")) _ordersGrid.Columns["OrderDate"].DefaultCellStyle.Format = "dd/MM/yyyy HH:mm";
            if (_ordersGrid.Columns.Contains("Total")) _ordersGrid.Columns["Total"].DefaultCellStyle.Format = "N0";

            if (_ordersGrid.Rows.Count > 0)
                await LoadSelectedDetailsAsync();
            else
                _detailsGrid.DataSource = null;
        }
        catch (Exception ex) { UiTheme.ShowError(FindForm()!, "Không tải được danh sách đơn hàng.\n" + ex.GetBaseException().Message); }
        finally { _loading = false; }
    }

    private async Task LoadSelectedDetailsAsync()
    {
        int? id = SelectedOrderId(showMessage: false);
        if (id is null) { _detailsGrid.DataSource = null; return; }
        try
        {
            using var context = AppDatabase.CreateContext();
            var details = await context.OrderDetail.AsNoTracking()
                .Where(d => d.OrderID == id.Value)
                .Include(d => d.Item)
                .Select(d => new
                {
                    d.ID,
                    d.ItemID,
                    ItemName = d.Item != null ? d.Item.ItemName : "(Sản phẩm đã xóa)",
                    Size = d.Item != null ? d.Item.Size : string.Empty,
                    d.Quantity,
                    d.UnitAmount,
                    LineTotal = d.Quantity * d.UnitAmount
                })
                .ToListAsync();
            _detailsGrid.DataSource = details;
            SetHeader(_detailsGrid, "ID", "Mã dòng");
            SetHeader(_detailsGrid, "ItemID", "Mã hàng");
            SetHeader(_detailsGrid, "ItemName", "Sản phẩm");
            SetHeader(_detailsGrid, "Size", "Kích cỡ");
            SetHeader(_detailsGrid, "Quantity", "Số lượng");
            SetHeader(_detailsGrid, "UnitAmount", "Đơn giá");
            SetHeader(_detailsGrid, "LineTotal", "Thành tiền");
            if (_detailsGrid.Columns.Contains("UnitAmount")) _detailsGrid.Columns["UnitAmount"].DefaultCellStyle.Format = "N0";
            if (_detailsGrid.Columns.Contains("LineTotal")) _detailsGrid.Columns["LineTotal"].DefaultCellStyle.Format = "N0";
            _detailTitle.Text = $"CHI TIẾT ĐƠN HÀNG #{id.Value}";
        }
        catch (Exception ex) { UiTheme.ShowError(FindForm()!, "Không tải được chi tiết đơn hàng.\n" + ex.GetBaseException().Message); }
    }

    private async Task MarkAsShippedAsync()
    {
        int? id = SelectedOrderId();
        if (id is null) return;
        try
        {
            using var context = AppDatabase.CreateContext();
            var order = await context.Order.FindAsync(id.Value);
            if (order is null) { UiTheme.ShowInfo(FindForm()!, "Đơn hàng không còn tồn tại."); return; }
            if (!string.Equals(order.OrderStatus, "Pending", StringComparison.OrdinalIgnoreCase) &&
                !string.Equals(order.OrderStatus, "Confirmed", StringComparison.OrdinalIgnoreCase))
            {
                UiTheme.ShowInfo(FindForm()!, $"Chỉ đơn Pending hoặc Confirmed mới được chuyển sang Shipped. Trạng thái hiện tại: {order.OrderStatus}.");
                return;
            }

            if (MessageBox.Show(FindForm(), $"Xác nhận chuyển đơn hàng #{order.OrderID} sang Shipped?\n\nLưu ý: tồn kho đã được trừ khi Agent đặt hàng trên Web, thao tác này không trừ kho lần nữa.",
                "Xác nhận giao hàng", MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes) return;

            order.OrderStatus = "Shipped";
            await context.SaveChangesAsync();
            UiTheme.ShowInfo(FindForm()!, $"Đơn hàng #{order.OrderID} đã được cập nhật sang Shipped.");
            await ReloadOrdersAsync();
        }
        catch (Exception ex) { UiTheme.ShowError(FindForm()!, "Không thể cập nhật trạng thái đơn hàng.\n" + ex.GetBaseException().Message); }
    }

    private int? SelectedOrderId(bool showMessage = true)
    {
        if (_ordersGrid.CurrentRow?.Cells["OrderID"].Value is int id) return id;
        if (showMessage) UiTheme.ShowInfo(FindForm()!, "Vui lòng chọn một đơn hàng trước.");
        return null;
    }

    private static void SetHeader(DataGridView grid, string key, string title)
    {
        if (grid.Columns.Contains(key)) grid.Columns[key].HeaderText = title;
    }
}
