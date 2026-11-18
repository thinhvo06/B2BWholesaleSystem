using B2B.WinForms.DataAccess;
using B2B.WinForms.Forms;

namespace B2B.WinForms;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        ApplicationConfiguration.Initialize();

        try
        {
            AppDatabase.VerifyConnection();
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                "Không thể kết nối database B2BWholesaleDB.\n\n" +
                "1. Khởi động SQL Server hoặc LocalDB.\n" +
                "2. Tạo database bằng B2B.Data/Scripts/SeedData.sql hoặc chạy Web để khởi tạo.\n" +
                "3. Kiểm tra connection string trong B2B.WinForms/App.config.\n\n" +
                "Chi tiết: " + ex.GetBaseException().Message,
                "B2B Wholesale - Database connection error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error);
            return;
        }

        // A successful logout returns to the login dialog; closing the main window exits.
        while (true)
        {
            using var login = new LoginForm();
            if (login.ShowDialog() != DialogResult.OK || login.AuthenticatedUser is null)
                break;

            using var main = new MainForm(login.AuthenticatedUser);
            main.ShowDialog();
            if (!main.LogoutRequested)
                break;
        }
    }
}
