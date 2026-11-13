using System.Security.Claims;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using B2B.Data.Context;
using B2B.Web.Models;

namespace B2B.Web.Controllers;

public class AccountController : Controller
{
    private readonly B2BDbContext _context;
    private readonly ILogger<AccountController> _logger;

    public AccountController(B2BDbContext context, ILogger<AccountController> logger)
    {
        _context = context;
        _logger = logger;
    }

    [HttpGet]
    public IActionResult Login(string? returnUrl = null)
    {
        if (User.Identity?.IsAuthenticated == true)
        {
            return RedirectToAction("Index", "Catalog");
        }

        return View(new LoginViewModel { ReturnUrl = returnUrl });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Login(LoginViewModel model)
    {
        if (!ModelState.IsValid)
        {
            return View(model);
        }

        // Query user from Database
        var user = await _context.Users
            .Include(u => u.Agent)
            .FirstOrDefaultAsync(u => u.UserName == model.UserName);

        if (user == null || user.password != model.Password)
        {
            ModelState.AddModelError(string.Empty, "Tên đăng nhập hoặc mật khẩu không chính xác.");
            return View(model);
        }

        // Check if user is locked
        if (user.@lock)
        {
            ModelState.AddModelError(string.Empty, "Tài khoản của bạn hiện đang bị khóa. Vui lòng liên hệ quản trị kho.");
            return View(model);
        }

        // Task 3.1: Only users with the Agent role can access the ordering portal
        if (!string.Equals(user.Role, "Agent", StringComparison.OrdinalIgnoreCase))
        {
            ModelState.AddModelError(string.Empty, "Truy cập bị từ chối: Tài khoản quyền 'Admin' chỉ được truy cập qua phần mềm WinForms Back-Office. Web Portal chỉ dành cho Đại lý (Agent).");
            return View(model);
        }

        // Find associated Agent
        int agentId = user.AgentID ?? (user.Agent != null ? user.Agent.AgentID : 1);
        string agentName = user.Agent?.AgentName ?? user.UserName;

        // Build Claims
        var claims = new List<Claim>
        {
            new Claim(ClaimTypes.NameIdentifier, user.UserID.ToString()),
            new Claim(ClaimTypes.Name, user.UserName),
            new Claim(ClaimTypes.Email, user.email),
            new Claim(ClaimTypes.Role, user.Role),
            new Claim("AgentID", agentId.ToString()),
            new Claim("AgentName", agentName)
        };

        var claimsIdentity = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
        var authProperties = new AuthenticationProperties
        {
            IsPersistent = model.RememberMe,
            ExpiresUtc = model.RememberMe ? DateTimeOffset.UtcNow.AddDays(7) : DateTimeOffset.UtcNow.AddHours(8)
        };

        await HttpContext.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, new ClaimsPrincipal(claimsIdentity), authProperties);

        _logger.LogInformation("Agent {UserName} (AgentID: {AgentID}) logged in successfully.", user.UserName, agentId);

        if (!string.IsNullOrEmpty(model.ReturnUrl) && Url.IsLocalUrl(model.ReturnUrl))
        {
            return Redirect(model.ReturnUrl);
        }

        return RedirectToAction("Index", "Catalog");
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Logout()
    {
        await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
        HttpContext.Session.Clear();
        return RedirectToAction("Login", "Account");
    }

    [HttpGet]
    public IActionResult AccessDenied()
    {
        return View();
    }
}
