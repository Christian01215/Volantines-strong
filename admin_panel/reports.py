"""Generación del reporte de ventas y ganancias del panel de administración."""
from collections import defaultdict
from datetime import date
from io import BytesIO

from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

MONTHS_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def _month_key(value):
    """Devuelve el primer día del mes local de una fecha."""
    if value is None:
        return date(timezone.now().year, timezone.now().month, 1)
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    return date(value.year, value.month, 1)


def _add_months(value, months):
    index = value.month - 1 + months
    year = value.year + index // 12
    month = index % 12 + 1
    return date(year, month, 1)


def _previous_year(value):
    return date(value.year - 1, value.month, 1)


def _variation(current, previous):
    if previous == 0:
        return "—" if current == 0 else "+100,0%"
    change = (current - previous) / previous * 100
    return f"{change:+.1f}%".replace(".", ",")


def _fetch_rows(orders):
    """Materializa pedidos e ítems con un número fijo de consultas."""
    return list(orders.prefetch_related("items__product__category"))


def monthly_summary(orders):
    """Resumen mensual con comparación mes anterior y mismo mes del año anterior."""
    rows = _fetch_rows(orders)
    totals = defaultdict(lambda: {"orders": 0, "units": 0, "revenue": 0, "profit": 0})

    for order in rows:
        key = _month_key(order.created_at)
        totals[key]["orders"] += 1
        for item in order.items.all():
            totals[key]["units"] += item.quantity
            totals[key]["revenue"] += item.line_total
            totals[key]["profit"] += item.line_profit

    current = _month_key(timezone.now())
    start = min(totals) if totals else current
    cursor = start
    while cursor <= current:
        if cursor not in totals:
            totals[cursor] = {"orders": 0, "units": 0, "revenue": 0, "profit": 0}
        cursor = _add_months(cursor, 1)

    summary = []
    for key in sorted(totals, reverse=True):
        data = totals[key]
        last_month = totals.get(_add_months(key, -1), {"revenue": 0, "profit": 0})
        last_year = totals.get(_previous_year(key), {"revenue": 0, "profit": 0})
        summary.append({
            "key": key,
            "label": f"{MONTHS_ES[key.month - 1]} {key.year}",
            "orders": data["orders"],
            "units": data["units"],
            "revenue": data["revenue"],
            "profit": data["profit"],
            "revenue_mom": _variation(data["revenue"], last_month["revenue"]),
            "profit_mom": _variation(data["profit"], last_month["profit"]),
            "revenue_yoy": _variation(data["revenue"], last_year["revenue"]),
            "profit_yoy": _variation(data["profit"], last_year["profit"]),
        })
    return summary


def _style_sheet(ws, widths):
    fill = PatternFill("solid", fgColor="A8262D")
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFFFF")
        cell.fill = fill
        cell.alignment = Alignment(horizontal="center")
    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(index)].width = width
    ws.freeze_panes = "A2"


def build_orders_workbook(orders):
    """Construye el XLSX completo y lo devuelve como BytesIO."""
    rows = _fetch_rows(orders)
    wb = Workbook()

    ws = wb.active
    ws.title = "Resumen mensual"
    ws.append([
        "Mes", "Pedidos", "Unidades", "Ingresos CLP", "Ganancia CLP",
        "Ingresos vs mes anterior", "Ganancia vs mes anterior",
        "Ingresos vs año anterior", "Ganancia vs año anterior",
    ])
    for row in monthly_summary(orders):
        ws.append([
            row["label"], row["orders"], row["units"], row["revenue"], row["profit"],
            row["revenue_mom"], row["profit_mom"], row["revenue_yoy"], row["profit_yoy"],
        ])
    for row in ws.iter_rows(min_row=2, min_col=4, max_col=5):
        for cell in row:
            cell.number_format = "#,##0"
    _style_sheet(ws, [22, 10, 11, 16, 16, 24, 24, 24, 24])

    ws = wb.create_sheet("Pedidos")
    ws.append([
        "Código", "Fecha", "Cliente", "RUT", "Estado", "Entrega",
        "Total CLP", "Ganancia CLP", "Comprobante",
    ])
    for order in rows:
        local_created = timezone.localtime(order.created_at) if timezone.is_aware(order.created_at) else order.created_at
        ws.append([
            order.code,
            local_created.strftime("%d/%m/%Y %H:%M"),
            order.customer_name or "—",
            order.customer_rut or "—",
            order.get_status_display(),
            order.get_delivery_type_display(),
            order.total,
            order.total_profit,
            order.receipt_url or "—",
        ])
    for row in ws.iter_rows(min_row=2, min_col=7, max_col=8):
        for cell in row:
            cell.number_format = "#,##0"
    _style_sheet(ws, [16, 18, 24, 16, 20, 24, 14, 16, 48])

    ws = wb.create_sheet("Detalle por producto")
    ws.append([
        "Pedido", "Fecha", "Producto", "Categoría", "Cantidad",
        "Precio unit. CLP", "Costo unit. CLP", "Subtotal CLP", "Ganancia CLP", "Diseño",
    ])
    for order in rows:
        local_created = timezone.localtime(order.created_at) if timezone.is_aware(order.created_at) else order.created_at
        for item in order.items.all():
            ws.append([
                order.code,
                local_created.strftime("%d/%m/%Y"),
                item.product.name,
                item.product.category.name if item.product.category else "Sin categoría",
                item.quantity,
                item.price,
                item.cost,
                item.line_total,
                item.line_profit,
                item.design_url or "—",
            ])
    for row in ws.iter_rows(min_row=2, min_col=6, max_col=9):
        for cell in row:
            cell.number_format = "#,##0"
    _style_sheet(ws, [16, 13, 26, 18, 10, 16, 16, 16, 16, 42])

    category_totals = defaultdict(lambda: {"units": 0, "revenue": 0, "profit": 0})
    for order in rows:
        for item in order.items.all():
            name = item.product.category.name if item.product.category else "Sin categoría"
            category_totals[name]["units"] += item.quantity
            category_totals[name]["revenue"] += item.line_total
            category_totals[name]["profit"] += item.line_profit

    ws = wb.create_sheet("Categorías")
    ws.append(["Categoría", "Unidades", "Ingresos CLP", "Ganancia CLP"])
    for name, data in sorted(category_totals.items(), key=lambda pair: pair[1]["revenue"], reverse=True):
        ws.append([name, data["units"], data["revenue"], data["profit"]])
    for row in ws.iter_rows(min_row=2, min_col=3, max_col=4):
        for cell in row:
            cell.number_format = "#,##0"
    _style_sheet(ws, [24, 12, 18, 18])

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output
