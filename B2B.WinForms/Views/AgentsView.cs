using B2B.Data.Entities;
using B2B.WinForms.Common;
using B2B.WinForms.DataAccess;
using B2B.WinForms.Dialogs;
using Microsoft.EntityFrameworkCore;

namespace B2B.WinForms.Views;

public sealed class AgentsView : UserControl
{
    private readonly DataGridView _grid = UiTheme.Grid();
    private readonly TextBox _search = UiTheme.TextBox("Tìm theo mã, tên, địa chỉ hoặc số điện thoại...");

    public AgentsView()
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
        _search.Width = 350;
        var add = UiTheme.Button("+ Thêm đại lý", primary: true);
        var edit = UiTheme.Button("Sửa thông tin");
        var delete = UiTheme.Button("Xóa", danger: true);
        add.Click += async (_, _) => await AddAsync();
        edit.Click += async (_, _) => await EditAsync();
        delete.Click += async (_, _) => await DeleteAsync();
        toolbar.Controls.AddRange([_search, add, edit, delete]);
        root.Controls.Add(toolbar, 0, 0);

        var card = new Panel { Dock = DockStyle.Fill, BackColor = UiTheme.Surface, Padding = new Padding(12) };
        var caption = UiTheme.Label("DANH SÁCH ĐẠI LÝ", 8.5f, true, UiTheme.Muted);
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
            var query = context.Agent.AsNoTracking();
            if (!string.IsNullOrWhiteSpace(keyword))
            {
                if (int.TryParse(keyword, out int agentId))
                    query = query.Where(a => a.AgentID == agentId || a.AgentName.Contains(keyword) || a.Address.Contains(keyword) || a.Phone.Contains(keyword));
                else
                    query = query.Where(a => a.AgentName.Contains(keyword) || a.Address.Contains(keyword) || a.Phone.Contains(keyword));
            }

            var rows = await query.OrderBy(a => a.AgentID)
                .Select(a => new { a.AgentID, a.AgentName, a.Address, a.Phone, OrderCount = a.Orders.Count })
                .ToListAsync();
            _grid.DataSource = rows;
            SetHeader("AgentID", "Mã đại lý");
            SetHeader("AgentName", "Tên đại lý");
            SetHeader("Address", "Địa chỉ");
            SetHeader("Phone", "Số điện thoại");
            SetHeader("OrderCount", "Số đơn hàng");
        }
        catch (Exception ex) { UiTheme.ShowError(FindForm()!, "Không tải được danh sách đại lý.\n" + ex.GetBaseException().Message); }
    }

    private void SetHeader(string key, string title)
    {
        if (_grid.Columns.Contains(key)) _grid.Columns[key].HeaderText = title;
    }

    private int? SelectedAgentId()
    {
        if (_grid.CurrentRow?.Cells["AgentID"].Value is int id) return id;
        UiTheme.ShowInfo(FindForm()!, "Vui lòng chọn một đại lý trước.");
        return null;
    }

    private async Task AddAsync()
    {
        using var dialog = new AgentEditDialog();
        if (dialog.ShowDialog(FindForm()) != DialogResult.OK || dialog.Values is null) return;
        try
        {
            using var context = AppDatabase.CreateContext();
            var v = dialog.Values;
            context.Agent.Add(new Agent { AgentName = v.AgentName, Address = v.Address, Phone = v.Phone });
            await context.SaveChangesAsync();
            await ReloadAsync();
        }
        catch (Exception ex) { UiTheme.ShowError(FindForm()!, "Không thể thêm đại lý.\n" + ex.GetBaseException().Message); }
    }

    private async Task EditAsync()
    {
        int? id = SelectedAgentId();
        if (id is null) return;
        try
        {
            using var context = AppDatabase.CreateContext();
            var agent = await context.Agent.FindAsync(id.Value);
            if (agent is null) { UiTheme.ShowInfo(FindForm()!, "Đại lý không còn tồn tại."); return; }
            using var dialog = new AgentEditDialog(agent);
            if (dialog.ShowDialog(FindForm()) != DialogResult.OK || dialog.Values is null) return;
            agent.AgentName = dialog.Values.AgentName;
            agent.Address = dialog.Values.Address;
            agent.Phone = dialog.Values.Phone;
            await context.SaveChangesAsync();
            await ReloadAsync();
        }
        catch (Exception ex) { UiTheme.ShowError(FindForm()!, "Không thể cập nhật đại lý.\n" + ex.GetBaseException().Message); }
    }

    private async Task DeleteAsync()
    {
        int? id = SelectedAgentId();
        if (id is null) return;
        if (MessageBox.Show(FindForm(), "Bạn chắc chắn muốn xóa đại lý này? Đại lý đang có đơn hàng sẽ không thể xóa.",
            "Xác nhận xóa", MessageBoxButtons.YesNo, MessageBoxIcon.Warning) != DialogResult.Yes) return;
        try
        {
            using var context = AppDatabase.CreateContext();
            var agent = await context.Agent.FindAsync(id.Value);
            if (agent is null) return;
            context.Agent.Remove(agent);
            await context.SaveChangesAsync();
            await ReloadAsync();
        }
        catch (DbUpdateException)
        {
            UiTheme.ShowError(FindForm()!, "Không thể xóa đại lý vì đang có đơn hàng liên kết. Bạn có thể cập nhật thông tin thay vì xóa để bảo toàn lịch sử giao dịch.");
        }
        catch (Exception ex) { UiTheme.ShowError(FindForm()!, "Không thể xóa đại lý.\n" + ex.GetBaseException().Message); }
    }
}
