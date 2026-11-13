using System.Drawing;
using System.Windows.Forms;

namespace B2B.WinForms.Common;

public static class UiTheme
{
    public static readonly Color Navy = Color.FromArgb(20, 35, 62);
    public static readonly Color NavyLight = Color.FromArgb(34, 53, 86);
    public static readonly Color Blue = Color.FromArgb(42, 111, 219);
    public static readonly Color BlueHover = Color.FromArgb(29, 91, 188);
    public static readonly Color Background = Color.FromArgb(245, 247, 251);
    public static readonly Color Surface = Color.White;
    public static readonly Color Text = Color.FromArgb(34, 45, 62);
    public static readonly Color Muted = Color.FromArgb(111, 123, 143);
    public static readonly Color Border = Color.FromArgb(224, 229, 237);
    public static readonly Color Danger = Color.FromArgb(198, 55, 67);
    public static readonly Color Success = Color.FromArgb(27, 132, 91);
    public static readonly Color Warning = Color.FromArgb(184, 116, 22);

    public static Font BodyFont(float size = 9.5f, FontStyle style = FontStyle.Regular) =>
        new("Segoe UI", size, style, GraphicsUnit.Point);

    public static Label Label(string text, float size = 9.5f, bool bold = false, Color? color = null)
    {
        return new Label
        {
            Text = text,
            AutoSize = true,
            Font = BodyFont(size, bold ? FontStyle.Bold : FontStyle.Regular),
            ForeColor = color ?? Text,
            Margin = new Padding(0, 4, 8, 4)
        };
    }

    public static Button Button(string text, bool primary = false, bool danger = false)
    {
        var button = new Button
        {
            Text = text,
            AutoSize = true,
            MinimumSize = new Size(92, 36),
            Padding = new Padding(12, 4, 12, 4),
            FlatStyle = FlatStyle.Flat,
            BackColor = danger ? Danger : primary ? Blue : Surface,
            ForeColor = primary || danger ? Color.White : Text,
            Font = BodyFont(9.2f, FontStyle.Bold),
            Cursor = Cursors.Hand,
            Margin = new Padding(4)
        };
        button.FlatAppearance.BorderColor = danger ? Danger : primary ? Blue : Border;
        button.FlatAppearance.MouseOverBackColor = danger ? Color.FromArgb(171, 42, 54) : primary ? BlueHover : Color.FromArgb(239, 243, 249);
        return button;
    }

    public static TextBox TextBox(string? placeholder = null)
    {
        return new TextBox
        {
            Font = BodyFont(9.5f),
            BorderStyle = BorderStyle.FixedSingle,
            PlaceholderText = placeholder ?? string.Empty,
            Width = 240,
            Margin = new Padding(0, 3, 8, 8)
        };
    }

    public static DataGridView Grid()
    {
        var grid = new DataGridView
        {
            Dock = DockStyle.Fill,
            BackgroundColor = Surface,
            BorderStyle = BorderStyle.None,
            GridColor = Border,
            RowHeadersVisible = false,
            AllowUserToAddRows = false,
            AllowUserToDeleteRows = false,
            ReadOnly = true,
            MultiSelect = false,
            SelectionMode = DataGridViewSelectionMode.FullRowSelect,
            AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
            AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.None,
            RowTemplate = { Height = 34 },
            EnableHeadersVisualStyles = false,
            ColumnHeadersHeight = 40,
            ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.DisableResizing,
            Font = BodyFont(9.2f),
            CellBorderStyle = DataGridViewCellBorderStyle.SingleHorizontal,
            AllowUserToResizeRows = false
        };
        grid.ColumnHeadersDefaultCellStyle = new DataGridViewCellStyle
        {
            BackColor = Color.FromArgb(239, 243, 249),
            ForeColor = Navy,
            Font = BodyFont(9.2f, FontStyle.Bold),
            SelectionBackColor = Color.FromArgb(239, 243, 249),
            SelectionForeColor = Navy,
            Padding = new Padding(8, 0, 8, 0)
        };
        grid.DefaultCellStyle = new DataGridViewCellStyle
        {
            BackColor = Surface,
            ForeColor = Text,
            SelectionBackColor = Color.FromArgb(225, 237, 255),
            SelectionForeColor = Text,
            Padding = new Padding(8, 0, 8, 0)
        };
        grid.AlternatingRowsDefaultCellStyle = new DataGridViewCellStyle
        {
            BackColor = Color.FromArgb(250, 251, 253),
            ForeColor = Text,
            SelectionBackColor = Color.FromArgb(225, 237, 255),
            SelectionForeColor = Text
        };
        return grid;
    }

    public static Panel Card(Control child, int padding = 16)
    {
        var panel = new Panel
        {
            BackColor = Surface,
            Padding = new Padding(padding),
            Margin = new Padding(0, 0, 0, 12),
            Dock = DockStyle.Fill
        };
        child.Dock = DockStyle.Fill;
        panel.Controls.Add(child);
        return panel;
    }

    public static void ShowError(IWin32Window owner, string message, string title = "Có lỗi xảy ra") =>
        MessageBox.Show(owner, message, title, MessageBoxButtons.OK, MessageBoxIcon.Error);

    public static void ShowInfo(IWin32Window owner, string message, string title = "Thông báo") =>
        MessageBox.Show(owner, message, title, MessageBoxButtons.OK, MessageBoxIcon.Information);
}
