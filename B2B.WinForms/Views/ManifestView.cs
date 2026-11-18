using System.Drawing.Printing;
using B2B.Data.Entities;
using B2B.WinForms.Common;
using B2B.WinForms.DataAccess;
using Microsoft.EntityFrameworkCore;

namespace B2B.WinForms.Views;

public sealed class ManifestView : UserControl
{
    private sealed class ManifestOrderOption
    {
        public int OrderId { get; init; }
        public string DisplayText { get; init; } = string.Empty;
        public override string ToString() => DisplayText;
    }

    private readonly ComboBox _orderPicker = new() { DropDownStyle = ComboBoxStyle.DropDownList, Width = 360, Font = UiTheme.BodyFont(9.2f) };
    private readonly Button _previewButton = UiTheme.Button("Xem trước khi in", primary: true);
    private readonly Button _printButton = UiTheme.Button("In / Lưu PDF");
    private readonly Label _agentValue = UiTheme.Label("Chưa chọn đơn hàng", 10, true, UiTheme.Navy);
    private readonly Label _addressValue = UiTheme.Label("", 9, false, UiTheme.Muted);
    private readonly Label _orderValue = UiTheme.Label("", 9, false, UiTheme.Muted);
    private readonly DataGridView _grid = UiTheme.Grid();
    private readonly PrintDocument _printDocument = new();
    private Order? _currentOrder;
    private int _printRowIndex;
    private bool _loadingPicker;

    public ManifestView(int? initialOrderId = null)
    {
        BackColor = UiTheme.Background;
        BuildLayout();
        _printDocument.DocumentName = "Shipping Manifest";
        _printDocument.DefaultPageSettings.Landscape = false;
        _printDocument.DefaultPageSettings.PaperSize = new PaperSize("A4", 827, 1169);
        _printDocument.DefaultPageSettings.Margins = new Margins(45, 45, 45, 45);
        _printDocument.PrintPage += PrintDocument_PrintPage;
        _previewButton.Click += (_, _) => PreviewManifest();
        _printButton.Click += (_, _) => PrintManifest();
        _orderPicker.SelectedIndexChanged += async (_, _) =>
        {
            if (!_loadingPicker) await LoadSelectedOrderAsync();
        };
        Load += async (_, _) => await LoadOrdersAsync(initialOrderId);
    }

    private void BuildLayout()
    {
        var root = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 1, RowCount = 2, BackColor = UiTheme.Background };
        root.RowStyles.Add(new RowStyle(SizeType.Absolute, 62));
        root.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        Controls.Add(root);

