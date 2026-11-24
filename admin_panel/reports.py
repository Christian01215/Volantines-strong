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

HEADER_COLOR = "A8262D"
TOTAL_COLOR = "E8E8E8"
MONEY_FORMAT = "#,##0"
PERCENT_FORMAT = "0.0%"


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


def _months_with_data(rows):
    """Cantidad de meses calendario que tienen al menos un pedido."""
    return {_month_key(order.created_at) for order in rows}


def _totals(rows):
    data = {"orders": len(rows), "units": 0, "revenue": 0, "cost": 0, "profit": 0}
    for order in rows:
        for item in order.items.all():
            data["units"] += item.quantity
            data["revenue"] += item.line_total
            data["cost"] += item.cost * item.quantity
            data["profit"] += item.line_profit
    return data


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


def recent_purchases_sales(rows, months=2):
    """Historial de compras (pedidos de clientes) y ventas de los últimos meses."""
    current = _month_key(timezone.now())
    keys = [_add_months(current, -offset) for offset in range(months - 1, -1, -1)]
    totals = {
        key: {"orders": 0, "units": 0, "revenue": 0, "cost": 0, "profit": 0}
        for key in keys
    }

    for order in rows:
        key = _month_key(order.created_at)
        if key not in totals:
            continue
        totals[key]["orders"] += 1
        for item in order.items.all():
            totals[key]["units"] += item.quantity
            totals[key]["revenue"] += item.line_total
            totals[key]["cost"] += item.cost * item.quantity
            totals[key]["profit"] += item.line_profit

    result = []
    for key in keys:
        data = totals[key]
        result.append({
            "label": f"{MONTHS_ES[key.month - 1]} {key.year}",
            "orders": data["orders"],
            "units": data["units"],
            "revenue": data["revenue"],
            "cost": data["cost"],
            "profit": data["profit"],
            "margin": (data["profit"] / data["revenue"]) if data["revenue"] else 0,
            "avg_ticket": (data["revenue"] / data["orders"]) if data["orders"] else 0,
        })
    return result


def _style_sheet(ws, widths):
    fill = PatternFill("solid", fgColor=HEADER_COLOR)
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFFFF")
        cell.fill = fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(index)].width = width
    ws.freeze_panes = "A2"
    if ws.max_row > 2:
        ws.auto_filter.ref = (
            f"A1:{get_column_letter(ws.max_column)}{ws.max_row - 1}"
        )


def _mark_total_row(ws, columns):
    fill = PatternFill("solid", fgColor=TOTAL_COLOR)
    for column in columns:
        cell = ws.cell(row=ws.max_row, column=column)
        cell.font = Font(bold=True, color="111111")
        cell.fill = fill


def _build_executive_sheet(wb, rows, period_label, summary, include_profit):
    ws = wb.active
    ws.title = "Resumen ejecutivo"

    for index, width in enumerate([36, 26, 18, 18], start=1):
        ws.column_dimensions[get_column_letter(index)].width = width

    for row_number, text, color, size in (
        (1, "VOLANTINES STRONG", HEADER_COLOR, 16),
        (2, "INFORME DE VENTAS", "111111", 12),
    ):
        fill = PatternFill("solid", fgColor=color)
        for column in range(1, 5):
            cell = ws.cell(row=row_number, column=column)
            cell.fill = fill
            cell.font = Font(bold=True, color="FFFFFF", size=size)
        ws.cell(row=row_number, column=1, value=text)
        ws.merge_cells(start_row=row_number, start_column=1, end_row=row_number, end_column=4)

    ws["A4"] = "Período"
    ws["B4"] = period_label
    ws["A5"] = "Generado"
    ws["B5"] = timezone.localdate().strftime("%d/%m/%Y")
    for cell_ref in ("A4", "A5"):
        ws[cell_ref].font = Font(bold=True, color=HEADER_COLOR)

    totals = _totals(rows)
    metrics = [
        ("Compras (pedidos de clientes)", totals["orders"], None),
        ("Unidades vendidas", totals["units"], None),
        ("Ventas (CLP)", totals["revenue"], MONEY_FORMAT),
        ("Costo de ventas (CLP)", totals["cost"], MONEY_FORMAT),
        (
            "Ticket promedio (CLP)",
            round(totals["revenue"] / totals["orders"]) if totals["orders"] else 0,
            MONEY_FORMAT,
        ),
    ]
    if include_profit:
        metrics.extend([
            ("Ganancia (CLP)", totals["profit"], MONEY_FORMAT),
            (
                "Margen %",
                (totals["profit"] / totals["revenue"]) if totals["revenue"] else 0,
                PERCENT_FORMAT,
            ),
        ])

    latest = summary[0] if summary else None
    metrics.append((
        "Ventas vs mes anterior",
        latest["revenue_mom"] if latest else "—",
        None,
    ))
    if include_profit:
        metrics.append((
            "Ganancia vs mes anterior",
            latest["profit_mom"] if latest else "—",
            None,
        ))

    fill = PatternFill("solid", fgColor=HEADER_COLOR)
    for column, title in ((1, "Indicador"), (2, "Valor")):
        cell = ws.cell(row=7, column=column, value=title)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = fill
        cell.alignment = Alignment(horizontal="center")

    for offset, (label, value, number_format) in enumerate(metrics, start=8):
        label_cell = ws.cell(row=offset, column=1, value=label)
        label_cell.font = Font(bold=True, color="111111")
        value_cell = ws.cell(row=offset, column=2, value=value)
        if number_format:
            value_cell.number_format = number_format
    ws.freeze_panes = "A8"


