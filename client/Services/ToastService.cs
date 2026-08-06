namespace DesktopManagerStock.Client.Services;

public enum TipoToast { Exito, Error, Info }

public class ToastMensaje
{
    public Guid Id { get; } = Guid.NewGuid();
    public string Texto { get; set; } = string.Empty;
    public TipoToast Tipo { get; set; } = TipoToast.Info;
    public string? AccionTexto { get; set; }
    public Func<Task>? OnAccion { get; set; }
}

/// <summary>
/// Notificaciones flotantes y transitorias (ver Components/Shared/ToastContainer.razor).
/// Antes, confirmar una acción (guardar, ajustar stock, etc.) solo cerraba el
/// modal en silencio — sin un mensaje que confirme "listo, se guardó". Esto
/// le da ese feedback sin tener que agregar un <div class="alert"> manual en
/// cada página. También soporta un botón de acción (ej. "Deshacer").
/// </summary>
public class ToastService
{
    private readonly List<ToastMensaje> _mensajes = new();
    public IReadOnlyList<ToastMensaje> Mensajes => _mensajes;

    public event Action? OnChange;

    public void Exito(string texto) => Mostrar(texto, TipoToast.Exito);
    public void Error(string texto) => Mostrar(texto, TipoToast.Error);
    public void Info(string texto) => Mostrar(texto, TipoToast.Info);

    /// <summary>Toast con un botón de acción (ej. "Deshacer"), visible por más tiempo que uno normal.</summary>
    public void ConAccion(string texto, string accionTexto, Func<Task> onAccion, TipoToast tipo = TipoToast.Exito, int milisegundos = 6000)
    {
        var toast = new ToastMensaje { Texto = texto, Tipo = tipo, AccionTexto = accionTexto, OnAccion = onAccion };
        _mensajes.Add(toast);
        OnChange?.Invoke();
        _ = DescartarLuegoDeAsync(toast.Id, milisegundos);
    }

    private void Mostrar(string texto, TipoToast tipo)
    {
        var toast = new ToastMensaje { Texto = texto, Tipo = tipo };
        _mensajes.Add(toast);
        OnChange?.Invoke();

        // Autodescarte: cada toast se cierra solo después de un rato. No hace
        // falta que el usuario haga clic en nada para que desaparezca.
        _ = DescartarLuegoDeAsync(toast.Id, tipo == TipoToast.Error ? 5000 : 3200);
    }

    private async Task DescartarLuegoDeAsync(Guid id, int milisegundos)
    {
        await Task.Delay(milisegundos);
        Descartar(id);
    }

    public void Descartar(Guid id)
    {
        if (_mensajes.RemoveAll(m => m.Id == id) > 0)
        {
            OnChange?.Invoke();
        }
    }
}
