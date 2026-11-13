using B2B.WinForms.Common;

namespace B2B.WinForms.Dialogs;

public sealed class StockInDialog : Form
{
    private readonly NumericUpDown _quantity = new() { Minimum = 1, Maximum = 1000000000, Value = 1, ThousandsSeparator = true, Width = 250 };
    public int Quantity => decimal.ToInt32(_quantity.Value);

    public StockInDialog(string itemName)
    {
        Text = "Nhập thêm hàng vào kho";
        StartPosition = FormStartPosition.CenterParent;
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false;
        MinimizeBox = false;
        ClientSize = new Size(390, 190);
        BackColor = UiTheme.Surface;

        var title = UiTheme.Label("Nhập thêm hàng", 14, true, UiTheme.Navy);
        title.Location = new Point(22, 18);
        var description = UiTheme.Label(itemName, 9, false, UiTheme.Muted);
        description.Location = new Point(24, 53);
        var label = UiTheme.Label("Số lượng nhập", 8.5f, true, UiTheme.Muted);
        label.Location = new Point(24, 85);
        _quantity.Location = new Point(24, 108);

        var save = UiTheme.Button("Xác nhận", primary: true);
        save.Location = new Point(170, 145);
        save.Click += (_, _) => { DialogResult = DialogResult.OK; Close(); };
        var cancel = UiTheme.Button("Hủy");
        cancel.Location = new Point(270, 145);
        cancel.DialogResult = DialogResult.Cancel;
        Controls.AddRange([title, description, label, _quantity, save, cancel]);
        AcceptButton = save;
        CancelButton = cancel;
    }
}
