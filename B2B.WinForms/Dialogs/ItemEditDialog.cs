using B2B.Data.Entities;
using B2B.WinForms.Common;

namespace B2B.WinForms.Dialogs;

public sealed record ItemEditorValues(string ItemName, string Size, decimal Price, int StockQuantity);

public sealed class ItemEditDialog : Form
{
    private readonly TextBox _name = UiTheme.TextBox("Tên mặt hàng");
    private readonly TextBox _size = UiTheme.TextBox("Ví dụ: 27 inch, 1TB...");
    private readonly NumericUpDown _price = new() { DecimalPlaces = 2, Maximum = 999999999999m, Minimum = 0, ThousandsSeparator = true, Width = 280 };
    private readonly NumericUpDown _stock = new() { Maximum = 1000000000, Minimum = 0, ThousandsSeparator = true, Width = 280 };

    public ItemEditorValues? Values { get; private set; }

    public ItemEditDialog(Item? item = null)
    {
        Text = item is null ? "Thêm mặt hàng" : "Cập nhật mặt hàng";
        StartPosition = FormStartPosition.CenterParent;
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false;
        MinimizeBox = false;
        ClientSize = new Size(480, 390);
        BackColor = UiTheme.Background;

        var panel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(24), BackColor = UiTheme.Surface };
        Controls.Add(panel);
        var title = UiTheme.Label(Text, 15, true, UiTheme.Navy);
        title.Location = new Point(24, 18);
        panel.Controls.Add(title);

        AddField(panel, "Tên mặt hàng *", _name, 65);
        AddField(panel, "Kích cỡ / Quy cách", _size, 125);
        AddField(panel, "Đơn giá (VND) *", _price, 185);
        AddField(panel, "Số lượng tồn kho *", _stock, 245);

        if (item is not null)
        {
            _name.Text = item.ItemName;
            _size.Text = item.Size;
            _price.Value = Math.Clamp(item.Price, _price.Minimum, _price.Maximum);
            _stock.Value = Math.Clamp(item.StockQuantity, (int)_stock.Minimum, (int)_stock.Maximum);
        }

        var save = UiTheme.Button("Lưu", primary: true);
        save.Location = new Point(250, 320);
        save.Click += (_, _) => SaveValues();
        var cancel = UiTheme.Button("Hủy");
        cancel.Location = new Point(350, 320);
        cancel.DialogResult = DialogResult.Cancel;
        panel.Controls.AddRange([save, cancel]);
        AcceptButton = save;
        CancelButton = cancel;
    }

    private static void AddField(Control parent, string labelText, Control input, int top)
    {
        var label = UiTheme.Label(labelText, 8.5f, true, UiTheme.Muted);
        label.Location = new Point(26, top);
        input.Location = new Point(26, top + 22);
        input.Size = new Size(400, 30);
        parent.Controls.Add(label);
        parent.Controls.Add(input);
    }

    private void SaveValues()
    {
        string name = _name.Text.Trim();
        if (string.IsNullOrWhiteSpace(name))
        {
            UiTheme.ShowError(this, "Tên mặt hàng không được để trống.");
            _name.Focus();
            return;
        }
        if (_price.Value <= 0)
        {
            UiTheme.ShowError(this, "Đơn giá phải lớn hơn 0.");
            _price.Focus();
            return;
        }

        Values = new ItemEditorValues(name, _size.Text.Trim(), _price.Value, decimal.ToInt32(_stock.Value));
        DialogResult = DialogResult.OK;
        Close();
    }
}
