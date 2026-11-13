using B2B.WinForms.Common;

namespace B2B.WinForms.Dialogs;

public sealed record AgentEditorValues(string AgentName, string Address, string Phone);

public sealed class AgentEditDialog : Form
{
    private readonly TextBox _name = UiTheme.TextBox("Tên đại lý");
    private readonly TextBox _address = UiTheme.TextBox("Địa chỉ giao dịch / giao hàng");
    private readonly TextBox _phone = UiTheme.TextBox("Số điện thoại");

    public AgentEditorValues? Values { get; private set; }

    public AgentEditDialog(B2B.Data.Entities.Agent? agent = null)
    {
        Text = agent is null ? "Thêm đại lý" : "Cập nhật đại lý";
        StartPosition = FormStartPosition.CenterParent;
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false;
        MinimizeBox = false;
        ClientSize = new Size(500, 340);
        BackColor = UiTheme.Background;

        var panel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(24), BackColor = UiTheme.Surface };
        Controls.Add(panel);
        var title = UiTheme.Label(Text, 15, true, UiTheme.Navy);
        title.Location = new Point(24, 18);
        panel.Controls.Add(title);

        AddField(panel, "Tên đại lý *", _name, 65);
        AddField(panel, "Địa chỉ", _address, 130);
        AddField(panel, "Số điện thoại", _phone, 195);

        if (agent is not null)
        {
            _name.Text = agent.AgentName;
            _address.Text = agent.Address;
            _phone.Text = agent.Phone;
        }

        var save = UiTheme.Button("Lưu", primary: true);
        save.Location = new Point(270, 270);
        save.Click += (_, _) => SaveValues();
        var cancel = UiTheme.Button("Hủy");
        cancel.Location = new Point(370, 270);
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
        input.Size = new Size(420, 30);
        parent.Controls.Add(label);
        parent.Controls.Add(input);
    }

    private void SaveValues()
    {
        string name = _name.Text.Trim();
        string phone = _phone.Text.Trim();
        if (string.IsNullOrWhiteSpace(name))
        {
            UiTheme.ShowError(this, "Tên đại lý không được để trống.");
            _name.Focus();
            return;
        }
        if (name.Length > 200 || _address.Text.Trim().Length > 300 || phone.Length > 50)
        {
            UiTheme.ShowError(this, "Tên tối đa 200 ký tự, địa chỉ tối đa 300 ký tự và số điện thoại tối đa 50 ký tự.");
            return;
        }

        Values = new AgentEditorValues(name, _address.Text.Trim(), phone);
        DialogResult = DialogResult.OK;
        Close();
    }
}