def _build_recent_sheet(wb, all_rows, include_profit):
    ws = wb.create_sheet("Compras y ventas 2 meses")
    header = [
        "Mes", "Compras (pedidos)", "Unidades", "Ventas CLP", "Costo de ventas CLP",
    ]
    if include_profit:
        header.extend(["Ganancia CLP", "Margen %"])
    ws.append(header)

    recent_rows = recent_purchases_sales(all_rows)
    for row in recent_rows:
        values = [
            row["label"], row["orders"], row["units"], row["revenue"], row["cost"],
        ]
        if include_profit:
            values.extend([row["profit"], row["margin"]])
        ws.append(values)

    totals_row = [
        "TOTAL",
        sum(row["orders"] for row in recent_rows),
        sum(row["units"] for row in recent_rows),
        sum(row["revenue"] for row in recent_rows),
        sum(row["cost"] for row in recent_rows),
    ]
    if include_profit:
        total_revenue = totals_row[3]
        total_profit = sum(row["profit"] for row in recent_rows)
        totals_row.extend([
            total_profit,
            (total_profit / total_revenue) if total_revenue else 0,
        ])
    ws.append(totals_row)

    widths = [22, 20, 12, 18, 22]
    if include_profit:
        widths.extend([18, 14])
    _style_sheet(ws, widths)

    money_columns = [4, 5] + ([6] if include_profit else [])
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for index in money_columns:
            row[index - 1].number_format = MONEY_FORMAT
        if include_profit:
            row[6].number_format = PERCENT_FORMAT
    _mark_total_row(ws, range(1, len(header) + 1))


def _build_monthly_sheet(wb, summary):
    ws = wb.create_sheet("Resumen mensual")
    ws.append([
        "Mes", "Pedidos", "Unidades", "Ingresos CLP", "Ganancia CLP",
        "Ingresos vs mes anterior", "Ganancia vs mes anterior",
        "Ingresos vs año anterior", "Ganancia vs año anterior",
    ])
    for row in summary:
        ws.append([
            row["label"], row["orders"], row["units"], row["revenue"], row["profit"],
            row["revenue_mom"], row["profit_mom"], row["revenue_yoy"], row["profit_yoy"],
        ])
    ws.append([
        "TOTAL",
        sum(row["orders"] for row in summary),
        sum(row["units"] for row in summary),
        sum(row["revenue"] for row in summary),
        sum(row["profit"] for row in summary),
        "", "", "", "",
    ])
    _style_sheet(ws, [22, 10, 11, 16, 16, 24, 24, 24, 24])
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=4, max_col=5):
        for cell in row:
            cell.number_format = MONEY_FORMAT
    _mark_total_row(ws, range(1, 10))


def _build_orders_sheet(wb, rows):
    ws = wb.create_sheet("Pedidos")
    ws.append([
        "Código", "Fecha", "Cliente", "RUT", "Estado", "Entrega",
        "Total CLP", "Ganancia CLP", "Comprobante",
    ])
    for order in rows:
        local_created = (
            timezone.localtime(order.created_at)
            if timezone.is_aware(order.created_at)
            else order.created_at
        )
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
    ws.append([
        "TOTAL", "", "", "", "", "",
        sum(order.total for order in rows),
        sum(order.total_profit for order in rows),
        "",
    ])
    _style_sheet(ws, [16, 18, 24, 16, 20, 24, 14, 16, 48])
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=7, max_col=8):
        for cell in row:
            cell.number_format = MONEY_FORMAT
    _mark_total_row(ws, range(1, 10))


def _build_detail_sheet(wb, rows):
    ws = wb.create_sheet("Detalle por producto")
    ws.append([
        "Pedido", "Fecha", "Producto", "Categoría", "Cantidad",
        "Precio unit. CLP", "Costo unit. CLP", "Subtotal CLP", "Ganancia CLP", "Diseño",
    ])
    items = []
    for order in rows:
        local_created = (
            timezone.localtime(order.created_at)
            if timezone.is_aware(order.created_at)
            else order.created_at
        )
        for item in order.items.all():
            items.append((order.code, local_created, item))
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
    ws.append([
        "TOTAL", "", "", "", sum(item.quantity for _, _, item in items),
        "", "",
        sum(item.line_total for _, _, item in items),
        sum(item.line_profit for _, _, item in items),
        "",
    ])
    _style_sheet(ws, [16, 13, 26, 18, 10, 16, 16, 16, 16, 42])
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=6, max_col=9):
        for cell in row:
            cell.number_format = MONEY_FORMAT
    _mark_total_row(ws, range(1, 11))


