using B2B.WinForms.Common;
using B2B.WinForms.DataAccess;
using B2B.WinForms.Views;

namespace B2B.WinForms.Forms;

public sealed class MainForm : Form
{
    private readonly AdminSession _session;
    private readonly Panel _content = new() { Dock = DockStyle.Fill, BackColor = UiTheme.Background, Padding = new Padding(22) };
    private readonly Label _pageTitle = new() { AutoSize = true, Font = UiTheme.BodyFont(16, FontStyle.Bold), ForeColor = UiTheme.Navy, Text = "Dashboard" };
    private readonly Label _signedInLabel = new() { AutoSize = true, ForeColor = Color.White, Font = UiTheme.BodyFont(9, FontStyle.Bold) };
    private readonly Dictionary<string, Button> _navigationButtons = new();
    private int? _manifestOrderId;

    public bool LogoutRequested { get; private set; }

    public MainForm(AdminSession session)
    {
        _session = session;
        Text = "B2B Wholesale | Back-Office";
        StartPosition = FormStartPosition.CenterScreen;
        WindowState = FormWindowState.Maximized;
        MinimumSize = new Size(1120, 720);
        BackColor = UiTheme.Background;
        Font = UiTheme.BodyFont();

        BuildShell();
        Navigate("Dashboard");
    }

    private void BuildShell()
    {
        var header = new Panel { Dock = DockStyle.Top, Height = 72, BackColor = UiTheme.Navy, Padding = new Padding(22, 0, 22, 0) };
        var brand = new Label
        {
            Text = "B2B  /  BACK-OFFICE",
            AutoSize = true,
            ForeColor = Color.White,
            Font = UiTheme.BodyFont(14, FontStyle.Bold),
            Location = new Point(22, 24)
        };
        _signedInLabel.Text = $"ADMIN  •  {_session.UserName}";
        _signedInLabel.Anchor = AnchorStyles.Top | AnchorStyles.Right;
        _signedInLabel.Location = new Point(Width - 260, 28);
        header.Resize += (_, _) => _signedInLabel.Location = new Point(header.ClientSize.Width - _signedInLabel.Width - 25, 28);
        header.Controls.Add(brand);
        header.Controls.Add(_signedInLabel);

        var sidebar = new Panel { Dock = DockStyle.Left, Width = 220, BackColor = UiTheme.NavyLight, Padding = new Padding(12, 18, 12, 14) };
        var navHeader = new Label
        {
            Text = "QUẢN TRỊ HỆ THỐNG",
            Dock = DockStyle.Top,
            Height = 34,
            ForeColor = Color.FromArgb(177, 193, 217),
            Font = UiTheme.BodyFont(8.2f, FontStyle.Bold),
            TextAlign = ContentAlignment.MiddleLeft,
            Padding = new Padding(10, 0, 0, 0)
        };
        sidebar.Controls.Add(navHeader);

        var navPanel = new FlowLayoutPanel
        {
            Dock = DockStyle.Top,
            Height = 300,
            FlowDirection = FlowDirection.TopDown,
            WrapContents = false,
            AutoScroll = false,
            Padding = new Padding(0, 10, 0, 0)
        };
        sidebar.Controls.Add(navPanel);
        AddNav(navPanel, "Dashboard", "Tổng quan");
        AddNav(navPanel, "Items", "Quản lý mặt hàng");
        AddNav(navPanel, "Agents", "Quản lý đại lý");
        AddNav(navPanel, "Orders", "Quản lý đơn hàng");
        AddNav(navPanel, "Manifest", "Phiếu giao hàng");

        var logoutButton = new Button
        {
            Text = "Đăng xuất",
            Dock = DockStyle.Bottom,
            Height = 42,
            FlatStyle = FlatStyle.Flat,
            BackColor = Color.FromArgb(48, 65, 96),
            ForeColor = Color.White,
            Font = UiTheme.BodyFont(9, FontStyle.Bold),
            Cursor = Cursors.Hand
        };
        logoutButton.FlatAppearance.BorderColor = Color.FromArgb(75, 91, 120);
        logoutButton.Click += (_, _) =>
        {
            LogoutRequested = true;
            Close();
        };
        sidebar.Controls.Add(logoutButton);

        var titleBar = new Panel { Dock = DockStyle.Top, Height = 58, BackColor = UiTheme.Surface, Padding = new Padding(22, 15, 22, 0) };
        titleBar.Controls.Add(_pageTitle);

        Controls.Add(_content);
        Controls.Add(titleBar);
        Controls.Add(sidebar);
        Controls.Add(header);
    }

    private void AddNav(FlowLayoutPanel panel, string key, string text)
    {
        var button = new Button
        {
            Text = "   " + text,
            Tag = key,
            Width = 194,
            Height = 43,
            TextAlign = ContentAlignment.MiddleLeft,
            FlatStyle = FlatStyle.Flat,
            BackColor = UiTheme.NavyLight,
            ForeColor = Color.FromArgb(224, 232, 244),
            Font = UiTheme.BodyFont(9.2f, FontStyle.Bold),
            Cursor = Cursors.Hand,
            Margin = new Padding(0, 3, 0, 3)
        };
        button.FlatAppearance.BorderSize = 0;
        button.Click += (_, _) => Navigate(key);
        panel.Controls.Add(button);
        _navigationButtons[key] = button;
    }

    private void Navigate(string page, int? orderId = null)
    {
        _manifestOrderId = orderId;
        _pageTitle.Text = page switch
        {
            "Dashboard" => "Tổng quan hoạt động",
            "Items" => "Quản lý mặt hàng",
            "Agents" => "Quản lý đại lý",
            "Orders" => "Quản lý đơn hàng",
            "Manifest" => "Phiếu giao hàng (Shipping Manifest)",
            _ => page
        };

        foreach (var pair in _navigationButtons)
        {
            bool active = pair.Key == page;
            pair.Value.BackColor = active ? UiTheme.Blue : UiTheme.NavyLight;
            pair.Value.ForeColor = Color.White;
        }

        foreach (Control oldView in _content.Controls)
            oldView.Dispose();
        _content.Controls.Clear();
        Control view = page switch
        {
            "Dashboard" => new DashboardView(),
            "Items" => new ItemsView(),
            "Agents" => new AgentsView(),
            "Orders" => new OrdersView(id => Navigate("Manifest", id)),
            "Manifest" => new ManifestView(_manifestOrderId),
            _ => new DashboardView()
        };
        view.Dock = DockStyle.Fill;
        _content.Controls.Add(view);
    }
}
