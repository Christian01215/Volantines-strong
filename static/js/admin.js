/*
 * Volantines Strong — panel de administración.
 * Reconstruido para conservar la etiqueta <script src="js/admin.js"> original.
 * El dashboard es server-rendered: este archivo sólo gestiona las acciones.
 */
(function () {
  'use strict';

  function csrfToken() {
    var input = document.querySelector('[name="csrfmiddlewaretoken"]');
    return input ? input.value : '';
  }

  function post(url, body) {
    return fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': csrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: body || new FormData()
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok || data.ok === false) {
          throw new Error(data.message || 'No se pudo completar la acción.');
        }
        return data;
      });
    });
  }

  // El botón "Actualizar pedidos" de admin.html recarga el server-rendered.
  window.loadAdminOrders = function () {
    window.location.reload();
  };

  // Exportar pedidos a Excel usando el CDN SheetJS del HTML original.
  var exportBtn = document.getElementById('export-orders-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', function () {
      if (!window.XLSX) return;

      var table = document.querySelector('.admin-orders-table');
      if (!table) return;

      var rows = [];
      table.querySelectorAll('thead th').forEach(function (th) {
        rows.push([th.textContent.trim()]);
      });

      var matrix = [];
      var headers = Array.prototype.map.call(
        table.querySelectorAll('thead th'),
        function (th) { return th.textContent.trim(); }
      );
      matrix.push(headers);

      table.querySelectorAll('tbody tr').forEach(function (tr) {
        matrix.push(Array.prototype.map.call(tr.querySelectorAll('td'), function (td) {
          var select = td.querySelector('select');
          if (select) return select.options[select.selectedIndex].text;
          return td.textContent.replace(/\s+/g, ' ').trim();
        }));
      });

      var sheet = XLSX.utils.aoa_to_sheet(matrix);
      var book = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(book, sheet, 'Pedidos');
      XLSX.writeFile(book, 'pedidos-volantines-strong.xlsx');
    });
  }

  // Cambio de estado desde el selector de la tabla.
  document.addEventListener('change', function (event) {
    var select = event.target;
    if (!select.matches('select[data-order-id][data-url]')) return;

    var body = new FormData();
    body.append('status', select.value);
    post(select.dataset.url, body)
      .then(function () { window.location.reload(); })
      .catch(function (error) {
        window.alert(error.message);
        window.location.reload();
      });
  });

  // Acciones de filas: editar producto, eliminar, notificar.
  document.addEventListener('click', function (event) {
    var button = event.target.closest('[data-action], [data-url]');
    if (!button || button.matches('select[data-order-id]')) return;

    var action = button.dataset.action;

    if (action === 'edit-product') {
      var row = button.closest('tr');
      if (!row) return;

      var values = {
        prod_id: row.dataset.id,
        prod_name: row.dataset.name,
        prod_category: row.dataset.category,
        prod_price: row.dataset.price,
        prod_stock: row.dataset.stock,
        prod_specs: row.dataset.specs,
        prod_desc: row.dataset.description
      };
      Object.keys(values).forEach(function (key) {
        var field = document.querySelector('[name="' + key + '"]');
        if (field) field.value = values[key] || '';
      });

      var title = document.getElementById('form-title');
      if (title) title.textContent = 'Editar producto';
      var saveBtn = document.getElementById('save-prod-btn');
      if (saveBtn) saveBtn.textContent = 'Actualizar producto ↗';
      var cancelBtn = document.getElementById('cancel-edit-btn');
      if (cancelBtn) cancelBtn.classList.remove('hidden');

      document.getElementById('product-form').scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }

    if (!button.dataset.url) return;

    if (action === 'delete-product') {
      if (!window.confirm('¿Eliminar este producto?')) return;
    }
    if (action === 'delete-order') {
      if (!window.confirm('¿Eliminar este pedido?')) return;
    }

    post(button.dataset.url)
      .then(function () { window.location.reload(); })
      .catch(function (error) { window.alert(error.message); });
  });

  var cancelBtn = document.getElementById('cancel-edit-btn');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', function () {
      window.location.href = window.location.pathname;
    });
  }

  // Preview de la galería seleccionada en el formulario de producto.
  var galleryInput = document.getElementById('prod-gallery-files');
  var galleryPreview = document.getElementById('product-gallery-preview');
  if (galleryInput && galleryPreview) {
    galleryInput.addEventListener('change', function () {
      galleryPreview.innerHTML = '';
      Array.prototype.slice.call(galleryInput.files).slice(0, 4).forEach(function (file) {
        var item = document.createElement('div');
        item.className = 'gallery-preview-item';
        var img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.alt = file.name;
        item.appendChild(img);
        galleryPreview.appendChild(item);
      });
    });
  }
})();
