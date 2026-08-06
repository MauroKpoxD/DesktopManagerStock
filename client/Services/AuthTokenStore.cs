using Microsoft.Maui.Storage;

namespace DesktopManagerStock.Client.Services;

/// <summary>
/// Guarda los tokens de sesión.
///
/// - access_token: solo en memoria (vive mientras el proceso esté corriendo).
///   No hace falta persistirlo: dura poco (ACCESS_TOKEN_EXPIRE_MINUTES en el
///   backend, 30 min por defecto) y si se pierde, AuthDelegatingHandler lo
///   renueva solo con el refresh_token.
/// - refresh_token: en SecureStorage, que en Windows/Mac usa el almacén de
///   credenciales cifrado del sistema operativo (nunca Preferences, que no
///   está cifrado).
/// </summary>
public class AuthTokenStore
{
    private const string RefreshTokenKey = "refresh_token";

    public string? AccessToken { get; private set; }

    public async Task GuardarAsync(string accessToken, string? refreshToken)
    {
        AccessToken = accessToken;
        if (!string.IsNullOrEmpty(refreshToken))
        {
            await SecureStorage.Default.SetAsync(RefreshTokenKey, refreshToken);
        }
    }

    public void ActualizarAccessToken(string accessToken)
    {
        AccessToken = accessToken;
    }

    public Task<string?> ObtenerRefreshTokenAsync() => SecureStorage.Default.GetAsync(RefreshTokenKey);

    public void LimpiarSesion()
    {
        AccessToken = null;
        SecureStorage.Default.Remove(RefreshTokenKey);
    }
}
