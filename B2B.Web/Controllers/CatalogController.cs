using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using B2B.Data.Context;
using B2B.Data.Entities;

namespace B2B.Web.Controllers;

[Authorize(Roles = "Agent")]
public class CatalogController : Controller
{
    private readonly B2BDbContext _context;

    public CatalogController(B2BDbContext context)
    {
        _context = context;
    }

    [HttpGet]
    public async Task<IActionResult> Index(string? search, string? sizeFilter, string? stockStatus)
    {
        var query = _context.Item.AsNoTracking().AsQueryable();

        if (!string.IsNullOrWhiteSpace(search))
        {
            search = search.Trim();
            query = query.Where(i => i.ItemName.Contains(search));
        }

        if (!string.IsNullOrWhiteSpace(sizeFilter) && sizeFilter != "All")
        {
            query = query.Where(i => i.Size == sizeFilter);
        }

        if (!string.IsNullOrWhiteSpace(stockStatus))
        {
            if (stockStatus == "in_stock")
            {
                query = query.Where(i => i.StockQuantity > 0);
            }
            else if (stockStatus == "low_stock")
            {
                query = query.Where(i => i.StockQuantity > 0 && i.StockQuantity <= 10);
            }
            else if (stockStatus == "out_of_stock")
            {
                query = query.Where(i => i.StockQuantity == 0);
            }
        }

        var items = await query.OrderBy(i => i.ItemName).ToListAsync();

        // Get distinct sizes for filter dropdown
        ViewBag.Sizes = await _context.Item
            .Where(i => !string.IsNullOrEmpty(i.Size))
            .Select(i => i.Size)
            .Distinct()
            .ToListAsync();

        ViewBag.CurrentSearch = search;
        ViewBag.CurrentSize = sizeFilter;
        ViewBag.CurrentStockStatus = stockStatus;

        return View(items);
    }
}
