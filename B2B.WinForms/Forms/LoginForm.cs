using B2B.Data.Entities;
using B2B.WinForms.Common;
using B2B.WinForms.DataAccess;
using Microsoft.EntityFrameworkCore;

namespace B2B.WinForms.Forms;

public sealed class LoginForm : Form
{
    private readonly TextBox _userName = UiTheme.TextBox("Nhập tên đăng nhập");
    private readonly TextBox _password = UiTheme.TextBox("Nhập mật khẩu");
    private readonly Button _loginButton = UiTheme.Button("ĐĂNG NHẬP", primary: true);
    private readonly Label _message = UiTheme.Label("Chỉ tài khoản Admin được phép sử dụng Back-Office.", 8.8f, color: UiTheme.Muted);

    public AdminSession? AuthenticatedUser { get; private set; }

    public LoginForm()
    {
        Text = "B2B Wholesale | Admin Login";
        StartPosition = FormStartPosition.CenterScreen;
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false;
        MinimizeBox = false;
        ClientSize = new Size(520, 590);
        BackColor = UiTheme.Background;
        Font = UiTheme.BodyFont();

        var shell = new Panel
        {
            Size = new Size(390, 465),
            BackColor = UiTheme.Surface,
            Padding = new Padding(30),
            Anchor = AnchorStyles.None
        };
        Controls.Add(shell);
        shell.Location = new Point((ClientSize.Width - shell.Width) / 2, (ClientSize.Height - shell.Height) / 2);

        var brand = new Label
        {
            Text = "B2B",
            Font = UiTheme.BodyFont(27, FontStyle.Bold),
            ForeColor = UiTheme.Blue,
            AutoSize = true,
            Location = new Point(30, 28)
        };
        var subBrand = new Label
        {
            Text = "WHOLESALE MANAGEMENT",
            Font = UiTheme.BodyFont(8.2f, FontStyle.Bold),
            ForeColor = UiTheme.Muted,
            AutoSize = true,
            Location = new Point(32, 72)
        };
        var title = new Label
        {
            Text = "Đăng nhập quản trị",
            Font = UiTheme.BodyFont(18, FontStyle.Bold),
            ForeColor = UiTheme.Navy,
            AutoSize = true,
            Location = new Point(30, 126)
        };
        var description = new Label
        {
            Text = "Đăng nhập bằng tài khoản có quyền Admin để quản lý kho và đơn hàng.",
            Font = UiTheme.BodyFont(9),
            ForeColor = UiTheme.Muted,
            AutoSize = false,
            Size = new Size(320, 40),
            Location = new Point(32, 165)
        };

        var userLabel = UiTheme.Label("TÊN ĐĂNG NHẬP", 8.3f, true, UiTheme.Muted);
        userLabel.Location = new Point(32, 224);
        _userName.Location = new Point(32, 247);
        _userName.Size = new Size(320, 34);
        var passLabel = UiTheme.Label("MẬT KHẨU", 8.3f, true, UiTheme.Muted);
        passLabel.Location = new Point(32, 293);
        _password.Location = new Point(32, 316);
        _password.Size = new Size(320, 34);
        _password.UseSystemPasswordChar = true;

        _loginButton.Location = new Point(32, 370);
        _loginButton.Size = new Size(320, 42);
        _loginButton.Anchor = AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Top;
        _loginButton.Click += async (_, _) => await LoginAsync();
        _password.KeyDown += async (_, e) =>
        {
            if (e.KeyCode == Keys.Enter)
            {
                e.SuppressKeyPress = true;
                await LoginAsync();
            }
        };
        _userName.KeyDown += async (_, e) =>
        {
            if (e.KeyCode == Keys.Enter)
            {
                e.SuppressKeyPress = true;
                await LoginAsync();
            }
        };

        _message.Location = new Point(32, 423);
        _message.Size = new Size(320, 28);
        _message.AutoSize = false;

        shell.Controls.AddRange([brand, subBrand, title, description, userLabel, _userName,
            passLabel, _password, _loginButton, _message]);
    }

    private async Task LoginAsync()
    {
        string userName = _userName.Text.Trim();
        string password = _password.Text;
        if (string.IsNullOrWhiteSpace(userName) || string.IsNullOrWhiteSpace(password))
        {
            ShowMessage("Vui lòng nhập tên đăng nhập và mật khẩu.", UiTheme.Warning);
            return;
        }

        _loginButton.Enabled = false;
        _message.Text = "Đang xác thực...";
        _message.ForeColor = UiTheme.Muted;
        try
        {
            await using var context = AppDatabase.CreateContext();
            Users? user = await context.Users.FirstOrDefaultAsync(u => u.UserName == userName);

            if (user is null)
            {
                bool locked = LoginAttemptTracker.RegisterFailure(userName);
                ShowMessage(locked
                    ? "Đã vượt quá số lần đăng nhập cho phép. Tài khoản đã bị khóa nếu tồn tại trong hệ thống."
                    : "Tên đăng nhập hoặc mật khẩu không chính xác.", UiTheme.Danger);
                return;
            }

            if (user.@lock)
            {
                ShowMessage("Tài khoản đang bị khóa. Vui lòng liên hệ quản trị viên.", UiTheme.Danger);
                return;
            }

            // The current shared schema and Web login both store/compare plain-text seed passwords.
            // Keep this comparison compatible with the group's existing Users.password data.
            if (!string.Equals(user.password, password, StringComparison.Ordinal))
            {
                bool shouldLock = LoginAttemptTracker.RegisterFailure(userName);
                if (shouldLock)
                {
                    user.@lock = true;
                    await context.SaveChangesAsync();
                    ShowMessage("Bạn đã nhập sai 5 lần. Tài khoản đã bị khóa.", UiTheme.Danger);
                }
                else
                {
                    ShowMessage("Tên đăng nhập hoặc mật khẩu không chính xác.", UiTheme.Danger);
                }
                return;
            }

            LoginAttemptTracker.Reset(userName);
            if (!string.Equals(user.Role, "Admin", StringComparison.OrdinalIgnoreCase))
            {
                ShowMessage("Truy cập bị từ chối. WinForms chỉ dành cho tài khoản có Role = Admin.", UiTheme.Danger);
                return;
            }

            AuthenticatedUser = new AdminSession { UserId = user.UserID, UserName = user.UserName };
            DialogResult = DialogResult.OK;
            Close();
        }
        catch (Exception ex)
        {
            string detail = ex.GetBaseException().Message;
            UiTheme.ShowError(this,
                "Không thể xác thực do lỗi kết nối hoặc cấu hình database.\n\n" + detail,
                "Lỗi kết nối database");
            ShowMessage("Kiểm tra SQL Server và App.config.", UiTheme.Danger);
        }
        finally
        {
            if (!IsDisposed)
                _loginButton.Enabled = true;
        }
    }

    private void ShowMessage(string message, Color color)
    {
        _message.Text = message;
        _message.ForeColor = color;
    }
}
