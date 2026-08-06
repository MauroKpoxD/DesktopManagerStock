namespace DesktopManagerStock.Client.Models;

public class Usuario
{
    public int Id { get; set; }
    public string Username { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Rol { get; set; } = "lector"; // "admin" | "editor" | "lector"
    public bool Activo { get; set; } = true;
}

/// <summary>Body para PUT /usuarios/{id} (solo admin). Todo opcional.</summary>
public class UsuarioUpdateRequest
{
    public string? Email { get; set; }
    public string? Rol { get; set; }
    public bool? Activo { get; set; }
}

/// <summary>Respuesta de POST /usuarios/{id}/resetear-password.</summary>
public class PasswordTemporalResponse
{
    public Usuario Usuario { get; set; } = new();
    public string PasswordTemporal { get; set; } = string.Empty;
}

/// <summary>Body para PUT /auth/me.</summary>
public class PerfilUpdateRequest
{
    public string Email { get; set; } = string.Empty;
}

/// <summary>Body para POST /auth/me/password.</summary>
public class CambioPasswordRequest
{
    public string PasswordActual { get; set; } = string.Empty;
    public string PasswordNueva { get; set; } = string.Empty;
}

/// <summary>Body para POST /auth/register.</summary>
public class RegistroRequest
{
    public string Username { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
    public string Rol { get; set; } = "lector";
}
