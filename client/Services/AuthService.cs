using System.Net.Http.Json;
using DesktopManagerStock.Client.Models;

namespace DesktopManagerStock.Client.Services;

/// <summary>
/// Maneja login/registro/logout hablando directo con la API, SIN pasar por
/// AuthDelegatingHandler (ver MauiProgram.cs: se registra con un HttpClient
/// tipado propio, no con el named client "ApiConAuth"). Esto evita que un
/// login con contraseña incorrecta dispare de rebote un intento de
/// renovación de token con un refresh_token viejo de otra sesión.
/// </summary>
public class AuthService
{
    private readonly HttpClient _http;
    private readonly AuthTokenStore _tokenStore;
    private readonly AppState _appState;

    public AuthService(HttpClient http, AuthTokenStore tokenStore, AppState appState)
    {
        _http = http;
        _tokenStore = tokenStore;
        _appState = appState;
    }

    public async Task<Usuario> LoginAsync(string username, string password)
    {
        // OAuth2PasswordRequestForm (usado en el backend) espera
        // application/x-www-form-urlencoded, no JSON.
        var form = new FormUrlEncodedContent(new Dictionary<string, string>
        {
            ["username"] = username,
            ["password"] = password,
        });

        var response = await _http.PostAsync("auth/login", form);
        await response.EnsureSuccessOrThrowAsync();

        var token = await response.Content.ReadFromJsonAsync<TokenResponse>(JsonDefaults.Options)
            ?? throw new ApiException(500, "La API no devolvió un token válido.");

        await _tokenStore.GuardarAsync(token.AccessToken, token.RefreshToken);

        var perfil = await ObtenerPerfilConTokenAsync(token.AccessToken);
        _appState.EstablecerUsuario(perfil);
        return perfil;
    }

    public async Task RegistrarAsync(RegistroRequest datos)
    {
        var response = await _http.PostAsJsonAsync("auth/register", datos, JsonDefaults.Options);
        await response.EnsureSuccessOrThrowAsync();
    }

    public async Task LogoutAsync()
    {
        var refreshToken = await _tokenStore.ObtenerRefreshTokenAsync();
        if (!string.IsNullOrEmpty(refreshToken))
        {
            try
            {
                await _http.PostAsJsonAsync("auth/logout", new RefreshTokenRequest { RefreshToken = refreshToken }, JsonDefaults.Options);
            }
            catch
            {
                // Si no hay conexión, igual limpiamos la sesión localmente;
                // el refresh token quedará revocado del lado del servidor la
                // próxima vez que expire solo, o si el usuario vuelve a hacer logout.
            }
        }
        _tokenStore.LimpiarSesion();
        _appState.EstablecerUsuario(null);
    }

    /// <summary>
    /// Se llama una vez al arrancar la app: si hay un refresh_token guardado
    /// de una sesión anterior, intenta canjearlo por un access_token nuevo
    /// para no pedirle login de nuevo al usuario cada vez que abre la app.
    /// </summary>
    public async Task<bool> RestaurarSesionAsync()
    {
        var refreshToken = await _tokenStore.ObtenerRefreshTokenAsync();
        if (string.IsNullOrEmpty(refreshToken))
        {
            return false;
        }

        try
        {
            var response = await _http.PostAsJsonAsync("auth/refresh", new RefreshTokenRequest { RefreshToken = refreshToken }, JsonDefaults.Options);
            if (!response.IsSuccessStatusCode)
            {
                _tokenStore.LimpiarSesion();
                return false;
            }

            var token = await response.Content.ReadFromJsonAsync<TokenResponse>(JsonDefaults.Options);
            if (token is null) return false;

            await _tokenStore.GuardarAsync(token.AccessToken, token.RefreshToken);
            var perfil = await ObtenerPerfilConTokenAsync(token.AccessToken);
            _appState.EstablecerUsuario(perfil);
            return true;
        }
        catch
        {
            // Sin conexión al arrancar: se deja que el usuario reintente
            // manualmente en vez de tirar la app abajo.
            return false;
        }
    }

    private async Task<Usuario> ObtenerPerfilConTokenAsync(string accessToken)
    {
        using var request = new HttpRequestMessage(HttpMethod.Get, "auth/me");
        request.Headers.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken);
        var response = await _http.SendAsync(request);
        await response.EnsureSuccessOrThrowAsync();
        return await response.Content.ReadFromJsonAsync<Usuario>(JsonDefaults.Options)
            ?? throw new ApiException(500, "La API no devolvió el perfil del usuario.");
    }
}
