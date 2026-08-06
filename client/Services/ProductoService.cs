using System.Net.Http.Json;
using DesktopManagerStock.Client.Models;

namespace DesktopManagerStock.Client.Services;

public class ProductoService
{
    private readonly HttpClient _http;

    public ProductoService(IHttpClientFactory factory)
    {
        _http = factory.CreateClient("ApiConAuth");
    }

    public async Task<PaginaResultado<Producto>> ListarAsync(int skip = 0, int limit = 100, bool incluirInactivos = false, string? categoria = null)
    {
        var url = $"productos?skip={skip}&limit={limit}&incluir_inactivos={incluirInactivos.ToString().ToLowerInvariant()}";
        if (!string.IsNullOrEmpty(categoria))
        {
            url += $"&categoria={Uri.EscapeDataString(categoria)}";
        }
        var response = await _http.GetAsync(url);
        await response.EnsureSuccessOrThrowAsync();
        var items = await response.Content.ReadFromJsonAsync<List<Producto>>(JsonDefaults.Options) ?? new();
        return new PaginaResultado<Producto> { Items = items, Total = response.LeerTotalCount(items.Count) };
    }

    public async Task<List<string>> ListarCategoriasAsync()
    {
        var response = await _http.GetAsync("productos/categorias");
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<List<string>>(JsonDefaults.Options) ?? new();
    }

    /// <summary>Sube un CSV para crear productos en lote (ver server/app/api/routes.py: POST /productos/importar-csv).</summary>
    public async Task<ImportacionResultado> ImportarCsvAsync(Stream contenidoArchivo, string nombreArchivo)
    {
        using var contenido = new MultipartFormDataContent();
        using var streamContent = new StreamContent(contenidoArchivo);
        streamContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("text/csv");
        contenido.Add(streamContent, "archivo", nombreArchivo);

        var response = await _http.PostAsync("productos/importar-csv", contenido);
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<ImportacionResultado>(JsonDefaults.Options)
            ?? throw new ApiException(500, "Respuesta vacía de la API.");
    }

    public async Task<List<Producto>> ListarStockBajoAsync(int? umbral = null)
    {
        var url = umbral.HasValue ? $"productos/stock/bajo?umbral={umbral.Value}" : "productos/stock/bajo";
        var response = await _http.GetAsync(url);
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<List<Producto>>(JsonDefaults.Options) ?? new();
    }

    public async Task<Producto> ObtenerAsync(int id)
    {
        var response = await _http.GetAsync($"productos/{id}");
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<Producto>(JsonDefaults.Options)
            ?? throw new ApiException(500, "Respuesta vacía de la API.");
    }

    public async Task<Producto> CrearAsync(ProductoCreateRequest datos)
    {
        var response = await _http.PostAsJsonAsync("productos", datos, JsonDefaults.Options);
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<Producto>(JsonDefaults.Options)
            ?? throw new ApiException(500, "Respuesta vacía de la API.");
    }

    public async Task<Producto> ActualizarAsync(int id, ProductoUpdateRequest datos)
    {
        var response = await _http.PutAsJsonAsync($"productos/{id}", datos, JsonDefaults.Options);
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<Producto>(JsonDefaults.Options)
            ?? throw new ApiException(500, "Respuesta vacía de la API.");
    }

    /// <summary>DELETE /productos/{id}: soft delete, no borra el historial (ver docs/API_DOCS.md).</summary>
    public async Task EliminarAsync(int id)
    {
        var response = await _http.DeleteAsync($"productos/{id}");
        await response.EnsureSuccessOrThrowAsync();
    }

    public async Task<Producto> ReactivarAsync(int id)
    {
        var response = await _http.PatchAsync($"productos/{id}/reactivar", content: null);
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<Producto>(JsonDefaults.Options)
            ?? throw new ApiException(500, "Respuesta vacía de la API.");
    }

    /// <summary>PATCH /productos/{id}/stock?cantidad=N&amp;tipo=entrada|salida</summary>
    public async Task<string> AjustarStockAsync(int id, int cantidad, bool esEntrada)
    {
        var tipo = esEntrada ? "entrada" : "salida";
        var response = await _http.PatchAsync($"productos/{id}/stock?cantidad={cantidad}&tipo={tipo}", content: null);
        await response.EnsureSuccessOrThrowAsync();
        var body = await response.Content.ReadFromJsonAsync<Dictionary<string, string>>(JsonDefaults.Options);
        return body != null && body.TryGetValue("mensaje", out var mensaje) ? mensaje : "Stock actualizado.";
    }
}
