using System.Net.Http.Json;
using DesktopManagerStock.Client.Models;

namespace DesktopManagerStock.Client.Services;

public class PerfilService
{
    private readonly HttpClient _http;
    private readonly AppState _appState;

    public PerfilService(IHttpClientFactory factory, AppState appState)
    {
        _http = factory.CreateClient("ApiConAuth");
        _appState = appState;
    }

    public async Task<Usuario> ObtenerAsync()
    {
        var response = await _http.GetAsync("auth/me");
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<Usuario>(JsonDefaults.Options)
            ?? throw new ApiException(500, "Respuesta vacía de la API.");
    }

    public async Task<Usuario> ActualizarEmailAsync(string email)
    {
        var response = await _http.PutAsJsonAsync("auth/me", new PerfilUpdateRequest { Email = email }, JsonDefaults.Options);
        await response.EnsureSuccessOrThrowAsync();
        var usuario = await response.Content.ReadFromJsonAsync<Usuario>(JsonDefaults.Options)
            ?? throw new ApiException(500, "Respuesta vacía de la API.");
        _appState.EstablecerUsuario(usuario); // refleja el nuevo email en el sidebar al instante
        return usuario;
    }

    public async Task CambiarPasswordAsync(string actual, string nueva)
    {
        var response = await _http.PostAsJsonAsync(
            "auth/me/password",
            new CambioPasswordRequest { PasswordActual = actual, PasswordNueva = nueva },
            JsonDefaults.Options);
        await response.EnsureSuccessOrThrowAsync();
    }
}