        var toolbar = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.LeftToRight, WrapContents = false, Padding = new Padding(0, 8, 0, 8) };
        toolbar.Controls.Add(UiTheme.Label("Chọn đơn hàng", 9, true));
        toolbar.Controls.Add(_orderPicker);
        toolbar.Controls.Add(_previewButton);
        toolbar.Controls.Add(_printButton);
        root.Controls.Add(toolbar, 0, 0);

        var body = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 1, RowCount = 2, BackColor = UiTheme.Background };
        body.RowStyles.Add(new RowStyle(SizeType.Absolute, 125));
        body.RowStyles.Add(new RowStyle(SizeType.Percent, 100));

        var summary = new Panel { Dock = DockStyle.Fill, BackColor = UiTheme.Surface, Padding = new Padding(18), Margin = new Padding(0, 0, 0, 12) };
        var heading = UiTheme.Label("SHIPPING MANIFEST  /  PHIẾU XUẤT KHO GIAO HÀNG", 10, true, UiTheme.Blue);
        heading.Location = new Point(18, 14);
        _agentValue.Location = new Point(18, 43);
        _addressValue.Location = new Point(18, 70);
        _orderValue.Location = new Point(18, 94);
        summary.Controls.AddRange([heading, _agentValue, _addressValue, _orderValue]);
        body.Controls.Add(summary, 0, 0);

        var gridCard = new Panel { Dock = DockStyle.Fill, BackColor = UiTheme.Surface, Padding = new Padding(12) };
        var caption = UiTheme.Label("DANH SÁCH SẢN PHẨM CẦN GIAO", 8.5f, true, UiTheme.Muted);
        caption.Dock = DockStyle.Top;
        caption.Height = 28;
        gridCard.Controls.Add(_grid);
        gridCard.Controls.Add(caption);
        body.Controls.Add(gridCard, 0, 1);
        root.Controls.Add(body, 0, 1);

        _previewButton.Enabled = false;
        _printButton.Enabled = false;
    }

    private async Task LoadOrdersAsync(int? initialOrderId)
    {
        try
        {
            using var context = AppDatabase.CreateContext();
            var orderRows = await context.Order.AsNoTracking()
                .Include(o => o.Agent)
                .OrderByDescending(o => o.OrderDate)
                .Select(o => new
                {
                    o.OrderID,
                    OrderDate = o.OrderDate,
                    AgentName = o.Agent != null ? o.Agent.AgentName : "Đại lý",
                    o.OrderStatus
                })
                .ToListAsync();
            var options = orderRows.Select(o => new ManifestOrderOption
            {
                OrderId = o.OrderID,
                DisplayText = $"#{o.OrderID}  |  {o.AgentName}  |  {o.OrderDate:dd/MM/yyyy}  |  {o.OrderStatus}"
            }).ToList();

            _loadingPicker = true;
            _orderPicker.DataSource = options;
            if (options.Count > 0)
            {
                int targetIndex = initialOrderId.HasValue ? options.FindIndex(x => x.OrderId == initialOrderId.Value) : 0;
                _orderPicker.SelectedIndex = targetIndex >= 0 ? targetIndex : 0;
            }
            _loadingPicker = false;
            await LoadSelectedOrderAsync();
        }
        catch (Exception ex)
        {
            _loadingPicker = false;
            UiTheme.ShowError(FindForm()!, "Không tải được danh sách đơn hàng để in phiếu.\n" + ex.GetBaseException().Message);
        }
    }

    private async Task LoadSelectedOrderAsync()
    {
        if (_orderPicker.SelectedItem is not ManifestOrderOption option)
        {
            _currentOrder = null;
            _grid.DataSource = null;
            _previewButton.Enabled = false;
            _printButton.Enabled = false;
            return;
        }

        try
        {
            using var context = AppDatabase.CreateContext();
            _currentOrder = await context.Order.AsNoTracking()
                .Include(o => o.Agent)
                .Include(o => o.OrderDetails).ThenInclude(d => d.Item)
                .FirstOrDefaultAsync(o => o.OrderID == option.OrderId);

            if (_currentOrder is null)
            {
                _grid.DataSource = null;
                _previewButton.Enabled = false;
                _printButton.Enabled = false;
                return;
            }

            _agentValue.Text = _currentOrder.Agent?.AgentName ?? "Đại lý không xác định";
            _addressValue.Text = "Địa chỉ: " + (_currentOrder.Agent?.Address ?? "Chưa cập nhật") +
                                 "     |     Điện thoại: " + (_currentOrder.Agent?.Phone ?? "Chưa cập nhật");
            _orderValue.Text = $"Mã đơn: #{_currentOrder.OrderID}     |     Ngày đặt: {_currentOrder.OrderDate:dd/MM/yyyy HH:mm}     |     Trạng thái: {_currentOrder.OrderStatus}     |     Ngày lập phiếu: {DateTime.Now:dd/MM/yyyy}";

            var rows = _currentOrder.OrderDetails.OrderBy(d => d.ID)
                .Select((d, index) => new
                {
                    STT = index + 1,
                    d.ItemID,
                    ItemName = d.Item?.ItemName ?? "Sản phẩm không xác định",
                    Size = d.Item?.Size ?? string.Empty,
                    d.Quantity
                })
                .ToList();
            _grid.DataSource = rows;
            SetHeader("STT", "STT");
            SetHeader("ItemID", "Mã hàng");
            SetHeader("ItemName", "Tên mặt hàng");
            SetHeader("Size", "Kích cỡ");
            SetHeader("Quantity", "Số lượng giao");
            _previewButton.Enabled = rows.Count > 0;
            _printButton.Enabled = rows.Count > 0;
        }
        catch (Exception ex) { UiTheme.ShowError(FindForm()!, "Không tải được nội dung phiếu giao hàng.\n" + ex.GetBaseException().Message); }
    }

    private void PreviewManifest()
    {
        if (_currentOrder is null) return;
        _printRowIndex = 0;
        using var preview = new PrintPreviewDialog
        {
            Document = _printDocument,
            Width = 1100,
            Height = 850,
            StartPosition = FormStartPosition.CenterParent
        };
        preview.ShowDialog(FindForm());
    }

    private void PrintManifest()
    {
        if (_currentOrder is null) return;
        _printRowIndex = 0;
        using var dialog = new PrintDialog
        {
            Document = _printDocument,
            AllowSomePages = false,
            UseEXDialog = true
        };
        if (dialog.ShowDialog(FindForm()) == DialogResult.OK)
        {
            try
            {
                _printRowIndex = 0;
                _printDocument.Print();
            }
            catch (Exception ex)
            {
                UiTheme.ShowError(FindForm()!, "Không thể in phiếu.\n" + ex.GetBaseException().Message);
            }
        }
    }

    private void PrintDocument_PrintPage(object? sender, PrintPageEventArgs e)
    {
        if (_currentOrder is null) { e.HasMorePages = false; return; }
        Graphics g = e.Graphics;
        Rectangle bounds = e.MarginBounds;
        int left = bounds.Left;
        int right = bounds.Right;
        int y = bounds.Top;

        using var titleFont = new Font("Arial", 18, FontStyle.Bold);
        using var headingFont = new Font("Arial", 10, FontStyle.Bold);
        using var bodyFont = new Font("Arial", 9, FontStyle.Regular);
        using var smallFont = new Font("Arial", 8, FontStyle.Regular);
        using var pen = new Pen(Color.Black, 1);
        using var lightPen = new Pen(Color.Gainsboro, 1);

        g.DrawString("B2B WHOLESALE DISTRIBUTION", headingFont, Brushes.Black, left, y);
        y += 28;
        g.DrawString("PHIẾU GIAO HÀNG / SHIPPING MANIFEST", titleFont, Brushes.Black, left, y);
        y += 42;
        g.DrawLine(pen, left, y, right, y);
        y += 14;

        string agentName = _currentOrder.Agent?.AgentName ?? "Đại lý không xác định";
        string address = _currentOrder.Agent?.Address ?? "Chưa cập nhật";
        string phone = _currentOrder.Agent?.Phone ?? "Chưa cập nhật";
        g.DrawString($"Mã đơn hàng: #{_currentOrder.OrderID}", headingFont, Brushes.Black, left, y);
        g.DrawString($"Ngày lập phiếu: {DateTime.Now:dd/MM/yyyy}", bodyFont, Brushes.Black, right - 180, y);
        y += 24;
        g.DrawString($"Đại lý nhận hàng: {agentName}", bodyFont, Brushes.Black, left, y);
        y += 20;
        g.DrawString($"Địa chỉ giao hàng: {address}", bodyFont, Brushes.Black, left, y);
        y += 20;
        g.DrawString($"Điện thoại: {phone}", bodyFont, Brushes.Black, left, y);
        y += 28;

        int[] widths = { 42, 65, 270, 115, 90 };
        string[] headers = { "STT", "Mã hàng", "Tên mặt hàng", "Kích cỡ", "Số lượng" };
        int x = left;
        for (int i = 0; i < headers.Length; i++)
        {
            g.FillRectangle(Brushes.Gainsboro, x, y, widths[i], 28);
            g.DrawRectangle(pen, x, y, widths[i], 28);
            g.DrawString(headers[i], smallFont, Brushes.Black, new RectangleF(x + 4, y + 6, widths[i] - 8, 20));
            x += widths[i];
        }
        y += 28;

        var lines = _currentOrder.OrderDetails.OrderBy(d => d.ID).ToList();
        int rowHeight = 27;
        int footerReserve = 120;
        while (_printRowIndex < lines.Count && y + rowHeight < bounds.Bottom - footerReserve)
        {
            var line = lines[_printRowIndex];
            string[] values =
            {
                (_printRowIndex + 1).ToString(),
                line.ItemID.ToString(),
                line.Item?.ItemName ?? "Sản phẩm không xác định",
                line.Item?.Size ?? string.Empty,
                line.Quantity.ToString("N0")
            };
            x = left;
            for (int i = 0; i < values.Length; i++)
            {
                g.DrawRectangle(lightPen, x, y, widths[i], rowHeight);
                var format = new StringFormat { Trimming = StringTrimming.EllipsisCharacter, Alignment = i == 4 ? StringAlignment.Center : StringAlignment.Near, LineAlignment = StringAlignment.Center };
                g.DrawString(values[i], bodyFont, Brushes.Black,
                    new RectangleF(x + 4, y + 2, widths[i] - 8, rowHeight - 4), format);
                x += widths[i];
            }
            y += rowHeight;
            _printRowIndex++;
        }

        if (_printRowIndex < lines.Count)
        {
            e.HasMorePages = true;
            return;
        }

        y += 24;
        g.DrawString("Tổng số dòng hàng: " + lines.Count.ToString("N0"), headingFont, Brushes.Black, left, y);
        y += 55;
        int signatureWidth = (right - left) / 2;
        g.DrawString("NGƯỜI GIAO HÀNG", headingFont, Brushes.Black, left + 25, y);
        g.DrawString("ĐẠI LÝ NHẬN HÀNG", headingFont, Brushes.Black, left + signatureWidth + 25, y);
        y += 22;
        g.DrawString("(Ký và ghi rõ họ tên)", smallFont, Brushes.Black, left + 25, y);
        g.DrawString("(Ký và ghi rõ họ tên)", smallFont, Brushes.Black, left + signatureWidth + 25, y);
        e.HasMorePages = false;
    }

    protected override void Dispose(bool disposing)
    {
        if (disposing) _printDocument.Dispose();
        base.Dispose(disposing);
    }

    private void SetHeader(string key, string title)
    {
        if (_grid.Columns.Contains(key)) _grid.Columns[key].HeaderText = title;
    }
}
