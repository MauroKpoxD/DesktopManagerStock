using System.Net.Http.Json;
using DesktopManagerStock.Client.Models;

namespace DesktopManagerStock.Client.Services;

/// <summary>Endpoints de /usuarios (administración, solo rol admin).</summary>
public class UsuarioService
{
    private readonly HttpClient _http;

    public UsuarioService(IHttpClientFactory factory)
    {
        _http = factory.CreateClient("ApiConAuth");
    }

    public async Task<PaginaResultado<Usuario>> ListarAsync(int skip = 0, int limit = 100)
    {
        var response = await _http.GetAsync($"usuarios?skip={skip}&limit={limit}");
        await response.EnsureSuccessOrThrowAsync();
        var items = await response.Content.ReadFromJsonAsync<List<Usuario>>(JsonDefaults.Options) ?? new();
        return new PaginaResultado<Usuario> { Items = items, Total = response.LeerTotalCount(items.Count) };
    }

    public async Task<Usuario> ObtenerAsync(int id)
    {
        var response = await _http.GetAsync($"usuarios/{id}");
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<Usuario>(JsonDefaults.Options)
            ?? throw new ApiException(500, "Respuesta vacía de la API.");
    }

    /// <summary>POST /usuarios (solo admin): crea un usuario con el rol que se elija.
    /// A diferencia de AuthService.RegistrarAsync (auto-registro público, siempre "lector").</summary>
    public async Task<Usuario> CrearAsync(RegistroRequest datos)
    {
        var response = await _http.PostAsJsonAsync("usuarios", datos, JsonDefaults.Options);
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<Usuario>(JsonDefaults.Options)
            ?? throw new ApiException(500, "Respuesta vacía de la API.");
    }

    public async Task<Usuario> ActualizarAsync(int id, UsuarioUpdateRequest datos)
    {
        var response = await _http.PutAsJsonAsync($"usuarios/{id}", datos, JsonDefaults.Options);
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<Usuario>(JsonDefaults.Options)
            ?? throw new ApiException(500, "Respuesta vacía de la API.");
    }

    /// <summary>Genera una contraseña temporal para un usuario que perdió acceso a la suya.
    /// La contraseña solo se puede leer en la respuesta de esta llamada.</summary>
    public async Task<PasswordTemporalResponse> ResetearPasswordAsync(int id)
    {
        var response = await _http.PostAsync($"usuarios/{id}/resetear-password", content: null);
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<PasswordTemporalResponse>(JsonDefaults.Options)
            ?? throw new ApiException(500, "Respuesta vacía de la API.");
    }
}
