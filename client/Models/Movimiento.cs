namespace DesktopManagerStock.Client.Models;

public class Movimiento
{
    public int Id { get; set; }
    public int ProductoId { get; set; }
    public string Tipo { get; set; } = string.Empty; // "entrada" | "salida"
    public int Cantidad { get; set; }
    public int StockResultante { get; set; }
    public int? UsuarioId { get; set; }
    public DateTime FechaHora { get; set; }
}
