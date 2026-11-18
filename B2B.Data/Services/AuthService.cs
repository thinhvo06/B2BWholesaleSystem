using System.Collections.Concurrent;
using Microsoft.EntityFrameworkCore;
using B2B.Data.Context;
using B2B.Data.Entities;

namespace B2B.Data.Services;

public class LoginAttemptTracker
{
    public int MaxFailedAttempts { get; }
    private readonly ConcurrentDictionary<string, int> _failedAttempts = new(StringComparer.OrdinalIgnoreCase);

    public LoginAttemptTracker(int maxFailedAttempts = 5)
    {
        MaxFailedAttempts = maxFailedAttempts;
    }

    public int RecordFailure(string userName)
    {
        return _failedAttempts.AddOrUpdate(userName, 1, (_, current) => current + 1);
    }

    public void Reset(string userName)
    {
        _failedAttempts.TryRemove(userName, out _);
    }

    public int GetAttempts(string userName)
    {
        return _failedAttempts.TryGetValue(userName, out var count) ? count : 0;
    }
}

public class AuthResult
{
    public bool Succeeded { get; init; }
    public Users? User { get; init; }
    public bool IsLockedOut { get; init; }
    public bool IsRoleDenied { get; init; }
    public int FailedAttempts { get; init; }
    public string ErrorMessage { get; init; } = string.Empty;
}

public class AuthService
{
    private readonly B2BDbContext _context;
    private readonly LoginAttemptTracker _tracker;

    public AuthService(B2BDbContext context, LoginAttemptTracker tracker)
    {
        _context = context;
        _tracker = tracker;
    }

    /// <summary>
    /// Authenticates a user for a specific application portal ('Agent' for Web, 'Admin' for WinForms).
    /// Enforces Role validation and persistent account lockout after MaxFailedAttempts wrong passwords.
    /// </summary>
    public async Task<AuthResult> AuthenticateAsync(string userName, string password, string requiredRole)
    {
        if (string.IsNullOrWhiteSpace(userName) || string.IsNullOrEmpty(password))
        {
            return new AuthResult
            {
                Succeeded = false,
                ErrorMessage = "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu."
            };
        }

        var user = await _context.Users
            .Include(u => u.Agent)
            .FirstOrDefaultAsync(u => u.UserName == userName);

        if (user == null)
        {
            return new AuthResult
            {
                Succeeded = false,
                ErrorMessage = "Tên đăng nhập hoặc mật khẩu không chính xác."
            };
        }

        // Check persistent lockout flag first
        if (user.@lock)
        {
            return new AuthResult
            {
                Succeeded = false,
                IsLockedOut = true,
                ErrorMessage = "Tài khoản của bạn hiện đang bị khóa. Vui lòng liên hệ quản trị kho."
            };
        }

        // Validate password & enforce lockout threshold on repeated failures
        if (!string.Equals(user.password, password, StringComparison.Ordinal))
        {
            int attempts = _tracker.RecordFailure(user.UserName);
            if (attempts >= _tracker.MaxFailedAttempts)
            {
                user.@lock = true;
                await _context.SaveChangesAsync();

                return new AuthResult
                {
                    Succeeded = false,
                    IsLockedOut = true,
                    FailedAttempts = attempts,
                    ErrorMessage = $"Tài khoản đã bị khóa do nhập sai mật khẩu quá {_tracker.MaxFailedAttempts} lần liên tiếp. Vui lòng liên hệ quản trị kho."
                };
            }

            return new AuthResult
            {
                Succeeded = false,
                FailedAttempts = attempts,
                ErrorMessage = $"Tên đăng nhập hoặc mật khẩu không chính xác (còn {_tracker.MaxFailedAttempts - attempts} lần thử trước khi khóa tài khoản)."
            };
        }

        // Enforce strict Role separation between Web ('Agent') and WinForms ('Admin')
        if (!string.Equals(user.Role, requiredRole, StringComparison.OrdinalIgnoreCase))
        {
            string roleMessage = string.Equals(requiredRole, "Agent", StringComparison.OrdinalIgnoreCase)
                ? "Truy cập bị từ chối: Tài khoản quyền 'Admin' chỉ được truy cập qua phần mềm WinForms Back-Office. Web Portal chỉ dành cho Đại lý (Agent)."
                : "Truy cập bị từ chối: Tài khoản quyền 'Agent' chỉ được sử dụng trên Web Portal. Ứng dụng WinForms chỉ dành cho Quản trị viên (Admin).";

            return new AuthResult
            {
                Succeeded = false,
                IsRoleDenied = true,
                ErrorMessage = roleMessage
            };
        }

        _tracker.Reset(user.UserName);

        return new AuthResult
        {
            Succeeded = true,
            User = user
        };
    }
}
