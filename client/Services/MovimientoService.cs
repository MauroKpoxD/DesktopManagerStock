using System.Net.Http.Json;
using DesktopManagerStock.Client.Models;

namespace DesktopManagerStock.Client.Services;

public class MovimientoService
{
    private readonly HttpClient _http;

    public MovimientoService(IHttpClientFactory factory)
    {
        _http = factory.CreateClient("ApiConAuth");
    }

    public async Task<PaginaResultado<Movimiento>> ListarAsync(int skip = 0, int limit = 100, int? productoId = null, string? tipo = null)
    {
        var query = new List<string> { $"skip={skip}", $"limit={limit}" };
        if (productoId.HasValue) query.Add($"producto_id={productoId.Value}");
        if (!string.IsNullOrEmpty(tipo)) query.Add($"tipo={tipo}");

        var response = await _http.GetAsync($"movimientos?{string.Join("&", query)}");
        await response.EnsureSuccessOrThrowAsync();
        var items = await response.Content.ReadFromJsonAsync<List<Movimiento>>(JsonDefaults.Options) ?? new();
        return new PaginaResultado<Movimiento> { Items = items, Total = response.LeerTotalCount(items.Count) };
    }

    public async Task<Movimiento> ObtenerAsync(int id)
    {
        var response = await _http.GetAsync($"movimientos/{id}");
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<Movimiento>(JsonDefaults.Options)
            ?? throw new ApiException(500, "Respuesta vacía de la API.");
    }

    public async Task<List<Movimiento>> ObtenerPorRangoAsync(int desde, int hasta)
    {
        var response = await _http.GetAsync($"movimientos/range?desde={desde}&hasta={hasta}");
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<List<Movimiento>>(JsonDefaults.Options) ?? new();
    }
}