def _build_category_sheet(wb, rows):
    category_totals = defaultdict(lambda: {"units": 0, "revenue": 0, "profit": 0})
    for order in rows:
        for item in order.items.all():
            name = item.product.category.name if item.product.category else "Sin categoría"
            category_totals[name]["units"] += item.quantity
            category_totals[name]["revenue"] += item.line_total
            category_totals[name]["profit"] += item.line_profit

    total_revenue = sum(data["revenue"] for data in category_totals.values())

    ws = wb.create_sheet("Categorías")
    ws.append([
        "Categoría", "Unidades", "Ingresos CLP", "Ganancia CLP", "Participación %",
    ])
    for name, data in sorted(
        category_totals.items(), key=lambda pair: pair[1]["revenue"], reverse=True
    ):
        ws.append([
            name,
            data["units"],
            data["revenue"],
            data["profit"],
            (data["revenue"] / total_revenue) if total_revenue else 0,
        ])
    ws.append([
        "TOTAL",
        sum(data["units"] for data in category_totals.values()),
        total_revenue,
        sum(data["profit"] for data in category_totals.values()),
        1 if total_revenue else 0,
    ])
    _style_sheet(ws, [24, 12, 18, 18, 16])
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=3, max_col=4):
        for cell in row:
            cell.number_format = MONEY_FORMAT
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=5, max_col=5):
        for cell in row:
            cell.number_format = PERCENT_FORMAT
    _mark_total_row(ws, range(1, 6))


def _build_customers_sheet(wb, rows):
    customer_totals = defaultdict(
        lambda: {"name": "", "orders": 0, "units": 0, "revenue": 0, "profit": 0}
    )
    for order in rows:
        key = (order.customer_email or "").strip().lower() or f"cliente-{order.code}"
        data = customer_totals[key]
        data["name"] = order.customer_name or "—"
        data["orders"] += 1
        for item in order.items.all():
            data["units"] += item.quantity
            data["revenue"] += item.line_total
            data["profit"] += item.line_profit

    ws = wb.create_sheet("Clientes")
    ws.append([
        "Cliente", "Correo", "Pedidos", "Unidades", "Ventas CLP",
        "Ganancia CLP", "Ticket promedio CLP",
    ])
    for key, data in sorted(
        customer_totals.items(), key=lambda pair: pair[1]["revenue"], reverse=True
    )[:20]:
        email = "" if key.startswith("cliente-") else key
        ws.append([
            data["name"],
            email,
            data["orders"],
            data["units"],
            data["revenue"],
            data["profit"],
            round(data["revenue"] / data["orders"]) if data["orders"] else 0,
        ])
    ws.append([
        "TOTAL", "",
        sum(data["orders"] for data in customer_totals.values()),
        sum(data["units"] for data in customer_totals.values()),
        sum(data["revenue"] for data in customer_totals.values()),
        sum(data["profit"] for data in customer_totals.values()),
        "",
    ])
    _style_sheet(ws, [26, 30, 10, 11, 16, 16, 22])
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=5, max_col=7):
        for cell in row:
            cell.number_format = MONEY_FORMAT
    _mark_total_row(ws, range(1, 8))


def _build_pickups_sheet(wb, rows):
    today = timezone.localdate()
    pickups = [
        order for order in rows
        if order.pickup_date
        and order.pickup_date >= today
        and order.status not in ("retirado", "cancelado")
    ]
    pickups.sort(key=lambda order: (order.pickup_date, order.pickup_slot))

    ws = wb.create_sheet("Retiros")
    ws.append([
        "Código", "Cliente", "Teléfono", "Fecha retiro", "Franja",
        "Tipo de entrega", "Total CLP", "Estado",
    ])
    for order in pickups[:20]:
        ws.append([
            order.code,
            order.customer_name or "—",
            order.customer_phone or "—",
            order.pickup_date.strftime("%d/%m/%Y"),
            order.pickup_slot or "—",
            order.get_delivery_type_display(),
            order.total,
            order.get_status_display(),
        ])
    ws.append([
        "TOTAL", "", "", "", "", "", sum(order.total for order in pickups), "",
    ])
    _style_sheet(ws, [16, 24, 18, 14, 14, 32, 14, 20])
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=7, max_col=7):
        for cell in row:
            cell.number_format = MONEY_FORMAT
    _mark_total_row(ws, range(1, 9))


def build_orders_workbook(orders, all_orders=None, period_label=None):
    """Construye el XLSX completo y lo devuelve como BytesIO."""
    rows = _fetch_rows(orders)
    all_rows = _fetch_rows(all_orders) if all_orders is not None else rows
    summary = monthly_summary(orders)
    include_profit = len(_months_with_data(all_rows)) > 2

    wb = Workbook()
    _build_executive_sheet(
        wb, rows, period_label or "Todos los pedidos", summary, include_profit
    )
    _build_recent_sheet(wb, all_rows, include_profit)
    _build_monthly_sheet(wb, summary)
    _build_orders_sheet(wb, rows)
    _build_detail_sheet(wb, rows)
    _build_category_sheet(wb, rows)
    _build_customers_sheet(wb, rows)
    _build_pickups_sheet(wb, rows)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output
