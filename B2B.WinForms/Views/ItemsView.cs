using B2B.Data.Entities;
using B2B.WinForms.Common;
using B2B.WinForms.DataAccess;
using B2B.WinForms.Dialogs;
using Microsoft.EntityFrameworkCore;

namespace B2B.WinForms.Views;

public sealed class ItemsView : UserControl
{
    private readonly DataGridView _grid = UiTheme.Grid();
    private readonly TextBox _search = UiTheme.TextBox("Tìm theo mã hoặc tên mặt hàng...");

    public ItemsView()
    {
        BackColor = UiTheme.Background;
        BuildLayout();
        Load += async (_, _) => await ReloadAsync();
        _search.TextChanged += async (_, _) => await ReloadAsync();
    }

    private void BuildLayout()
    {
        var root = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 1, RowCount = 2, BackColor = UiTheme.Background };
        root.RowStyles.Add(new RowStyle(SizeType.Absolute, 62));
        root.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        Controls.Add(root);

        var toolbar = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.LeftToRight, WrapContents = false, Padding = new Padding(0, 8, 0, 8) };
        _search.Width = 300;
        var add = UiTheme.Button("+ Thêm mặt hàng", primary: true);
        var edit = UiTheme.Button("Sửa thông tin");
        var stockIn = UiTheme.Button("Nhập thêm kho");
        var delete = UiTheme.Button("Xóa", danger: true);
        add.Click += async (_, _) => await AddAsync();
        edit.Click += async (_, _) => await EditAsync();
        stockIn.Click += async (_, _) => await StockInAsync();
        delete.Click += async (_, _) => await DeleteAsync();
        toolbar.Controls.AddRange([_search, add, edit, stockIn, delete]);
        root.Controls.Add(toolbar, 0, 0);

        var card = new Panel { Dock = DockStyle.Fill, BackColor = UiTheme.Surface, Padding = new Padding(12) };
        var caption = UiTheme.Label("DANH SÁCH MẶT HÀNG", 8.5f, true, UiTheme.Muted);
        caption.Dock = DockStyle.Top;
        caption.Height = 28;
        card.Controls.Add(_grid);
        card.Controls.Add(caption);
        root.Controls.Add(card, 0, 1);
    }

    private async Task ReloadAsync()
    {
        try
        {
            using var context = AppDatabase.CreateContext();
            string keyword = _search.Text.Trim();
            var query = context.Item.AsNoTracking();
            if (!string.IsNullOrWhiteSpace(keyword))
            {
                if (int.TryParse(keyword, out int itemId))
                    query = query.Where(i => i.ItemID == itemId || i.ItemName.Contains(keyword));
                else
                    query = query.Where(i => i.ItemName.Contains(keyword));
            }
            var rows = await query.OrderBy(i => i.ItemID)
                .Select(i => new { i.ItemID, i.ItemName, i.Size, i.Price, i.StockQuantity })
                .ToListAsync();
            _grid.DataSource = rows;
            SetHeader("ItemID", "Mã hàng");
            SetHeader("ItemName", "Tên mặt hàng");
            SetHeader("Size", "Kích cỡ");
            SetHeader("Price", "Đơn giá (VND)");
            SetHeader("StockQuantity", "Tồn kho");
            if (_grid.Columns.Contains("Price"))
                _grid.Columns["Price"].DefaultCellStyle.Format = "N0";
            if (_grid.Columns.Contains("StockQuantity"))
                _grid.Columns["StockQuantity"].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
        }
        catch (Exception ex)
        {
            UiTheme.ShowError(FindForm()!, "Không tải được danh sách mặt hàng.\n" + ex.GetBaseException().Message);
        }
    }

    private void SetHeader(string key, string title)
    {
        if (_grid.Columns.Contains(key)) _grid.Columns[key].HeaderText = title;
    }

    private int? SelectedItemId()
    {
        if (_grid.CurrentRow?.Cells["ItemID"].Value is int id) return id;
        UiTheme.ShowInfo(FindForm()!, "Vui lòng chọn một mặt hàng trước.");
        return null;
    }

    private async Task AddAsync()
    {
        using var dialog = new ItemEditDialog();
        if (dialog.ShowDialog(FindForm()) != DialogResult.OK || dialog.Values is null) return;
        try
        {
            using var context = AppDatabase.CreateContext();
            var v = dialog.Values;
            context.Item.Add(new Item { ItemName = v.ItemName, Size = v.Size, Price = v.Price, StockQuantity = v.StockQuantity });
            await context.SaveChangesAsync();
            await ReloadAsync();
        }
        catch (Exception ex) { UiTheme.ShowError(FindForm()!, "Không thể thêm mặt hàng.\n" + ex.GetBaseException().Message); }
    }

    private async Task EditAsync()
    {
        int? id = SelectedItemId();
        if (id is null) return;
        try
        {
            using var context = AppDatabase.CreateContext();
            var item = await context.Item.FindAsync(id.Value);
            if (item is null) { UiTheme.ShowInfo(FindForm()!, "Mặt hàng không còn tồn tại."); return; }
            using var dialog = new ItemEditDialog(item);
            if (dialog.ShowDialog(FindForm()) != DialogResult.OK || dialog.Values is null) return;
            Apply(dialog.Values, item);
            await context.SaveChangesAsync();
            await ReloadAsync();
        }
        catch (Exception ex) { UiTheme.ShowError(FindForm()!, "Không thể cập nhật mặt hàng.\n" + ex.GetBaseException().Message); }
    }

    private async Task StockInAsync()
    {
        int? id = SelectedItemId();
        if (id is null) return;
        try
        {
            using var context = AppDatabase.CreateContext();
            var item = await context.Item.FindAsync(id.Value);
            if (item is null) return;
            using var dialog = new StockInDialog(item.ItemName);
            if (dialog.ShowDialog(FindForm()) != DialogResult.OK) return;
            checked { item.StockQuantity += dialog.Quantity; }
            await context.SaveChangesAsync();
            await ReloadAsync();
            UiTheme.ShowInfo(FindForm()!, $"Đã nhập thêm {dialog.Quantity:N0} sản phẩm. Tồn kho mới: {item.StockQuantity:N0}.");
        }
        catch (OverflowException) { UiTheme.ShowError(FindForm()!, "Số lượng tồn kho vượt giới hạn cho phép."); }
        catch (Exception ex) { UiTheme.ShowError(FindForm()!, "Không thể nhập thêm hàng.\n" + ex.GetBaseException().Message); }
    }

    private async Task DeleteAsync()
    {
        int? id = SelectedItemId();
        if (id is null) return;
        if (MessageBox.Show(FindForm(), "Bạn chắc chắn muốn xóa mặt hàng này?\nMặt hàng đã có trong đơn hàng sẽ không thể xóa.",
            "Xác nhận xóa", MessageBoxButtons.YesNo, MessageBoxIcon.Warning) != DialogResult.Yes) return;
        try
        {
            using var context = AppDatabase.CreateContext();
            var item = await context.Item.FindAsync(id.Value);
            if (item is null) return;
            context.Item.Remove(item);
            await context.SaveChangesAsync();
            await ReloadAsync();
        }
        catch (DbUpdateException)
        {
            UiTheme.ShowError(FindForm()!, "Không thể xóa vì mặt hàng đang được tham chiếu trong OrderDetail. Hãy giữ mặt hàng để bảo toàn lịch sử đơn hàng.");
        }
        catch (Exception ex) { UiTheme.ShowError(FindForm()!, "Không thể xóa mặt hàng.\n" + ex.GetBaseException().Message); }
    }

    private static void Apply(ItemEditorValues values, Item item)
    {
        item.ItemName = values.ItemName;
        item.Size = values.Size;
        item.Price = values.Price;
        item.StockQuantity = values.StockQuantity;
    }
}
