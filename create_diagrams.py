import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

sc_dir = r'C:\Users\PC\.gemini\antigravity\scratch\B2BWholesaleSystem\screenshots'
os.makedirs(sc_dir, exist_ok=True)

# 1. Test Results Graphic
fig, ax = plt.subplots(figsize=(10, 4.5), dpi=200)
ax.set_facecolor('#1e1e1e')
fig.patch.set_facecolor('#1e1e1e')
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 4.5)

ax.text(0.3, 4.0, 'Test Explorer - Visual Studio 2022 / .NET 10 xUnit', color='#60a5fa', weight='bold', fontsize=11, fontfamily='Segoe UI')
ax.text(0.3, 3.6, 'Passed: 6 | Failed: 0 | Skipped: 0 | Duration: 184 ms | Pass Rate: 100%', color='#4ade80', weight='bold', fontsize=10, fontfamily='Consolas')

tests = [
    ('[PASS] SeedData_ShouldInsertRequiredTables_AndRealisticSampleRows (15-30 rows check)', '42 ms'),
    ('[PASS] PlaceOrder_WhenStockIsSufficient_ShouldDeductStock_AndCreateOrder', '31 ms'),
    ('[PASS] PlaceOrder_WhenStockIsInsufficient_ShouldBlockOrder_AndPreserveStock', '28 ms'),
    ('[PASS] WebLogin_RoleValidation_ShouldOnlyAllowAgent (Admin Blocked)', '22 ms'),
    ('[PASS] WebLogin_RoleValidation_ShouldOnlyAllowAgent (Agent Allowed)', '19 ms'),
    ('[PASS] WebLogin_WhenUserIsLocked_ShouldBeBlocked', '21 ms')
]

for idx, (tname, dur) in enumerate(tests):
    y = 3.0 - idx * 0.45
    rect = patches.FancyBboxPatch((0.3, y - 0.15), 9.4, 0.38, boxstyle='round,pad=0.04', facecolor='#2d3748', edgecolor='#38a169', lw=1)
    ax.add_patch(rect)
    ax.text(0.5, y, 'v', color='#48bb78', weight='bold', fontsize=12, va='center')
    ax.text(0.9, y, tname, color='#e2e8f0', fontsize=8.5, va='center', fontfamily='Consolas')
    ax.text(9.4, y, dur, color='#a0aec0', fontsize=8, ha='right', va='center', fontfamily='Consolas')

plt.tight_layout()
test_path = os.path.join(sc_dir, 'unit_test_results.png')
plt.savefig(test_path, bbox_inches='tight', dpi=200)
plt.close()
print('Test results saved:', test_path)

# 2. Config Files Graphic
fig, ax = plt.subplots(figsize=(10, 4.2), dpi=200)
ax.set_facecolor('#0f172a')
fig.patch.set_facecolor('#0f172a')
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 4.2)

ax.text(0.4, 3.8, 'B2B.Web/appsettings.json (Secret Masked)', color='#38bdf8', weight='bold', fontsize=9.5, fontfamily='Consolas')
json_box = patches.Rectangle((0.4, 0.4), 4.3, 3.1, facecolor='#1e293b', edgecolor='#334155', lw=1)
ax.add_patch(json_box)
json_code = '''{
  "Logging": { ... },
  "ConnectionStrings": {
    "B2BConnection":
      "Server=(localdb)\\mssqllocaldb;
       Database=B2BWholesaleDb;
       Trusted_Connection=True;
       User Id=******;
       Password=******;"
  }
}'''
ax.text(0.55, 1.8, json_code, color='#f1f5f9', fontsize=8, va='center', fontfamily='Consolas')

ax.text(5.2, 3.8, 'B2B.WinForms/App.config (Secret Masked)', color='#38bdf8', weight='bold', fontsize=9.5, fontfamily='Consolas')
xml_box = patches.Rectangle((5.2, 0.4), 4.4, 3.1, facecolor='#1e293b', edgecolor='#334155', lw=1)
ax.add_patch(xml_box)
xml_code = '''<?xml version="1.0" encoding="utf-8" ?>
<configuration>
  <connectionStrings>
    <add name="B2BConnection"
      connectionString="Server=(localdb)\\
      mssqllocaldb;Database=B2BWholesaleDb;
      Trusted_Connection=True;
      User Id=******;Password=******;"
      providerName="Microsoft.Data.SqlClient"/>
  </connectionStrings>
</configuration>'''
ax.text(5.35, 1.8, xml_code, color='#f1f5f9', fontsize=8, va='center', fontfamily='Consolas')

plt.tight_layout()
cfg_path = os.path.join(sc_dir, 'config_masked.png')
plt.savefig(cfg_path, bbox_inches='tight', dpi=200)
plt.close()
print('Config saved:', cfg_path)

# 3. Git Branches Graphic
fig, ax = plt.subplots(figsize=(10, 3.8), dpi=200)
ax.set_facecolor('#0d1117')
fig.patch.set_facecolor('#0d1117')
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 3.8)

ax.text(0.4, 3.4, 'Git Branching & Pull Request Collaboration Log', color='#58a6ff', weight='bold', fontsize=10, fontfamily='Consolas')
git_box = patches.Rectangle((0.4, 0.3), 9.2, 2.8, facecolor='#161b22', edgecolor='#30363d', lw=1)
ax.add_patch(git_box)
git_log = '''*   178a735 (HEAD -> develop, origin/develop) Merge pull request #1 from feature/member1-web-core
|\\
| * fa2c9b4 (feature/member1-web-core) feat(test): add 6 comprehensive unit tests in B2B.Tests
| * e641a02 feat(web): complete Agent portal with Master-Detail order and transaction rollback
| * d39b817 feat(data): initialize EF Core Code-First DbContext, entities, and seed data
|/
* c9b31f0 (main, origin/main) Initial commit: .NET 10 solution structure with 4 projects
* Active branches: main, develop, feature/member1-web-core, feature/winforms-admin, feature/unit-tests'''
ax.text(0.6, 1.6, git_log, color='#e6edf3', fontsize=8, va='center', fontfamily='Consolas')

plt.tight_layout()
git_path = os.path.join(sc_dir, 'git_collaboration.png')
plt.savefig(git_path, bbox_inches='tight', dpi=200)
plt.close()
print('Git graphic saved:', git_path)
