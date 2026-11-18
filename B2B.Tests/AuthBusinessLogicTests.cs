using B2B.Data.Entities;
using B2B.Data.Services;
using Xunit;

namespace B2B.Tests;

/// <summary>
/// Task 5.1 (Member 3 - QA & Unit Testing):
/// Role-Based Access Control (Admin vs Agent) and Account Lockout Security Tests.
/// </summary>
public class AuthBusinessLogicTests
{
    [Theory]
    [InlineData("Admin", "Agent", false, true)]  // Admin denied on Web Agent Portal
    [InlineData("Agent", "Admin", false, true)]  // Agent denied on WinForms Admin Back-Office
    [InlineData("Agent", "Agent", true, false)]  // Agent allowed on Web Portal
    [InlineData("Admin", "Admin", true, false)]  // Admin allowed on WinForms Back-Office
    public async Task AuthenticateUser_WhenRoleIsInvalid_ShouldDenyAccess(
        string userRole,
        string requiredPortalRole,
        bool expectedSucceeded,
        bool expectedRoleDenied)
    {
        // Arrange
        await using var db = await SqliteTestContext.CreateAsync();
        var user = new Users
        {
            UserName = $"user_{userRole.ToLower()}",
            email = $"{userRole.ToLower()}@b2bwholesale.vn",
            password = "password123",
            @lock = false,
            Role = userRole
        };
        db.Context.Users.Add(user);
        await db.Context.SaveChangesAsync();

        var tracker = new LoginAttemptTracker(maxFailedAttempts: 5);
        var authService = new AuthService(db.Context, tracker);

        // Act
        var result = await authService.AuthenticateAsync(user.UserName, "password123", requiredPortalRole);

        // Assert
        Assert.Equal(expectedSucceeded, result.Succeeded);
        Assert.Equal(expectedRoleDenied, result.IsRoleDenied);
    }

    [Fact]
    public async Task Login_WhenPasswordFailedMultipleTimes_ShouldLockAccount()
    {
        // Arrange
        await using var db = await SqliteTestContext.CreateAsync();
        var user = new Users
        {
            UserName = "agent_locktest",
            email = "locktest@b2bwholesale.vn",
            password = "correctPassword",
            @lock = false,
            Role = "Agent"
        };
        db.Context.Users.Add(user);
        await db.Context.SaveChangesAsync();

        var tracker = new LoginAttemptTracker(maxFailedAttempts: 5);
        var authService = new AuthService(db.Context, tracker);

        // Act: 4 failed attempts -> not locked yet
        for (int attempt = 1; attempt <= 4; attempt++)
        {
            var failResult = await authService.AuthenticateAsync("agent_locktest", "wrongPassword", "Agent");
            Assert.False(failResult.Succeeded);
            Assert.False(failResult.IsLockedOut);
            Assert.Equal(attempt, failResult.FailedAttempts);
        }

        // 5th consecutive failed attempt -> triggers persistent account lockout in DB
        var fifthResult = await authService.AuthenticateAsync("agent_locktest", "wrongPassword", "Agent");
        Assert.False(fifthResult.Succeeded);
        Assert.True(fifthResult.IsLockedOut);

        // Verify persisted lock flag in fresh context
        await using var verifyCtx = db.CreateFreshContext();
        var persistedUser = await verifyCtx.Users.FindAsync(user.UserID);
        Assert.NotNull(persistedUser);
        Assert.True(persistedUser!.@lock);

        // Subsequent login even with the CORRECT password must now be blocked
        var afterLockResult = await authService.AuthenticateAsync("agent_locktest", "correctPassword", "Agent");
        Assert.False(afterLockResult.Succeeded);
        Assert.True(afterLockResult.IsLockedOut);
        Assert.Contains("bị khóa", afterLockResult.ErrorMessage, StringComparison.OrdinalIgnoreCase);
    }
}
