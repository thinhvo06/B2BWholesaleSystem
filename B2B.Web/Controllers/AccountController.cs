using System.Security.Claims;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using B2B.Data.Services;
using B2B.Web.Models;

namespace B2B.Web.Controllers;

public class AccountController : Controller
{
    private readonly AuthService _authService;
    private readonly ILogger<AccountController> _logger;

    public AccountController(AuthService authService, ILogger<AccountController> logger)
    {
        _authService = authService;
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

        // Task 3.1: Authenticate via shared AuthService enforcing Role='Agent' and lockout threshold
        var authResult = await _authService.AuthenticateAsync(model.UserName, model.Password, requiredRole: "Agent");

        if (!authResult.Succeeded || authResult.User == null)
        {
            ModelState.AddModelError(string.Empty, authResult.ErrorMessage);
            return View(model);
        }

        var user = authResult.User;

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
